from marshmallow import Schema, fields, validate

class DepartmentSchema(Schema):
    idDepartment = fields.Int(dump_only=True)
    name = fields.Str(validate=validate.Length(max=100))

department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)

class UserSchema(Schema):
    idUser = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    email = fields.Email(required=True, validate=validate.Length(max=45))
    idDepartment = fields.Int(required=True)
    dept = fields.Nested(DepartmentSchema(only=('name',)), dump_only=True)
    role = fields.Str(validate=validate.OneOf(['user', 'admin']), missing='user')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class EquipmentSchema(Schema):
    idEquipment = fields.Int(dump_only=True)
    asset_uid = fields.Str(dump_only=True)
    
    # 關聯負責人資料，提取 name 和 dept
    owner = fields.Nested(UserSchema(only=('name', 'dept')), dump_only=True)
    idUser = fields.Int(required=True)
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(validate=validate.Length(max=100), allow_none=True)
    model = fields.Str(validate=validate.Length(max=100), allow_none=True)
    spec = fields.Str(validate=validate.Length(max=255), allow_none=True)
    serial_number = fields.Str(validate=validate.Length(max=100), allow_none=True)
    supplier = fields.Str(validate=validate.Length(max=100), allow_none=True)
    purchase_date = fields.Date(allow_none=True)
    purchase_price = fields.Decimal(as_string=True, allow_none=True)
    location = fields.Str(validate=validate.Length(max=100), allow_none=True)
    department = fields.Str(validate=validate.Length(max=100), allow_none=True)
    start_date = fields.Date(allow_none=True)
    warranty_expiry = fields.Date(allow_none=True)
    status = fields.Str(validate=validate.OneOf(['in_use', 'repairing', 'scrapped']), missing='in_use')
    
    # created_at = fields.DateTime(dump_only=True)
    # updated_at = fields.DateTime(dump_only=True)

equipment_schema = EquipmentSchema()
equipments_schema = EquipmentSchema(many=True)
