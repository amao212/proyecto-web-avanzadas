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


