from routes.root import root_bp
from routes.user import user_bp
from routes.department import dept_bp

def register_blueprints(app):
    app.register_blueprint(root_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dept_bp)