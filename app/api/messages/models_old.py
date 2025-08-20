"""
Modelos de request/response para la API de mensajes
Define esquemas de validación usando Flask-RESTX para documentación automática
"""
from flask_restx import fields

# Modelo base para mensajes
BaseMessage = {
    'phone_number': fields.String(
        required=True,
        description='Número de teléfono en formato internacional (+5491123456789)',
        example='+5491123456789'
    ),
    'content': fields.String(
        required=True,
        description='Contenido del mensaje',
        example='Hola, este es un mensaje de prueba'
    ),
    'line_id': fields.String(
        required=False,
        description='ID de la línea de mensajería (opcional)',
        example='demo-line-001'
    )
}

# Modelo para envío de mensajes de texto
TextMessageRequest = BaseMessage.copy()

# Modelo de respuesta para mensajes
MessageResponse = {
    'id': fields.String(
        required=True,
        description='ID único del mensaje en la base de datos',
        example='550e8400-e29b-41d4-a716-446655440000'
    ),
    'whatsapp_message_id': fields.String(
        required=True,
        description='ID del mensaje asignado por WhatsApp',
        example='wamid.HBgNNTU5MTEyMzQ1Njc4OQAM'
    ),
    'phone_number': fields.String(
        required=True,
        description='Número de teléfono destinatario',
        example='+5491123456789'
    ),
    'message_type': fields.String(
        required=True,
        description='Tipo de mensaje',
        enum=['text', 'image', 'document', 'audio', 'video'],
        example='text'
    ),
    'content': fields.String(
        required=True,
        description='Contenido del mensaje',
        example='Hola, este es un mensaje de prueba'
    ),
    'status': fields.String(
        required=True,
        description='Estado del mensaje',
        enum=['pending', 'sent', 'delivered', 'read', 'failed'],
        example='sent'
    ),
    'direction': fields.String(
        required=True,
        description='Dirección del mensaje',
        enum=['inbound', 'outbound'],
        example='outbound'
    ),
    'line_id': fields.String(
        required=True,
        description='ID de la línea de mensajería utilizada',
        example='demo-line-001'
    ),
    'created_at': fields.DateTime(
        required=True,
        description='Fecha y hora de creación',
        example='2024-01-15T10:30:00Z'
    ),
    'updated_at': fields.DateTime(
        required=True,
        description='Fecha y hora de última actualización',
        example='2024-01-15T10:30:00Z'
    ),
    'retry_count': fields.Integer(
        required=True,
        description='Número de reintentos',
        example=0
    ),
    'error_message': fields.String(
        required=False,
        description='Mensaje de error en caso de fallo',
        example=None
    )
}

# Modelo de paginación
Pagination = {
    'page': fields.Integer(
        required=True,
        description='Página actual',
        example=1
    ),
    'per_page': fields.Integer(
        required=True,
        description='Elementos por página',
        example=10
    ),
    'total': fields.Integer(
        required=True,
        description='Total de elementos',
        example=25
    ),
    'pages': fields.Integer(
        required=True,
        description='Total de páginas',
        example=3
    ),
    'has_prev': fields.Boolean(
        required=True,
        description='Tiene página anterior',
        example=False
    ),
    'has_next': fields.Boolean(
        required=True,
        description='Tiene página siguiente',
        example=True
    ),
    'prev_page': fields.Integer(
        required=False,
        description='Número de página anterior',
        example=None
    ),
    'next_page': fields.Integer(
        required=False,
        description='Número de página siguiente',
        example=2
    )
}

# Modelo de datos de lista de mensajes (se define en routes.py por referencias circulares)
# MessageListData será creado dinámicamente

# Modelo de respuesta para lista de mensajes (se define en routes.py por referencias circulares)  
# MessageListResponse será creado dinámicamente

# Modelo de filtros para mensajes
MessageFilters = {
    'phone_number': fields.String(
        required=False,
        description='Filtrar por número de teléfono',
        example='+5491123456789'
    ),
    'status': fields.String(
        required=False,
        description='Filtrar por estado',
        enum=['pending', 'sent', 'delivered', 'read', 'failed'],
        example='sent'
    ),
    'message_type': fields.String(
        required=False,
        description='Filtrar por tipo de mensaje',
        enum=['text', 'image', 'document', 'audio', 'video'],
        example='text'
    ),
    'direction': fields.String(
        required=False,
        description='Filtrar por dirección',
        enum=['inbound', 'outbound'],
        example='outbound'
    ),
    'line_id': fields.String(
        required=False,
        description='Filtrar por línea de mensajería',
        example='demo-line-001'
    )
}

# Modelo para actualización de estado
UpdateMessageStatusRequest = {
    'status': fields.String(
        required=True,
        description='Nuevo estado del mensaje',
        enum=['pending', 'sent', 'delivered', 'read', 'failed'],
        example='delivered'
    )
}

# Modelo de respuesta de error
ErrorResponse = {
    'success': fields.Boolean(
        required=True,
        description='Indica si la operación fue exitosa',
        example=False
    ),
    'message': fields.String(
        required=True,
        description='Mensaje de error',
        example='Número de teléfono inválido'
    ),
    'error_code': fields.String(
        required=True,
        description='Código de error',
        example='VALIDATION_ERROR'
    ),
    'details': fields.String(
        required=False,
        description='Detalles adicionales del error',
        example='El formato debe ser +país código número'
    )
}
