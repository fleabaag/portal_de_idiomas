from app.extensions import db
from .Usuario import Usuario

class Profesor(Usuario):
    __tablename__ = "profesor"

    id_profesor = db.Column(db.Integer, db.ForeignKey("usuario.id_user"), primary_key=True)
    especialidad = db.Column(db.String(100))
    sueldo = db.Column(db.Float)

    cursos = db.relationship("Curso", back_populates="profesor")

    __mapper_args__ = {
        "polymorphic_identity": "profesor",
    }