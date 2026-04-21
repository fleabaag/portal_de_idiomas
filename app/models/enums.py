from enum import Enum

class RolUsuario(Enum):
    ADMIN = "admin"
    PROFESOR = "profesor"
    ALUMNO = "alumno"


class EstadoCurso(Enum):
    BORRADOR = "borrador"
    PUBLICADO = "publicado"
    CERRADO = "cerrado"
    
class PeriodoEnum(Enum):
    PRIMAVERA = "Primavera"
    OTONO = "Otoño"    