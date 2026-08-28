"""Configuración del microservicio de pedidos (Microservicio 1)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Ruta base del microservicio (carpeta donde vive este archivo)
BASE_DIR = Path(__file__).resolve().parent

# Carga variables del archivo .env ubicado en la raíz del proyecto
load_dotenv(BASE_DIR.parent / ".env")


class Config:
    """Parámetros de configuración del microservicio de pedidos."""

    HOST = os.getenv("PEDIDOS_HOST", "0.0.0.0")
    PORT = int(os.getenv("PEDIDOS_PORT", "5001"))

    # SQLite en desarrollo; migrable a PostgreSQL en producción.
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(BASE_DIR / "database" / "pedidos.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "cambio-en-produccion")

    # Dirección de correo usada por el conector de notificaciones
    NOTIFICACION_EMAIL = os.getenv("NOTIFICACION_EMAIL", "tienda@sanfranciscodeasis.com")