"""Microservicio 1 — Recepción de Pedidos de San Francisco de Asís.

Aplicación Flask independiente, ejecutable en su propio puerto.
- Puerto por defecto: 5001
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Instancia compartida de la base de datos (Flask-SQLAlchemy)
db = SQLAlchemy()

CORS_ORIGINS = ["*"]


def create_app() -> Flask:
    """Fábrica de la aplicación Flask del microservicio de pedidos."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

    # Importar modelos para que SQLAlchemy los conozca antes de crear tablas
    from models.cliente import Cliente  # noqa: F401
    from models.pedido import Pedido, PedidoItem  # noqa: F401
    from models.producto import Producto  # noqa: F401
    from models.tienda import Tienda  # noqa: F401

    # Registrar blueprints (rutas)
    from routes.pedidos_routes import pedidos_bp
    from routes.productos_routes import productos_bp
    from routes.tiendas_routes import tiendas_bp

    app.register_blueprint(tiendas_bp, url_prefix="/api")
    app.register_blueprint(productos_bp, url_prefix="/api")
    app.register_blueprint(pedidos_bp, url_prefix="/api")

    # Crear tablas y sembrar datos iniciales (5 tiendas + catálogo)
    with app.app_context():
        db.create_all()
        from services.seed import seed_database

        seed_database()

    @app.errorhandler(404)
    def recurso_no_encontrado(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(500)
    def error_interno(error):
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.route("/")
    def inicio():
        return jsonify(
            {
                "servicio": "Microservicio 1 — Recepción de Pedidos",
                "estado": "activo",
                "endpoints": [
                    "GET  /api/tiendas",
                    "GET  /api/tiendas/<id>/productos",
                    "POST /api/pedidos",
                    "GET  /api/pedidos?tienda_id=",
                    "PATCH /api/pedidos/<id>/estado",
                ],
            }
        )

    return app


# Variable `app` a nivel de módulo para que funcione con gunicorn: `gunicorn app:app`
app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=True)