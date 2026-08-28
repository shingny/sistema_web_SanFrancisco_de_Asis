"""Modelo de datos: Producto (tortas y bocaditos por tienda)."""

import json

from app import db


class Producto(db.Model):
    """Producto de la panadería/pastelería.

    - tipo: 'torta' o 'bocadito'
    - tamanos y sabores: listas serializadas como JSON en la base de datos.
    """

    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    tienda_id = db.Column(db.Integer, db.ForeignKey("tiendas.id"), nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False, default="torta")
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(300), default="")
    precio_base = db.Column(db.Float, nullable=False, default=0.0)
    tamanos = db.Column(db.Text, default="[]")
    sabores = db.Column(db.Text, default="[]")

    def _parsear_lista(self, valor):
        """Convierte el texto JSON de la base de datos en una lista Python."""
        try:
            return json.loads(valor or "[]")
        except (TypeError, ValueError):
            return []

    def to_dict(self):
        """Serializa el producto a diccionario (JSON)."""
        return {
            "id": self.id,
            "tienda_id": self.tienda_id,
            "tipo": self.tipo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio_base": self.precio_base,
            "tamanos": self._parsear_lista(self.tamanos),
            "sabores": self._parsear_lista(self.sabores),
        }