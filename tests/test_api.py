import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Juego

if app.config.get('SQLALCHEMY_DATABASE_URI') != 'sqlite:///:memory:':
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    if hasattr(db, '_app_engines') and app in db._app_engines:
        for engine in db._app_engines[app].values():
            engine.dispose()
        db._app_engines.pop(app, None)
    app.extensions.pop('sqlalchemy', None)
    db.init_app(app)


class TestAPI(unittest.TestCase):

    def setUp(self):
        """Inicializa la base de datos en memoria con un registro inicial para la API."""
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = app.test_client()

        juego_inicial = Juego(nombre="Elden Ring", descripcion="RPG de mundo abierto", precio=69.99)
        db.session.add(juego_inicial)
        db.session.commit()
        self.juego_id = juego_inicial.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_api_get_lista_juegos(self):
        """Verifica que GET /api/juegos retorne 200 OK y una lista JSON."""
        respuesta = self.client.get('/api/juegos')
        self.assertEqual(respuesta.status_code, 200)
        datos = json.loads(respuesta.data)
        self.assertIsInstance(datos, list)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]['nombre'], "Elden Ring")

    def test_api_post_crear_juego(self):
        """Verifica que POST /api/juegos cree un recurso y devuelva 201 Created."""
        payload = {
            "nombre": "The Witcher 3",
            "descripcion": "RPG de fantasía oscura",
            "precio": 39.99
        }
        respuesta = self.client.post(
            '/api/juegos',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(respuesta.status_code, 201)
        datos = json.loads(respuesta.data)
        self.assertEqual(datos['nombre'], "The Witcher 3")

    def test_api_post_datos_incompletos_400(self):
        """Verifica que POST sin campos obligatorios devuelva 400 Bad Request."""
        payload_incompleto = {"nombre": "Juego Incompleto"}
        respuesta = self.client.post(
            '/api/juegos',
            data=json.dumps(payload_incompleto),
            content_type='application/json'
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_api_get_juego_por_id_y_404(self):
        """Verifica la consulta individual (200) y el manejo de ID inexistente (404)."""
        resp_ok = self.client.get(f'/api/juegos/{self.juego_id}')
        self.assertEqual(resp_ok.status_code, 200)

        resp_404 = self.client.get('/api/juegos/9999')
        self.assertEqual(resp_404.status_code, 404)

    def test_api_put_actualizar_juego(self):
        """Verifica la actualización completa mediante PUT /api/juegos/<id>."""
        payload = {
            "nombre": "Elden Ring: Shadow of the Erdtree",
            "descripcion": "Edición completa",
            "precio": 89.99
        }
        respuesta = self.client.put(
            f'/api/juegos/{self.juego_id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(respuesta.status_code, 200)
        datos = json.loads(respuesta.data)
        self.assertEqual(datos['nombre'], "Elden Ring: Shadow of the Erdtree")

    def test_api_delete_eliminar_juego(self):
        """Verifica la eliminación de un juego mediante DELETE /api/juegos/<id> (204)."""
        respuesta = self.client.delete(f'/api/juegos/{self.juego_id}')
        self.assertEqual(respuesta.status_code, 204)

        verificacion = self.client.get(f'/api/juegos/{self.juego_id}')
        self.assertEqual(verificacion.status_code, 404)


if __name__ == '__main__':
    unittest.main()