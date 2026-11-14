import pytest

from app import create_app
from app.extensions import db
from app.models import Rol, Usuario
from config import TestConfig

CLAVE = "Clave1234"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def crear_usuario(app, email="admin@test.com", rol="admin"):
    with app.app_context():
        u = Usuario(nombre="Usuario Test", email=email, rol=Rol.query.filter_by(nombre=rol).one())
        u.set_password(CLAVE)
        db.session.add(u)
        db.session.commit()


@pytest.fixture
def login(app, client):
    def _login(rol="admin"):
        email = f"{rol}@test.com"
        crear_usuario(app, email, rol)
        r = client.post("/login", data={"email": email, "password": CLAVE})
        assert r.status_code == 302
        return client
    return _login
