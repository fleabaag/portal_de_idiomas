import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Curso, EstadoCurso, Idioma, Material, Niveles, PeriodoEnum

user_bp = Blueprint("user", __name__, url_prefix="/user")

ALLOWED_MATERIAL_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "odt",
    "txt",
    "rtf",
    "ppt",
    "pptx",
    "xls",
    "xlsx",
    "csv",
}


def allowed_material_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_MATERIAL_EXTENSIONS

@user_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if current_user.is_profesor():
        idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()
        cursos = (
            Curso.query.filter_by(id_profesor=current_user.id_user)
            .order_by(Curso.id_curso.desc())
            .all()
        )

        if request.method == "POST":
            try:
                idioma_id = int(request.form.get("id_idioma", ""))
                nivel_key = request.form.get("nivel", "")
                periodo_key = request.form.get("periodo", "")
                anio = int(request.form.get("anio", ""))
                descripcion = request.form.get("descripcion_curso", "").strip() or None

                if anio < 2000 or anio > 2100:
                    raise ValueError("El año debe estar entre 2000 y 2100.")

                idioma = Idioma.query.get(idioma_id)
                if not idioma:
                    raise ValueError("El idioma seleccionado no existe.")

                if nivel_key not in Niveles.__members__:
                    raise ValueError("El nivel seleccionado no es válido.")

                if periodo_key not in PeriodoEnum.__members__:
                    raise ValueError("El periodo seleccionado no es válido.")

                nuevo_curso = Curso(
                    id_profesor=current_user.id_user,
                    id_idioma=idioma.id_idioma,
                    nivel=Niveles[nivel_key],
                    estado=EstadoCurso.BORRADOR,
                    descripcion_curso=descripcion,
                    periodo=PeriodoEnum[periodo_key],
                    anio=anio,
                )

                db.session.add(nuevo_curso)
                db.session.commit()
                flash("Curso creado correctamente.", "success")
                return redirect(url_for("user.dashboard"))
            except ValueError as error:
                flash(str(error), "error")
            except Exception:
                db.session.rollback()
                flash("No se pudo crear el curso. Intenta de nuevo.", "error")

        return render_template(
            "profesor-dashboard.html",
            idiomas=idiomas,
            cursos=cursos,
            niveles=Niveles,
            periodos=PeriodoEnum,
        )

    return render_template("dashboard.html")


@user_bp.route("/cursos/<int:id_curso>")
@login_required
def curso_detalle(id_curso):
    if not current_user.is_profesor():
        flash("Solo los profesores pueden acceder a esta sección.", "error")
        return redirect(url_for("user.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("user.dashboard"))

    return render_template("profesor-curso-detalle.html", curso=curso)


@user_bp.route("/cursos/<int:id_curso>/materiales", methods=["POST"])
@login_required
def subir_material(id_curso):
    if not current_user.is_profesor():
        flash("Solo los profesores pueden subir materiales.", "error")
        return redirect(url_for("user.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("user.dashboard"))

    if curso.estado != EstadoCurso.PUBLICADO:
        flash("Solo puedes subir materiales a un curso publicado.", "error")
        return redirect(url_for("user.curso_detalle", id_curso=id_curso))

    titulo = request.form.get("titulo_material", "").strip()
    archivo = request.files.get("archivo_material")

    if not titulo:
        flash("El título del material es obligatorio.", "error")
        return redirect(url_for("user.curso_detalle", id_curso=id_curso))

    if not archivo or archivo.filename == "":
        flash("Debes seleccionar un archivo.", "error")
        return redirect(url_for("user.curso_detalle", id_curso=id_curso))

    if not allowed_material_file(archivo.filename):
        flash("Formato no permitido. Usa PDF, Word, Excel, PowerPoint, texto u otros documentos comunes.", "error")
        return redirect(url_for("user.curso_detalle", id_curso=id_curso))

    original_filename = secure_filename(archivo.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = secure_filename(
        f"curso_{curso.id_curso}_{len(curso.materiales) + 1}_{original_filename}"
    )

    upload_directory = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_directory, exist_ok=True)
    archivo.save(os.path.join(upload_directory, stored_filename))

    material = Material(
        id_curso=curso.id_curso,
        titulo=titulo,
        tipo_archivo=extension,
        url_archivo=url_for("user.descargar_material", filename=stored_filename),
    )

    db.session.add(material)
    db.session.commit()
    flash("Material subido correctamente.", "success")
    return redirect(url_for("user.curso_detalle", id_curso=id_curso))


@user_bp.route("/materiales/<path:filename>")
@login_required
def descargar_material(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@user_bp.route("/cursos/<int:id_curso>/publicar", methods=["POST"])
@login_required
def publicar_curso(id_curso):
    if not current_user.is_profesor():
        flash("Solo los profesores pueden publicar cursos.", "error")
        return redirect(url_for("user.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("user.dashboard"))

    if curso.estado == EstadoCurso.PUBLICADO:
        flash("Ese curso ya está publicado.", "success")
        return redirect(url_for("user.dashboard"))

    if curso.estado == EstadoCurso.CERRADO:
        flash("No puedes publicar un curso cerrado.", "error")
        return redirect(url_for("user.dashboard"))

    curso.estado = EstadoCurso.PUBLICADO
    db.session.commit()
    flash("Curso publicado correctamente.", "success")
    return redirect(url_for("user.dashboard"))