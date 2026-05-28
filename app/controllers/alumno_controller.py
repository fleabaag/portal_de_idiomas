from datetime import datetime
from collections import defaultdict

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Curso, EstadoCurso, Inscripcion

alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Muestra el catalogo de cursos"""
    if not current_user.is_alumno():
        return redirect(url_for("auth.login"))

    cursos_publicados = (
        Curso.query.filter_by(estado=EstadoCurso.PUBLICADO)
        .order_by(Curso.id_curso.desc())
        .all()
    )
    ids_inscritos = {i.id_curso for i in current_user.inscripciones}

    cursos_por_idioma = defaultdict(list)
    for curso in cursos_publicados:
        cursos_por_idioma[curso.idioma.nombre_idioma].append(curso)

    return render_template(
        "alumno/alumno-dashboard.html",
        cursos=cursos_publicados,
        ids_inscritos=ids_inscritos,
        cursos_por_idioma=dict(cursos_por_idioma),
    )


@alumno_bp.route("/cursos/<int:id_curso>", methods=["GET"])
@login_required
def curso_detalle(id_curso):
    """Muestra el detalle de un curso inscrito con sus materiales."""
    if not current_user.is_alumno():
        return redirect(url_for("auth.login"))

    curso = Curso.query.get_or_404(id_curso)

    inscripcion = Inscripcion.query.filter_by(
        id_alumno=current_user.id_user, id_curso=id_curso
    ).first()

    inscrito = inscripcion is not None

    # Agrupar horarios igual que en profesor
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
        "alumno/alumno-curso-detalle.html",
        curso=curso,
        inscrito=inscrito,
        inscripcion=inscripcion,
        horarios_grouped=horarios_grouped,
    )


@alumno_bp.route("/inscritos", methods=["GET"])
@login_required
def cursos_inscritos():
    """Cursos en los que el alumno está inscrito"""
    if not current_user.is_alumno():
        return redirect(url_for("auth.login"))

    cursos_inscritos = [inscripcion.curso for inscripcion in current_user.inscripciones]

    return render_template(
        "alumno/alumno-dashboard-inscritos.html", cursos_inscritos=cursos_inscritos
    )


@alumno_bp.route("/cursos/<int:id_curso>/inscribir", methods=["POST"])
@login_required
def inscribir_curso(id_curso):
    """Inscribe al alumno actual al curso indicado."""
    if not current_user.is_alumno():
        flash("Solo los alumnos pueden inscribirse a cursos.", "error")
        return redirect(url_for("alumno.dashboard"))

    curso = Curso.query.get(id_curso)

    if not curso:
        flash("Ese curso no existe.", "error")
        return redirect(url_for("alumno.dashboard"))

    if curso.estado != EstadoCurso.PUBLICADO:
        flash("Solo puedes inscribirte a cursos publicados.", "error")
        return redirect(url_for("alumno.dashboard"))

    ya_inscrito = Inscripcion.query.filter_by(
        id_alumno=current_user.id_user,
        id_curso=curso.id_curso,
    ).first()

    if ya_inscrito:
        flash("Ya estabas inscrito a ese curso.", "error")
        return redirect(url_for("alumno.dashboard"))

    try:
        inscripcion = Inscripcion(
            id_alumno=current_user.id_user,
            id_curso=curso.id_curso,
            fecha_inscripcion=datetime.utcnow(),
        )
        db.session.add(inscripcion)
        db.session.commit()
        flash(
            "Te inscribiste correctamente a {} {}.".format(
                curso.idioma.nombre_idioma, curso.nivel.value
            ),
            "success",
        )
    except Exception:
        db.session.rollback()
        flash("No se pudo realizar la inscripcion. Intenta de nuevo.", "error")

    return redirect(url_for("alumno.dashboard"))
