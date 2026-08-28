"""Datos iniciales (seed) del microservicio de pedidos.

Crea las 5 tiendas y el catálogo de tortas y bocaditos de cada tienda
si la base de datos está vacía.
"""

from app import db
from models.producto import Producto
from models.tienda import Tienda

TIENDAS = [
    {
        "nombre": "San Francisco de Asís · Centro",
        "zona": "Huancayo Centro",
        "direccion": "Jr. Real Nº 110",
        "horario": "Lun-Dom 8:00 - 21:00",
    },
    {
        "nombre": "San Francisco de Asís · Giraldez",
        "zona": "Huancayo Centro",
        "direccion": "Calle Real Nº 430",
        "horario": "Lun-Dom 9:00 - 21:00",
    },
    {
        "nombre": "San Francisco de Asís · Lima",
        "zona": "Huancayo Centro",
        "direccion": "Jr. Lima Nº 562",
        "horario": "Lun-Dom 9:00 - 20:30",
    },
    {
        "nombre": "San Francisco de Asís · Amazonas",
        "zona": "Huancayo Centro",
        "direccion": "Jr. Amazonas Nº 320",
        "horario": "Lun-Dom 8:30 - 20:00",
    },
    {
        "nombre": "San Francisco de Asís · El Tambo",
        "zona": "El Tambo",
        "direccion": "Av. Mariscal Castilla Nº 2110",
        "horario": "Lun-Dom 8:00 - 21:30",
    },
]

TORTAS = [
    {
        "nombre": "Torta Tres Leches",
        "descripcion": "Bizcocho esponjoso bañado en tres leches",
        "precio_base": 85.0,
        "tamanos": ["mediana", "grande", "familiar"],
        "sabores": ["clásica", "fresa", "vainilla"],
    },
    {
        "nombre": "Torta de Chocolate",
        "descripcion": "Suave bizcocho de chocolate con relleno cremoso",
        "precio_base": 80.0,
        "tamanos": ["mediana", "grande", "familiar"],
        "sabores": ["clásica", "durazno", "menta"],
    },
    {
        "nombre": "Torta de Fresa",
        "descripcion": "Bizcocho de vainilla con fresas frescas",
        "precio_base": 90.0,
        "tamanos": ["mediana", "grande", "familiar"],
        "sabores": ["fresa", "chocolate"],
    },
    {
        "nombre": "Selva Negra",
        "descripcion": "Bizcocho de chocolate, crema batida y cerezas",
        "precio_base": 95.0,
        "tamanos": ["mediana", "grande", "familiar"],
        "sabores": ["clásica"],
    },
    {
        "nombre": "Cheesecake",
        "descripcion": "Tarta de queso horneada con coulis de frutos rojos",
        "precio_base": 75.0,
        "tamanos": ["mediana", "grande"],
        "sabores": ["fresa", "arándano", "lúcuma"],
    },
]

BOCADITOS = [
    {
        "nombre": "Mini Pasta Dulce",
        "descripcion": "Porción ideal para eventos",
        "precio_base": 15.0,
        "tamanos": ["25 unid", "50 unid"],
        "sabores": ["canela", "vainilla"],
    },
    {
        "nombre": "Hojitas de Naranja",
        "descripcion": "Hojaldradas y aromáticas",
        "precio_base": 18.0,
        "tamanos": ["30 unid", "60 unid"],
        "sabores": ["naranja"],
    },
    {
        "nombre": "Empanaditas Dulces",
        "descripcion": "Rellenas de manjar o fresa",
        "precio_base": 25.0,
        "tamanos": ["20 unid", "40 unid"],
        "sabores": ["manjar", "fresa"],
    },
    {
        "nombre": "Galletas de Mantequilla",
        "descripcion": "Crujientes y caseras",
        "precio_base": 20.0,
        "tamanos": ["30 unid", "60 unid"],
        "sabores": ["mantequilla", "chispas"],
    },
    {
        "nombre": "Brownies",
        "descripcion": "Densos y chocolatosos",
        "precio_base": 30.0,
        "tamanos": ["20 unid", "40 unid"],
        "sabores": ["chocolate", "nuez"],
    },
]


def seed_database():
    """Inserta las tiendas y el catálogo únicamente si la BD está vacía."""
    if Tienda.query.count() > 0:
        return

    for datos in TIENDAS:
        db.session.add(Tienda(**datos))
    db.session.commit()

    tiendas = Tienda.query.all()
    for tienda in tiendas:
        for torta in TORTAS:
            db.session.add(Producto(tienda_id=tienda.id, tipo="torta", **torta))
        for bocadito in BOCADITOS:
            db.session.add(Producto(tienda_id=tienda.id, tipo="bocadito", **bocadito))
    db.session.commit()