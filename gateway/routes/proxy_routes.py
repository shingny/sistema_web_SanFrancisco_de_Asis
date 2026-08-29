"""Rutas del API Gateway: autenticación y proxy hacia los microservicios."""

from flask import Blueprint, current_app, jsonify, request
import requests

proxy_bp = Blueprint("proxy", __name__)
auth_bp = Blueprint("auth", __name__)

# Prefijos públicos: consultas que hace el frontend de cliente sin token.
# GET  /pedidos/api/tiendas                     (incluye /pedidos/api/tiendas/<id>/productos)
# POST /pedidos/api/pedidos                     (crea pedido)
PUBLICAS_GET = ["/pedidos/api/tiendas"]
PUBLICAS_POST = ["/pedidos/api/pedidos"]
PUBLICAS_PATCH = []


def _es_ruta_publica(metodo, ruta):
    """Indica si una ruta puede responderse sin token de autorización.

    El parámetro `ruta` llega sin la barra inicial (p. ej. "pedidos/api/tiendas"),
    mientras que los prefijos públicos se definen con "/". Normalizamos añadiendo
    la barra inicial para que la comparación sea correcta.
    """
    normalizada = ruta if ruta.startswith("/") else "/" + ruta
    if metodo == "GET":
        return any(normalizada.startswith(prefijo) for prefijo in PUBLICAS_GET)
    if metodo == "POST":
        return any(normalizada.startswith(prefijo) for prefijo in PUBLICAS_POST)
    if metodo == "PATCH":
        return any(normalizada.startswith(prefijo) for prefijo in PUBLICAS_PATCH)
    return False


def _esta_autorizado():
    """Comprueba el header Authorization: Bearer <token> contra la configuración."""
    cabecera = request.headers.get("Authorization", "")
    if not cabecera.startswith("Bearer "):
        return False
    token = cabecera.split(" ", 1)[1]
    return token == current_app.config["PANEL_TOKEN"]


def _servicio_destino(ruta):
    """Devuelve (base_url, ruta_interna) según el prefijo de la ruta entrante."""
    if ruta.startswith("pedidos"):
        return current_app.config["PEDIDOS_URL"], ruta[len("pedidos"):]
    if ruta.startswith("reservas"):
        return current_app.config["SEPARADO_URL"], ruta[len("reservas"):]
    return None, None


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Autentica al personal de tienda y devuelve el token de sesión."""
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password") or ""

    if usuario == current_app.config["PANEL_USER"] and password == current_app.config["PANEL_PASSWORD"]:
        return jsonify(
            {
                "token": current_app.config["PANEL_TOKEN"],
                "usuario": usuario,
                "mensaje": "Sesión iniciada correctamente",
            }
        ), 200

    return jsonify({"error": "Usuario o contraseña incorrectos"}), 401


@proxy_bp.route("/<path:ruta>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def proxy(ruta):
    """Enruta la petición hacia el microservicio correspondiente."""
    base_url, ruta_interna = _servicio_destino(ruta)

    if base_url is None:
        return jsonify({"error": "Ruta no reconocida por el gateway"}), 404

    if not _es_ruta_publica(request.method, ruta) and not _esta_autorizado():
        return jsonify({"error": "No autorizado para el panel de tienda"}), 401

    url = base_url + ruta_interna
    if request.query_string:
        url += "?" + request.query_string.decode("utf-8")

    # Reenvío de la petición al microservicio.
    # Se hace una distinción entre JSON y multipart (subida de imágenes).
    try:
        if request.method in ("POST", "PATCH", "PUT"):
            if request.mimetype == "multipart/form-data":
                cuerpo = request.data
                cabeceras = {"Content-Type": request.content_type}
                respuesta = requests.request(
                    request.method,
                    url,
                    data=cuerpo,
                    headers=cabeceras,
                    timeout=60,
                )
            else:
                cabeceras = {"Content-Type": "application/json"}
                cuerpo = request.get_json(silent=True)
                respuesta = requests.request(
                    request.method, url, json=cuerpo, headers=cabeceras, timeout=60
                )
        else:
            cabeceras = {"Content-Type": "application/json"}
            respuesta = requests.request(
                request.method, url, headers=cabeceras, timeout=60
            )
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Microservicio de destino no disponible"}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "Tiempo de espera agotado en el microservicio"}), 504

    try:
        return respuesta.json(), respuesta.status_code
    except ValueError:
        return respuesta.text, respuesta.status_code, {"Content-Type": "text/plain; charset=utf-8"}