from app.extensions import db


class Idioma(db.Model):
    __tablename__ = "idioma"

    # =========================
    # Atributos
    # =========================
    
    id_idioma = db.Column(db.Integer, primary_key=True, nullable=False)  # PK

    nombre_idioma = db.Column(db.String(100), unique=True, nullable=False)  # Nombre del Idioma

    descripcion_idioma = db.Column(db.Text, nullable=True)

    # =========================
    # Relaciones
    # =========================

    profesor_idioma = db.relationship(
        "ProfesorIdioma", back_populates="idioma"
    )  # Relación N:M Profesor - profesor_idioma - Idioma

    cursos = db.relationship(
        "Curso", back_populates="idioma"
    )  # Relación Idioma 1:M Cursos
