import os
from flask import Flask
from dotenv import load_dotenv
from routes import register_blueprints
from models.database import db

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    register_blueprints(app)
    db.init_app(app)
    return app

app = create_app()