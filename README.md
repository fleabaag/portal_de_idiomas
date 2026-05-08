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

Para eliminar y crear de nuevo todos los registros y poblar la base de datos con 3 usuarios simples alumno, administrador y profesor basta con ejecutar:

```
python3 seed.py
```
