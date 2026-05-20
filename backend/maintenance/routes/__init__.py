from routes.root import root_bp
from routes.maintenance import maintenance_bp
from routes.upload_image import uploadImg_bp

def register_blueprints(app):
    app.register_blueprint(root_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(uploadImg_bp)