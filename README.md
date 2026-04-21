# Repositorio oficial del proyecto de Ingeniería de Software

## Descripción del proyecto: 
Crear un sistema web que permita administrar cursos de idiomas, facilitando la gestión de profesores, alumnos, cursos y materiales didácticos, asegurando un control adecuado de accesos y procesos de inscripción

Colaboradores:
- @fleabaag
- @tainzoe9
- @Tonagg
- @JorgeLazaro7

## Ejecutar de manera local:
Es necesario tener un entorno virtual activado, si aún no tienes uno iniciado dentro del directorio del proyecto ejecuta la siguiente comando:
```
python3 -m venv .venv
```

Posteriormente activa el entorno virtual con el siguiente comando:

```
source .venv/bin/activate
```
Para desactivar sólo hace falta escribir el comando `deactivate`.

Una vez activado el `venv` hay que instalar los requerimientos para el proyecto. Entonces es necesario ejecutar el siguiente comando:

```
pip install -r requirements.txt
```

Finalmente ejecutar:
```
python3 run.py
```

## Para crear las tablas de la base de datos:

Primeramente es importante revisar que esté delcarada en `.flaskenv` la siguiente variable: 
```
FLASK_APP=run.py
```
Y que el `.env` tenga los datos correctos de la base de datos. 

Una vez hecho esto, dentro del directorio principal ejecutar:
```
flask shell
```
Y dentro de la shell ejecutar lo siguiente (sólo en desarrollo):

```python
from app import create_app
from app.extensions import db
app = create_app()
app.app_context().push()
db.drop_all()
db.create_all()

```