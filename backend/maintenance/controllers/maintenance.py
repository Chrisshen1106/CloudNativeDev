from models.database import db
from models import MaintenanceModel, MaintenanceSchema

class MaintenanceController:
    
    def __init__(self):
        self.schema = MaintenanceSchema
        self.model = MaintenanceModel

    def get_all_forms(self) -> list[MaintenanceModel]:
        try:
            return MaintenanceModel.query.all()
        except Exception as e:
            raise e

    def get_all_forms_by_user_id(self, user_id: int) -> list[MaintenanceModel]:
        try:
            return MaintenanceModel.query.filter_by(applicant_id=user_id).all()
        except Exception as e:
            raise e

    def create_form(self, data: dict) -> MaintenanceModel:
        try:
            new_form = MaintenanceModel(**data)
            db.session.add(new_form)
            db.session.commit()
            return new_form
        except Exception as e:
            db.session.rollback()
            raise e
        
    def get_form_by_id(self, id: int) -> MaintenanceModel | None:
        try:
            form = self.model.query.get(id)
            if form:
                return form
            return None
        except Exception as e:
            raise e
        
    def update_form_status_by_id(self, id: int, status: str) -> MaintenanceModel:
        try:            
            form = self.model.query.get(id)
            if form:
                form.status = status
                # 如果是完成維修，應該也要把資產狀態設回 in_use
                if status == 'completed':
                   from sqlalchemy import text
                   db.session.execute(text("UPDATE Equipment SET status = 'in_use' WHERE idEquipment = :id"), {'id': form.idEquipment})
                db.session.commit()
                return form
            raise ValueError("Form not found")
        except Exception as e:
            db.session.rollback()
            raise e
        
    def update_form_by_id(self, id: int, data: dict) -> MaintenanceModel:
        try:
            form = self.model.query.get(id)
            if form:
                print('update_form_by_id data:', data)
                for key, value in data.items():
                    print(f'setting {key} = {value}')
                    setattr(form, key, value)
                
                # 同步更新資產狀態
                if 'status' in data:
                    from sqlalchemy import text
                    if data['status'] in ['approved', 'repairing']:
                        db.session.execute(text("UPDATE Equipment SET status = 'repairing' WHERE idEquipment = :id"), {'id': form.idEquipment})
                    elif data['status'] == 'completed':
                        db.session.execute(text("UPDATE Equipment SET status = 'in_use' WHERE idEquipment = :id"), {'id': form.idEquipment})

                db.session.commit()
                print('after commit, reviewer_id:', getattr(form, 'reviewer_id', None))
                return form
            raise ValueError("Form not found")
        except Exception as e:
            db.session.rollback()
            raise e
        
    def delete_form_by_id(self, id: int) -> None:
        try:
            form = self.model.query.get(id)
            if form:
                # 刪除前先把資產狀態設回 in_use，避免資產卡在維修狀態
                from sqlalchemy import text
                db.session.execute(text("UPDATE Equipment SET status = 'in_use' WHERE idEquipment = :id"), {'id': form.idEquipment})
                
                db.session.delete(form)
                db.session.commit()
                return
            raise ValueError("Form not found")
        except Exception as e:
            db.session.rollback()
            raise e

maintenance_controller = MaintenanceController()