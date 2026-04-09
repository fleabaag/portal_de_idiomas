from flask_sqlalchemy import SQLAlchemy
from .Usuario import Usuario
from app.extensions import login_manager

db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))