# Sistema web de inventario, lotes y reabastecimiento — Bimestre 1

Commit 2 de 5 · **Recuperación de clave, proveedores, lotes y movimientos**

PYME ficticia: *Distribuidora Andina* (alimentos no perecibles y bebidas). Stack: Python · Flask · Jinja2 · SQLAlchemy · bcrypt · pytest.

## Novedades de esta versión
- Recuperación de contraseña con token de un solo uso y caducidad (correo simulado en consola).
- Permisos por rol (`admin`, `bodega`, `ventas`) con respuesta 403.
- Proveedores, **lotes** (recepción de mercadería con costo, caducidad y ubicación) y **movimientos** de entrada/salida.
- Salidas con **FEFO**: se despacha primero el lote apto que caduca antes; los vencidos se excluyen.
- Stock disponible por producto, detalle con lotes y movimientos, comando `flask --app run seed` con datos de demostración.
- 13 pruebas automatizadas.

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
