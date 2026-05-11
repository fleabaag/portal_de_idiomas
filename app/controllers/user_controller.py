from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Curso, EstadoCurso, Idioma, Niveles, PeriodoEnum

user_bp = Blueprint("user", __name__, url_prefix="/user")

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