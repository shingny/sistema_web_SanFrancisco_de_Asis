"""Rutas de productos / catálogo por tienda (Microservicio 1).

Incluye operaciones para gestionar las imágenes de los productos,
que se almacenan en Cloudinary.
"""

from flask import Blueprint, jsonify, request

from app import db
from models.producto import Producto
from models.tienda import Tienda
from services.cloudinary_service import eliminar_imagen, subir_imagen

productos_bp = Blueprint("productos", __name__)


def _slug_archivo(nombre):
    """Convierte un nombre de producto en un slug seguro para archivo."""
    seguro = "".join(c if c.isalnum() or c in "-_" else "-" for c in nombre.lower())
    return seguro or "producto"


@productos_bp.route("/tiendas/<int:tienda_id>/productos", methods=["GET"])
def listar_productos(tienda_id):
    """Devuelve el catálogo de productos de una tienda.

    Filtro opcional por tipo: ?tipo=torta | ?tipo=bocadito
    """
    tienda = db.session.get(Tienda, tienda_id)
    if not tienda:
        return jsonify({"error": "Tienda no encontrada"}), 404

    tipo = request.args.get("tipo")
    query = Producto.query.filter_by(tienda_id=tienda_id)
    if tipo:
        query = query.filter(Producto.tipo == tipo)
    productos = query.order_by(Producto.tipo, Producto.nombre).all()

    return jsonify([producto.to_dict() for producto in productos]), 200


@productos_bp.route("/productos", methods=["GET"])
def listar_todos_los_productos():
    """Lista productos para el panel. Filtros: ?tienda_id= &tipo="""
    tienda_id = request.args.get("tienda_id", type=int)
    tipo = request.args.get("tipo")

    query = Producto.query.order_by(Producto.tienda_id, Producto.tipo, Producto.nombre)
    if tienda_id:
        query = query.filter(Producto.tienda_id == tienda_id)
    if tipo:
        query = query.filter(Producto.tipo == tipo)

    return jsonify([producto.to_dict() for producto in query.all()]), 200


@productos_bp.route("/imagenes", methods=["POST"])
def subir_imagen_producto():
    """Sube una imagen a Cloudinary y (opcional) la asocia a un producto.

    Envía un multipart/form-data:
      - imagen: archivo de imagen obligatorio
      - producto_id: id del producto al que asociar (opcional)
      - nombre: nombre base del archivo (opcional)
    """
    archivo = request.files.get("imagen")
    if not archivo:
        return jsonify({"error": "El campo 'imagen' (archivo) es obligatorio"}), 400

    producto = None
    producto_id = request.form.get("producto_id", type=int)
    if producto_id:
        producto = db.session.get(Producto, producto_id)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

    nombre = (request.form.get("nombre") or "").strip()
    if not nombre and producto:
        nombre = _slug_archivo(producto.nombre)

    datos_bytes = archivo.read()
    # Usamos un public_id único por producto para evitar que dos productos
    # (p. ej. el mismo nombre en distintas tiendas) compartan imagen.
    nombre_archivo = f"{producto.id}-{nombre}" if producto else (nombre or "producto")
    resultado = subir_imagen(datos_bytes, nombre_archivo=nombre_archivo)

    if not resultado.get("url"):
        return jsonify({"error": "No se pudo subir la imagen a Cloudinary"}), 502

    if producto:
        producto.imagen_url = resultado["url"]
        producto.public_id = resultado.get("public_id", "")
        db.session.commit()
        return jsonify({"mensaje": "Imagen actualizada", "producto": producto.to_dict()}), 200

    return jsonify({"mensaje": "Imagen subida", "imagen": resultado}), 201


@productos_bp.route("/productos/<int:producto_id>/imagen", methods=["PATCH", "DELETE"])
def gestionar_imagen_producto(producto_id):
    """Actualiza (PATCH) o elimina (DELETE) la imagen de un producto."""
    producto = db.session.get(Producto, producto_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    if request.method == "DELETE":
        if producto.public_id:
            eliminar_imagen(producto.public_id)
        producto.imagen_url = ""
        producto.public_id = ""
        db.session.commit()
        return jsonify({"mensaje": "Imagen eliminada", "producto": producto.to_dict()}), 200

    data = request.get_json(silent=True) or {}
    url = (data.get("imagen_url") or "").strip()
    public_id = (data.get("public_id") or "").strip()
    if not url:
        return jsonify({"error": "El campo 'imagen_url' es obligatorio"}), 400

    # Si ya había una imagen en Cloudinary, liberamos el recurso anterior.
    if producto.public_id and public_id != producto.public_id:
        eliminar_imagen(producto.public_id)

    producto.imagen_url = url
    producto.public_id = public_id
    db.session.commit()
    return jsonify(producto.to_dict()), 200