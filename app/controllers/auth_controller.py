from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
import re

from app.models.Usuario import Usuario
from app.models.Alumno import Alumno
from app.models.enums import RolUsuario
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


# =========================
# LOGIN
# =========================


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


# =========================
# REGISTER
# =========================


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Permite el registro de nuevos estudiantes en el sistema

    Returns:
        Regresa a la vista de iniciar sesión o a la misma vista de registro para completar el registro
    """

    if request.method == "POST":

        nombre = request.form["nombre"]
        primer_apellido = request.form["primer_apellido"]
        segundo_apellido = request.form["segundo_apellido"]

        email = request.form["email"]

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # =========================
        # VALIDACIONES
        # =========================

        # Validar forma de email
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash("Ingresa un correo electrónico válido", "error")

            return render_template("auth/register.html", form_data=request.form)

        # Email existente
        existing_user = Usuario.query.filter_by(email=email).first()

        if existing_user:
            flash("El correo ya está registrado", "error")
            render_template("auth/register.html", form_data=request.form)

        # Confirmar contraseña
        if password != confirm_password:
            flash("Las contraseñas no coinciden", "error")
            render_template("auth/register.html", form_data=request.form)

        # Password segura
        if not valid_password(password):
            flash(
                "La contraseña debe tener mínimo 8 caracteres, "
                "una mayúscula, una minúscula y un número",
                "error",
            )
            render_template("auth/register.html", form_data=request.form)

        # =========================
        # CREAR ALUMNO
        # =========================

        alumno = Alumno(
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            email=email,
            rol=RolUsuario.ALUMNO,
        )

        alumno.set_contrasena(password)

        db.session.add(alumno)
        db.session.commit()

        flash("Cuenta creada correctamente.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# =========================
# LOGOUT
# =========================


@auth_bp.route("/logout")
def logout():
    """Maneja el cierre de sesión de los usuarios.

    Returns:
        str: Redirige a la página de inicio de sesión.
    """
    logout_user()
    return redirect(url_for("auth.login"))


# =========================
# PASSWORD VALIDATION
# =========================


def valid_password(password):
    """
    Valida que la contraseña tenga:
    - mínimo 8 caracteres
    - una mayúscula
    - una minúscula
    - un número
    """

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"

    return re.match(pattern, password)
