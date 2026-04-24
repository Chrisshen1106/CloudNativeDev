from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_
from datetime import datetime
from models import db, Equipment
from schemas import equipment_schema, equipments_schema

# 建立 Blueprint
equipment_bp = Blueprint('equipment_bp', __name__, url_prefix='/api/equipment')

@equipment_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    取得目前所有存在的資產分類 (Category)
    ---
    tags:
      - Equipment
    responses:
      200:
        description: 成功取得分類列表
    """
    # 透過 SQLAlchemy 找出獨立的 (distinct) category，並且排除掉空值 (None 或空字串)
    query = db.session.query(Equipment.category).distinct()
    
    # 權限控管：這裡也可以做限制，如果是一般員工只看到自己有的 category，管理員看全公司有的
    if getattr(g, 'user_role', 'user') != 'admin':
        user_id = getattr(g, 'user_id', None)
        query = query.filter(Equipment.idUser == user_id)
        
    categories = [row.category for row in query.all() if row.category]
    return jsonify(categories), 200

@equipment_bp.route('', methods=['GET'])
def get_equipments():
    """
    取得資產列表
    ---
    tags:
      - Equipment
    description: 支援全域模糊搜尋 (keyword) 以及依分類 (category)、狀態 (status) 進行篩選
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
      - name: keyword
        in: query
        type: string
        description: 全域搜尋 (支援搜尋 ID, 名稱, 分類, 型號, 規格, 地點, 部門, 狀態, 日期等所有欄位)
      - name: category
        in: query
        type: string
        description: 依分類精確篩選 (在此欄位手動輸入，或參考 /api/equipment/categories)
      - name: status
        in: query
        type: string
        enum: ['in_use', 'repairing', 'scrapped']
        description: "依狀態精確篩選"
      - name: idUser
        in: query
        type: integer
        description: 依使用者 ID 精確篩選
    responses:
      200:
        description: 成功取得資產列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Equipment.query
    
    # 權限控管：一般使用者只能看自己的，管理員可看全部
    if getattr(g, 'user_role', 'user') != 'admin':
        # 假設 g.user_id 存在
        user_id = getattr(g, 'user_id', None)
        query = query.filter_by(idUser=user_id)

    # 關鍵字全域模糊搜尋 (所有欄位)
    keyword = request.args.get('keyword')
    if keyword:
        kw = f"%{keyword}%"
        search_filter = or_(
            db.cast(Equipment.idEquipment, db.String).ilike(kw),
            db.cast(Equipment.idUser, db.String).ilike(kw),
            Equipment.name.ilike(kw),
            Equipment.category.ilike(kw),
            Equipment.model.ilike(kw),
            Equipment.spec.ilike(kw),
            Equipment.serial_number.ilike(kw),
            Equipment.supplier.ilike(kw),
            db.cast(Equipment.purchase_date, db.String).ilike(kw),
            db.cast(Equipment.purchase_price, db.String).ilike(kw),
            Equipment.location.ilike(kw),
            Equipment.department.ilike(kw),
            db.cast(Equipment.start_date, db.String).ilike(kw),
            db.cast(Equipment.warranty_expiry, db.String).ilike(kw),
            Equipment.status.ilike(kw)
        )
        query = query.filter(search_filter)

    # 分類篩選
    category = request.args.get('category')
    if category:
        query = query.filter(Equipment.category == category)

    # 狀態篩選
    status = request.args.get('status')
    if status:
        query = query.filter(Equipment.status == status)

    # 依使用者 ID 篩選
    filter_idUser = request.args.get('idUser', type=int)
    if filter_idUser:
        query = query.filter(Equipment.idUser == filter_idUser)

    # 分頁處理 (由於沒有 created_at，改用 idEquipment 排序)
    pagination = query.order_by(Equipment.idEquipment.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
        "data": equipments_schema.dump(pagination.items)
    }), 200

@equipment_bp.route('/<int:id>', methods=['GET'])
def get_equipment(id):
    """
    取得單一資產詳情
    ---
    tags:
      - Equipment
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 成功取得資產
      404:
        description: 找不到該資產
    """
    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")
    
    # 權限檢核
    if getattr(g, 'user_role', 'user') != 'admin' and equipment.idUser != getattr(g, 'user_id', None):
        return jsonify({"message": "權限不足"}), 403
        
    return jsonify(equipment_schema.dump(equipment)), 200

@equipment_bp.route('', methods=['POST'])
def create_equipment():
    """
    新增資產
    ---
    tags:
      - Equipment
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            idUser:
              type: integer
              example: 1
            name:
              type: string
              example: "MacBook Pro"
            category:
              type: string
              example: "電腦類"
            model:
              type: string
              example: "16-inch 2024"
            spec:
              type: string
            serial_number:
              type: string
            supplier:
              type: string
            purchase_date:
              type: string
              format: date
              example: "2026-04-18"
            purchase_price:
              type: number
            location:
              type: string
            department:
              type: string
            start_date:
              type: string
              format: date
            warranty_expiry:
              type: string
              format: date
            status:
              type: string
              enum: ['in_use', 'repairing', 'scrapped']
    responses:
      201:
        description: 成功新增資產
      400:
        description: 資料格式錯誤
    """
    # 權限：假設只有管理員可以新增資產
    if getattr(g, 'user_role', 'user') != 'admin':
        return jsonify({"message": "僅管理員可新增資產"}), 403
        
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "未提供資料"}), 400

    # 驗證傳入資料
    errors = equipment_schema.validate(json_data)
    if errors:
        return jsonify({"message": "資料格式錯誤", "errors": errors}), 400

    new_equipment = Equipment(**json_data)
    
    try:
        db.session.add(new_equipment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "建立資產失敗", "error": str(e)}), 500

    return jsonify(equipment_schema.dump(new_equipment)), 201

@equipment_bp.route('/<int:id>', methods=['PATCH'])
def update_equipment(id):
    """
    更新資產資訊
    ---
    tags:
      - Equipment
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            idUser:
              type: integer
            name:
              type: string
            category:
              type: string
            model:
              type: string
            spec:
              type: string
            serial_number:
              type: string
            supplier:
              type: string
            purchase_date:
              type: string
              format: date
            purchase_price:
              type: number
            location:
              type: string
            department:
              type: string
            start_date:
              type: string
              format: date
            warranty_expiry:
              type: string
              format: date
            status:
              type: string
              enum: ['in_use', 'repairing', 'scrapped']
          example:
            idUser: 1
            name: "MacBook Pro"
            category: "電腦類"
            model: "16-inch 2024"
            spec: "M3 Max, 64GB RAM, 2TB SSD"
            serial_number: "C02XR123456"
            supplier: "Apple"
            purchase_date: "2024-01-10"
            purchase_price: 120000
            location: "A辦公室"
            department: "工程部"
            start_date: "2024-01-15"
            warranty_expiry: "2027-01-14"
            status: "repairing"
    responses:
      200:
        description: 成功更新資產
      400:
        description: 資料格式錯誤或未提供資料
      403:
        description: 權限不足，僅管理員可更新資產
      404:
        description: 找不到該資產
    """
    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")

    if getattr(g, 'user_role', 'user') != 'admin':
        return jsonify({"message": "僅管理員可更新資產"}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "未提供更新資料"}), 400

    errors = equipment_schema.validate(json_data, partial=True) # partial=True 允許部分更新
    if errors:
        return jsonify({"message": "資料格式錯誤", "errors": errors}), 400

    for key, value in json_data.items():
        if hasattr(equipment, key):
            setattr(equipment, key, value)

    db.session.commit()
    return jsonify(equipment_schema.dump(equipment)), 200

@equipment_bp.route('/<int:id>', methods=['DELETE'])
def delete_equipment(id):
    """
    刪除資產
    ---
    tags:
      - Equipment
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 資產已成功刪除
      404:
        description: 找不到該資產
    """
    equipment = Equipment.query.filter_by(idEquipment=id).first_or_404(description="找不到該資產")

    if getattr(g, 'user_role', 'user') != 'admin':
        return jsonify({"message": "僅管理員可刪除資產"}), 403

    # 實作硬刪除 (因為資料庫沒有 is_deleted 欄位)
    db.session.delete(equipment)
    db.session.commit()
    
    return jsonify({"message": "資產已成功刪除"}), 200

@equipment_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_equipments(user_id):
    """
    取得特定使用者的資產列表
    ---
    tags:
      - Equipment
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 使用者 ID
    responses:
      200:
        description: 成功取得該使用者的資產
    """
    equipments = Equipment.query.filter_by(idUser=user_id).all()
    return jsonify(equipments_schema.dump(equipments)), 200

@equipment_bp.route('/admin/by-users', methods=['GET'])
def get_equipments_by_users():
    """
    (管理員) 搜尋特定多位使用者的資產
    ---
    tags:
      - Equipment
    parameters:
      - name: user_ids
        in: query
        type: string
        required: true
        description: 使用者 ID 列表，以逗號分隔 (例如 1,2,3)
    responses:
      200:
        description: 成功取得資產列表
      400:
        description: 參數錯誤
      403:
        description: 權限不足，僅管理員可用
    """
    if getattr(g, 'user_role', 'user') != 'admin':
        return jsonify({"message": "權限不足，僅管理員可用"}), 403
        
    user_ids_str = request.args.get('user_ids', '')
    if not user_ids_str:
        return jsonify({"message": "請提供 user_ids 參數，例如 ?user_ids=1,2,3"}), 400
        
    try:
        # 將 "1, 2, 3" 轉換成整數陣列 [1, 2, 3]
        user_ids = [int(u.strip()) for u in user_ids_str.split(',') if u.strip()]
    except ValueError:
        return jsonify({"message": "user_ids 格式錯誤，請傳入整數並以逗號分隔"}), 400
        
    equipments = Equipment.query.filter(Equipment.idUser.in_(user_ids)).all()
    return jsonify(equipments_schema.dump(equipments)), 200

@equipment_bp.route('/admin/stats', methods=['GET'])
def get_admin_equipment_stats():
    """
    (管理員) 取得全系統所有資產的統計數量
    ---
    tags:
      - Equipment
    responses:
      200:
        description: 成功取得所有資產統計
    """
    query = Equipment.query
    
    total = query.count()
    in_use = query.filter_by(status='in_use').count()
    repairing = query.filter_by(status='repairing').count()
    scrapped = query.filter_by(status='scrapped').count()
    
    return jsonify({
        "total": total,
        "in_use": in_use,
        "repairing": repairing,
        "scrapped": scrapped
    }), 200

@equipment_bp.route('/user/<int:user_id>/stats', methods=['GET'])
def get_user_equipment_stats(user_id):
    """
    (一般使用者) 取得特定使用者的資產統計數量
    ---
    tags:
      - Equipment
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 使用者 ID
    responses:
      200:
        description: 成功取得該使用者的資產統計
    """
    query = Equipment.query.filter_by(idUser=user_id)
        
    total = query.count()
    in_use = query.filter_by(status='in_use').count()
    repairing = query.filter_by(status='repairing').count()
    scrapped = query.filter_by(status='scrapped').count()
    
    return jsonify({
        "total": total,
        "in_use": in_use,
        "repairing": repairing,
        "scrapped": scrapped
    }), 200

@equipment_bp.route('/admin/status/<string:status_val>', methods=['GET'])
def get_admin_equipments_by_status(status_val):
    """
    (管理員) 依狀態取得所有資產 (正常使用、維修中...)
    ---
    tags:
      - Equipment
    parameters:
      - name: status_val
        in: path
        type: string
        required: true
        enum: ['in_use', 'repairing', 'scrapped']
        description: "資產狀態 (in_use: 正常使用, repairing: 維修中)"
    responses:
      200:
        description: 成功取得該狀態的所有資產
    """
    equipments = Equipment.query.filter_by(status=status_val).all()
    return jsonify(equipments_schema.dump(equipments)), 200

@equipment_bp.route('/user/<int:user_id>/status/<string:status_val>', methods=['GET'])
def get_equipments_by_user_and_status(user_id, status_val):
    """
    (一般使用者) 依狀態取得特定使用者的資產 (正常使用、維修中...)
    ---
    tags:
      - Equipment
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 使用者 ID
      - name: status_val
        in: path
        type: string
        required: true
        enum: ['in_use', 'repairing', 'scrapped']
        description: "資產狀態 (in_use: 正常使用, repairing: 維修中)"
    responses:
      200:
        description: 成功取得該使用者特定狀態的資產
    """
    equipments = Equipment.query.filter_by(idUser=user_id, status=status_val).all()
    return jsonify(equipments_schema.dump(equipments)), 200
