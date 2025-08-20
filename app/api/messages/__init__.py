"""
Módulo de API para mensajes de WhatsApp
Exporta el namespace de mensajes para registro en la aplicación principal
"""
from app.api.messages.routes import api

# Exportar el namespace para uso en entrypoint.py
messages_ns = api