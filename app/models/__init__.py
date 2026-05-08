from .Usuario import Usuario
from .Profesor import Profesor
from .Alumno import Alumno
from .Curso import Curso
from .Material import Material
from .Inscripcion import Inscripcion
from .enums import RolUsuario, EstadoCurso
from .Horario import Horario
from .Idioma import Idioma
from .profesor_idioma import ProfesorIdioma

from app.extensions import login_manager


@login_manager.user_loader
def load_user(id_user):
    return Usuario.query.get(int(id_user))
