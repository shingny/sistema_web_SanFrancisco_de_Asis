"""Modelo de datos: Reserva (torta separada para recojo)."""

from datetime import datetime

from app import db

# Estados permitidos del ciclo de vida de una reserva
ESTADOS_RESERVA = [
    "reservado",
    "en_preparacion",
    "listo_para_recojo",
    "entregado",
    "cancelado",
]


class Reserva(db.Model):
    """Torta ya comprada en tienda física y separada/reservada para recojo."""

    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    tienda_id = db.Column(db.Integer, nullable=False, index=True)
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_celular = db.Column(db.String(30), nullable=False, index=True)
    producto = db.Column(db.String(120), nullable=False)  # nombre del producto separado
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    fecha_compra = db.Column(db.String(20), nullable=False)  # fecha de compra en tienda
    fecha_recojo = db.Column(db.String(20), nullable=False)  # fecha pactada de recojo
    estado = db.Column(db.String(30), nullable=False, default="reservado")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Serializa la reserva a diccionario (JSON)."""
        return {
            "id": self.id,
            "tienda_id": self.tienda_id,
            "cliente": {
                "nombre": self.cliente_nombre,
                "celular": self.cliente_celular,
            },
            "producto": self.producto,
            "cantidad": self.cantidad,
            "fecha_compra": self.fecha_compra,
            "fecha_recojo": self.fecha_recojo,
            "estado": self.estado,
            "fecha_creacion": (
                self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")
                if self.fecha_creacion
                else None
            ),
        }