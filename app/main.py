from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from .extensions import db
from .forms import ProductoForm
from .models import Producto

bp = Blueprint("main", __name__)


def _pagina():
    return max(request.args.get("page", 1, type=int), 1)


@bp.route("/")
def index():
    return redirect(url_for("main.dashboard" if current_user.is_authenticated else "auth.signin"))


@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", total_productos=Producto.query.filter_by(estado="activo").count())


@bp.route("/productos")
@login_required
def productos():
    q = request.args.get("q", "").strip()[:100]
    estado = request.args.get("estado", "")
    query = Producto.query
    if q:
        query = query.filter(or_(Producto.sku.ilike(f"{q}%"), Producto.nombre.ilike(f"%{q}%")))
    if estado in ("activo", "inactivo"):
        query = query.filter(Producto.estado == estado)
    pag = query.order_by(Producto.nombre).paginate(page=_pagina(), per_page=current_app.config["POR_PAGINA"],
                                                   error_out=False)
    return render_template("productos/lista.html", pag=pag, q=q, estado=estado,
                           filtros={k: v for k, v in (("q", q), ("estado", estado)) if v})


@bp.route("/productos/<int:id>")
@login_required
def producto_detalle(id):
    p = db.get_or_404(Producto, id)
    return render_template("productos/detalle.html", p=p)


@bp.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def producto_nuevo():
    form = ProductoForm()
    if form.validate_on_submit():
        p = Producto(sku=form.sku.data, nombre=form.nombre.data, descripcion=form.descripcion.data or None,
                     stock_minimo=form.stock_minimo.data, unidad=form.unidad.data, estado=form.estado.data)
        db.session.add(p)
        db.session.commit()
        flash("Producto creado.", "success")
        return redirect(url_for("main.producto_detalle", id=p.id))
    return render_template("productos/form.html", form=form, titulo="Nuevo producto")


@bp.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def producto_editar(id):
    p = db.get_or_404(Producto, id)
    form = ProductoForm(obj=p, producto_id=p.id)
    if form.validate_on_submit():
        p.sku, p.nombre, p.descripcion = form.sku.data, form.nombre.data, form.descripcion.data or None
        p.stock_minimo, p.unidad, p.estado = form.stock_minimo.data, form.unidad.data, form.estado.data
        db.session.commit()
        flash("Producto actualizado.", "success")
        return redirect(url_for("main.producto_detalle", id=p.id))
    return render_template("productos/form.html", form=form, titulo=f"Editar {p.nombre}")


@bp.route("/productos/<int:id>/eliminar", methods=["POST"])
@login_required
def producto_eliminar(id):
    p = db.get_or_404(Producto, id)
    db.session.delete(p)
    db.session.commit()
    flash("Producto eliminado.", "success")
    return redirect(url_for("main.productos"))
