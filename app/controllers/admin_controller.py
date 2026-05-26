from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
import re

from app.extensions import db
from app.models import Curso, Idioma, Inscripcion
from app.models import Profesor
from app.models.enums import EstadoCurso, Niveles, PeriodoEnum, RolUsuario

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
    return render_template("admin/admin-dashboard.html", idiomas=idiomas)


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
    profesores = Profesor.query.order_by(Profesor.nombre, Profesor.primer_apellido).all()
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


@admin_bp.route("/cursos/<int:id_curso>")
@login_required
def curso_detalle(id_curso):
    """Muestra el detalle administrativo de un curso y sus calificaciones."""

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)
    return render_template("admin/admin-curso-detalle.html", curso=curso)


@admin_bp.route("/cursos/<int:id_curso>/editar", methods=["GET", "POST"])
@login_required
def editar_curso(id_curso):
    """Permite al admin editar la información base de un curso."""

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

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

            curso.id_idioma = idioma.id_idioma
            curso.nivel = Niveles[nivel_key]
            curso.periodo = PeriodoEnum[periodo_key]
            curso.anio = anio
            curso.descripcion_curso = descripcion

            db.session.commit()
            flash("Curso actualizado correctamente.", "success")
            return redirect(url_for("admin.curso_detalle", id_curso=id_curso))
        except ValueError as error:
            flash(str(error), "validation")
        except Exception:
            db.session.rollback()
            flash("No se pudo actualizar el curso.", "error")

    idiomas = Idioma.query.order_by(Idioma.nombre_idioma).all()
    return render_template(
        "admin/admin-editar-curso.html",
        curso=curso,
        idiomas=idiomas,
        niveles=Niveles,
        periodos=PeriodoEnum,
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


@admin_bp.route("/profesores")
@login_required
def profesores():
    """
    Muestra la lista de profesores registrados.

    Returns:
        str: Vista de administración de profesores.
    """

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    profesores = Profesor.query.order_by(Profesor.nombre).all()

    return render_template("admin/profesores.html", profesores=profesores)


@admin_bp.route("/profesores/crear", methods=["GET", "POST"])
@login_required
def crear_profesor():
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

            return render_template("admin/crear-profesor.html", form_data=request.form)

        # Email válido
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash("Correo electrónico inválido", "validation")

            return render_template("admin/crear-profesor.html", form_data=request.form)

        # Email único
        if Profesor.query.filter_by(email=email).first():

            flash("Ese correo ya está registrado", "error")

            return render_template("admin/crear-profesor.html", form_data=request.form)

        # Password segura
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"

        if not re.match(password_pattern, password):

            flash(
                "La contraseña debe tener mínimo "
                "8 caracteres, una mayúscula, "
                "una minúscula y un número",
                "validation",
            )

            return render_template("admin/crear-profesor.html", form_data=request.form)

        # Confirmación password
        if password != confirm_password:

            flash("Las contraseñas no coinciden", "validation")

            return render_template("admin/crear-profesor.html", form_data=request.form)

        # Sueldo válido
        try:
            sueldo = float(sueldo)

            if sueldo <= 0:
                raise ValueError

        except ValueError:

            flash("El sueldo debe ser mayor a 0", "validation")

            return render_template("admin/crear-profesor.html", form_data=request.form)

        # =========================
        # CREAR PROFESOR
        # =========================

        profesor = Profesor(
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            email=email,
            sueldo=sueldo,
            rol=RolUsuario.PROFESOR,
        )

        profesor.set_contrasena(password)

        db.session.add(profesor)
        db.session.commit()

        flash("Profesor registrado correctamente", "success")

        return redirect(url_for("admin.profesores"))

    return render_template("admin/crear-profesor.html")


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

        return redirect(url_for("admin.profesores"))

    profesor.sueldo = nuevo_sueldo

    db.session.commit()

    flash(f"Sueldo actualizado para " f"{profesor.nombre_completo}", "success")

    return redirect(url_for("admin.profesores"))


@admin_bp.route("/profesores/<int:id_profesor>/eliminar", methods=["POST"])
@login_required
def eliminar_profesor(id_profesor):
    """
    Elimina un profesor si no tiene cursos publicados.

    Args:
        id_profesor (int): ID del profesor.

    Returns:
        Response: Redirección al panel.
    """

    if not current_user.is_admin():
        return redirect(url_for("auth.login"))

    profesor = Profesor.query.get_or_404(id_profesor)

    tiene_cursos_publicados = any(
        curso.estado == EstadoCurso.PUBLICADO for curso in profesor.cursos
    )

    if tiene_cursos_publicados:

        flash(
            "No se puede eliminar el profesor " "porque tiene cursos activos",
            "error",
        )

        return redirect(url_for("admin.profesores"))

    db.session.delete(profesor)

    db.session.commit()

    flash("Profesor eliminado correctamente", "success")

    return redirect(url_for("admin.profesores"))