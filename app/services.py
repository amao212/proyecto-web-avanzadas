from .extensions import db
from .models import Rol


def asegurar_datos_base():
    for nombre in ("admin", "bodega", "ventas"):
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
    db.session.commit()
