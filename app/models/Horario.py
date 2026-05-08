from app.extensions import db
from .enums import DiasSemana


class Horario(db.Model):
    __tablename__ = "horario"

    # =========================
    # Atributos
    # =========================

    id_horario = db.Column(db.Integer, primary_key=True, nullable=False)  # PK

    id_curso = db.Column(
        db.Integer, db.ForeignKey("curso.id_curso"), nullable=False
    )  # FK

    # Días de Lunes a Sábado
    dia = db.Column(db.Enum(DiasSemana), nullable=False)

    # La hora de inicio debe ser anterior a la hora de finalización
    hora_inicio = db.Column(db.Time, nullable=False)

    # La hora de inicio debe ser anterior a la hora de finalización
    hora_fin = db.Column(db.Time, nullable=False)

    # =========================
    # Relaciones
    # =========================

    curso = db.relationship(
        "Curso", back_populates="horario"
    )  # Relación Curso 1:M Horario

    # =========================
    # Constraints
    # =========================

    __table_args__ = (
        db.CheckConstraint(
            "hora_inicio < hora_fin", name="check_hora_inicio_before_fin"
        ),
    )
