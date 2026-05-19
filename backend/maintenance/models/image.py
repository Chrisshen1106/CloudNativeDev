from datetime import datetime
from marshmallow import Schema, fields, validate
from models.database import db

class ImageSchema(Schema):
    id = fields.Str(dump_only=True)
    image_id = fields.Str(required=True, validate=validate.Length(max=255))
    user_id = fields.Int(required=True)
    bucket = fields.Str(required=True)
    object_key = fields.Str(required=True)
    fileName = fields.Str(required=True, validate=validate.Length(max=255))
    contentType = fields.Str(required=True, validate=validate.Length(max=100))
    created_at = fields.DateTime(dump_only=True)


class ImageModel(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    bucket = db.Column(db.String(255), nullable=False)
    object_key = db.Column(db.String(255), nullable=False)
    fileName = db.Column(db.String(255), nullable=False)
    contentType = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)