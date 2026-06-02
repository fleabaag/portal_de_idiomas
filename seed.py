"""
Usuarios de prueba (los de siempre):
  admin@test.com / ADMIN
  profesor@test.com / PROFESOR
  alumno@test.com / ALUMNO
"""

import random
import unicodedata
from datetime import datetime, time, timedelta

from app import create_app
from app.extensions import db
from app.models import (
    Alumno,
    Curso,
    Horario,
    Idioma,
    Inscripcion,
    Material,
    Profesor,
    RolUsuario,
    Usuario,
)
from app.models.enums import DiasSemana, EstadoCurso, Niveles, PeriodoEnum


def quitar_acentos(texto):
    """Quita acentos y caracteres especiales de un texto para usarlo en correos.
    """
    # Normaliza separando la letra base de su acento y elimina los acentos
    texto_normalizado = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in texto_normalizado if not unicodedata.combining(c))
    # La queda como u; cualquier otro caracter que sea difereente se elimina
    return "".join(c for c in sin_acentos if c.isalnum()).lower()

# Semilla fija para que los datos sean reproducibles entre corridas
random.seed(42)

app = create_app()

with app.app_context():
    print("Reiniciando base de datos...")
    db.drop_all()
    db.create_all()

    
    #  ADMIN
    
    admin = Usuario(
        email="admin@test.com",
        nombre="ADMIN",
        primer_apellido="Principal",
        rol=RolUsuario.ADMIN,
    )
    admin.set_contrasena("ADMIN")
    db.session.add(admin)

    # 2 IDIOMAS
    
    idiomas = [
        Idioma(nombre_idioma="Inglés", descripcion_idioma="Idioma anglosajón, el más solicitado a nivel internacional."),
        Idioma(nombre_idioma="Francés", descripcion_idioma="Idioma romance hablado en Francia, Canadá y África."),
        Idioma(nombre_idioma="Alemán", descripcion_idioma="Idioma germánico de gran relevancia en la ingeniería y la ciencia."),
        Idioma(nombre_idioma="Italiano", descripcion_idioma="Idioma romance reconocido por su valor cultural y artístico."),
        Idioma(nombre_idioma="Japonés", descripcion_idioma="Idioma asiático de creciente demanda en tecnología y cultura."),
    ]
    db.session.add_all(idiomas)
    db.session.commit()  # commit para que los idiomas tengan id

   
    # 3. PROFESORES
    
    profesor_prueba = Profesor(
        email="profesor@test.com",
        nombre="PROFESOR",
        primer_apellido="Prueba",
        segundo_apellido="Prueba 2",
        sueldo=18000.0,
    )
    profesor_prueba.set_contrasena("PROFESOR")
    db.session.add(profesor_prueba)

    # 
    datos_profesores = [
        ("María", "Hernández", "López", 22000.0),
        ("Carlos", "Ramírez", "Soto", 19500.0),
        ("Giovanna", "Bianchi", "Rossi", 21000.0),
        ("Klaus", "Müller", None, 23000.0),
        ("Akiko", "Tanaka", "Yamamoto", 20000.0),
    ]
    profesores = [profesor_prueba]
    for nombre, ap1, ap2, sueldo in datos_profesores:
        email = f"{quitar_acentos(nombre)}{quitar_acentos(ap1)}@idiomas.unam.mx"
        prof = Profesor(
            email=email,
            nombre=nombre,
            primer_apellido=ap1,
            segundo_apellido=ap2,
            sueldo=sueldo,
        )
        prof.set_contrasena("profesor123")
        db.session.add(prof)
        profesores.append(prof)

    # 
    #  ALUMNO
    
    alumno_prueba = Alumno(
        email="alumno@test.com",
        nombre="ALUMNO",
        primer_apellido="Prueba",
        segundo_apellido="Prueba 2",
    )
    alumno_prueba.set_contrasena("ALUMNO")
    db.session.add(alumno_prueba)

    # Alumnos adicionales
    datos_alumnos = [
        ("Camila", "Martínez", "Rodríguez"),
        ("Mateo", "Sánchez", "García"),
        ("Lucas", "Pérez", "Gómez"),
        ("Sofía", "González", "López"),
        ("Nicolás", "Torres", "Jiménez"),
        ("Valentina", "Díaz", "Morales"),
        ("Santiago", "Flores", "Ortiz"),
        ("Isabella", "Reyes", "Cruz"),
        ("Sebastián", "Vargas", None),
        ("Regina", "Castro", "Núñez"),
        ("Emiliano", "Ruiz", "Mendoza"),
        ("Renata", "Álvarez", "Romero"),
        ("Diego", "Herrera", "Silva"),
        ("Ximena", "Téllez", "Olvera"),
        ("Gabriel", "Velasco", "Andrade"),
    ]
    alumnos = [alumno_prueba]
    for i, (nombre, ap1, ap2) in enumerate(datos_alumnos):
        correo = f"{quitar_acentos(nombre)}{quitar_acentos(ap1)}@alumnos.unam.mx"
        alum = Alumno(
            email=correo,
            nombre=nombre,
            primer_apellido=ap1,
            segundo_apellido=ap2,
        )
        alum.set_contrasena("alumno123")
        db.session.add(alum)
        alumnos.append(alum)

    db.session.commit()  # commit para que profesores y alumnos tengan id

    # 
    # CURSOS
    # Cada profesor enseña principalmente un idioma (por su perfil)
    # idiomas: 0=Inglés 1=Francés 2=Alemán 3=Italiano 4=Japonés
    # profesores: 0=Prueba 1=María 2=Carlos 3=Giovanna 4=Klaus 5=Akiko
    niveles = list(Niveles)
    periodos = list(PeriodoEnum)

   
    config_cursos = [
        (0, 0, Niveles.A_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Curso introductorio de inglés para principiantes."),
        (0, 0, Niveles.B_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Inglés intermedio enfocado en conversación."),
        (1, 0, Niveles.A_DOS, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Inglés básico-intermedio con énfasis en gramática."),
        (1, 1, Niveles.A_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Primeros pasos en el idioma francés."),
        (2, 1, Niveles.B_DOS, EstadoCurso.CERRADO, PeriodoEnum.OTONO, 2025, "Francés avanzado, preparación para certificación DELF."),
        (2, 2, Niveles.A_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Alemán para principiantes, vocabulario cotidiano."),
        (3, 2, Niveles.B_UNO, EstadoCurso.CERRADO, PeriodoEnum.OTONO, 2025, "Alemán intermedio, lectura y comprensión."),
        (3, 3, Niveles.A_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Introducción al italiano y su cultura."),
        (3, 3, Niveles.C_UNO, EstadoCurso.BORRADOR, PeriodoEnum.OTONO, 2026, "Italiano avanzado, literatura y conversación culta."),
        (4, 2, Niveles.C_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Alemán avanzado para fines académicos."),
        (5, 4, Niveles.A_UNO, EstadoCurso.PUBLICADO, PeriodoEnum.PRIMAVERA, 2026, "Japonés desde cero: hiragana y katakana."),
        (5, 4, Niveles.A_DOS, EstadoCurso.BORRADOR, PeriodoEnum.OTONO, 2026, "Japonés básico, introducción a kanji."),
    ]

    cursos = []
    for prof_idx, idi_idx, nivel, estado, periodo, anio, desc in config_cursos:
        curso = Curso(
            id_profesor=profesores[prof_idx].id_profesor,
            id_idioma=idiomas[idi_idx].id_idioma,
            nivel=nivel,
            estado=estado,
            descripcion_curso=desc,
            periodo=periodo,
            anio=anio,
        )
        db.session.add(curso)
        cursos.append(curso)

    db.session.commit()  # commit para que los cursos tengan id

    # 6. HORARIOS
   
    bloques_posibles = [
        ([DiasSemana.LUNES, DiasSemana.MIERCOLES, DiasSemana.VIERNES], time(10, 0), time(11, 0)),
        ([DiasSemana.MARTES, DiasSemana.JUEVES], time(9, 0), time(10, 30)),
        ([DiasSemana.LUNES, DiasSemana.MIERCOLES], time(16, 0), time(17, 30)),
        ([DiasSemana.MARTES, DiasSemana.JUEVES], time(18, 0), time(19, 30)),
        ([DiasSemana.SABADO], time(9, 0), time(12, 0)),
        ([DiasSemana.VIERNES], time(14, 0), time(16, 0)),
    ]

    for curso in cursos:
        # Cada curso toma 1 bloque aleatorio (algunos 2)
        num_bloques = random.choice([1, 1, 2])
        bloques_curso = random.sample(bloques_posibles, num_bloques)
        for dias, h_ini, h_fin in bloques_curso:
            for dia in dias:
                horario = Horario(
                    id_curso=curso.id_curso,
                    dia=dia,
                    hora_inicio=h_ini,
                    hora_fin=h_fin,
                )
                db.session.add(horario)

    db.session.commit()

    # 7. MATERIALES
    # Solo los cursos PUBLICADOS y CERRADOS tienen material
    titulos_material = [
        ("Presentación del curso", "pdf"),
        ("Temario completo", "pdf"),
        ("Módulo 1 - Vocabulario básico", "pdf"),
        ("Módulo 1 - Ejercicios", "docx"),
        ("Módulo 2 - Gramática", "pdf"),
        ("Tarea 1", "docx"),
        ("Presentación de apoyo", "pptx"),
        ("Lista de verbos", "xlsx"),
    ]

    for curso in cursos:
        if curso.estado in (EstadoCurso.PUBLICADO, EstadoCurso.CERRADO):
            # Entre 3 y 6 materiales por curso
            num_mat = random.randint(3, 6)
            materiales_curso = random.sample(titulos_material, num_mat)
            for titulo, tipo in materiales_curso:
                material = Material(
                    id_curso=curso.id_curso,
                    titulo=titulo,
                    tipo_archivo=tipo,
                    url_archivo=f"uploads/curso_{curso.id_curso}_{titulo.replace(' ', '_').lower()}.{tipo}",
                )
                db.session.add(material)

    db.session.commit()


    # 8. INSCRIPCIONES (con calificaciones en cursos cerrados)
   
    # Los alumnos se inscriben a cursos PUBLICADOS y CERRADOS
    cursos_inscribibles = [c for c in cursos if c.estado in (EstadoCurso.PUBLICADO, EstadoCurso.CERRADO)]

    for alumno in alumnos:
        # Cada alumno se inscribe a entre 1 y 4 cursos distintos
        num_cursos = random.randint(1, 4)
        cursos_alumno = random.sample(cursos_inscribibles, min(num_cursos, len(cursos_inscribibles)))
        for curso in cursos_alumno:
            # Fecha de inscripción aleatoria en los últimos 60 días
            dias_atras = random.randint(1, 60)
            fecha_insc = datetime.now() - timedelta(days=dias_atras)

            # Si el curso está CERRADO, ya tiene calificación; si está PUBLICADO, puede o no
            if curso.estado == EstadoCurso.CERRADO:
                calif = round(random.uniform(6.0, 10.0), 1)
            else:
                # 30% de los publicados ya tienen una calificación parcial
                calif = round(random.uniform(7.0, 10.0), 1) if random.random() < 0.3 else None

            inscripcion = Inscripcion(
                id_alumno=alumno.id_alumno,
                id_curso=curso.id_curso,
                fecha_inscripcion=fecha_insc,
                calificacion=calif,
            )
            db.session.add(inscripcion)

    db.session.commit()

 