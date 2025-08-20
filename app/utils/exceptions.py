"""
Excepciones personalizadas para el microservicio WhatsApp API
Define excepciones específicas del dominio para mejor manejo de errores
"""

class WhatsAppAPIError(Exception):
    """
    Excepción base para errores de la API de WhatsApp
    """
    def __init__(self, message: str, error_code: str = None, status_code: int = 500):
        self.message = message
        self.error_code = error_code or 'WHATSAPP_API_ERROR'
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(Exception):
    """
    Excepción para errores de validación de datos
    """
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        self.error_code = 'VALIDATION_ERROR'
        super().__init__(self.message)

class AuthenticationError(Exception):
    """
    Excepción para errores de autenticación
    """
    def __init__(self, message: str = "Autenticación requerida"):
        self.message = message
        self.error_code = 'AUTHENTICATION_ERROR'
        super().__init__(self.message)

class AuthorizationError(Exception):
    """
    Excepción para errores de autorización
    """
    def __init__(self, message: str = "No autorizado"):
        self.message = message
        self.error_code = 'AUTHORIZATION_ERROR'
        super().__init__(self.message)

class RateLimitError(Exception):
    """
    Excepción para cuando se exceden los límites de velocidad
    """
    def __init__(self, message: str = "Límite de velocidad excedido", retry_after: int = None):
        self.message = message
        self.retry_after = retry_after
        self.error_code = 'RATE_LIMIT_EXCEEDED'
        super().__init__(self.message)

class WebhookValidationError(Exception):
    """
    Excepción para errores de validación de webhooks
    """
    def __init__(self, message: str, webhook_data: dict = None):
        self.message = message
        self.webhook_data = webhook_data
        self.error_code = 'WEBHOOK_VALIDATION_ERROR'
        super().__init__(self.message)

class MessageSendError(Exception):
    """
    Excepción para errores al enviar mensajes
    """
    def __init__(self, message: str, line_id: str = None, phone_number: str = None):
        self.message = message
        self.line_id = line_id
        self.phone_number = phone_number
        self.error_code = 'MESSAGE_SEND_ERROR'
        super().__init__(self.message)

class MediaDownloadError(Exception):
    """
    Excepción para errores al descargar archivos multimedia
    """
    def __init__(self, message: str, media_id: str = None, url: str = None):
        self.message = message
        self.media_id = media_id
        self.url = url
        self.error_code = 'MEDIA_DOWNLOAD_ERROR'
        super().__init__(self.message)

class DatabaseError(Exception):
    """
    Excepción para errores de base de datos
    """
    def __init__(self, message: str, operation: str = None):
        self.message = message
        self.operation = operation
        self.error_code = 'DATABASE_ERROR'
        super().__init__(self.message)

class ConfigurationError(Exception):
    """
    Excepción para errores de configuración
    """
    def __init__(self, message: str, config_key: str = None):
        self.message = message
        self.config_key = config_key
        self.error_code = 'CONFIGURATION_ERROR'
        super().__init__(self.message)

class LineNotFoundError(Exception):
    """
    Excepción cuando no se encuentra una línea de mensajería
    """
    def __init__(self, line_id: str):
        self.line_id = line_id
        self.message = f"Línea de mensajería no encontrada: {line_id}"
        self.error_code = 'LINE_NOT_FOUND'
        super().__init__(self.message)

class MessageNotFoundError(Exception):
    """
    Excepción cuando no se encuentra un mensaje
    """
    def __init__(self, message_id: str):
        self.message_id = message_id
        self.message = f"Mensaje no encontrado: {message_id}"
        self.error_code = 'MESSAGE_NOT_FOUND'
        super().__init__(self.message)

class ContactNotFoundError(Exception):
    """
    Excepción cuando no se encuentra un contacto
    """
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.message = f"Contacto no encontrado: {phone_number}"
        self.error_code = 'CONTACT_NOT_FOUND'
        super().__init__(self.message)

# Funciones auxiliares para manejo de excepciones

def format_error_response(exception: Exception) -> dict:
    """
    Formatea una excepción en respuesta de error estándar
    Args:
        exception: Excepción a formatear
    Returns:
        dict: Respuesta de error estructurada
    """
    if hasattr(exception, 'error_code'):
        return {
            'error': exception.error_code,
            'message': str(exception),
            'details': getattr(exception, '__dict__', {})
        }
    
    return {
        'error': 'INTERNAL_ERROR',
        'message': 'Error interno del servidor',
        'details': {'original_error': str(exception)}
    }

def get_http_status_for_exception(exception: Exception) -> int:
    """
    Obtiene código de estado HTTP apropiado para una excepción
    Args:
        exception: Excepción a evaluar
    Returns:
        int: Código de estado HTTP
    """
    if hasattr(exception, 'status_code'):
        return exception.status_code
    
    exception_status_map = {
        ValidationError: 400,
        AuthenticationError: 401,
        AuthorizationError: 403,
        LineNotFoundError: 404,
        MessageNotFoundError: 404,
        ContactNotFoundError: 404,
        RateLimitError: 429,
        WhatsAppAPIError: 502,
        MediaDownloadError: 502,
        DatabaseError: 500,
        ConfigurationError: 500,
        WebhookValidationError: 400
    }
    
    return exception_status_map.get(type(exception), 500)
