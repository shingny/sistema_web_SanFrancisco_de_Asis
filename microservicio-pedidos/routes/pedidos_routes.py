"""Rutas de pedidos (Microservicio 1)."""

from flask import Blueprint, jsonify, request

from app import db
from models.cliente import Cliente
from models.pedido import ESTADOS_PEDIDO, Pedido, PedidoItem
from models.producto import Producto
from models.tienda import Tienda
from services.notificaciones import notificar_pedido

pedidos_bp = Blueprint("pedidos", __name__)


def _validar_pedido(data):
    """Valida el payload de creación de un pedido.

    Devuelve (errores, diccionario normalizado).
    """
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

    items = data.get("items") or []
    if not items:
        errores.append("El pedido debe incluir al menos un ítem en 'items'")

    return errores, {
        "tienda_id": tienda_id,
        "cliente": {"nombre": nombre, "celular": celular, "email": cliente.get("email", "")},
        "items": items,
        "mensaje": (data.get("mensaje") or "").strip(),
        "fecha_entrega": (data.get("fecha_entrega") or "").strip(),
        "metodo_pago": (data.get("metodo_pago") or "efectivo").strip(),
    }


@pedidos_bp.route("/pedidos", methods=["POST"])
def crear_pedido():
    """Crea un nuevo pedido y notifica a la tienda seleccionada."""
    data = request.get_json(silent=True) or {}
    errores, normalizado = _validar_pedido(data)

    if normalizado["tienda_id"]:
        tienda = db.session.get(Tienda, normalizado["tienda_id"])
        if not tienda:
            errores.append("La tienda seleccionada no existe")

    if errores:
        return jsonify({"error": errores}), 400

    cliente = Cliente(
        nombre=normalizado["cliente"]["nombre"],
        celular=normalizado["cliente"]["celular"],
        email=normalizado["cliente"]["email"],
    )
    db.session.add(cliente)
    db.session.flush()

    pedido = Pedido(
        tienda_id=normalizado["tienda_id"],
        cliente_id=cliente.id,
        mensaje=normalizado["mensaje"],
        fecha_entrega=normalizado["fecha_entrega"] or None,
        metodo_pago=normalizado["metodo_pago"],
        estado="nuevo",
    )
    db.session.add(pedido)
    db.session.flush()

    total = 0.0
    for item in normalizado["items"]:
        producto = db.session.get(Producto, item.get("producto_id"))
        if not producto:
            continue
        cantidad = max(1, int(item.get("cantidad", 1) or 1))
        precio_unitario = float(producto.precio_base)
        pedido.items.append(
            PedidoItem(
                producto_id=producto.id,
                nombre=producto.nombre,
                cantidad=cantidad,
                tamano=(item.get("tamano") or "").strip(),
                sabor=(item.get("sabor") or "").strip(),
                precio=precio_unitario,
            )
        )
        total += precio_unitario * cantidad

    if not pedido.items:
        return jsonify({"error": "Ninguno de los ítems enviados corresponde a un producto válido"}), 400

    pedido.total = round(total, 2)
    db.session.commit()

    # Notifica en tiempo real al personal de la tienda (simulado vía log)
    notificar_pedido(pedido, tipo="pedido_nuevo")

    return jsonify(pedido.to_dict()), 201


@pedidos_bp.route("/pedidos", methods=["GET"])
def listar_pedidos():
    """Lista pedidos; filtros opcionales: ?tienda_id= &estado="""
    tienda_id = request.args.get("tienda_id", type=int)
    estado = request.args.get("estado")

    query = Pedido.query.order_by(Pedido.fecha_creacion.desc())
    if tienda_id:
        query = query.filter(Pedido.tienda_id == tienda_id)
    if estado:
        query = query.filter(Pedido.estado == estado)

    pedidos = query.all()
    return jsonify([pedido.to_dict() for pedido in pedidos]), 200


@pedidos_bp.route("/pedidos/<int:pedido_id>/estado", methods=["PATCH"])
def actualizar_estado_pedido(pedido_id):
    """Actualiza el estado del pedido (kanban)."""
    data = request.get_json(silent=True) or {}
    nuevo_estado = (data.get("estado") or "").strip().lower()

    if nuevo_estado not in ESTADOS_PEDIDO:
        return (
            jsonify({"error": f"Estado inválido. Válidos: {', '.join(ESTADOS_PEDIDO)}"}),
            400,
        )

    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404

    pedido.estado = nuevo_estado
    db.session.commit()

    notificar_pedido(pedido, tipo="estado_actualizado")

    return jsonify(pedido.to_dict()), 200