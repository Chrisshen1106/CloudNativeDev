from marshmallow import Schema, fields, validate
from models.database import db

class UserSchema(Schema):
    idUser = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    idDepartment = fields.Integer(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['user', 'admin']))
    

class UserModel(db.Model):
    __tablename__ = 'User'
    
    idUser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    idDepartment = db.Column(db.Integer, db.ForeignKey('department.idDepartment'), nullable=False)
    role = db.Column(db.Enum('user', 'admin', name='user_role'), nullable=False)
    
    department = db.relationship("DepartmentModel", back_populates="users")