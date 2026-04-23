from models.database import db
from models.department import DepartmentSchema, DepartmentModel

class DepartmentController:
    def __init__(self, db, department_schema, department_model):
        self.db = db
        self.department_schema = department_schema
        self.department_model = department_model
        
department_model = DepartmentModel()
department_schema = DepartmentSchema()
department_controller = DepartmentController(db, department_schema, department_model)