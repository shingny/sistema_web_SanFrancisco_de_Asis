"""Microservicio 2 — Separado / Reserva de Tortas de San Francisco de Asís.

Aplicación Flask independiente, ejecutable en su propio puerto.
- Puerto por defecto: 5002

Gestiona las tortas ya compradas en tienda física que quedan
separadas/reservadas para su recojo y el inventario asociado.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Instancia compartida de la base de datos (Flask-SQLAlchemy)
db = SQLAlchemy()

CORS_ORIGINS = ["*"]


def create_app() -> Flask:
    """Fábrica de la aplicación Flask del microservicio de separado."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

    # Importar modelos para que SQLAlchemy los conozca antes de crear tablas
    from models.inventario import Inventario  # noqa: F401
    from models.reserva import Reserva  # noqa: F401

    # Registrar blueprints (rutas)
    from routes.reservas_routes import reservas_bp

    app.register_blueprint(reservas_bp, url_prefix="/api")

    # Crear tablas y sembrar los productos del inventario
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
                "servicio": "Microservicio 2 — Separado de Tortas",
                "estado": "activo",
                "endpoints": [
                    "POST /api/reservas",
                    "GET  /api/reservas?tienda_id=",
                    "PATCH /api/reservas/<id>/estado",
                    "GET  /api/inventario?tienda_id=",
                ],
            }
        )

    return app


# Variable `app` a nivel de módulo para que funcione con gunicorn: `gunicorn app:app`
app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=True)