from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from models import db, Equipment, Form, User

equipment_bp = Blueprint('equipment_bp', __name__, url_prefix='/api/asset')


def _fmt_date(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value) if value else None


def format_user(user_id):
    if not user_id:
        return None
    user = User.query.filter_by(idUser=user_id).first()
    if not user:
        return None
    return {
        "idUser": user.idUser,
        "name": user.name,
        "department": user.dept.name if user.dept else None,
    }


# Request JSON key -> Equipment model attribute
FIELD_MAP = {
    'name':           'name',
    'category':       'category',
    'status':         'status',
    'model':          'model',
    'specs':          'spec',
    'serial_Number':  'serial_number',
    'notes':          'notes',
    'supplier':       'supplier',
    'purchase_price': 'purchase_price',
    'purchase_date':  'purchase_date',
    'activationDate': 'start_date',
    'warrantyExpiry': 'warranty_expiry',
    'location':       'location',
    'ownerId':        'idOwner',
    'idUser':         'idUser',
    'department':     'department',
    'userDepartment': 'userDepartment',
}


@equipment_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_assets():
    user_id = int(get_jwt_identity())
    role = get_jwt().get('role')

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)

    query = Equipment.query
    if role != 'admin':
        query = query.filter_by(idUser=user_id)

    equipments = query.order_by(Equipment.idEquipment.desc()).all()

    items = []
    for e in equipments:
        assigned_user = format_user(e.idUser)
        items.append({
            "assetNumber": e.idEquipment,
            "name": e.name,
            "category": e.category,
            "model": e.model,
            "location": e.location,
            "department": e.department,
            "status": e.status,
            "idUser": e.idUser,
            "userName": assigned_user["name"] if assigned_user else None,
            "userDepartment": assigned_user["department"] if assigned_user else e.userDepartment,
        })

    return jsonify({
        "total": len(items),
        "items": items,
    }), 200


@equipment_bp.route('/assets/<int:id>', methods=['GET'])
@jwt_required()
def get_asset(id):
    user_id = int(get_jwt_identity())
    role = get_jwt().get('role')

    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")

    if role != 'admin' and equipment.idUser != user_id:
        return jsonify({"message": "權限不足"}), 403

    history = []
    for form in equipment.forms:
        req_year = form.requestDate.year if form.requestDate else datetime.now().year
        reviewer_name = form.reviewer.name if form.reviewer else None
        history.append({
            "id": f"REQ-{req_year}-{form.idForm:03d}",
            "requestDate": form.requestDate.isoformat() if form.requestDate else None,
            "faultDescription": form.issue_description,
            "status": form.status,
            "reviewerId": form.reviewer_id,
            "reviewerName": reviewer_name,
            "reviewNote": form.reviewNote,
            "repairDate": form.repair_start_date.isoformat() if form.repair_start_date else None,
            "repairCost": float(form.repair_cost) if form.repair_cost is not None else None,
            "completionDate": form.repair_end_date.isoformat() if form.repair_end_date else None,
            "repair_solution": form.repair_solution,
            "repair_description": form.repair_description,
        })

    return jsonify({
        **_equipment_to_dict(equipment),
        "maintenanceHistory": history,
    }), 200


@equipment_bp.route('/assets', methods=['POST'])
@jwt_required()
def create_asset():
    if get_jwt().get('role') != 'admin':
        return jsonify({"message": "僅管理員可新增資產"}), 403


    data = request.get_json()
    if not data:
        return jsonify({"message": "未提供資料"}), 400

    # 若有 idUser，優先設為 idUser，否則 fallback ownerId 或 isOwner
    id_user = data.get('idUser') or data.get('ownerId') or data.get('isOwner')
    if id_user is not None:
        equipment = Equipment(idUser=int(id_user))
    else:
        equipment = Equipment(idUser=int(get_jwt_identity()))

    for api_key, model_attr in FIELD_MAP.items():
        if api_key in data:
            setattr(equipment, model_attr, data[api_key])

    try:
        db.session.add(equipment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "新增資產失敗", "error": str(e)}), 500

    return jsonify({"id": equipment.idEquipment}), 201


def _equipment_to_dict(equipment):
    assigned_user = format_user(equipment.idUser)
    owner_user = format_user(equipment.idOwner)
    return {
        "name": equipment.name,
        "category": equipment.category,
        "status": equipment.status,
        "model": equipment.model,
        "specs": equipment.spec,
        "serial_Number": equipment.serial_number,
        "notes": equipment.notes,
        "supplier": equipment.supplier,
        "purchase_price": float(equipment.purchase_price) if equipment.purchase_price is not None else None,
        "purchase_date": _fmt_date(equipment.purchase_date),
        "activationDate": _fmt_date(equipment.start_date),
        "warrantyExpiry": _fmt_date(equipment.warranty_expiry),
        "location": equipment.location,
        "ownerId": equipment.idOwner,
        "ownerName": owner_user["name"] if owner_user else None,
        "isOwner": str(equipment.idUser) if equipment.idUser is not None else None,
        "idUser": equipment.idUser,
        "userName": assigned_user["name"] if assigned_user else None,
        "userDepartment": assigned_user["department"] if assigned_user else equipment.userDepartment,
        "department": equipment.department,
        "version": equipment.version,
    }


@equipment_bp.route('/assets/<int:id>', methods=['PUT'])
@jwt_required()
def update_asset(id):
    if get_jwt().get('role') != 'admin':
        return jsonify({"message": "僅管理員可編輯資產"}), 403

    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")

    data = request.get_json()
    if not data:
        return jsonify({"message": "未提供資料"}), 400

    client_version = data.get('version')
    if client_version is None:
        return jsonify({"message": "缺少 version 欄位"}), 400

    if client_version != equipment.version:
        return jsonify({"success": False, "content": _equipment_to_dict(equipment)}), 409

    for api_key, model_attr in FIELD_MAP.items():
        if api_key in data:
            # isOwner 轉 int 存 idUser
            if api_key == 'isOwner':
                setattr(equipment, model_attr, int(data[api_key]))
            else:
                setattr(equipment, model_attr, data[api_key])

    # 若有 idUser，直接設置
    if 'idUser' in data:
        equipment.idUser = int(data['idUser'])

    equipment.version += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "更新資產失敗", "error": str(e)}), 500

    return jsonify({"success": True}), 200


@equipment_bp.route('/assets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asset(id):
    if get_jwt().get('role') != 'admin':
        return jsonify({"message": "僅管理員可刪除資產"}), 403

    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")

    try:
        db.session.delete(equipment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "刪除資產失敗", "error": str(e)}), 500

    return jsonify({"success": True}), 200


@equipment_bp.route('/status/repairing/<int:id>', methods=['PUT'])
@jwt_required()
def set_status_repairing(id):
    if get_jwt().get('role') != 'admin':
        return jsonify({"message": "僅管理員可修改資產狀態"}), 403

    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")
    equipment.status = 'repairing'

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "更新失敗", "error": str(e)}), 500

    return jsonify({}), 200


@equipment_bp.route('/status/in_use/<int:id>', methods=['PUT'])
@jwt_required()
def set_status_in_use(id):
    if get_jwt().get('role') != 'admin':
        return jsonify({"message": "僅管理員可修改資產狀態"}), 403

    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")
    equipment.status = 'in_use'

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "更新失敗", "error": str(e)}), 500

    return jsonify({}), 200
