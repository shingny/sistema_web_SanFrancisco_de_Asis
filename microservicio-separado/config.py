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


def _sqlalchemy_uri():
    """Devuelve la URI de SQLAlchemy para PostgreSQL (psycopg v3) o SQLite local."""
    url = os.getenv(
        "DATABASE_URL",
        os.getenv("DATABASE_URL_SEPARADO", "sqlite:///" + str(DATABASE_DIR / "reservas.db")),
    )
    # Si es una URL de PostgreSQL tipo postgresql://..., forzamos el dialecto
    # psycopg (v3) que tiene wheels nativos para Python 3.14 en Render.
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    return url


class Config:
    """Parámetros de configuración del microservicio de separado de tortas."""

    # En Render la plataforma inyecta la variable PORT automáticamente.
    HOST = os.getenv("SEPARADO_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT") or os.getenv("SEPARADO_PORT") or "5002")

    # Base de datos: si existe DATABASE_URL (PostgreSQL en Alwaysdata/Render),
    # se usa esa; en caso contrario se usa SQLite local.
    SQLALCHEMY_DATABASE_URI = _sqlalchemy_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "cambio-en-produccion")

    # Dirección de correo usada por el conector de notificaciones
    NOTIFICACION_EMAIL = os.getenv("NOTIFICACION_EMAIL", "tienda@sanfranciscodeasis.com")