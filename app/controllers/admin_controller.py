from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Idioma

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
        return redirect(url_for("/"))

    if request.method == "POST":
        nombre_idioma = request.form.get("nombre_idioma", "").strip()
        descripcion_idioma = request.form.get("descripcion_idioma", "").strip() or None

        if not nombre_idioma:
            flash("El nombre del idioma es obligatorio.", "error")
        elif Idioma.query.filter_by(nombre_idioma=nombre_idioma).first():
            flash("Ese idioma ya existe.", "error")
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