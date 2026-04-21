from flask import Blueprint, render_template
from flask_login import login_required

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")