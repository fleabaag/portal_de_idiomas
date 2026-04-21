from datetime import datetime
from app.extensions import db
from .enums import PeriodoEnum

class Inscripcion(db.Model):
    __tablename__ = "inscripcion"

    id_inscripcion = db.Column(db.Integer, primary_key=True)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)

    alumno_id = db.Column(db.Integer, db.ForeignKey("alumno.id_alumno"))
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id_curso"))
    
    calificacion = db.Column(db.Float, nullable=True)
    periodo = db.Column(db.Enum(PeriodoEnum), nullable=False)
    anio = db.Column(db.Integer, nullable=False)

    alumno = db.relationship("Alumno", back_populates="inscripciones")
    curso = db.relationship("Curso", back_populates="inscripciones")