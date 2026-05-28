import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Curso, EstadoCurso, Idioma, Material, Niveles, PeriodoEnum, Inscripcion, Horario
from app.models.enums import DiasSemana
from datetime import datetime, time

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
    """Muestra el panel de control del profesor y permite crear nuevos cursos."""
    if current_user.is_profesor():
        idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()
        cursos = (
            Curso.query.filter_by(id_profesor=current_user.id_user)
            .order_by(Curso.id_curso.desc())
            .all()
        )
        
        anio_actual = datetime.now().year

        # Agrupar cursos por estado
        cursos_publicados = [c for c in cursos if c.estado == EstadoCurso.PUBLICADO]
        cursos_borrador = [c for c in cursos if c.estado == EstadoCurso.BORRADOR]
        cursos_archivados = [c for c in cursos if c.estado == EstadoCurso.CERRADO]

        if request.method == "POST":
            try:
                # Validar información del curso
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

                # Crear el curso
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
                db.session.flush()  # Para obtener el id del curso

                # Procesar horarios
                horario_index = 0
                while True:
                    dias_seleccionados = request.form.getlist(f"horario_{horario_index}_dias")
                    hora_inicio_str = request.form.get(f"horario_{horario_index}_inicio", "").strip()
                    hora_fin_str = request.form.get(f"horario_{horario_index}_fin", "").strip()

                    if not dias_seleccionados or not hora_inicio_str or not hora_fin_str:
                        break

                    # Convertir strings de hora a objetos time
                    hora_inicio = convertir_hora_string_a_time(hora_inicio_str)
                    hora_fin = convertir_hora_string_a_time(hora_fin_str)

                    if hora_inicio >= hora_fin:
                        raise ValueError(f"En horario {horario_index + 1}: la hora de inicio debe ser anterior a la de término.")

                    # Crear horarios para cada día seleccionado
                    for dia_str in dias_seleccionados:
                        if dia_str not in DiasSemana.__members__:
                            raise ValueError(f"Día inválido: {dia_str}")

                        horario = Horario(
                            id_curso=nuevo_curso.id_curso,
                            dia=DiasSemana[dia_str],
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin
                        )
                        db.session.add(horario)

                    horario_index += 1

                db.session.commit()
                flash("Curso creado correctamente.", "success")
                return redirect(url_for("profesor.dashboard"))

            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")
            except Exception as e:
                db.session.rollback()
                flash(f"No se pudo crear el curso. Intenta de nuevo. {str(e)}", "error")

        return render_template(
            "profesor/profesor-dashboard.html",
            idiomas=idiomas,
            cursos=cursos,
            cursos_publicados=cursos_publicados,
            cursos_borrador=cursos_borrador,
            cursos_archivados=cursos_archivados,
            niveles=Niveles,
            periodos=PeriodoEnum,
            anio_actual=anio_actual
        )

    return redirect(url_for("auth.login"))


def convertir_hora_string_a_time(hora_str):
    """Convierte string de hora (ej: '7:00 AM') a objeto time."""
    formatos = ["%I:%M %p", "%H:%M"]
    
    for formato in formatos:
        try:
            dt = datetime.strptime(hora_str.strip(), formato)
            return dt.time()
        except ValueError:
            continue
    
    raise ValueError(f"Formato de hora inválido: {hora_str}")


@profesor_bp.route("/cursos/<int:id_curso>", methods=["GET", "POST"])
@login_required
def curso_detalle(id_curso):
    """Muestra y permite editar (según estado) los detalles de un curso específico."""
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

    # Agrupar horarios existentes por (inicio, fin) => lista de dias
    horarios_grouped = []
    try:
        groups = {}
        for h in curso.horario:
            key = (h.hora_inicio, h.hora_fin)
            groups.setdefault(key, []).append(h.dia.name)
        for (inicio, fin), dias in groups.items():
            horarios_grouped.append({
                "inicio": inicio.strftime("%I:%M %p"),
                "fin": fin.strftime("%I:%M %p"),
                "dias": dias,
            })
    except Exception:
        horarios_grouped = []

    # Procesar edición enviada desde el formulario en la misma vista
    if request.method == "POST":
        # No permitir edición si archivado
        if curso.estado == EstadoCurso.CERRADO:
            flash("El curso archivado no puede ser editado.", "error")
            return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

        try:
            # Determinar qué campos pueden editarse según estado
            editar_todo = curso.estado == EstadoCurso.BORRADOR
            editar_descr_y_horarios = curso.estado == EstadoCurso.PUBLICADO

            # Campos editables en BORRADOR
            if editar_todo:
                idioma_id = int(request.form.get("id_idioma", ""))
                nivel_key = request.form.get("nivel", "")
                periodo_key = request.form.get("periodo", "")
                anio = int(request.form.get("anio", ""))
                if anio < 2000 or anio > 2100:
                    raise ValueError("El año debe estar entre 2000 y 2100.")
                idioma = Idioma.query.get(idioma_id)
                if not idioma:
                    raise ValueError("El idioma seleccionado no existe.")
                if nivel_key not in Niveles.__members__:
                    raise ValueError("El nivel seleccionado no es válido.")
                if periodo_key not in PeriodoEnum.__members__:
                    raise ValueError("El periodo seleccionado no es válido.")

                curso.id_idioma = idioma.id_idioma
                curso.nivel = Niveles[nivel_key]
                curso.periodo = PeriodoEnum[periodo_key]
                curso.anio = anio

            # Descripción editable en BORRADOR y PUBLICADO
            descripcion = request.form.get("descripcion_curso", "").strip() or None
            if editar_todo or editar_descr_y_horarios:
                curso.descripcion_curso = descripcion

            # Procesar horarios si está permitido (BORRADOR o PUBLICADO)
            if editar_todo or editar_descr_y_horarios:
                # Recolectar hasta 3 horarios enviados
                nuevos_horarios = []
                idx = 0
                while idx < 3:
                    dias = request.form.getlist(f"horario_{idx}_dias")
                    inicio_str = request.form.get(f"horario_{idx}_inicio", "").strip()
                    fin_str = request.form.get(f"horario_{idx}_fin", "").strip()
                    # Si no hay datos en este índice, continuar
                    if not dias and not inicio_str and not fin_str:
                        idx += 1
                        continue
                    if not dias:
                        raise ValueError(f"Horario {idx+1}: debes seleccionar al menos un día.")
                    if not inicio_str or not fin_str:
                        raise ValueError(f"Horario {idx+1}: debes seleccionar hora inicio y término.")
                    # Convertir y validar horas
                    hora_inicio = convertir_hora_string_a_time(inicio_str)
                    hora_fin = convertir_hora_string_a_time(fin_str)
                    if hora_inicio >= hora_fin:
                        raise ValueError(f"Horario {idx+1}: la hora de inicio debe ser anterior a la de término.")
                    nuevos_horarios.append((dias, hora_inicio, hora_fin))
                    idx += 1

                # Reemplazar horarios existentes por los nuevos (si se recibieron)
                # Primero eliminar horarios previos del curso
                db.session.flush()
                if nuevos_horarios:
                    db.session.query(Horario).filter_by(id_curso=curso.id_curso).delete(synchronize_session=False)
                    for dias, hi, hf in nuevos_horarios:
                        for dia_str in dias:
                            if dia_str not in DiasSemana.__members__:
                                raise ValueError(f"Día inválido: {dia_str}")
                            nuevo_h = Horario(
                                id_curso=curso.id_curso,
                                dia=DiasSemana[dia_str],
                                hora_inicio=hi,
                                hora_fin=hf
                            )
                            db.session.add(nuevo_h)
                # If no nuevos_horarios provided, keep existing (no deletion)

            db.session.commit()
            flash("Curso actualizado correctamente.", "success")
            return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))
        except ValueError as err:
            db.session.rollback()
            flash(str(err), "error")
        except Exception as err:
            db.session.rollback()
            flash("No se pudo actualizar el curso. Intenta de nuevo.", "error")

    return render_template(
        "profesor/profesor-curso-detalle.html",
        curso=curso,
        horarios_grouped=horarios_grouped,
        Niveles=Niveles,
        PeriodoEnum=PeriodoEnum
    )


@profesor_bp.route("/cursos/<int:id_curso>/editar", methods=["GET", "POST"])
@login_required
def editar_curso(id_curso):
    """Permite a un profesor editar la información básica de un curso."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden editar cursos.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

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

            if curso.estado == EstadoCurso.CERRADO:
                raise ValueError("No puedes editar un curso cerrado.")

            curso.id_idioma = idioma.id_idioma
            curso.nivel = Niveles[nivel_key]
            curso.periodo = PeriodoEnum[periodo_key]
            curso.anio = anio
            curso.descripcion_curso = descripcion

            db.session.commit()
            flash("Curso actualizado correctamente.", "success")
            return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))
        except ValueError as error:
            flash(str(error), "error")
        except Exception:
            db.session.rollback()
            flash("No se pudo actualizar el curso. Intenta de nuevo.", "error")

    idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()
    return render_template(
        "profesor/profesor-editar-curso.html",
        curso=curso,
        idiomas=idiomas,
        niveles=Niveles,
        periodos=PeriodoEnum,
    )
    
    
@profesor_bp.route("/cursos/<int:id_curso>/cerrar", methods=["POST"])
@login_required
def cerrar_curso(id_curso):
    """Cierra un curso para evitar nuevas inscripciones o publicación."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden cerrar cursos.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado == EstadoCurso.CERRADO:
        flash("Ese curso ya está cerrado.", "success")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

    curso.estado = EstadoCurso.CERRADO
    db.session.commit()
    flash("Curso cerrado correctamente.", "success")
    return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))


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
        flash("El título del material es obligatorio.", "validation")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

    if not archivo or archivo.filename == "":
        flash("Debes seleccionar un archivo.", "validation")
        return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

    if not allowed_material_file(archivo.filename):
        flash("Formato no permitido. Usa PDF, Word, Excel, PowerPoint, texto u otros documentos comunes.", "validation")
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
        flash("Ese curso ya está publicado.", "error")
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

@profesor_bp.route("/cursos/<int:id_curso>/calificaciones", methods=["POST"])
@login_required
def actualizar_calificacion_curso(id_curso):
    """Permite al profesor registrar o actualizar calificaciones de sus alumnos."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden subir calificaciones.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    try:
        inscripcion_id_alumno = int(request.form.get("id_alumno", ""))
        calificacion_raw = request.form.get("calificacion", "").strip()

        inscripcion = Inscripcion.query.filter_by(
            id_alumno=inscripcion_id_alumno,
            id_curso=curso.id_curso,
        ).first()

        if not inscripcion:
            flash("La inscripción no existe para este curso.", "error")
            return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))

        if calificacion_raw == "":
            inscripcion.calificacion = None
        else:
            calificacion = float(calificacion_raw)
            if calificacion < 0.0 or calificacion > 10.0:
                raise ValueError("La calificación debe estar entre 0.0 y 10.0.")
            inscripcion.calificacion = calificacion

        db.session.commit()
        flash("Calificación actualizada correctamente.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except Exception:
        db.session.rollback()
        flash("No se pudo actualizar la calificación. Intenta de nuevo.", "error")

    return redirect(url_for("profesor.curso_detalle", id_curso=id_curso))


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
            flash("El título del material es obligatorio.", "validation")
            return redirect(url_for("profesor.actualizar_material", id_material=id_material))

        try:
            material.titulo = nuevo_titulo

            if nuevo_archivo and nuevo_archivo.filename != "":
                if not allowed_material_file(nuevo_archivo.filename):
                    flash("Formato no permitido.", "validation")
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


@profesor_bp.route("/borradores", methods=["GET"])
@login_required
def borradores():
    """Muestra solo los cursos en estado BORRADOR del profesor."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden acceder a esta sección.", "error")
        return redirect(url_for("profesor.dashboard"))

    idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()
    cursos = Curso.query.filter_by(
        id_profesor=current_user.id_user,
        estado=EstadoCurso.BORRADOR
    ).order_by(Curso.id_curso.desc()).all()

    cursos_borrador = cursos

    return render_template(
        "profesor/profesor-borradores.html",
        idiomas=idiomas,
        cursos_borrador=cursos_borrador,
        niveles=Niveles,
        periodos=PeriodoEnum,
    )


@profesor_bp.route("/archivados", methods=["GET"])
@login_required
def archivados():
    """Muestra solo los cursos en estado CERRADO (Archivados) del profesor."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden acceder a esta sección.", "error")
        return redirect(url_for("profesor.dashboard"))

    cursos = Curso.query.filter_by(
        id_profesor=current_user.id_user,
        estado=EstadoCurso.CERRADO
    ).order_by(Curso.id_curso.desc()).all()

    cursos_archivados = cursos

    return render_template(
        "profesor/profesor-archivados.html",
        cursos_archivados=cursos_archivados,
    )


@profesor_bp.route("/cursos/<int:id_curso>/archivar", methods=["POST"])
@login_required
def archivar_curso(id_curso):
    """Permite archivar un curso publicado."""
    if not current_user.is_profesor():
        flash("Solo los profesores pueden archivar cursos.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso = Curso.query.filter_by(
        id_curso=id_curso,
        id_profesor=current_user.id_user,
    ).first()

    if not curso:
        flash("No tienes acceso a ese curso.", "error")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado == EstadoCurso.CERRADO:
        flash("Ese curso ya está archivado.", "info")
        return redirect(url_for("profesor.dashboard"))

    if curso.estado != EstadoCurso.PUBLICADO:
        flash("Solo puedes archivar cursos publicados.", "error")
        return redirect(url_for("profesor.dashboard"))

    curso.estado = EstadoCurso.CERRADO
    db.session.commit()
    flash("Curso archivado correctamente.", "success")
    return redirect(url_for("profesor.dashboard"))
