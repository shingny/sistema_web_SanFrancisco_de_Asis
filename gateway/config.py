"""Configuración del API Gateway."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Ruta base del gateway (carpeta donde vive este archivo)
BASE_DIR = Path(__file__).resolve().parent

# Carga variables del archivo .env ubicado en la raíz del proyecto
load_dotenv(BASE_DIR.parent / ".env")


class Config:
    """Parámetros de configuración del API Gateway."""

    HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
    PORT = int(os.getenv("GATEWAY_PORT", "5000"))

    # URL internas de los microservicios
    PEDIDOS_URL = os.getenv("PEDIDOS_URL", "http://127.0.0.1:5001")
    SEPARADO_URL = os.getenv("SEPARADO_URL", "http://127.0.0.1:5002")

    # Credenciales del panel administrativo de tienda (autenticación básica)
    PANEL_USER = os.getenv("PANEL_USER", "admin")
    PANEL_PASSWORD = os.getenv("PANEL_PASSWORD", "san-francisco-2024")
    PANEL_TOKEN = os.getenv("PANEL_TOKEN", "sfa-token-demo-2024")

    SECRET_KEY = os.getenv("SECRET_KEY", "cambio-en-produccion")