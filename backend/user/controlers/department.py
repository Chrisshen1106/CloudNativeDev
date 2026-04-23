from models.database import db
from models import DepartmentSchema, DepartmentModel

class DepartmentController:
    def createDepartment(self, data: dict) -> dict | None:
        try:
            schema = DepartmentSchema()
            department_data = schema.load(data)
            new_department = DepartmentModel(**department_data)
            db.session.add(new_department)
            db.session.commit()
            return schema.dump(new_department)
        except Exception as e:
            print(f"Error creating department: {e}")
            return None
    
    def getDepartmentById(self, id: int) -> dict | None:
        department = DepartmentModel.query.get(id)
        if department:
            return DepartmentSchema().dump(department)
        return None
    
    def getAllDepartments(self) -> list[dict]:
        departments = DepartmentModel.query.all()
        return DepartmentSchema(many=True).dump(departments)

department_controller = DepartmentController()