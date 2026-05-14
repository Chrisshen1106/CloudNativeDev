from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'department'
    
    idDepartment = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))

    # 建立與使用者的關聯 (一對多)
    users = db.relationship('User', backref='dept', lazy=True)

class User(db.Model):
    __tablename__ = 'User'
    
    idUser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    idDepartment = db.Column(db.Integer, db.ForeignKey('department.idDepartment'), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), nullable=False, server_default='user')

    # 建立與設備的關聯
    equipments = db.relationship('Equipment', backref='owner', lazy=True)

class Equipment(db.Model):
    __tablename__ = 'Equipment'
    
    idEquipment = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # asset_uid = db.Column(db.String(20), unique=True, nullable=False)
    idUser = db.Column(db.Integer, db.ForeignKey('User.idUser'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    model = db.Column(db.String(100))
    spec = db.Column(db.String(255))
    serial_number = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(10, 2))
    location = db.Column(db.String(100))
    department = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    status = db.Column(db.Enum('in_use', 'repairing', 'scrapped'), nullable=False, server_default='in_use')
    idOwner = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.String(255), nullable=True)

    # is_deleted = db.Column(db.Boolean, default=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Form(db.Model):
    __tablename__ = 'Form'
    
    idForm = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('User.idUser'), nullable=False)
    idEquipment = db.Column(db.Integer, db.ForeignKey('Equipment.idEquipment'), nullable=False)
    issue_description = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('User.idUser'))
    review_result = db.Column(db.String(100))
    repair_start_date = db.Column(db.Date)
    repair_end_date = db.Column(db.Date)
    repair_description = db.Column(db.Text)
    repair_solution = db.Column(db.Text)
    repair_cost = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50))
    repair_vendor = db.Column(db.String(100))
    repair_person = db.Column(db.String(100))
    reviewNote = db.Column(db.String(255))
    requestDate = db.Column(db.DateTime, default=datetime.utcnow)

    # 建立關聯
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='submitted_forms')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_forms')
    equipment = db.relationship('Equipment', backref='forms')
