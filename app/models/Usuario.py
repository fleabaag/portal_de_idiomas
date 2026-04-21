from datetime import datetime
from flask_login import UserMixin
from app.extensions import db
from .enums import RolUsuario
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id_user = db.Column(db.Integer, primary_key=True)
    
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    nombre = db.Column(db.String(100), nullable=False)
    primer_apellido = db.Column(db.String(100), nullable=False)
    segundo_apellido = db.Column(db.String(100), nullable=True)

    rol = db.Column(db.Enum(RolUsuario), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    
    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    
    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    # Herencia
    __mapper_args__ = {
        "polymorphic_on": rol,
        "polymorphic_identity": "usuario"
    }

    def get_id(self):
        return str(self.id)

    def nombre_completo(self):
        if self.segundo_apellido:
            return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido}"
        return f"{self.nombre} {self.primer_apellido}"
