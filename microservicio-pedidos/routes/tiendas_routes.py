"""Rutas de tiendas (Microservicio 1)."""

from flask import Blueprint, jsonify

from app import db
from models.tienda import Tienda

tiendas_bp = Blueprint("tiendas", __name__)


@tiendas_bp.route("/tiendas", methods=["GET"])
def listar_tiendas():
    """Devuelve las 5 tiendas disponibles para elegir."""
    tiendas = Tienda.query.order_by(Tienda.id).all()
    return jsonify([tienda.to_dict() for tienda in tiendas]), 200


@tiendas_bp.route("/tiendas/<int:tienda_id>", methods=["GET"])
def detalle_tienda(tienda_id):
    """Devuelve los datos de una tienda específica."""
    tienda = db.session.get(Tienda, tienda_id)
    if not tienda:
        return jsonify({"error": "Tienda no encontrada"}), 404
    return jsonify(tienda.to_dict()), 200