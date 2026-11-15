from app.extensions import socketio
from app.models import Mensaje, SalaChat

from .conftest import CLAVE


def _recibidos(sio, nombre):
    return [e["args"][0] for e in sio.get_received() if e["name"] == nombre]


def test_websocket_rechaza_usuarios_sin_sesion(app, client):
    assert not socketio.test_client(app, flask_test_client=client).is_connected()


def test_chat_en_tiempo_real_entre_dos_usuarios_con_historial(app, login):
    from app.models import Rol, Usuario
    from app.extensions import db
    c1 = login("admin")
    c2 = app.test_client()
    with app.app_context():
        u = Usuario(nombre="Segundo Usuario", email="b@test.com", rol=Rol.query.filter_by(nombre="ventas").one())
        u.set_password(CLAVE)
        db.session.add(u); db.session.commit()
        sala = SalaChat.query.filter_by(nombre="General").one().id
    c2.post("/login", data={"email": "b@test.com", "password": CLAVE})
    s1, s2 = socketio.test_client(app, flask_test_client=c1), socketio.test_client(app, flask_test_client=c2)
    assert s1.is_connected() and s2.is_connected()
    pres = _recibidos(s1, "presencia")[-1]
    assert len(pres) == 2
    s1.emit("unirse", {"sala_id": sala}); s2.emit("unirse", {"sala_id": sala})
    s1.get_received(); s2.get_received()
    s1.emit("mensaje", {"sala_id": sala, "texto": "  hola <b>equipo</b>  "})
    recibido = _recibidos(s2, "mensaje")[0]
    assert recibido["texto"] == "hola <b>equipo</b>"
    with app.app_context():
        assert Mensaje.query.one().contenido == "hola <b>equipo</b>"
    s3 = socketio.test_client(app, flask_test_client=c2)
    s3.emit("unirse", {"sala_id": sala})
    assert _recibidos(s3, "historial")[0]["mensajes"][0]["texto"] == "hola <b>equipo</b>"


def test_chat_valida_mensajes_en_servidor(app, login):
    c = login("admin")
    with app.app_context():
        sala = SalaChat.query.filter_by(nombre="General").one().id
    s = socketio.test_client(app, flask_test_client=c)
    s.get_received()
    s.emit("mensaje", {"sala_id": sala, "texto": "sin unirse"})
    s.emit("unirse", {"sala_id": sala}); s.get_received()
    for malo in ("   ", "x" * 501, 123, None):
        s.emit("mensaje", {"sala_id": sala, "texto": malo})
    s.emit("unirse", {"sala_id": 9999})
    assert len(_recibidos(s, "error_chat")) == 5
    with app.app_context():
        assert Mensaje.query.count() == 0


def test_alerta_de_stock_minimo_llega_por_websocket_y_crea_reposicion(app, login, datos):
    from app.models import SolicitudReposicion
    c = login("admin")
    s = socketio.test_client(app, flask_test_client=c)
    s.get_received()
    c.post(f"/productos/{datos['producto_id']}/salida", data={"cantidad": 27})
    alertas = _recibidos(s, "alerta")
    assert any(a["tipo"] == "stock_minimo" for a in alertas)
    with app.app_context():
        assert SolicitudReposicion.query.filter_by(estado="pendiente").count() == 1
    c.post(f"/productos/{datos['producto_id']}/salida", data={"cantidad": 1})
    with app.app_context():
        assert SolicitudReposicion.query.count() == 1


def test_salas_segun_el_rol(app, login):
    from app.models import Rol, Usuario
    from app.extensions import db
    c = login("bodega")
    r = c.get("/chat").data
    assert b"General" in r and b"Bodega" in r and b"Ventas" not in r.replace(b"Ventas Demo", b"")
    with app.app_context():
        ventas = SalaChat.query.filter_by(nombre="Ventas").one().id
        general = SalaChat.query.filter_by(nombre="General").one().id
    s = socketio.test_client(app, flask_test_client=c)
    s.get_received()
    s.emit("unirse", {"sala_id": ventas})
    assert _recibidos(s, "error_chat")[0]["mensaje"] == "No tienes acceso a esa sala."
    s.emit("mensaje", {"sala_id": ventas, "texto": "intruso"})
    s.emit("unirse", {"sala_id": general})
    assert _recibidos(s, "historial")[0]["sala"] == "General"
    with app.app_context():
        assert Mensaje.query.count() == 0


def test_ventas_ve_general_y_ventas_y_admin_ve_todas(app, login):
    c = login("ventas")
    r = c.get("/chat").data
    assert b"General" in r and b"Ventas" in r and b">Bodega<" not in r
    c2 = app.test_client()
    crear = __import__("tests.conftest", fromlist=["crear_usuario"]).crear_usuario
    crear(app, "adm@test.com", "admin")
    c2.post("/login", data={"email": "adm@test.com", "password": CLAVE})
    r2 = c2.get("/chat").data
    assert b"General" in r2 and b">Bodega<" in r2 and b"Ventas" in r2
