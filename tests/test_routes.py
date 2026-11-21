import os
import re
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Juego, User

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


class TestRoutes(unittest.TestCase):

    def setUp(self):
        """Prepara el cliente de pruebas y un usuario base en la BD en memoria."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['REMEMBER_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_DOMAIN'] = None
        app.config['SERVER_NAME'] = None
        app.config['SESSION_PROTECTION'] = None

        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        if hasattr(app, 'login_manager'):
            app.login_manager.session_protection = None

        self.client = app.test_client()

        user_data = {
            "username": "jony_test",
            "password": "TestPassword123"
        }
        if hasattr(User, "email"):
            user_data["email"] = "jony_test@example.com"

        usuario = User(**user_data)
        db.session.add(usuario)
        db.session.commit()
        self.usuario_id = str(usuario.get_id())

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def _iniciar_sesion(self):
        """Autentica el cliente de pruebas enviando el formulario y asegurando la sesión."""
        get_login = self.client.get('/auth/login')
        html = get_login.get_data(as_text=True)

        nombres = re.findall(r'<input[^>]+name=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
        payload = {}
        for campo in nombres:
            cl = campo.lower()
            if cl in ('csrf_token', 'submit'):
                continue
            elif 'mail' in cl or 'correo' in cl:
                payload[campo] = 'jony_test@example.com'
            elif 'pass' in cl or 'contra' in cl or 'clave' in cl:
                payload[campo] = 'TestPassword123'
            elif 'remember' in cl or 'recordar' in cl:
                continue
            else:
                payload[campo] = 'jony_test'

        if not payload:
            payload = {'username': 'jony_test', 'password': 'TestPassword123'}

        self.client.post('/auth/login', data=payload, follow_redirects=True)

        with self.client.session_transaction() as sess:
            sess['_user_id'] = self.usuario_id
            sess['_fresh'] = True

    def test_ruta_login_publica(self):
        """Verifica que la vista de inicio de sesión cargue correctamente (200 OK)."""
        respuesta = self.client.get('/auth/login')
        self.assertEqual(respuesta.status_code, 200)

    def test_ruta_protegida_sin_sesion_redirige(self):
        """Verifica que acceder a /juegos sin iniciar sesión redirija al login (302)."""
        respuesta = self.client.get('/juegos', follow_redirects=False)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/auth/login', respuesta.headers['Location'])

    def test_acceso_ruta_protegida_con_sesion(self):
        """Verifica el inicio de sesión y el acceso permitido a /juegos."""
        self._iniciar_sesion()
        respuesta = self.client.get('/juegos')
        self.assertEqual(respuesta.status_code, 200)

    def test_guardar_juego_autenticado(self):
        """Verifica la creación de un juego desde el formulario web autenticado."""
        self._iniciar_sesion()
        respuesta = self.client.post('/guardar_juego', data={
            'nombre': 'God of War',
            'descripcion': 'Acción y mitología nórdica',
            'precio': '49.99'
        }, follow_redirects=True)

        self.assertEqual(respuesta.status_code, 200)
        juego_creado = Juego.query.filter_by(nombre='God of War').first()
        self.assertIsNotNone(juego_creado)

    def test_ruta_inexistente_devuelve_404(self):
        """Verifica que una URL inexistente active el manejador personalizado 404."""
        respuesta = self.client.get('/ruta_totalmente_inexistente')
        self.assertEqual(respuesta.status_code, 404)


if __name__ == '__main__':
    unittest.main()