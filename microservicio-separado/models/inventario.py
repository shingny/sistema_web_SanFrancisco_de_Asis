"""Modelo de datos: Inventario de tortas disponibles por tienda."""

from app import db


class Inventario(db.Model):
    """Existencia disponible de cada producto para separar en una tienda."""

    __tablename__ = "inventario"

    id = db.Column(db.Integer, primary_key=True)
    tienda_id = db.Column(db.Integer, nullable=False, index=True)
    producto = db.Column(db.String(120), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        """Serializa el inventario a diccionario (JSON)."""
        return {
            "id": self.id,
            "tienda_id": self.tienda_id,
            "producto": self.producto,
            "cantidad": self.cantidad,
        }