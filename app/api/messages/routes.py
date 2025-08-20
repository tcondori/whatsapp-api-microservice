"""
Endpoints REST para mensajes de WhatsApp
Implementa la API REST usando Flask-RESTX con documentación automática
"""
from flask import request
from flask_restx import Namespace, Resource, fields

from app.api.messages.services import MessageService
from app.private.auth import require_api_key
from app.utils.exceptions import ValidationError, MessageSendError, LineNotFoundError, MessageNotFoundError
from app.utils.helpers import create_error_response

# Importar definiciones de campos
from app.api.messages.models import (
    TEXT_MESSAGE_FIELDS, MESSAGE_RESPONSE_FIELDS, UPDATE_STATUS_FIELDS,
    ERROR_RESPONSE_FIELDS, HEALTH_RESPONSE_FIELDS
)

# Crear namespace para mensajes
api = Namespace(
    'messages',
    description='Operaciones de mensajes de WhatsApp',
    path='/messages'
)

# Definir modelos usando el namespace
text_message_request = api.model('TextMessageRequest', TEXT_MESSAGE_FIELDS)
message_response = api.model('MessageResponse', MESSAGE_RESPONSE_FIELDS)
update_status_request = api.model('UpdateMessageStatusRequest', UPDATE_STATUS_FIELDS)
error_response = api.model('ErrorResponse', ERROR_RESPONSE_FIELDS)
health_response = api.model('HealthResponse', HEALTH_RESPONSE_FIELDS)

# Modelo simple para lista de mensajes (sin referencias complejas)
message_list_response = api.model('MessageListResponse', {
    'success': fields.Boolean(
        required=True,
        description='Indica si la operación fue exitosa',
        example=True
    ),
    'message': fields.String(
        required=True,
        description='Mensaje descriptivo de la operación',
        example='Mensajes obtenidos exitosamente'
    ),
    'data': fields.Raw(
        required=True,
        description='Datos de respuesta con mensajes y paginación'
    )
})

# Inicializar servicio
message_service = MessageService()

@api.route('/text')
class TextMessageResource(Resource):
    """
    Endpoint para envío de mensajes de texto
    """
    
    @api.doc('send_text_message', security='ApiKeyAuth')
    @api.expect(text_message_request, validate=True)
    @api.response(200, 'Mensaje enviado exitosamente', message_response)
    @api.response(400, 'Error de validación', error_response)
    @api.response(401, 'No autorizado')
    @api.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Envía un mensaje de texto a través de WhatsApp
        
        Envía un mensaje de texto a un número de teléfono específico
        usando una línea de mensajería configurada.
        """
        try:
            # Obtener datos del request
            message_data = request.json
            
            # Validar datos requeridos
            if not message_data:
                api.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_text_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            api.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            api.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            api.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@api.route('')
class MessageListResource(Resource):
    """
    Endpoint para listar mensajes con filtros
    """
    
    @api.doc('get_messages', security='ApiKeyAuth')
    @api.param('page', 'Número de página', type='integer', default=1)
    @api.param('per_page', 'Elementos por página', type='integer', default=10)
    @api.param('phone_number', 'Filtrar por número de teléfono')
    @api.param('status', 'Filtrar por estado', enum=['pending', 'sent', 'delivered', 'read', 'failed'])
    @api.param('message_type', 'Filtrar por tipo', enum=['text', 'image', 'document', 'audio', 'video'])
    @api.param('direction', 'Filtrar por dirección', enum=['inbound', 'outbound'])
    @api.param('line_id', 'Filtrar por línea de mensajería')
    @api.response(200, 'Lista de mensajes obtenida exitosamente', message_list_response)
    @api.response(400, 'Error de validación', error_response)
    @api.response(401, 'No autorizado')
    @api.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def get(self):
        """
        Obtiene lista de mensajes con filtros opcionales y paginación
        
        Permite filtrar mensajes por diferentes criterios como número de teléfono,
        estado, tipo de mensaje, etc. Los resultados están paginados.
        """
        try:
            # Obtener parámetros de query
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Construir filtros
            filters = {}
            if request.args.get('phone_number'):
                filters['phone_number'] = request.args.get('phone_number')
            if request.args.get('status'):
                filters['status'] = request.args.get('status')
            if request.args.get('message_type'):
                filters['message_type'] = request.args.get('message_type')
            if request.args.get('direction'):
                filters['direction'] = request.args.get('direction')
            if request.args.get('line_id'):
                filters['line_id'] = request.args.get('line_id')
            
            # Obtener mensajes usando el servicio
            result = message_service.get_messages(
                filters=filters if filters else None,
                page=page,
                per_page=per_page
            )
            
            return result
            
        except ValidationError as e:
            api.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            api.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@api.route('/<string:message_id>')
class MessageResource(Resource):
    """
    Endpoint para operaciones con mensajes específicos
    """
    
    @api.doc('get_message_by_id', security='ApiKeyAuth')
    @api.param('message_id', 'ID del mensaje')
    @api.response(200, 'Mensaje encontrado exitosamente', message_response)
    @api.response(400, 'Error de validación', error_response)
    @api.response(401, 'No autorizado')
    @api.response(404, 'Mensaje no encontrado', error_response)
    @api.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def get(self, message_id):
        """
        Obtiene un mensaje específico por su ID
        
        Busca y retorna la información completa de un mensaje
        usando su ID único en la base de datos.
        """
        try:
            # Validar ID del mensaje
            if not message_id or not message_id.strip():
                api.abort(400,
                message="ID del mensaje requerido",
                error_code="MISSING_MESSAGE_ID"
            )
            
            # Obtener mensaje usando el servicio
            result = message_service.get_message_by_id(message_id.strip())
            
            return result
            
        except MessageNotFoundError as e:
            api.abort(404, message=f"Mensaje no encontrado: {message_id}",
                error_code="MESSAGE_NOT_FOUND"
            )
        except ValidationError as e:
            api.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            return create_error_response(
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            ), 500

@api.route('/whatsapp/<string:whatsapp_message_id>')
class WhatsAppMessageResource(Resource):
    """
    Endpoint para operaciones con mensajes por ID de WhatsApp
    """
    
    @api.doc('get_message_by_whatsapp_id', security='ApiKeyAuth')
    @api.param('whatsapp_message_id', 'ID del mensaje en WhatsApp')
    @api.response(200, 'Mensaje encontrado exitosamente', message_response)
    @api.response(401, 'No autorizado')
    @api.response(404, 'Mensaje no encontrado', error_response)
    @api.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def get(self, whatsapp_message_id):
        """
        Obtiene un mensaje por su ID de WhatsApp
        
        Busca un mensaje usando el ID que fue asignado
        por la API de WhatsApp Business.
        """
        try:
            # Validar ID de WhatsApp
            if not whatsapp_message_id or not whatsapp_message_id.strip():
                api.abort(400,
                message="ID del mensaje de WhatsApp requerido",
                error_code="MISSING_WHATSAPP_MESSAGE_ID"
            )
            
            # Obtener mensaje usando el servicio
            result = message_service.get_message_by_whatsapp_id(whatsapp_message_id.strip())
            
            return result
            
        except MessageNotFoundError as e:
            api.abort(404, message=f"Mensaje no encontrado: {whatsapp_message_id}",
                error_code="MESSAGE_NOT_FOUND"
            )
        except Exception as e:
            return create_error_response(
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            ), 500

@api.route('/whatsapp/<string:whatsapp_message_id>/status')
class MessageStatusResource(Resource):
    """
    Endpoint para actualización de estado de mensajes
    """
    
    @api.doc('update_message_status', security='ApiKeyAuth')
    @api.param('whatsapp_message_id', 'ID del mensaje en WhatsApp')
    @api.expect(update_status_request, validate=True)
    @api.response(200, 'Estado actualizado exitosamente')
    @api.response(400, 'Error de validación', error_response)
    @api.response(401, 'No autorizado')
    @api.response(404, 'Mensaje no encontrado', error_response)
    @api.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def patch(self, whatsapp_message_id):
        """
        Actualiza el estado de un mensaje de WhatsApp
        
        Permite actualizar el estado de entrega de un mensaje
        (ej: sent, delivered, read, failed).
        """
        try:
            # Validar ID de WhatsApp
            if not whatsapp_message_id or not whatsapp_message_id.strip():
                api.abort(400,
                message="ID del mensaje de WhatsApp requerido",
                error_code="MISSING_WHATSAPP_MESSAGE_ID"
            )
            
            # Obtener datos del request
            status_data = request.json
            if not status_data or 'status' not in status_data:
                api.abort(400,
                message="Estado del mensaje requerido",
                error_code="MISSING_STATUS"
            )
            
            new_status = status_data['status']
            
            # Actualizar estado usando el servicio
            result = message_service.update_message_status(
                whatsapp_message_id.strip(), 
                new_status
            )
            
            return result
            
        except MessageNotFoundError as e:
            api.abort(404, message=f"Mensaje no encontrado: {whatsapp_message_id}",
                error_code="MESSAGE_NOT_FOUND"
            )
        except ValidationError as e:
            api.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            return create_error_response(
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            ), 500

# Endpoint de prueba simple para verificar funcionalidad
@api.route('/test')
class MessageTestResource(Resource):
    """
    Endpoint de prueba para verificar funcionalidad básica
    """
    
    @api.doc('test_messages_api', security='ApiKeyAuth')
    @api.response(200, 'API de mensajes funcionando correctamente')
    @api.response(401, 'No autorizado')
    @require_api_key
    def get(self):
        """
        Endpoint de prueba para verificar que la API de mensajes funciona
        
        Devuelve información básica sobre el estado del servicio de mensajes.
        """
        try:
            # Obtener estadísticas básicas
            total_messages = len(message_service.msg_repo.get_all())
            available_lines = len([line for line in message_service.line_repo.get_all() if line.is_active])
            
            return {
                'success': True,
                'message': 'API de mensajes funcionando correctamente',
                'data': {
                    'service_status': 'active',
                    'total_messages': total_messages,
                    'available_lines': available_lines,
                    'supported_endpoints': [
                        'POST /api/v1/messages/text - Enviar mensaje de texto',
                        'GET /api/v1/messages - Listar mensajes con filtros',
                        'GET /api/v1/messages/{id} - Obtener mensaje por ID',
                        'GET /api/v1/messages/whatsapp/{whatsapp_id} - Obtener por ID de WhatsApp',
                        'PATCH /api/v1/messages/whatsapp/{whatsapp_id}/status - Actualizar estado'
                    ]
                }
            }
            
        except Exception as e:
            api.abort(500, 
                message="Error verificando estado del servicio",
                error_code="SERVICE_ERROR",
                details=str(e)
            )
