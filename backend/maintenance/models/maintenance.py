from marshmallow import Schema, fields, validate
from models.database import db

class MaintenanceSchema(Schema):
    idForm = fields.Int(dump_only=True)
    applicant_id = fields.Int(required=True)
    idEquipment = fields.Int(required=True)
    reviewer_id = fields.Int(required=True)

    issue_description = fields.Str(required=True, validate=validate.Length(max=255))
    status = fields.Str(required=True, validate=validate.OneOf(['pending', 'approved', 'rejected', 'repairing', 'completed']))
    review_result = fields.Str(required=True, validate=validate.OneOf(['approved', 'rejected']))
    repair_start_date = fields.DateTime(required=True)
    repair_end_date = fields.DateTime(required=True)
    repair_description = fields.Str(required=True, validate=validate.Length(max=255))
    repair_solution = fields.Str(required=True, validate=validate.Length(max=255))
    repair_cost = fields.Decimal(as_string=True, required=True, places=2)
    repair_vendor = fields.Str(required=True, validate=validate.Length(max=100))
    repair_person = fields.Str(required=True, validate=validate.Length(max=100))

class MaintenanceModel(db.Model):
    __tablename__ = 'Form'
    
    idForm = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('User.idUser'), nullable=False)
    idEquipment = db.Column(db.Integer, db.ForeignKey('Equipment.idEquipment'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('User.idUser'), nullable=False)

    issue_description = db.Column(db.String(255))
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'repairing', 'completed', name='status_enum'))
    review_result = db.Column(db.Enum('approved', 'rejected', name='review_result_enum'))
    repair_start_date = db.Column(db.DateTime)
    repair_end_date = db.Column(db.DateTime)
    repair_description = db.Column(db.String(255))
    repair_solution = db.Column(db.String(255))
    repair_cost = db.Column(db.Decimal(10, 2))
    repair_vendor = db.Column(db.String(100))
    repair_person = db.Column(db.String(100))