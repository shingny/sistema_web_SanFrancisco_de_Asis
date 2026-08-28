"""Rutas de reservas y de inventario (Microservicio 2)."""

from datetime import date

from flask import Blueprint, jsonify, request

from app import db
from models.inventario import Inventario
from models.reserva import ESTADOS_RESERVA, Reserva
from services.notificaciones import notificar_reserva

reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/reservas", methods=["POST"])
def crear_reserva():
    """Registra una torta comprada en tienda y la separa para recojo."""
    data = request.get_json(silent=True) or {}
    errores = []

    tienda_id = data.get("tienda_id")
    if not tienda_id:
        errores.append("El campo 'tienda_id' es obligatorio")

    cliente = data.get("cliente") or {}
    nombre = (cliente.get("nombre") or "").strip()
    celular = (cliente.get("celular") or "").strip()
    if not nombre:
        errores.append("El campo 'cliente.nombre' es obligatorio")
    if not celular:
        errores.append("El campo 'cliente.celular' es obligatorio")

    producto = (data.get("producto") or "").strip()
    if not producto:
        errores.append("El campo 'producto' es obligatorio")

    fecha_compra = (data.get("fecha_compra") or "").strip()
    fecha_recojo = (data.get("fecha_recojo") or "").strip()
    if not fecha_compra:
        data["fecha_compra"] = fecha_compra = date.today().isoformat()
    if not fecha_recojo:
        errores.append("El campo 'fecha_recojo' es obligatorio")

    if errores:
        return jsonify({"error": errores}), 400

    # Descontar del inventario si el producto existe en la tienda
    inventario = Inventario.query.filter_by(
        tienda_id=tienda_id, producto=producto
    ).first()
    if inventario:
        if inventario.cantidad <= 0:
            return jsonify({"error": "No hay stock disponible para separar este producto"}), 409
        inventario.cantidad -= 1

    cantidad = max(1, int(data.get("cantidad", 1) or 1))

    reserva = Reserva(
        tienda_id=tienda_id,
        cliente_nombre=nombre,
        cliente_celular=celular,
        producto=producto,
        cantidad=cantidad,
        fecha_compra=fecha_compra,
        fecha_recojo=fecha_recojo,
        estado="reservado",
    )
    db.session.add(reserva)
    db.session.commit()

    # Notifica al personal de la tienda (simulado vía log)
    notificar_reserva(reserva, tipo="reserva_nueva")

    return jsonify(reserva.to_dict()), 201


@reservas_bp.route("/reservas", methods=["GET"])
def listar_reservas():
    """Lista reservas; filtros opcionales: ?tienda_id= &estado="""
    tienda_id = request.args.get("tienda_id", type=int)
    estado = request.args.get("estado")

    query = Reserva.query.order_by(Reserva.fecha_creacion.desc())
    if tienda_id:
        query = query.filter(Reserva.tienda_id == tienda_id)
    if estado:
        query = query.filter(Reserva.estado == estado)

    return jsonify([reserva.to_dict() for reserva in query.all()]), 200


@reservas_bp.route("/reservas/<int:reserva_id>/estado", methods=["PATCH"])
def actualizar_estado_reserva(reserva_id):
    """Actualiza el estado de una reserva (kanban)."""
    data = request.get_json(silent=True) or {}
    nuevo_estado = (data.get("estado") or "").strip().lower()

    if nuevo_estado not in ESTADOS_RESERVA:
        return (
            jsonify({"error": f"Estado inválido. Válidos: {', '.join(ESTADOS_RESERVA)}"}),
            400,
        )

    reserva = db.session.get(Reserva, reserva_id)
    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    reserva.estado = nuevo_estado
    db.session.commit()

    notificar_reserva(reserva, tipo="estado_actualizado")

    return jsonify(reserva.to_dict()), 200


@reservas_bp.route("/inventario", methods=["GET"])
def listar_inventario():
    """Lista inventario; filtro opcional: ?tienda_id="""
    tienda_id = request.args.get("tienda_id", type=int)

    query = Inventario.query.order_by(Inventario.tienda_id, Inventario.producto)
    if tienda_id:
        query = query.filter(Inventario.tienda_id == tienda_id)

    return jsonify([item.to_dict() for item in query.all()]), 200