from marshmallow import Schema, fields, validate
from models.database import db

class MaintenanceSchema(Schema):
    idForm = fields.Int(dump_only=True)
    applicant_id = fields.Int(required=True)
    idEquipment = fields.Int(required=True)
    reviewer_id = fields.Int(required=False)

    issue_description = fields.Str(required=False, validate=validate.Length(max=255))
    status = fields.Str(required=False, validate=validate.OneOf(['pending', 'approved', 'rejected', 'repairing', 'completed']))
    review_result = fields.Str(required=False, validate=validate.OneOf(['approved', 'rejected']))
    repair_start_date = fields.DateTime(required=False)
    repair_end_date = fields.DateTime(required=False)
    repair_description = fields.Str(required=False, validate=validate.Length(max=255))
    repair_solution = fields.Str(required=False, validate=validate.Length(max=255))
    repair_cost = fields.Decimal(as_string=True, required=False, places=2)
    repair_vendor = fields.Str(required=False, validate=validate.Length(max=100))
    repair_person = fields.Str(required=False, validate=validate.Length(max=100))

class MaintenanceModel(db.Model):
    __tablename__ = 'Form'
    
    idForm = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.Integer, nullable=False)
    idEquipment = db.Column(db.Integer, nullable=False)
    reviewer_id = db.Column(db.Integer, nullable=True)

    issue_description = db.Column(db.String(255), nullable=True)
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', 'repairing', 'completed', name='status_enum'),
        default='pending',
        nullable=False,
    )
    review_result = db.Column(db.Enum('approved', 'rejected', name='review_result_enum'))
    repair_start_date = db.Column(db.DateTime)
    repair_end_date = db.Column(db.DateTime)
    repair_description = db.Column(db.String(255))
    repair_solution = db.Column(db.String(255))
    repair_cost = db.Column(db.Numeric(10, 2))
    repair_vendor = db.Column(db.String(100))
    repair_person = db.Column(db.String(100))