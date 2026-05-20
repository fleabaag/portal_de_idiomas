from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from app.models.Usuario import Usuario
from app.models.Alumno import Alumno
from app.models.enums import RolUsuario
from app.extensions import db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    """Maneja el inicio de sesion de los usuarios."""
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]
        user = Usuario.query.filter_by(email=username).first()

        if user and user.check_contrasena(password):
            login_user(user)
            if user.is_admin():
                return redirect(url_for("admin.dashboard"))
            if user.is_profesor():
                return redirect(url_for("profesor.dashboard"))
            else:
                return redirect(url_for("alumno.dashboard"))

        flash("E-mail o contraseña incorrectos", "error")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Cierra la sesion del usuario."""
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Permite que un visitante se registre con rol ALUMNO."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        primer_apellido = request.form.get("primer_apellido", "").strip()
        segundo_apellido = request.form.get("segundo_apellido", "").strip() or None
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if not nombre or not primer_apellido or not email or not password:
            flash("Los campos con asterisco son obligatorios.", "error")
            return render_template("auth/registro.html")

        if password != password_confirm:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("auth/registro.html")

        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está en uso.", "error")
            return render_template("auth/registro.html")

        try:
            nuevo_alumno = Alumno(
                email=email,
                nombre=nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                rol=RolUsuario.ALUMNO,
            )
            nuevo_alumno.set_contrasena(password)
            db.session.add(nuevo_alumno)
            db.session.commit()

            login_user(nuevo_alumno)
            flash("Bienvenido al Portal de Idiomas.", "success")
            return redirect(url_for("alumno.dashboard"))
        except Exception:
            db.session.rollback()
            flash("No se pudo crear la cuenta. Intenta de nuevo.", "error")

    return render_template("auth/registro.html")
