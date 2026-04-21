from app import create_app
from app.extensions import db
from app.models import Usuario, RolUsuario

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = Usuario(
        email="admin@test.com",
        nombre="Admin",
        primer_apellido="Principal",
        rol=RolUsuario.ADMIN
    )
    admin.set_contrasena("ADMIN")
    
    profesor = Usuario(
        email="profesor@test.com",
        nombre="Profesor",
        primer_apellido="Prueba",
        segundo_apellido='Prueba 2',
        rol=RolUsuario.PROFESOR
    )
    profesor.set_contrasena("PROFESOR")
    
    alumno = Usuario(
        email="alumno@test.com",
        nombre="Alumno",
        primer_apellido="Pérez",
        segundo_apellido='Maverick',
        rol=RolUsuario.ALUMNO
    )
    alumno.set_contrasena("ALUMNO")

    db.session.add(admin)
    db.session.add(profesor)
    db.session.add(alumno)
    db.session.commit()

    # Mensaje de éxito
    print("Datos de prueba creados correctamente")