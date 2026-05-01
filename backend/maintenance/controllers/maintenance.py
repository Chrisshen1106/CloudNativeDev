from models.database import db
from models import MaintenanceModel, MaintenanceSchema

class MaintenanceController:
    
    def __init__(self):
        self.schema = MaintenanceSchema
        self.model = MaintenanceModel

    def getAllForms(self) -> list[dict]:
        try:
            schema = MaintenanceSchema(many=True)
            maintenances = MaintenanceModel.query.all()
            return schema.dump(maintenances)
        except Exception as e:
            raise e

    def createForm(self, data: dict) -> MaintenanceModel:
        try:
            new_form = MaintenanceModel(**data)
            db.session.add(new_form)
            db.session.commit()
            return new_form
        except Exception as e:
            db.session.rollback()
            raise e
        
    def getMaintenanceById(self, id: int) -> dict:
        try:
            schema = MaintenanceSchema()
            maintenance = MaintenanceModel.query.get(id)
            if maintenance:
                return schema.dump(maintenance)
            raise ValueError("Maintenance record not found")
        except Exception as e:
            raise e
        
    def getAllMaintenanceByUserId(self, user_id: int) -> list:
        try:
            schema = MaintenanceSchema(many=True)
            maintenances = MaintenanceModel.query.filter_by(applicant_id=user_id).all()
            if maintenances:
                return schema.dump(maintenances)
            raise ValueError(f"No maintenance records found for the specified user id: {user_id}")
        except Exception as e:
            raise e
        
    def updateMaintenanceStatusById(self, id: int, data: dict) -> dict:
        try:
            schema = MaintenanceSchema()
            update_data = schema.load(data, partial=True)
            
            if 'status' not in update_data:
                raise ValueError("Status field is required for update")
            maintenance = MaintenanceModel.query.get(id)
            if maintenance:
                maintenance.status = update_data['status']
                db.session.commit()
                return schema.dump(maintenance)
            raise ValueError("Maintenance record not found")
        except Exception as e:
            db.session.rollback()
            raise e

maintenance_controller = MaintenanceController()