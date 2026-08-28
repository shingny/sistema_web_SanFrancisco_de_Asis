"""Servicio transversal de notificaciones (Microservicio 1).

En desarrollo registra las notificaciones por consola y en un archivo de log.
Para producción basta con sustituir el cuerpo de `enviar_notificacion()`
por la integración real con WhatsApp Business API, Twilio o Flask-Mail (SMTP),
sin necesidad de tocar el resto del sistema.
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
        tipo (str): tipo de notificación (pedido_nuevo, estado_actualizado, ...).
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
    #   whatsapp_api.enviar_plantilla(destino, "pedido_nuevo", parametros)
    #   o con Flask-Mail:
    #   mail.send(Message(mensaje, recipients=[destino]))


def notificar_pedido(pedido, tipo="pedido_nuevo"):
    """Genera el mensaje de notificación a partir de un pedido y lo envía."""
    productos = ", ".join(
        f"{item.cantidad} x {item.nombre}" for item in pedido.items
    )
    mensaje = (
        f"Tienda #{pedido.tienda_id} | Pedido #{pedido.id} | "
        f"Cliente: {pedido.cliente.nombre} ({pedido.cliente.celular}) | "
        f"Productos: {productos} | Total: S/ {pedido.total}"
    )
    enviar_notificacion(mensaje, tipo=tipo)