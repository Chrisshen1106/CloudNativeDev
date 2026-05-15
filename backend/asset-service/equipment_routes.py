from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from models import db, Equipment, Form, User

equipment_bp = Blueprint('equipment_bp', __name__, url_prefix='/api')


def format_asset_number(equipment):
    year = equipment.purchase_date.year if equipment.purchase_date else datetime.now().year
    return equipment.idEquipment;


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
    'department':     'department',
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

    items = [
        {
            "assetNumber": format_asset_number(e),
            "name": e.name,
            "category": e.category,
            "model": e.model,
            "location": e.location,
            "department": e.department,
            "status": e.status, 
        }
        for e in equipments
    ]

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
            "reviewerId": form.reviewer_id,
            "reviewerName": reviewer_name,
            "reviewNote": form.repair_description,
            "repairDate": form.repair_start_date.isoformat() if form.repair_start_date else None,
            "repairCost": float(form.repair_cost) if form.repair_cost is not None else None,
            "completionDate": form.repair_end_date.isoformat() if form.repair_end_date else None,
        })

    return jsonify({
        "assetNumber": format_asset_number(equipment),
        "name": equipment.name,
        "category": equipment.category,
        "model": equipment.model,
        "specs": equipment.spec,
        "serialNumber": equipment.serial_number,
        "supplier": equipment.supplier,
        "purchaseDate": equipment.purchase_date.isoformat() if equipment.purchase_date else None,
        "purchasePrice": float(equipment.purchase_price) if equipment.purchase_price is not None else None,
        "location": equipment.location,
        "ownerId": equipment.idOwner,
        "department": equipment.department,
        "activationDate": equipment.start_date.isoformat() if equipment.start_date else None,
        "warrantyExpiry": equipment.warranty_expiry.isoformat() if equipment.warranty_expiry else None,
        "status": equipment.status,
        "notes": equipment.notes,
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


    # 若有 ownerId，則 idUser 也設為 ownerId，確保資產歸屬正確
    id_user = data.get('ownerId')
    if id_user is not None:
      equipment = Equipment(idUser=id_user)
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


@equipment_bp.route('/assets/<int:id>', methods=['PUT'])
@jwt_required()
def update_asset(id):
    if get_jwt().get('role') != 'admin':
        return jsonify({"message": "僅管理員可編輯資產"}), 403

    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")

    data = request.get_json()
    if not data:
        return jsonify({"message": "未提供資料"}), 400

    for api_key, model_attr in FIELD_MAP.items():
        if api_key in data:
            setattr(equipment, model_attr, data[api_key])

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


@equipment_bp.route('/asset/status/repairing/<int:id>', methods=['PUT'])
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


@equipment_bp.route('/asset/status/in_use/<int:id>', methods=['PUT'])
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