from flask import Flask
from .config import Config
from .extensions import db
from .controllers import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register routes
    register_blueprints(app)

    return app
