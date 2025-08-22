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

# Definición de campos para mensaje de contactos (formato oficial Meta)
CONTACTS_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje',
        enum=['contacts'],
        default='contacts',
        example='contacts'
    ),
    'contacts': fields.List(
        fields.Raw(),
        required=True,
        description='Array de contactos según formato oficial WhatsApp Business API',
        example=[
            {
                "name": {
                    "formatted_name": "Juan Pérez",
                    "first_name": "Juan",
                    "last_name": "Pérez"
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "CELL",
                        "wa_id": "5491123456789"
                    }
                ],
                "emails": [
                    {
                        "email": "juan.perez@email.com",
                        "type": "WORK"
                    }
                ]
            }
        ]
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para mensaje de ubicación (formato oficial Meta)
LOCATION_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='59167028778'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje',
        enum=['location'],
        default='location',
        example='location'
    ),
    'location': fields.Raw(
        required=True,
        description='Datos de la ubicación según formato oficial WhatsApp Business API',
        example={
            'latitude': -34.6037,
            'longitude': -58.3816,
            'name': 'Obelisco de Buenos Aires',
            'address': 'Av. 9 de Julio s/n, C1043 CABA, Argentina'
        }
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para mensaje interactivo con botones (formato oficial Meta)
INTERACTIVE_BUTTONS_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje',
        enum=['interactive'],
        default='interactive',
        example='interactive'
    ),
    'interactive': fields.Raw(
        required=True,
        description='Contenido del mensaje interactivo con botones según formato oficial WhatsApp Business API',
        example={
            'type': 'button',
            'header': {
                'type': 'text',
                'text': '¿Cómo podemos ayudarte?'
            },
            'body': {
                'text': 'Selecciona una de las siguientes opciones:'
            },
            'footer': {
                'text': 'Responde tocando un botón'
            },
            'action': {
                'buttons': [
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'btn_info',
                            'title': 'Información'
                        }
                    },
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'btn_soporte',
                            'title': 'Soporte'
                        }
                    },
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'btn_ventas',
                            'title': 'Ventas'
                        }
                    }
                ]
            }
        }
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para mensaje interactivo con lista (formato oficial Meta)
INTERACTIVE_LIST_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje',
        enum=['interactive'],
        default='interactive',
        example='interactive'
    ),
    'interactive': fields.Raw(
        required=True,
        description='Contenido del mensaje interactivo con lista según formato oficial WhatsApp Business API',
        example={
            'type': 'list',
            'header': {
                'type': 'text',
                'text': 'Nuestros Servicios'
            },
            'body': {
                'text': 'Elige el servicio que te interesa:'
            },
            'footer': {
                'text': 'Toca para ver las opciones'
            },
            'action': {
                'button': 'Ver Opciones',
                'sections': [
                    {
                        'title': 'Servicios Principales',
                        'rows': [
                            {
                                'id': 'srv_consulta',
                                'title': 'Consulta Gratuita',
                                'description': 'Agenda una consulta sin costo'
                            },
                            {
                                'id': 'srv_desarrollo',
                                'title': 'Desarrollo Web',
                                'description': 'Sitios web y aplicaciones'
                            },
                            {
                                'id': 'srv_marketing',
                                'title': 'Marketing Digital',
                                'description': 'Campañas y estrategias digitales'
                            }
                        ]
                    },
                    {
                        'title': 'Soporte',
                        'rows': [
                            {
                                'id': 'sup_tecnico',
                                'title': 'Soporte Técnico',
                                'description': 'Ayuda con problemas técnicos'
                            },
                            {
                                'id': 'sup_facturacion',
                                'title': 'Facturación',
                                'description': 'Consultas sobre facturación'
                            }
                        ]
                    }
                ]
            }
        }
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para mensaje de plantilla (Template Message) con variables
TEMPLATE_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'type': fields.String(
        required=True,
        description='Tipo de mensaje',
        enum=['template'],
        default='template',
        example='template'
    ),
    'template': fields.Raw(
        required=True,
        description='Configuración de la plantilla según formato oficial Meta WhatsApp Business API',
        example={
            'name': 'hello_world',
            'language': {
                'code': 'es'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': 'Juan Pérez'
                        }
                    ]
                }
            ]
        }
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para plantilla de texto básica
TEMPLATE_TEXT_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'template_name': fields.String(
        required=True,
        description='Nombre de la plantilla aprobada',
        example='hello_world'
    ),
    'language_code': fields.String(
        required=True,
        description='Código de idioma y localización (ISO 639-1)',
        example='es'
    ),
    'variables': fields.List(
        fields.String(),
        required=False,
        description='Lista de variables para reemplazar en la plantilla (orden importa)',
        example=['Juan Pérez', 'Producto ABC', '29.99']
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
    )
}

# Definición de campos para plantilla multimedia con variables
TEMPLATE_MEDIA_MESSAGE_FIELDS = {
    'to': fields.String(
        required=True,
        description='Número de teléfono destino en formato internacional',
        example='5491123456789'
    ),
    'template_name': fields.String(
        required=True,
        description='Nombre de la plantilla multimedia aprobada',
        example='order_confirmation'
    ),
    'language_code': fields.String(
        required=True,
        description='Código de idioma y localización',
        example='es'
    ),
    'header_media': fields.Raw(
        required=False,
        description='Contenido multimedia para el header',
        example={
            'type': 'image',
            'image': {
                'link': 'https://example.com/product.jpg'
            }
        }
    ),
    'body_variables': fields.List(
        fields.String(),
        required=False,
        description='Variables para el cuerpo del mensaje',
        example=['Juan', 'ABC-123', '$29.99']
    ),
    'button_parameters': fields.List(
        fields.Raw(),
        required=False,
        description='Parámetros para botones dinámicos',
        example=[
            {
                'type': 'quick_reply',
                'index': 0,
                'payload': 'confirm_order_123'
            }
        ]
    ),
    'messaging_line_id': fields.Integer(
        required=False,
        description='ID de la línea de mensajería a utilizar',
        example=1
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