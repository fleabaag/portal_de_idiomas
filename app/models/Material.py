from app.extensions import db

class Material(db.Model):
    __tablename__ = "material"

    id_material = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    tipo_archivo = db.Column(db.String(50))
    url_archivo = db.Column(db.String(255))

    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id_curso"))
    curso = db.relationship("Curso", back_populates="material")