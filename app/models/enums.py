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


class DiasSemana(Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    
class Niveles(Enum):
    A_UNO = "A1"
    A_DOS = "A2"
    B_UNO = "B1"
    B_DOS = "B2"
    C_UNO = "C1"
    C_DOS = "C2"
