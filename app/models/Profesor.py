from app.extensions import db
from .Usuario import Usuario
from .enums import RolUsuario


class Profesor(Usuario):
    __tablename__ = "profesor"

    # =========================
    # Atributos
    # =========================
    
    id_profesor = db.Column(
        db.Integer, db.ForeignKey("usuario.id_user"), primary_key=True, nullable=False
    )  # PK

    sueldo = db.Column(db.Float, nullable=True)  # Debe ser mayor a 0

    # =========================
    # Relaciones
    # =========================
    
    cursos = db.relationship(
        "Curso", back_populates="profesor", cascade="all, delete-orphan"
    )  # Relacion Profesor 1:M Curso

    profesor_idioma = db.relationship(
        "ProfesorIdioma", back_populates="profesor"
    )  # Relación N:M Profesor - profesor_idioma - Idioma

    # =========================
    # Herencia
    # =========================
    
    __mapper_args__ = {
        "polymorphic_identity": RolUsuario.PROFESOR,
    }

    # =========================
    # Constraints
    # =========================
    
    __table_args__ = (db.CheckConstraint("sueldo > 0", name="check_sueldo_range"),)
