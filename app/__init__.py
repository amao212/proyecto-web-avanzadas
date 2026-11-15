from zoneinfo import ZoneInfo
from datetime import timezone

from flask import Flask

from config import Config

from .extensions import csrf, db, login_manager, socketio


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app, async_mode="threading")

    from . import sockets
    from .auth import bp as auth_bp
    from .cli import register_cli
    from .main import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    register_cli(app)

    @app.template_filter("fecha")
    def fecha(d):
        return d.strftime("%d/%m/%Y") if d else "—"

    @app.template_filter("hora_local")
    def hora_local(dt):
        if not dt:
            return "—"
        return dt.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(app.config["ZONA_HORARIA"])).strftime("%d/%m/%Y %H:%M")

    with app.app_context():
        from .services import asegurar_datos_base
        db.create_all()
        asegurar_datos_base()
    return app
