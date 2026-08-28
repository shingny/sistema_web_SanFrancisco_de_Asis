"""Modelo de datos: Cliente."""

from app import db


class Cliente(db.Model):
    """Cliente que realiza el pedido web."""

    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    celular = db.Column(db.String(30), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, default="")

    def to_dict(self):
        """Serializa el cliente a diccionario (JSON)."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "celular": self.celular,
            "email": self.email or "",
        }