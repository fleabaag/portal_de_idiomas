from .Usuario import Usuario
from .Profesor import Profesor
from .Alumno import Alumno
from .Curso import Curso
from .Material import Material
from .Inscripcion import Inscripcion
from .enums import RolUsuario, EstadoCurso, PeriodoEnum, Niveles
from .Horario import Horario
from .Idioma import Idioma
from .profesor_idioma import ProfesorIdioma
from sqlalchemy.orm.exc import ObjectDeletedError

from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(id_user):
    try:
        user = db.session.get(Usuario, int(id_user))
        if user is None:
            return None

        # Fuerza la carga para detectar filas huérfanas de herencia antes de usar current_user.
        _ = user.email
        return user
    except ObjectDeletedError:
        db.session.rollback()
        return None
