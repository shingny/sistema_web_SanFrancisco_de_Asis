"""Servicio de integración con Cloudinary para imágenes de productos.

Encapsula la configuración y las operaciones (subir y eliminar) para que
el resto del sistema no dependa directamente del SDK de Cloudinary.
"""

import io

from cloudinary import config as cloudinary_config, uploader, utils
from cloudinary.exceptions import Error as CloudinaryError

from config import Config


def configurar():
    """Configura el objeto global del SDK a partir de las variables de entorno.

    Si se define `CLOUDINARY_URL`, el SDK la usa directamente (basta con
    configurar a partir de un valor). Si no, se usan los tres campos por
    separado. El SDK de Cloudinary también lee `CLOUDINARY_URL` del entorno
    de forma automática; reconfiguramos para asegurar coherencia.
    """
    cloudinary_config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
        secure=True,
    )


def subir_imagen(datos_bytes, nombre_archivo="producto", carpeta=None) -> dict:
    """Sube una imagen a Cloudinary y devuelve {url, public_id}.

    - datos_bytes: contenido binario de la imagen.
    - nombre_archivo: nombre base para generar un public_id legible.
    - carpeta: carpeta opcional dentro de Cloudinary.
    """
    configurar()

    public_id = f"{carpeta or Config.CLOUDINARY_DEFAULT_FOLDER}{nombre_archivo}"

    try:
        resultado = uploader.upload(
            io.BytesIO(datos_bytes),
            public_id=public_id,
            overwrite=True,
            resource_type="image",
            folder="",
        )
        return {
            "url": resultado.get("secure_url", ""),
            "public_id": resultado.get("public_id", public_id),
        }
    except CloudinaryError as error:
        # Al final de tu proyecto deberías registrar el error de forma real
        print(f"[cloudinary] Error al subir imagen: {error}")
        return {}


def eliminar_imagen(public_id) -> bool:
    """Elimina una imagen de Cloudinary por su public_id (no crítico si falla)."""
    configurar()
    try:
        uploader.destroy(public_id)
        return True
    except CloudinaryError as error:
        print(f"[cloudinary] Error al eliminar imagen {public_id}: {error}")
        return False


def url_placeholder(clave="producto") -> str:
    """Devuelve una URL por defecto (placeholder) de Cloudinary.

    Se usa cuando un producto aún no tiene imagen propia. Si no se ha
    configurado Cloudinary, devuelve una cadena vacía (el frontend mostrará
    el fondo de color de la tarjeta).
    """
    if not Config.CLOUDINARY_CLOUD_NAME:
        return ""
    try:
        configurar()
        return utils.cloudinary_url(
            Config.CLOUDINARY_PUBLIC_ID_PLACEHOLDER,
            width=400,
            height=300,
            crop="fill",
        )[0]
    except Exception as error:  # noqa: BLE001
        print(f"[cloudinary] Error al generar placeholder: {error}")
        return ""


def url_placeholder_por_nombre(nombre: str) -> str:
    """Genera una URL placeholder determinista de Cloudinary para un producto.

    Sin configurar Cloudinary devuelve cadena vacía (el frontend usa el color
    de fondo de la tarjeta como respaldo).
    """
    if not Config.CLOUDINARY_CLOUD_NAME:
        return ""
    try:
        configurar()
        clave = (nombre or "producto").strip().lower()
        # public_id válido en Cloudinary: minúsculas, sin espacios/raro
        public_id = "".join(c if c.isalnum() or c in "-_" else "-" for c in clave)
        public_id = f"{Config.CLOUDINARY_DEFAULT_FOLDER}placeholder-{public_id}"
        return utils.cloudinary_url(public_id, width=400, height=300, crop="fill")[0]
    except Exception as error:  # noqa: BLE001
        print(f"[cloudinary] Error al generar placeholder: {error}")
        return ""
