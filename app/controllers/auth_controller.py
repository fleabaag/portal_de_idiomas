from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from app.models.Usuario import Usuario
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    """Maneja el inicio de sesión de los usuarios.

    Returns:
        str: Renderiza la plantilla de inicio de sesión o redirige al panel correspondiente según el rol del usuario.
    """
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
    """Maneja el cierre de sesión de los usuarios.

    Returns:
        str: Redirige a la página de inicio de sesión.
    """
    logout_user()
    return redirect(url_for("auth.login"))