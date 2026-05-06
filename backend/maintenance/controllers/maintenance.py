from models.database import db
from models import MaintenanceModel, MaintenanceSchema

class MaintenanceController:
    
    def __init__(self):
        self.schema = MaintenanceSchema
        self.model = MaintenanceModel

    def getAllForms(self) -> list[MaintenanceModel]:
        try:
            return MaintenanceModel.query.all()
        except Exception as e:
            raise e

    def getAllFormsByUserId(self, user_id: int) -> list[MaintenanceModel]:
        try:
            return MaintenanceModel.query.filter_by(applicant_id=user_id).all()
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
        
    def getFormById(self, id: int) -> MaintenanceModel | None:
        try:
            form = self.model.query.get(id)
            if form:
                return form
            return None
        except Exception as e:
            raise e
        
    def updateFormStatusById(self, id: int, status: str) -> MaintenanceModel:
        try:            
            form = self.model.query.get(id)
            if form:
                form.status = status
                db.session.commit()
                return form
            raise ValueError("Form not found")
        except Exception as e:
            db.session.rollback()
            raise e
        
    def updateFormById(self, id: int, data: dict) -> MaintenanceModel:
        try:
            form = self.model.query.get(id)
            if form:
                for key, value in data.items():
                    setattr(form, key, value)
                db.session.commit()
                return form
            raise ValueError("Form not found")
        except Exception as e:
            db.session.rollback()
            raise e

maintenance_controller = MaintenanceController()