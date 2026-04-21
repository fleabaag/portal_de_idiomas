from datetime import datetime
from app.extensions import db
from .Usuario import Usuario
from .enums import RolUsuario


class Alumno(Usuario):
    __tablename__ = "alumno"

    id_alumno = db.Column(db.Integer, db.ForeignKey("usuario.id_user"), primary_key=True)
    nivel_actual = db.Column(db.String(50))
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)

    inscripciones = db.relationship("Inscripcion", back_populates="alumno")

    __mapper_args__ = {
        "polymorphic_identity": RolUsuario.ALUMNO,
    }