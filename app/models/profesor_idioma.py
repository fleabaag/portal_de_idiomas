from app.extensions import db


class ProfesorIdioma(db.Model):
    __tablename__ = "profesor_idioma"

    # =========================
    # Atributos
    # =========================
    
    id_profesor = db.Column(
        db.Integer,
        db.ForeignKey("profesor.id_profesor"),
        primary_key=True,
        nullable=False,
    )  # FK

    id_idioma = db.Column(
        db.Integer, db.ForeignKey("idioma.id_idioma"), primary_key=True, nullable=False
    )  # FK

    # =========================
    # Relaciones
    # =========================
    
    profesor = db.relationship(
        "Profesor", back_populates="profesor_idioma"
    )  # Relación N:M Profesor - profesor_idioma - Idioma

    idioma = db.relationship(
        "Idioma", back_populates="profesor_idioma"
    )  # Relación N:M Profesor - profesor_idioma - Idioma
