"""Servicio transversal de notificaciones (Microservicio 2).

Misma estrategia que el microservicio de pedidos: registro en consola/log
en desarrollo, listo para sustituir por WhatsApp Business API / Twilio / SMTP.
"""

import os
from datetime import datetime

from config import BASE_DIR

LOG_DIR = BASE_DIR / "database" / "logs"
LOG_FILE = LOG_DIR / "notificaciones.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def enviar_notificacion(mensaje, destino=None, tipo="info"):
    """Punto único de envío de notificaciones.

    Parámetros:
        mensaje (str): contenido del mensaje.
        destino (str): teléfono/correo del destinatario (el personal de tienda).
        tipo (str): tipo de notificación (reserva_nueva, estado_actualizado, ...).
    """
    destino = destino or os.getenv("NOTIFICACION_EMAIL", "tienda@sanfranciscodeasis.com")
    linea = (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"[{tipo}] Para: {destino} -> {mensaje}"
    )

    # Salida por consola del servicio
    print(linea)

    # Registro persistente en archivo de log
    with open(LOG_FILE, "a", encoding="utf-8") as archivo:
        archivo.write(linea + "\n")

    # ── Integración pendiente con WhatsApp Business API / Twilio / SMTP ──
    # Ejemplo:
    #   whatsapp_api.enviar_plantilla(destino, "reserva_nueva", parametros)


def notificar_reserva(reserva, tipo="reserva_nueva"):
    """Genera el mensaje de notificación a partir de una reserva y lo envía."""
    mensaje = (
        f"Tienda #{reserva.tienda_id} | Reserva #{reserva.id} | "
        f"Cliente: {reserva.cliente_nombre} ({reserva.cliente_celular}) | "
        f"Producto: {reserva.cantidad} x {reserva.producto} | "
        f"Recojo: {reserva.fecha_recojo}"
    )
    enviar_notificacion(mensaje, tipo=tipo)