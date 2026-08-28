"""Rutas de productos / catálogo por tienda (Microservicio 1)."""

from flask import Blueprint, jsonify, request

from app import db
from models.producto import Producto
from models.tienda import Tienda

productos_bp = Blueprint("productos", __name__)


@productos_bp.route("/tiendas/<int:tienda_id>/productos", methods=["GET"])
def listar_productos(tienda_id):
    """Devuelve el catálogo de productos de una tienda.

    Filtro opcional por tipo: ?tipo=torta | ?tipo=bocadito
    """
    tienda = db.session.get(Tienda, tienda_id)
    if not tienda:
        return jsonify({"error": "Tienda no encontrada"}), 404

    tipo = request.args.get("tipo")
    query = Producto.query.filter_by(tienda_id=tienda_id)
    if tipo:
        query = query.filter(Producto.tipo == tipo)
    productos = query.order_by(Producto.tipo, Producto.nombre).all()

    return jsonify([producto.to_dict() for producto in productos]), 200