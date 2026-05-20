import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Curso, EstadoCurso, Idioma, Material, Niveles, PeriodoEnum

profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")


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
    "png",
    "jpg",
    "jpeg",
}


def allowed_material_file(filename):
    """Verifica si el archivo tiene una extensión permitida.

    Args:
        filename (str): El nombre del archivo a verificar.

    Returns:
        bool: True si el archivo tiene una extensión válida, False en caso contrario.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_MATERIAL_EXTENSIONS

@profesor_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Muestra el panel de control del profesor y permite crear nuevos cursos.

    Raises:
        ValueError: Si el año está fuera del rango permitido (2000-2100).
        ValueError: Si el idioma seleccionado no existe.
        ValueError: Si el nivel seleccionado no es válido.
        ValueError: Si el periodo seleccionado no es válido.

    Returns:
        str: Renderiza la plantilla del panel de control del profesor o redirige en caso de error.
    """
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
                return redirect(url_for("profesor.dashboard"))
            except ValueError as error:
                flash(str(error), "error")
            except Exception:
                db.session.rollback()
                flash("No se pudo crear el curso. Intenta de nuevo.", "error")

        return render_template(
            "profesor/profesor-dashboard.html",
            idiomas=idiomas,
            cursos=cursos,
            niveles=Niveles,
            periodos=PeriodoEnum,
        )

    return redirect(url_for("auth.login"))


@profesor_bp.route("/cursos/<int:id_curso>")
@login_required
def curso_detalle(id_curso):
    """Muestra los detalles de un curso específico.

    Args:
        id_curso (int): El ID del curso a mostrar.

    Returns:
        str: Renderiza la plantilla con los detalles del curso o redirige en caso de error.
    """
    if not current_user.is_profesor():
        flash("Solo los profesores pueden acceder a esta sección.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    return render_template("profesor/profesor-curso-detalle.html", curso=curso)


@profesor_bp.route("/cursos/<int:id_curso>/materiales", methods=["POST"])
@login_required
def subir_material(id_curso):
    """Permite a un profesor subir materiales a un curso publicado.

    Args:
        id_curso (int): El ID del curso al que se subirá el material.

    Returns:
        str: Redirige a la página de detalles del curso o muestra mensajes de error.
    """
    if not current_user.is_profesor():
        flash("Solo los profesores pueden subir materiales.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado != EstadoCurso.PUBLICADO:
        flash("Solo puedes subir materiales a un curso publicado.", "error")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

    titulo = request.form.get("titulo_material", "").strip()
    archivo = request.files.get("archivo_material")

    if not titulo:
        flash("El título del material es obligatorio.", "error")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

    if not archivo or archivo.filename == "":
        flash("Debes seleccionar un archivo.", "error")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

    if not allowed_material_file(archivo.filename):
        flash("Formato no permitido. Usa PDF, Word, Excel, PowerPoint, texto u otros documentos comunes.", "error")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

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
        url_archivo=url_for("profesor.descargar_material", filename=stored_filename),
    )

    db.session.add(material)
    db.session.commit()
    flash("Material subido correctamente.", "success")
    return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))


@profesor_bp.route("/materiales/<path:filename>")
@login_required
def descargar_material(filename):
    """Peemitee descargar un archivo de material subido.

    Args:
        filename (str): El nombre del archivo a descargar.

    Returns:
        Response: Descarga el archivo desde el directorio de subida.
    """
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@profesor_bp.route("/cursos/<int:id_curso>/publicar", methods=["POST"])
@login_required
def publicar_curso(id_curso):
    """Permite a un profesor publicar un curso.

    Args:
        id_curso (int): El ID del curso a publicar.

    Returns:
        str: Redirige al panel de control del profesor con un mensaje de éxito o error.
    """
    if not current_user.is_profesor():
        flash("Solo los profesores pueden publicar cursos.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado == EstadoCurso.PUBLICADO:
        flash("Ese curso ya está publicado.", "success")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado == EstadoCurso.CERRADO:
        flash("No puedes publicar un curso cerrado.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso.estado = EstadoCurso.PUBLICADO
    db.session.commit()
    flash("Curso publicado correctamente.", "success")
    return redirect(url_for("profesor.dashboard"))

@profesor_bp.route("/materiales/<int:id_material>/eliminar", methods=["POST"])
@login_required
def eliminar_material(id_material):
    """Permite a un profesor eliminar un material de su curso.

    Args:
        id_material (int): El ID del material a eliminar.

    Returns:
        str: Redirige al detalle del curso con un mensaje de éxito o error.
    """
    if not current_user.is_profesor():
        flash("Solo los profesores pueden eliminar materiales.", "error")
        return redirect(url_for("profesor.dashboard"))

    material = Material.query.get(id_material)

    if not material:
        flash("El material no existe.", "error")
        return redirect(url_for("profesor.dashboard"))

    if material.curso.id_profesor != current_user.id_user:
        flash("No tienes permisos para eliminar este material.", "error")
        return redirect(url_for("profesor.dashboard"))

    id_curso = material.id_curso

    try:
        filename = os.path.basename(material.url_archivo)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass

    try:
        db.session.delete(material)
        db.session.commit()
        flash("Material eliminado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el material. Intenta de nuevo.", "error")

    return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

@profesor_bp.route("/cursos/<int:id_curso>/eliminar", methods=["POST"])
@login_required
def eliminar_curso(id_curso):
    """Permite eliminar un curso en estado BORRADOR o CERRADO."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden eliminar cursos.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado == EstadoCurso.PUBLICADO:
        flash("No puedes eliminar un curso publicado. Ciérralo primero.", "error")
        return redirect(url_for("profesor.dashboard"))

    try:
        for material in curso.materiales:
            try:
                filename = os.path.basename(material.url_archivo)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass

        for material in list(curso.materiales):
            db.session.delete(material)
        for inscripcion in list(curso.inscripciones):
            db.session.delete(inscripcion)

        db.session.delete(curso)
        db.session.commit()
        flash("Curso eliminado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el curso. Intenta de nuevo.", "error")

    return redirect(url_for("profesor.dashboard"))


@profesor_bp.route("/materiales/<int:id_material>/editar", methods=["GET", "POST"])
@login_required
def actualizar_material(id_material):
    """Permite a un profesor editar el titulo y/o reemplazar el archivo de un material."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden actualizar materiales.", "error")
        return redirect(url_for("profesor.dashboard"))

    material = Material.query.get(id_material)

    if not material:
        flash("El material no existe.", "error")
        return redirect(url_for("profesor.dashboard"))

    if material.curso.id_profesor != current_user.id_user:
        flash("No tienes permisos para editar este material.", "error")
        return redirect(url_for("profesor.dashboard"))

    if request.method == "POST":
        nuevo_titulo = request.form.get("titulo_material", "").strip()
        nuevo_archivo = request.files.get("archivo_material")

        if not nuevo_titulo:
            flash("El título del material es obligatorio.", "error")
            return redirect(url_for("profesor.actualizar_material", id_material=id_material))

        try:
            material.titulo = nuevo_titulo

            if nuevo_archivo and nuevo_archivo.filename != "":
                if not allowed_material_file(nuevo_archivo.filename):
                    flash("Formato no permitido.", "error")
                    return redirect(url_for("profesor.actualizar_material", id_material=id_material))

                try:
                    filename_viejo = os.path.basename(material.url_archivo)
                    filepath_viejo = os.path.join(current_app.config["UPLOAD_FOLDER"], filename_viejo)
                    if os.path.exists(filepath_viejo):
                        os.remove(filepath_viejo)
                except Exception:
                    pass

                original_filename = secure_filename(nuevo_archivo.filename)
                extension = original_filename.rsplit(".", 1)[1].lower()
                stored_filename = secure_filename(
                    f"curso_{material.id_curso}_{material.id_material}_{original_filename}"
                )

                upload_directory = current_app.config["UPLOAD_FOLDER"]
                os.makedirs(upload_directory, exist_ok=True)
                nuevo_archivo.save(os.path.join(upload_directory, stored_filename))

                material.tipo_archivo = extension
                material.url_archivo = url_for("profesor.descargar_material", filename=stored_filename)

            db.session.commit()
            flash("Material actualizado correctamente.", "success")
            return redirect(url_for("profesor.curso_detalle", id_curso=material.id_curso))
        except Exception:
            db.session.rollback()
            flash("No se pudo actualizar el material. Intenta de nuevo.", "error")

    return render_template("profesor/profesor-editar-material.html", material=material)
