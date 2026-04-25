from routes.root import root_bp
from routes.maintenance import maintenance_bp

def register_blueprints(app):
    app.register_blueprint(root_bp)
    app.register_blueprint(maintenance_bp)