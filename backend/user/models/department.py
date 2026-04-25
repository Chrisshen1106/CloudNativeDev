from marshmallow import Schema, fields, validate
from models.database import db

class DepartmentSchema(Schema):
    idDepartment = fields.Integer(dump_only=True)
    name = fields.String(required=True)

class DepartmentModel(db.Model):
    __tablename__ = 'department'
    
    idDepartment = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    
    users = db.relationship("UserModel", back_populates="department")