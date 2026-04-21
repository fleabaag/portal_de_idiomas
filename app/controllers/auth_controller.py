from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from app.models.Usuario import Usuario
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]

        user = Usuario.query.filter_by(email=username).first()
        
        if user and user.check_contrasena(password):
            login_user(user)

            if user.is_admin():
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        
        flash("E-mail o contraseña incorrectos", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))