import os
import sys
import unittest
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Juego, User

# Configurar SQLite en memoria una sola vez antes de ejecutar las pruebas
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


class TestModels(unittest.TestCase):

    def setUp(self):
        """Crea las tablas limpias en memoria antes de cada prueba."""
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Limpia la sesión y elimina las tablas después de cada prueba."""
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_crear_juego(self):
        """Verifica la inserción y consulta de un videojuego en la base de datos."""
        juego = Juego(nombre="Halo Infinite", descripcion="Shooter espacial", precio=59.99)
        db.session.add(juego)
        db.session.commit()

        recuperado = Juego.query.filter_by(nombre="Halo Infinite").first()
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.descripcion, "Shooter espacial")
        self.assertAlmostEqual(float(recuperado.precio), 59.99)

    def test_actualizar_juego(self):
        """Verifica la modificación de los atributos de un videojuego existente."""
        juego = Juego(nombre="Minecraft", descripcion="Sandbox", precio=29.99)
        db.session.add(juego)
        db.session.commit()

        juego.precio = 19.99
        juego.descripcion = "Sandbox de construcción y aventura"
        db.session.commit()

        actualizado = db.session.get(Juego, juego.id)
        self.assertAlmostEqual(float(actualizado.precio), 19.99)
        self.assertEqual(actualizado.descripcion, "Sandbox de construcción y aventura")

    def test_eliminar_juego(self):
        """Verifica el borrado de un registro de videojuego."""
        juego = Juego(nombre="Cyberpunk 2077", descripcion="RPG futurista", precio=49.99)
        db.session.add(juego)
        db.session.commit()
        juego_id = juego.id

        db.session.delete(juego)
        db.session.commit()

        eliminado = db.session.get(Juego, juego_id)
        self.assertIsNone(eliminado)

    def test_crear_usuario(self):
        """Verifica la creación de un usuario, protección de lectura y hash seguro."""
        clave_plana = "SuperSecreto123"
        usuario = User(username="tester", password=clave_plana)
        db.session.add(usuario)
        db.session.commit()

        guardado = User.query.filter_by(username="tester").first()
        self.assertIsNotNone(guardado)
        with self.assertRaises(AttributeError):
            _ = guardado.password
        self.assertNotEqual(guardado.password_hash, clave_plana)
        self.assertTrue(check_password_hash(guardado.password_hash, clave_plana))


if __name__ == '__main__':
    unittest.main()