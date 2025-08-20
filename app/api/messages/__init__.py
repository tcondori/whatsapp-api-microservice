"""
Módulo de API para mensajes de WhatsApp
Exporta el namespace de mensajes para registro en la aplicación principal
"""
from app.api.messages.routes import messages_ns

# Exportar el namespace para uso en entrypoint.py
__all__ = ['messages_ns']