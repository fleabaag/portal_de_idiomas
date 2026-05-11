from app import create_app
from app.extensions import db
from app.models import Alumno, Idioma, Profesor, RolUsuario, Usuario

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = Usuario(
        email="admin@test.com",
        nombre="ADMIN",
        primer_apellido="Principal",
        rol=RolUsuario.ADMIN
    )
    admin.set_contrasena("ADMIN")
    
    profesor = Profesor(
        email="profesor@test.com",
        nombre="PROFESOR",
        primer_apellido="Prueba",
        segundo_apellido="Prueba 2",
    )
    profesor.set_contrasena("PROFESOR")
    
    alumno = Alumno(
        email="alumno@test.com",
        nombre="ALUMNO",
        primer_apellido="Pérez",
        segundo_apellido="Maverick",
    )
    alumno.set_contrasena("ALUMNO")

    db.session.add(admin)
    db.session.add(profesor)
    db.session.add(alumno)
    db.session.commit()

    idiomas = [
        Idioma(nombre_idioma="Inglés", descripcion_idioma="Idioma anglosajón"),
        Idioma(nombre_idioma="Francés", descripcion_idioma="Idioma romance"),
        Idioma(nombre_idioma="Alemán", descripcion_idioma="Idioma germánico"),
        Idioma(nombre_idioma="Italiano", descripcion_idioma="Idioma romance"),
        Idioma(nombre_idioma="Japonés", descripcion_idioma="Idioma asiático"),
    ]

    db.session.add_all(idiomas)
    db.session.commit()

    # Mensaje de éxito
    print("Datos de prueba creados correctamente")