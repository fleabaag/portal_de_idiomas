from datetime import datetime
from app.extensions import db


class Inscripcion(db.Model):
    __tablename__ = "inscripcion"

    # =========================
    # Atributos
    # =========================
    id_alumno = db.Column(
        db.Integer, db.ForeignKey("alumno.id_alumno"), primary_key=True, nullable=False
    )  # FK

    id_curso = db.Column(
        db.Integer, db.ForeignKey("curso.id_curso"), primary_key=True, nullable=False
    )  # FK

    fecha_inscripcion = db.Column(db.DateTime, default=datetime, nullable=False)

    calificacion = db.Column(db.Float, nullable=True)  # Debe ser entre 0.0 y 10.0

    # =========================
    # Relaciones
    # =========================
    
    alumno = db.relationship(
        "Alumno", back_populates="inscripciones"
    )  # Relación N:M Curso - Inscripción - Alumnos

    curso = db.relationship(
        "Curso", back_populates="inscripciones"
    )  # Relación N:M Curso - Inscripción - Alumnos

    # =========================
    # Constraints
    # =========================
    
    __table_args__ = (
        db.CheckConstraint(
            "calificacion IS NULL OR (calificacion >= 0.0 AND calificacion <= 10.0)",
            name="check_calificacion_range",
        ),
    )
