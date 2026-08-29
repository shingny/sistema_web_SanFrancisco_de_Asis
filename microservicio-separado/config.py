"""Configuración del microservicio de separado de tortas (Microservicio 2)."""

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
    """Parámetros de configuración del microservicio de separado de tortas."""

    # En Render la plataforma inyecta la variable PORT automáticamente.
    HOST = os.getenv("SEPARADO_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT") or os.getenv("SEPARADO_PORT") or "5002")

    # Base de datos: si existe DATABASE_URL (PostgreSQL en Alwaysdata/Render),
    # se usa esa; en caso contrario se usa SQLite local.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        os.getenv("DATABASE_URL_SEPARADO", "sqlite:///" + str(DATABASE_DIR / "reservas.db")),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "cambio-en-produccion")

    # Dirección de correo usada por el conector de notificaciones
    NOTIFICACION_EMAIL = os.getenv("NOTIFICACION_EMAIL", "tienda@sanfranciscodeasis.com")