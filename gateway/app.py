"""API Gateway — San Francisco de Asís.

Enruta las peticiones del frontend hacia el microservicio correspondiente:

    - /pedidos/*   -> Microservicio 1 (Recepción de Pedidos)  puerto 5001
    - /reservas/*  -> Microservicio 2 (Separado de Tortas)    puerto 5002

Maneja CORS y la autenticación del panel de tienda.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes.proxy_routes import auth_bp, proxy_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": False}})

# Blueprint de autenticación y de proxy/enrutamiento
app.register_blueprint(auth_bp)
app.register_blueprint(proxy_bp)


@app.route("/")
def inicio():
    """Página de estado del gateway."""
    return jsonify(
        {
            "servicio": "API Gateway — San Francisco de Asís",
            "estado": "activo",
            "rutas": {
                "cliente": ["/pedidos/api/tiendas", "/pedidos/api/tiendas/<id>/productos", "/pedidos/api/pedidos (POST)"],
                "panel": ["/api/auth/login", "/pedidos/api/pedidos (GET/PATCH)", "/reservas/api/reservas"],
            },
        }
    )


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=True)