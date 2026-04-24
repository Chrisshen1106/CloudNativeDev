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
    
    def getUserByEmail(self, data: dict) -> dict | None:
        try:
            validated_data = self.schema(only=['email']).load(data)
            user = self.model.query.filter_by(email=validated_data['email']).first()
            if user:
                return self.schema().dump(user)
            return None
        except Exception as e:
            raise ValueError(f"Error getting user by email: {e}")
    
    def getAllUsers(self) -> list[dict]:
        users = self.model.query.all()
        return self.schema(many=True).dump(users)
        
user_controller = UserController()