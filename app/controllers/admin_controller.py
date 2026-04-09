from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    # 🔒 PROTECT ADMIN ROUTE
    if not current_user.is_admin():
        return redirect(url_for("user.dashboard"))

    return render_template("admin-view.html")