from .test_controller import index_bp

def register_blueprints(app):
    app.register_blueprint(index_bp)