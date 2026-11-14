from datetime import datetime, timezone

import bcrypt
from flask_login import UserMixin

from .extensions import db, login_manager


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Rol(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=ahora, nullable=False)
    rol = db.relationship("Rol")

    def set_password(self, plano):
        self.password_hash = bcrypt.hashpw(plano.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

    def check_password(self, plano):
        try:
            return bcrypt.checkpw(plano.encode("utf-8"), self.password_hash.encode("ascii"))
        except ValueError:
            return False


@login_manager.user_loader
def cargar_usuario(user_id):
    u = db.session.get(Usuario, int(user_id))
    return u if u and u.activo else None


class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(30), unique=True, index=True, nullable=False)
    nombre = db.Column(db.String(120), index=True, nullable=False)
    descripcion = db.Column(db.String(500))
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)
    unidad = db.Column(db.String(10), nullable=False, default="unidad")
    estado = db.Column(db.String(10), index=True, nullable=False, default="activo")
    creado_en = db.Column(db.DateTime, default=ahora, nullable=False)
