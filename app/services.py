import hashlib
import secrets
from datetime import date, timedelta

from flask import current_app
from sqlalchemy import case, func, or_

from .extensions import db
from .models import Lote, Movimiento, Rol, TokenReset, ahora


class StockInsuficiente(ValueError):
    pass


def asegurar_datos_base():
    for nombre in ("admin", "bodega", "ventas"):
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
    db.session.commit()


def conds_aptos():
    return [
        Lote.estado == "disponible",
        Lote.cantidad_disponible > 0,
        or_(Lote.fecha_caducidad.is_(None), Lote.fecha_caducidad >= date.today()),
    ]


def stock_disponible(producto_id):
    return (db.session.query(func.coalesce(func.sum(Lote.cantidad_disponible), 0))
            .filter(Lote.producto_id == producto_id, *conds_aptos()).scalar())


def orden_fefo():
    return (case((Lote.fecha_caducidad.is_(None), 1), else_=0),
            Lote.fecha_caducidad, Lote.fecha_ingreso, Lote.id)


def registrar_entrada(producto, datos, usuario):
    lote = Lote(producto_id=producto.id, codigo=datos["codigo"], proveedor_id=datos["proveedor_id"],
                cantidad_inicial=datos["cantidad"], cantidad_disponible=datos["cantidad"],
                costo_unitario=datos["costo"], fecha_ingreso=datos["fecha_ingreso"],
                fecha_caducidad=datos.get("fecha_caducidad"), ubicacion=datos.get("ubicacion") or None)
    db.session.add(lote)
    db.session.flush()
    db.session.add(Movimiento(tipo="ENTRADA", producto_id=producto.id, lote_id=lote.id,
                              cantidad=datos["cantidad"], usuario_id=usuario.id, motivo="Recepción de mercadería"))
    db.session.commit()
    return lote


def registrar_salida(producto, cantidad, usuario, motivo=None):
    lotes = (Lote.query.filter(Lote.producto_id == producto.id, *conds_aptos())
             .order_by(*orden_fefo()).with_for_update().all())
    disponible = sum(l.cantidad_disponible for l in lotes)
    if cantidad > disponible:
        raise StockInsuficiente(f"Stock insuficiente: solo hay {disponible} disponible(s) para la venta.")
    restante, usados = cantidad, []
    for lote in lotes:
        if restante == 0:
            break
        tomar = min(lote.cantidad_disponible, restante)
        lote.cantidad_disponible -= tomar
        if lote.cantidad_disponible == 0:
            lote.estado = "agotado"
        db.session.add(Movimiento(tipo="SALIDA", producto_id=producto.id, lote_id=lote.id, cantidad=tomar,
                                  usuario_id=usuario.id, motivo=motivo or "Despacho"))
        usados.append((lote.codigo, tomar))
        restante -= tomar
    db.session.commit()
    return usados


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def crear_token_reset(usuario):
    TokenReset.query.filter_by(usuario_id=usuario.id, usado=False).update({"usado": True})
    token = secrets.token_urlsafe(32)
    db.session.add(TokenReset(usuario_id=usuario.id, token_hash=_hash_token(token),
                              expira_en=ahora() + timedelta(minutes=current_app.config["RESET_TOKEN_MINUTOS"])))
    db.session.commit()
    return token


def validar_token(token):
    t = TokenReset.query.filter_by(token_hash=_hash_token(token)).first()
    return t if t and not t.usado and t.expira_en > ahora() else None


def consumir_token(registro, nueva_password):
    registro.usuario.set_password(nueva_password)
    registro.usado = True
    db.session.commit()
