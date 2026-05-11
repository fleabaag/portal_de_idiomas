from datetime import datetime
from app.extensions import db
from .Usuario import Usuario
from .enums import RolUsuario


class Alumno(Usuario):
    __tablename__ = "alumno"

    # =========================
    # Atributos
    # =========================

    id_alumno = db.Column(
        db.Integer, db.ForeignKey("usuario.id_user"), primary_key=True, nullable=False
    )  # PK

    fecha_ingreso = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=True
    )  # Fecha en la que se inscribió por primera vez a un curso

    # =========================
    # Relaciones
    # =========================

    inscripciones = db.relationship(
        "Inscripcion", back_populates="alumno"
    )  # Relación N:M Curso - Inscripción - Alumnos

    # =========================
    # Herencia
    # =========================

    __mapper_args__ = {
        "polymorphic_identity": RolUsuario.ALUMNO,
    }
