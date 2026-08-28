"""Modelo de datos: Pedido y detalle de ítems del pedido."""

from datetime import datetime

from app import db

# Estados permitidos del ciclo de vida de un pedido
ESTADOS_PEDIDO = ["nuevo", "en_preparacion", "listo", "entregado", "cancelado"]


class Pedido(db.Model):
    """Pedido realizado por un cliente para recojo en tienda."""

    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    tienda_id = db.Column(db.Integer, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    mensaje = db.Column(db.String(200), default="")  # texto para la torta
    fecha_entrega = db.Column(db.String(20), nullable=True)
    metodo_pago = db.Column(db.String(30), nullable=False, default="efectivo")
    estado = db.Column(db.String(20), nullable=False, default="nuevo")
    total = db.Column(db.Float, nullable=False, default=0.0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship("Cliente", backref="pedidos")
    items = db.relationship(
        "PedidoItem", backref="pedido", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Serializa el pedido a diccionario (JSON)."""
        return {
            "id": self.id,
            "tienda_id": self.tienda_id,
            "cliente": self.cliente.to_dict() if self.cliente else None,
            "items": [item.to_dict() for item in self.items],
            "mensaje": self.mensaje,
            "fecha_entrega": self.fecha_entrega,
            "metodo_pago": self.metodo_pago,
            "estado": self.estado,
            "total": self.total,
            "fecha_creacion": (
                self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")
                if self.fecha_creacion
                else None
            ),
        }


class PedidoItem(db.Model):
    """Ítem (producto personalizado) asociado a un pedido."""

    __tablename__ = "pedidos_items"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, nullable=True)
    nombre = db.Column(db.String(120), nullable=False)  # copia del nombre del producto
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    tamano = db.Column(db.String(40), default="")
    sabor = db.Column(db.String(60), default="")
    precio = db.Column(db.Float, nullable=False, default=0.0)  # precio unitario

    def to_dict(self):
        """Serializa el ítem a diccionario (JSON)."""
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "tamano": self.tamano,
            "sabor": self.sabor,
            "precio": self.precio,
            "subtotal": round(self.precio * self.cantidad, 2),
        }