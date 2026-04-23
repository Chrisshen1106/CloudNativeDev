from routes.root import root_bp

def register_blueprints(app):
    app.register_blueprint(root_bp)