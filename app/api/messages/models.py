"""
Modelos para la API de Mensajes usando Flask-RESTX
Definiciones de campos para la documentación Swagger
"""
from flask_restx import fields


# Definición de campos para mensaje de texto
TEXT_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'text': fields.String(
        required=True,
        description='Contenido del mensaje de texto',
        example='Hola, este es un mensaje de prueba'
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para mensaje de imagen (formato oficial Meta/WhatsApp)
IMAGE_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje multimedia',
        enum=['image'],
        default='image',
        example='image'
    ),
    'image': fields.Raw(
        required=True,
        description='Datos de la imagen según formato oficial WhatsApp Business API',
        example={
            'link': 'https://example.com/image.jpg',
            'caption': 'Descripción opcional de la imagen'
        }
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para mensaje de imagen con upload por archivo
MEDIA_UPLOAD_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje multimedia',
        enum=['image'],
        default='image',
        example='image'
    ),
    'caption': fields.String(
        required=False,
        description='Texto descriptivo de la imagen',
        example='Esta es una imagen subida'
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición alternativa para imagen con upload directo
IMAGE_UPLOAD_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'image_url': fields.String(
        required=False,
        description='URL de la imagen (alternativa a upload)',
        example='https://example.com/image.jpg'
    ),
    'caption': fields.String(
        required=False,
        description='Texto descriptivo de la imagen',
        example='Esta es una imagen de ejemplo'
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para respuesta de mensaje
MESSAGE_RESPONSE_FIELDS = {
    'success': fields.Boolean(
        required=True,
        description='Indica si la operación fue exitosa',
        example=True
    ),
    'message': fields.String(
        required=True,
        description='Mensaje descriptivo de la operación',
        example='Mensaje enviado exitosamente'
    ),
    'data': fields.Raw(
        required=False,
        description='Datos adicionales de respuesta'
    )
}

# Definición de campos para actualizar estado de mensaje
UPDATE_STATUS_FIELDS = {
    'status': fields.String(
        required=True,
        description='Nuevo estado del mensaje',
        enum=['sent', 'delivered', 'read', 'failed'],
        example='delivered'
    )
}

# Definición de campos para respuesta de error
ERROR_RESPONSE_FIELDS = {
    'success': fields.Boolean(
        required=True,
        description='Indica si la operación fue exitosa',
        example=False,
        default=False
    ),
    'message': fields.String(
        required=True,
        description='Mensaje de error',
        example='Error al procesar la solicitud'
    ),
    'error_code': fields.String(
        required=False,
        description='Código de error específico',
        example='INVALID_PHONE_NUMBER'
    )
}

# Definición de campos para respuesta de salud
HEALTH_RESPONSE_FIELDS = {
    'status': fields.String(
        required=True,
        description='Estado de la aplicación',
        example='healthy'
    ),
    'timestamp': fields.String(
        required=True,
        description='Timestamp de la verificación',
        example='2024-01-15T10:30:00Z'
    ),
    'version': fields.String(
        required=True,
        description='Versión de la aplicación',
        example='1.0.0'
    )
}