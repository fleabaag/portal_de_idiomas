from app.extensions import db

class Horario(db.Model):
    __tablename__ = "horario"

    id_horario = db.Column(db.Integer, primary_key=True)

    dia = db.Column(db.String(10), nullable=False)
    # Ej: "Lunes", "Martes", etc.

    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id_curso"))

    curso = db.relationship("Curso", back_populates="horario")