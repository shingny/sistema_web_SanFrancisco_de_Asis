"""Datos iniciales (seed) del microservicio de separado.

Siembra el inventario de tortas de cada una de las 5 tiendas
si la base de datos está vacía.
"""

from app import db
from models.inventario import Inventario

# Tiendas existentes en el sistema (ids esperados: 1 a 5)
TIENDAS = [1, 2, 3, 4, 5]

PRODUCTOS_INVENTARIO = [
    "Torta Tres Leches",
    "Torta de Chocolate",
    "Torta de Fresa",
    "Selva Negra",
    "Cheesecake",
]


def seed_database():
    """Inserta los productos del inventario únicamente si la BD está vacía."""
    if Inventario.query.count() > 0:
        return

    for tienda_id in TIENDAS:
        for producto in PRODUCTOS_INVENTARIO:
            db.session.add(
                Inventario(tienda_id=tienda_id, producto=producto, cantidad=6)
            )
    db.session.commit()