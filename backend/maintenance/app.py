import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from routes import register_blueprints
from models.database import db

load_dotenv()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    register_blueprints(app)
    db.init_app(app)
    jwt.init_app(app)
    return app

app = create_app()