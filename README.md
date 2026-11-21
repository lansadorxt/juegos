![CI](https://github.com/lansadorxt/juegos/actions/workflows/ci.yml/badge.svg)
[![Coverage](https://codecov.io/gh/lansadorxt/juegos/branch/master/graph/badge.svg)](https://codecov.io/gh/lansadorxt/juegos)

# Pruebas Unitarias con `unittest` — Microaplicación de Videojuegos (Flask)

Suite de pruebas unitarias desarrollada con el módulo nativo `unittest` de Python para verificar la integridad de los modelos ORM, las rutas web con autenticación y los endpoints de la API RESTful.

## Cobertura de Pruebas (`tests/`)

* **`tests/test_models.py` (4 pruebas):** Valida las operaciones CRUD (`crear`, `leer`, `actualizar`, `eliminar`) sobre el modelo `Juego` y la creación de usuarios en `User`, verificando el cifrado automático de contraseñas y la protección de lectura del atributo `password`.
* **`tests/test_routes.py` (5 pruebas):** Utiliza `app.test_client()` para comprobar el acceso a rutas públicas (`/auth/login`), la redirección (`302`) al intentar entrar sin sesión a rutas protegidas con `@login_required` (`/juegos`), el acceso autenticado, el guardado de registros vía formulario web y el manejador de error `404`.
* **`tests/test_api.py` (6 pruebas):** Comprueba los endpoints RESTful (`/api/juegos` y `/api/juegos/<int:id>`) con los métodos `GET`, `POST`, `PUT` y `DELETE`, validando respuestas JSON y códigos de estado `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request` y `404 Not Found`.

## Ejecución de las Pruebas

```bash
python -m unittest discover -s tests -v