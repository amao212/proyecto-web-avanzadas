from app.models import Usuario

from .conftest import CLAVE, crear_usuario

REGISTRO = {"nombre": "Ana Pérez", "email": "ana@test.com", "area": "ventas",
            "password": "Segura123", "confirmar": "Segura123"}


def test_registro_valido_y_validaciones_de_servidor(client, app):
    assert client.post("/registro", data=REGISTRO).status_code == 302
    malo = dict(REGISTRO, email="otra@test.com", password="abc", confirmar="xyz")
    r = client.post("/registro", data=malo)
    assert r.status_code == 200 and b"Entre 8 y 64" in r.data and b"no coinciden" in r.data
    assert b"ya est" in client.post("/registro", data=REGISTRO).data
    assert b"Correo inv" in client.post("/registro", data=dict(REGISTRO, email="no-es-correo")).data


def test_contrasena_se_guarda_con_hash_bcrypt_y_sal(client, app):
    client.post("/registro", data=REGISTRO)
    crear_usuario(app, "otro@test.com", "ventas")
    with app.app_context():
        a, b = Usuario.query.filter_by(email="ana@test.com").one(), Usuario.query.filter_by(email="otro@test.com").one()
        assert a.password_hash.startswith("$2b$") and "Segura123" not in a.password_hash
        assert a.check_password("Segura123") and not a.check_password("incorrecta1")
        a.set_password(CLAVE); h1 = a.password_hash; a.set_password(CLAVE)
        assert h1 != a.password_hash


def test_login_correcto_e_incorrecto(client, app):
    crear_usuario(app)
    r = client.post("/login", data={"email": "admin@test.com", "password": "mala12345"})
    assert r.status_code == 200 and b"incorrectos" in r.data
    r = client.post("/login", data={"email": "admin@test.com", "password": CLAVE})
    assert r.status_code == 302 and r.headers["Location"].endswith("/dashboard")


def test_login_ignora_redireccion_externa(client, app):
    crear_usuario(app)
    r = client.post("/login?next=https://evil.com", data={"email": "admin@test.com", "password": CLAVE})
    assert r.headers["Location"].endswith("/dashboard")


def test_rutas_protegidas_exigen_sesion(client):
    for url in ("/dashboard", "/productos", "/productos/nuevo"):
        r = client.get(url)
        assert r.status_code == 302 and "/login" in r.headers["Location"], url


