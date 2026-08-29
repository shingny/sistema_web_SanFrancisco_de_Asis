"""Configuración del microservicio de pedidos (Microservicio 1)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Ruta base del microservicio (carpeta donde vive este archivo)
BASE_DIR = Path(__file__).resolve().parent

# Carpeta donde se aloja la base de datos (se crea si no existe)
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Carga variables del archivo .env ubicado en la raíz del proyecto
load_dotenv(BASE_DIR.parent / ".env")


class Config:
    """Parámetros de configuración del microservicio de pedidos."""

    # En Render la plataforma inyecta la variable PORT automáticamente.
    HOST = os.getenv("PEDIDOS_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT") or os.getenv("PEDIDOS_PORT") or "5001")

    # Base de datos: si existe DATABASE_URL (PostgreSQL en Alwaysdata/Render),
    # se usa esa; en caso contrario se usa SQLite local.
    #   Ej. Alwaysdata: postgresql://usuario:clave@host:puerto/nombre_bd
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        os.getenv("DATABASE_URL_PEDIDOS", "sqlite:///" + str(DATABASE_DIR / "pedidos.db")),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "cambio-en-produccion")

    # Dirección de correo usada por el conector de notificaciones
    NOTIFICACION_EMAIL = os.getenv("NOTIFICACION_EMAIL", "tienda@sanfranciscodeasis.com")

    # ---------- Cloudinary (imágenes de productos) ----------
    # Se configuran en Render / Alwaysdata o en el entorno local (.env).
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_URL = os.getenv(
        "CLOUDINARY_URL", ""
    )  # opcional: cloudinary://key:secret@cloud_name
    # Prefijo público de las imágenes por defecto (placeholder) en Cloudinary
    CLOUDINARY_DEFAULT_FOLDER = os.getenv("CLOUDINARY_DEFAULT_FOLDER", "san-francisco/")
    CLOUDINARY_PUBLIC_ID_PLACEHOLDER = os.getenv(
        "CLOUDINARY_PUBLIC_ID_PLACEHOLDER", "san-francisco/logo"
    )