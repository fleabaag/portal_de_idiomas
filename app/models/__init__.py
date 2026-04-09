from .Usuario import Usuario
from .Profesor import Profesor
from .Alumno import Alumno
from .Curso import Curso
from .Material import Material
from .Inscripcion import Inscripcion
from .enums import RolUsuario, EstadoCurso

# from app.extensions import login_manager


# @login_manager.user_loader
# def load_user(user_id):
#     return Usuario.query.get(int(user_id))