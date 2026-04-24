from models.database import db
from models import UserSchema, UserModel

class UserController:
    def createUser(self, data: dict) -> dict:
        try:
            schema = UserSchema()
            user_data = schema.load(data)
            new_user = UserModel(**user_data)
            db.session.add(new_user)
            db.session.commit()
            return schema.dump(new_user)
        except Exception as e:
            raise ValueError(f"Error creating user: {e}")
    
    def getUserById(self, id: int) -> dict | None:
        try:
            user = UserModel.query.get(id)
            if user:
                return UserSchema().dump(user)
            return None
        except Exception as e:
            raise ValueError(f"Error getting user by ID: {e}")
    
    def getAllUsers(self) -> list[dict]:
        users = UserModel.query.all()
        return UserSchema(many=True).dump(users)
        
user_controller = UserController()