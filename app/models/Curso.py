from app.extensions import db
from .enums import EstadoCurso

class Curso(db.Model):
    __tablename__ = "curso"

    id_curso = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    estado = db.Column(db.Enum(EstadoCurso), nullable=False)

    profesor_id = db.Column(db.Integer, db.ForeignKey("profesor.id_profesor"))
    profesor = db.relationship("Profesor", back_populates="curso")

    materiales = db.relationship("Material", back_populates="curso")
    inscripciones = db.relationship("Inscripcion", back_populates="curso")