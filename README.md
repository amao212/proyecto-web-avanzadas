# Sistema web de inventario, lotes y reabastecimiento — Bimestre 1

**Base del proyecto y autenticación**

PYME ficticia: *Distribuidora Andina* (alimentos no perecibles y bebidas). Stack: Python · Flask · Jinja2 · SQLAlchemy · bcrypt · pytest.

## Novedades de esta versión
- Estructura Flask (application factory, blueprints, SQLAlchemy, Jinja2) con configuración por variables de entorno.
- Registro, inicio y cierre de sesión con contraseñas **bcrypt** (hash con sal), roles `admin`/`bodega`/`ventas` y rutas protegidas.
- CSRF en todos los formularios y validación en cliente (HTML5) y servidor (WTForms).
- CRUD de **productos** (catálogo): listado paginado con búsqueda y filtro por estado, detalle por identificador, edición y eliminación con confirmación.
- 7 pruebas automatizadas.

## Cómo ejecutarlo
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# la base se crea sola al iniciar
python run.py
pytest
```
Variables de entorno en `.env.example`. No subir `.env` ni bases de datos.
