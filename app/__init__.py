import os

from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .controllers import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    from app import models 

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register routes
    register_blueprints(app)

    return app
