"""Modelo de datos: Tienda."""

from app import db


class Tienda(db.Model):
    """Tienda física de San Francisco de Asís.

    Existen 5 tiendas: 4 en Huancayo Centro y 1 en El Tambo.
    """

    __tablename__ = "tiendas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    zona = db.Column(db.String(50), nullable=False)  # Huancayo Centro / El Tambo
    direccion = db.Column(db.String(200), nullable=False)
    horario = db.Column(db.String(100), nullable=False, default="Lun-Dom 8:00 - 21:00")
    estado = db.Column(db.String(20), nullable=False, default="abierto")  # abierto / cerrado

    productos = db.relationship("Producto", backref="tienda", lazy=True)

    def to_dict(self):
        """Serializa la tienda a diccionario (JSON)."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "zona": self.zona,
            "direccion": self.direccion,
            "horario": self.horario,
            "estado": self.estado,
        }