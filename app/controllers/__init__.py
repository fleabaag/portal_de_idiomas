from .auth_controller import auth_bp
from .profesor_controller import profesor_bp
from .admin_controller import admin_bp
from .alumno_controller import alumno_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(profesor_bp)
    app.register_blueprint(admin_bp)    
    app.register_blueprint(alumno_bp)        