from models.database import db
from models.user import UserSchema, UserModel

class UserController:
    def __init__(self, db, user_schema, user_model):
        self.db = db
        self.user_schema = user_schema
        self.user_model = user_model
        
user_model = UserModel()
user_schema = UserSchema()
user_controller = UserController(db, user_schema, user_model)