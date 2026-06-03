from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from datetime import datetime, time
import re

from app.extensions import db
from app.models import Idioma, Curso, Profesor, Alumno, Horario, Usuario
from app.models.enums import RolUsuario, EstadoCurso, Niveles, PeriodoEnum, DiasSemana

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def convertir_hora_string_a_time(hora_str: str) -> time:
    """
    Convierte una cadena de hora a objeto datetime.time.

    Formatos soportados:
    - HH:MM           (24 horas)
    - HH:MM:SS        (24 horas)
    - HH:MM AM/PM
    - HH:MM:SS AM/PM
    """

    if not hora_str:
        raise ValueError("La hora no puede estar vacía.")

    hora_str = hora_str.strip()

    formatos = [
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p",
        "%I:%M:%S %p",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(hora_str, formato).time()
        except ValueError:
            continue

    raise ValueError(
        f"Formato de hora inválido: '{hora_str}'. " "Use HH:MM o HH:MM AM/PM."
    )


@admin_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Muestra el panel de control del administrador y permite agregar nuevos idiomas.

    Returns:
        str: Renderiza la plantilla del panel de control del administrador o redirige en caso de error.
    """
    # Protege la ruta del administrador
    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nombre_idioma = request.form.get("nombre_idioma", "").strip()
        descripcion_idioma = request.form.get("descripcion_idioma", "").strip() or None

        if not nombre_idioma:
            flash("El nombre del idioma es obligatorio.", "validation")
        elif Idioma.query.filter_by(nombre_idioma=nombre_idioma).first():
            flash("Ese idioma ya existe.", "info")
        else:
            idioma = Idioma(
                nombre_idioma=nombre_idioma,
                descripcion_idioma=descripcion_idioma,
            )
            db.session.add(idioma)
            db.session.commit()
            flash("Idioma agregado correctamente.", "success")
            return redirect(url_for("admin.dashboard"))

    idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()
    total_cursos = Curso.query.count()
    total_idiomas = Idioma.query.count()
    total_profesores = Profesor.query.count()
    total_alumnos = Alumno.query.count()
    cursos_publicados = Curso.query.filter_by(estado=EstadoCurso.PUBLICADO).count()
    cursos_borrador = Curso.query.filter_by(estado=EstadoCurso.BORRADOR).count()
    cursos_cerrados = Curso.query.filter_by(estado=EstadoCurso.CERRADO).count()

    return render_template(
        "admin/admin-dashboard.html",
        idiomas=idiomas,
        total_cursos=total_cursos,
        total_idiomas=total_idiomas,
        total_profesores=total_profesores,
        total_alumnos=total_alumnos,
        cursos_publicados=cursos_publicados,
        cursos_borrador=cursos_borrador,
        cursos_cerrados=cursos_cerrados,
    )


@admin_bp.route("/cursos")
@login_required
def cursos():
    """Muestra todos los cursos del sistema para administración."""

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    profesor_id = request.args.get("profesor_id", type=int)
    idioma_id = request.args.get("idioma_id", type=int)
    estado = request.args.get("estado", type=str)

    query = Curso.query.order_by(Curso.id_curso.desc())

    if profesor_id:
        query = query.filter(Curso.id_profesor == profesor_id)

    if idioma_id:
        query = query.filter(Curso.id_idioma == idioma_id)

    if estado:
        try:
            query = query.filter(Curso.estado == EstadoCurso[estado])
        except KeyError:
            flash("El estado seleccionado no es válido.", "validation")

    cursos = query.all()
    profesores = Profesor.query.order_by(
        Profesor.nombre, Profesor.primer_apellido
    ).all()
    idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()

    return render_template(
        "admin/admin-cursos.html",
        cursos=cursos,
        profesores=profesores,
        idiomas=idiomas,
        estados=EstadoCurso,
        filtros={
            "profesor_id": profesor_id,
            "idioma_id": idioma_id,
            "estado": estado,
        },
    )


@admin_bp.route("/cursos/<int:id_curso>", methods=["GET", "POST"])
@login_required
def curso_detalle(id_curso):

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

    if request.method == "POST":

        if curso.estado == EstadoCurso.CERRADO:
            flash("El curso archivado no puede ser editado.", "error")
            return redirect(url_for("admin.curso_detalle", id_curso=id_curso))

        try:

            editar_todo = curso.estado == EstadoCurso.BORRADOR
            editar_descr_y_horarios = curso.estado == EstadoCurso.PUBLICADO

            # =========================
            # CAMPOS EDITABLES SOLO EN BORRADOR
            # =========================

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

            # =========================
            # DESCRIPCIÓN
            # =========================

            descripcion = request.form.get("descripcion_curso", "").strip() or None

            if editar_todo or editar_descr_y_horarios:
                curso.descripcion_curso = descripcion

            # =========================
            # HORARIOS
            # =========================

            if editar_todo or editar_descr_y_horarios:

                nuevos_horarios = []

                idx = 0

                while idx < 3:

                    dias = request.form.getlist(f"horario_{idx}_dias")

                    inicio_str = request.form.get(f"horario_{idx}_inicio", "").strip()

                    fin_str = request.form.get(f"horario_{idx}_fin", "").strip()

                    if not dias and not inicio_str and not fin_str:
                        idx += 1
                        continue

                    if not dias:
                        raise ValueError(
                            f"Horario {idx+1}: debes seleccionar al menos un día."
                        )

                    if not inicio_str or not fin_str:
                        raise ValueError(
                            f"Horario {idx+1}: debes seleccionar hora inicio y término."
                        )

                    hora_inicio = convertir_hora_string_a_time(inicio_str)

                    hora_fin = convertir_hora_string_a_time(fin_str)

                    if hora_inicio >= hora_fin:
                        raise ValueError(
                            f"Horario {idx+1}: la hora de inicio debe ser anterior a la de término."
                        )

                    nuevos_horarios.append((dias, hora_inicio, hora_fin))

                    idx += 1

                db.session.flush()

                if nuevos_horarios:

                    db.session.query(Horario).filter_by(id_curso=curso.id_curso).delete(
                        synchronize_session=False
                    )

                    for dias, hi, hf in nuevos_horarios:

                        for dia_str in dias:

                            if dia_str not in DiasSemana.__members__:
                                raise ValueError(f"Día inválido: {dia_str}")

                            db.session.add(
                                Horario(
                                    id_curso=curso.id_curso,
                                    dia=DiasSemana[dia_str],
                                    hora_inicio=hi,
                                    hora_fin=hf,
                                )
                            )

            db.session.commit()

            flash("Curso actualizado correctamente.", "success")

            return redirect(url_for("admin.curso_detalle", id_curso=id_curso))

        except ValueError as err:

            db.session.rollback()

            flash(str(err), "error")

        except Exception as err:

            db.session.rollback()

            flash("No se pudo actualizar el curso. Intenta de nuevo.", "error")
        # ==========================
        # HORARIOS PARA VISTA
        # ==========================

    horarios_grouped = []
    try:
        groups = {}
        for h in curso.horario:
            key = (h.hora_inicio, h.hora_fin)
            groups.setdefault(key, []).append(h.dia.name)
        for (inicio, fin), dias in groups.items():
            horarios_grouped.append(
                {
                    "inicio": inicio.strftime("%I:%M %p"),
                    "fin": fin.strftime("%I:%M %p"),
                    "dias": dias,
                }
            )
    except Exception:
        horarios_grouped = []

    return render_template(
        "admin/admin-curso-detalle.html",
        curso=curso,
        horarios_grouped=horarios_grouped,
        Niveles=Niveles,
        PeriodoEnum=PeriodoEnum,
    )


@admin_bp.route("/cursos/<int:id_curso>/cerrar", methods=["POST"])
@login_required
def cerrar_curso(id_curso):
    """Cierra un curso para que no siga activo."""

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

    if curso.estado == EstadoCurso.CERRADO:
        flash("Ese curso ya está cerrado.", "info")
        return redirect(url_for("admin.curso_detalle", id_curso=id_curso))

    curso.estado = EstadoCurso.CERRADO
    db.session.commit()
    flash("Curso cerrado correctamente.", "success")
    return redirect(url_for("admin.curso_detalle", id_curso=id_curso))


@admin_bp.route("/cursos/<int:id_curso>/publicar", methods=["POST"])
@login_required
def publicar_curso(id_curso):

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

    if curso.estado != EstadoCurso.BORRADOR:
        flash("Solo cursos en borrador pueden publicarse.", "validation")
        return redirect(url_for("admin.cursos"))

    curso.estado = EstadoCurso.PUBLICADO
    db.session.commit()

    flash("Curso publicado correctamente.", "success")
    return redirect(url_for("admin.cursos"))


@admin_bp.route("/cursos/<int:id_curso>/archivar", methods=["POST"])
@login_required
def archivar_curso(id_curso):

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

    if curso.estado != EstadoCurso.PUBLICADO:
        flash("Solo cursos publicados pueden archivarse.", "validation")
        return redirect(url_for("admin.cursos"))

    curso.estado = EstadoCurso.CERRADO
    db.session.commit()

    flash("Curso archivado correctamente.", "success")
    return redirect(url_for("admin.cursos"))


@admin_bp.route("/cursos/<int:id_curso>/eliminar", methods=["POST"])
@login_required
def eliminar_curso(id_curso):

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

    if curso.estado not in [EstadoCurso.BORRADOR, EstadoCurso.CERRADO]:
        flash("Solo cursos borrador o cerrados pueden eliminarse.", "validation")
        return redirect(url_for("admin.cursos"))

    db.session.delete(curso)
    db.session.commit()

    flash("Curso eliminado correctamente.", "success")
    return redirect(url_for("admin.cursos"))


@admin_bp.route("/usuarios")
@login_required
def usuarios():

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    administradores = (
        Usuario.query.filter_by(rol=RolUsuario.ADMIN).order_by(Usuario.nombre).all()
    )

    profesores = Profesor.query.order_by(Profesor.nombre).all()

    alumnos = Alumno.query.order_by(Alumno.nombre).all()

    return render_template(
        "admin/usuarios.html",
        administradores=administradores,
        profesores=profesores,
        alumnos=alumnos,
    )


@admin_bp.route("/usuarios/crear", methods=["GET", "POST"])
@login_required
def crear_usuario():
    """
    Permite registrar un nuevo profesor.

    Returns:
        str: Vista del formulario o redirección.
    """

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        primer_apellido = request.form.get("primer_apellido", "").strip()
        segundo_apellido = request.form.get("segundo_apellido", "").strip() or None

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        sueldo = request.form.get("sueldo", "").strip()

        # =========================
        # VALIDACIONES
        # =========================

        if not nombre or not primer_apellido:
            flash("Nombre y apellido son obligatorios", "validation")

            return render_template("admin/crear-usuario.html", form_data=request.form)

        # Email válido
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash("Correo electrónico inválido", "validation")

            return render_template("admin/crear-usuario.html", form_data=request.form)

        # Email único
        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("Ese correo ya está registrado", "error")

            return render_template("admin/crear-usuario.html", form_data=request.form)

        # Password segura
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"

        if not re.match(password_pattern, password):

            flash(
                "La contraseña debe tener mínimo "
                "8 caracteres, una mayúscula, "
                "una minúscula y un número",
                "validation",
            )

            return render_template("admin/crear-usuario.html", form_data=request.form)

        # Confirmación password
        if password != confirm_password:

            flash("Las contraseñas no coinciden", "validation")

            return render_template("admin/crear-usuario.html", form_data=request.form)

        # =========================
        # CREAR Usuario
        # =========================

        rol = request.form.get("rol", "").strip()

        if rol == RolUsuario.PROFESOR.name:
        
            # validar sueldo

            usuario = Profesor(
                nombre=nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                email=email,
                sueldo=sueldo,
                rol=RolUsuario.PROFESOR,
            )

        elif rol == RolUsuario.ADMIN.name:
        
            usuario = Usuario(
                nombre=nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                email=email,
                rol=RolUsuario.ADMIN,
            )

        else:
            flash("Rol inválido", "validation")
            return render_template(
                "admin/crear-usuario.html",
                form_data=request.form
            )

        try:
            usuario.set_contrasena(password)
            db.session.add(usuario)
            db.session.commit()

            flash("Usuario registrado correctamente", "success")

            return redirect(url_for("admin.usuarios"))

        except Exception:
            db.session.rollback()

            flash("No se pudo registrar el usuario.", "error")

            return render_template("admin/crear-usuario.html", form_data=request.form)

    return render_template("admin/crear-usuario.html")


@admin_bp.route("/profesores/<int:id_profesor>/sueldo", methods=["POST"])
@login_required
def cambiar_sueldo(id_profesor):
    """
    Permite modificar el sueldo mensual de un profesor.

    Args:
        id_profesor (int): ID del profesor.

    Returns:
        Response: Redirección al panel de profesores.
    """

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    profesor = Profesor.query.get_or_404(id_profesor)

    nuevo_sueldo = request.form.get("sueldo", "").strip()

    try:

        nuevo_sueldo = float(nuevo_sueldo)

        if nuevo_sueldo <= 0:
            raise ValueError

    except ValueError:

        flash("El sueldo debe ser mayor a 0", "validation")

        return redirect(url_for("admin.usuarios"))

    profesor.sueldo = nuevo_sueldo

    db.session.commit()

    flash(f"Sueldo actualizado para " f"{profesor.nombre_completo}", "success")

    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/<int:id_usuario>/eliminar", methods=["POST"])
@login_required
def eliminar_usuario(id_usuario):
    """
    Elimina un usuario.

    Restricciones:
    - No se puede eliminar al último administrador.
    - Un profesor no puede eliminarse si tiene cursos
      en BORRADOR o PUBLICADO.
    """

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    usuario = Usuario.query.get_or_404(id_usuario)

    # Evitar eliminar la propia cuenta
    if usuario.id_user == current_user.id_user:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("admin.usuarios"))

    # =========================
    # ADMINISTRADORES
    # =========================

    if usuario.rol == RolUsuario.ADMIN:

        total_admins = Usuario.query.filter_by(rol=RolUsuario.ADMIN).count()

        if total_admins <= 1:

            flash("No se puede eliminar el último administrador del sistema.", "error")

            return redirect(url_for("admin.usuarios"))

    # =========================
    # PROFESORES
    # =========================

    elif usuario.rol == RolUsuario.PROFESOR:

        tiene_cursos_asociados = any(
            curso.estado in (EstadoCurso.PUBLICADO, EstadoCurso.BORRADOR)
            for curso in usuario.cursos
        )

        if tiene_cursos_asociados:

            flash(
                "No se puede eliminar el profesor porque tiene cursos asociados.",
                "error",
            )

            return redirect(url_for("admin.usuarios"))

    # =========================
    # ELIMINAR
    # =========================

    try:

        db.session.delete(usuario)
        db.session.commit()

        flash(f"{usuario.nombre_completo} eliminado correctamente.", "success")

    except Exception:

        db.session.rollback()

        flash("No se pudo eliminar el usuario.", "error")

    return redirect(url_for("admin.usuarios"))
