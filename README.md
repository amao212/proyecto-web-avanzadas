# Sistema web de inventario, lotes y reabastecimiento — Bimestre 1

**Tiempo real: chat con WebSockets**

PYME ficticia: *Distribuidora Andina* (alimentos no perecibles y bebidas). Stack: Python · Flask · Jinja2 · SQLAlchemy · Flask-SocketIO · bcrypt · pytest.

## Novedades de esta versión
- Servidor WebSocket propio dentro del monolito (Flask-SocketIO) con autenticación en el handshake.
- Chat con salas (*General*, *Bodega*, *Ventas*), historial persistido y usuarios conectados.
- Validación y saneamiento de mensajes en el servidor; el cliente pinta con `textContent` (anti-XSS).
- Cliente socket.io local y notificaciones tipo *toast*.
- 16 pruebas automatizadas.

## Cómo ejecutarlo
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run seed
python run.py
pytest
```
Variables de entorno en `.env.example`. No subir `.env` ni bases de datos.
