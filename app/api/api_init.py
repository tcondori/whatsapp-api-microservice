"""
Inicialización del módulo API y registro de namespaces
"""
from flask_restx import Api

from .messages.routes import messages_ns
from .contacts.routes import contacts_ns
from .media.routes import media_ns
from .webhooks.routes import webhook_ns


def create_api(app):
    """
    Crea y configura la API con todos los namespaces
    Args:
        app: Instancia de Flask
    Returns:
        Api configurada
    """
    api = Api(
        app,
        version='1.0',
        title='WhatsApp Business API',
        description='Microservicio para integración con WhatsApp Business API',
        doc='/docs/',
        prefix='/api/v1'
    )
    
    # Registrar namespaces
    api.add_namespace(messages_ns, path='/messages')
    api.add_namespace(contacts_ns, path='/contacts') 
    api.add_namespace(media_ns, path='/media')
    api.add_namespace(webhook_ns, path='/webhooks')
    
    return api
