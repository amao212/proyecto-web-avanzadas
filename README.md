# Sistema web de inventario, lotes y reabastecimiento — Bimestre 1

Commit 4 de 5 · **Alertas en vivo, reposición, salas por rol y mejoras visuales**

PYME ficticia: *Distribuidora Andina* (alimentos no perecibles y bebidas). Stack: Python · Flask · Jinja2 · SQLAlchemy · Flask-SocketIO · bcrypt · pytest.

## Novedades de esta versión
- Tras cada movimiento se evalúan alertas de **stock mínimo** y **lotes próximos a caducar**, emitidas por WebSocket a los usuarios conectados.
- Solicitudes de **reposición** automáticas (sin duplicar pendientes) y página para atenderlas.
- Dashboard con stock en nivel mínimo, lotes por caducar y lotes vencidos.
- Chat por rol: *bodega* ve General y Bodega, *ventas* ve General y Ventas, *admin* todas (validado también en el servidor).
- Mejoras visuales (tarjetas de resumen, foco accesible, diseño responsivo del chat) y optimización de consultas (carga anticipada de relaciones y agregación SQL del stock).
- 19 pruebas automatizadas.

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
