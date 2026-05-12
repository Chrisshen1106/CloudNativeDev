from models.database import db
from models import UserSchema, UserModel

class UserController:
    def __init__(self):
        self.schema = UserSchema
        self.model = UserModel
        
    def createUser(self, data: dict) -> dict:
        try:
            schema = self.schema()
            user_data = schema.load(data)
            new_user = self.model(**user_data)
            db.session.add(new_user)
            db.session.commit()
            return schema.dump(new_user)
        except Exception as e:
            raise ValueError(f"Error creating user: {e}")
    
    def getUserById(self, id: int) -> dict | None:
        try:
            user = self.model.query.get(id)
            if user:
                return self.schema().dump(user)
            return None
        except Exception as e:
            raise ValueError(f"Error getting user by ID: {e}")
    
    def getUserByEmail(self, email: str) -> UserModel | None:
        try:
            user = self.model.query.filter_by(email=email).first()
            if user:
                return user
            return None
        except Exception as e:
            raise ValueError(f"Error getting user by email: {e}")
    
    def getAllUsers(self) -> list[UserModel]:
        users = self.model.query.all()
        return users
    
    def deleteUserById(self, id: int) -> bool:
        try:
            user = self.model.query.get(id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            raise ValueError(f"Error deleting user by ID: {e}")

user_controller = UserController()