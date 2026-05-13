from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Idioma, Curso, Material

alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")

@alumno_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    
    # [AQUÍ VA CÓDIGO DE FUNCIONALIDADES PARA ALUMNO] 
    
    
    return render_template('alumno/alumno-dashboard.html')


