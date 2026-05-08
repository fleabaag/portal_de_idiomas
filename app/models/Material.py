from app.extensions import db


class Material(db.Model):
    __tablename__ = "material"

    # =========================
    # Atributos
    # =========================
    
    id_material = db.Column(db.Integer, primary_key=True, nullable=False)  # PK

    id_curso = db.Column(db.Integer, db.ForeignKey("curso.id_curso"), nullable=False)  # FK

    titulo = db.Column(db.String(100), nullable=False)

    tipo_archivo = db.Column(db.String(50), nullable=True)

    url_archivo = db.Column(db.String(255), nullable=True)

    # =========================
    # Relaciones
    # =========================
    
    curso = db.relationship(
        "Curso", back_populates="materiales"
    )  # Relación Curso 1:M Material
