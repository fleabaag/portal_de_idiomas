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
        segundo_apellido = request.form["segundo_apellido"] or None

        email = request.form["email"]

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # =========================
        # VALIDACIONES
        # =========================

        if not nombre or not primer_apellido or not email or not password:
            flash("Los campos marcados con asterisco son obligatorios.", "warning")
            return render_template("auth/register.html", form_data=request.form)

        # Validar forma de email
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash("Ingresa un correo electrónico válido", "validation")

            return render_template("auth/register.html", form_data=request.form)

        # Email existente
        existing_user = Usuario.query.filter_by(email=email).first()

        if existing_user:
            flash("El correo ya está registrado", "error")
            return render_template("auth/register.html", form_data=request.form)

        # Confirmar contraseña
        if password != confirm_password:
            flash("Las contraseñas no coinciden", "validation")
            return render_template("auth/register.html", form_data=request.form)

        # Password segura
        if not valid_password(password):
            flash(
                "La contraseña debe tener mínimo 8 caracteres, "
                "una mayúscula, una minúscula y un número",
                "validation",
            )
            return render_template("auth/register.html", form_data=request.form)

        # =========================
        # CREAR ALUMNO
        # =========================

        try:
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

            flash("Cuenta creada correctamente", "success")
            return redirect(url_for("auth.login"))

        except Exception:
            db.session.rollback()
            flash("No se pudo crear la cuenta", "error")

            return render_template("auth/register.html", form_data=request.form)

    return render_template("auth/register.html")


# =========================
# LOGOUT
# =========================


@auth_bp.route("/logout")
def logout():
    """Cierra la sesion del usuario."""
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
