from app.extensions import db
from app.models import Producto

PROD = {"sku": "abc-100", "nombre": "Arroz 1kg", "descripcion": "", "stock_minimo": 5, "unidad": "unidad", "estado": "activo"}


def test_crud_producto_completo(login, app):
    c = login("admin")
    assert c.post("/productos/nuevo", data=PROD).status_code == 302
    with app.app_context():
        p = Producto.query.one()
        assert p.sku == "ABC-100"
        pid = p.id
    assert b"Ya existe" in c.post("/productos/nuevo", data=PROD).data
    assert b"Entre 3 y 120" in c.post("/productos/nuevo", data=dict(PROD, sku="X-1", nombre="ab")).data
    assert b"Arroz 1kg" in c.get(f"/productos/{pid}").data
    assert c.post(f"/productos/{pid}/editar", data=dict(PROD, nombre="Arroz Premium")).status_code == 302
    with app.app_context():
        assert db.session.get(Producto, pid).nombre == "Arroz Premium"
    assert c.post(f"/productos/{pid}/eliminar").status_code == 302
    with app.app_context():
        assert Producto.query.count() == 0
    assert c.get(f"/productos/{pid}").status_code == 404


def test_listado_paginado_y_busqueda(login, app):
    c = login("admin")
    with app.app_context():
        db.session.add_all(Producto(sku=f"SKU-{i:03d}", nombre=f"Producto {i}") for i in range(25))
        db.session.add(Producto(sku="ZZZ-1", nombre="Café especial"))
        db.session.commit()
    p1 = c.get("/productos").data
    assert b"Siguiente" in p1 and b"de 26 registros" in p1
    assert p1.count(b"Ver</a>") == 10 and c.get("/productos?page=3").data.count(b"Ver</a>") == 6
    r = c.get("/productos?q=caf%C3%A9")
    assert b"Caf" in r.data and b"SKU-001" not in r.data
    assert b"No se encontraron" in c.get("/productos?q=%25%27%3B--").data


