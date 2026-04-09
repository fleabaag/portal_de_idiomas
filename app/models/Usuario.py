from datetime import datetime
from enum import Enum
from flask_login import UserMixin

from app.extensions import db


class RolEnum(Enum):
    usuario = "usuario"
    administrador = "administrador"


class Usuario(db.Model, UserMixin):
    __tablename__ = "Usuario"

    id_user = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    
    rol = db.Column(db.Enum(RolEnum), default=RolEnum.usuario, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Usuario {self.nombre_usuario}>"
    
    def get_id(self):
        return str(self.id_user)

    def is_admin(self):
        return self.rol == RolEnum.administrador    