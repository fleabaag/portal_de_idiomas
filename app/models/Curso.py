from app.extensions import db
from .enums import EstadoCurso, Niveles, PeriodoEnum


class Curso(db.Model):
    __tablename__ = "curso"

    # =========================
    # Atributos
    # =========================

    id_curso = db.Column(db.Integer, primary_key=True, nullable=False)  # PK

    id_profesor = db.Column(
        db.Integer, db.ForeignKey("profesor.id_profesor"), nullable=False
    )  # FK

    id_idioma = db.Column(
        db.Integer, db.ForeignKey("idioma.id_idioma"), nullable=False
    )  # FK

    nivel = db.Column(db.Enum(Niveles), nullable=False)

    estado = db.Column(db.Enum(EstadoCurso), nullable=False)

    descripcion = db.Column(db.Text, nullable=True)
    
    periodo = db.Column(db.Enum(PeriodoEnum), nullable=False)

    anio = db.Column(db.Integer, nullable=False)  # Debe ser mayor a 2000 y menor a 2100    

    # =========================
    # Relaciones
    # =========================

    # Relacion Profesor 1:M Curso
    profesor = db.relationship("Profesor", back_populates="cursos")

    # Relación Curso 1:M Material
    materiales = db.relationship("Material", back_populates="curso")

    # Relación Curso 1:M Horario
    horario = db.relationship("Horario", back_populates="curso", cascade="all, delete")

    # Relación N:M Curso - Inscripción - Alumnos
    inscripciones = db.relationship("Inscripcion", back_populates="curso")

    # Relación Idioma 1:M Cursos
    idioma = db.relationship("Idioma", back_populates="cursos")
    
    # =========================
    # Constraints
    # =========================
    
    __table_args__ = (
        db.CheckConstraint("anio >= 2000 AND anio <= 2100", name="check_anio_range"),
    )
    
