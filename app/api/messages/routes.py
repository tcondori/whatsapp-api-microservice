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
    ERROR_RESPONSE_FIELDS, HEALTH_RESPONSE_FIELDS, IMAGE_MESSAGE_FIELDS, 
    IMAGE_UPLOAD_MESSAGE_FIELDS, MEDIA_UPLOAD_MESSAGE_FIELDS, LOCATION_MESSAGE_FIELDS,
    CONTACTS_MESSAGE_FIELDS, INTERACTIVE_BUTTONS_MESSAGE_FIELDS, INTERACTIVE_LIST_MESSAGE_FIELDS
)

# Crear namespace para mensajes
messages_ns = Namespace(
    'messages',
    description='Operaciones de mensajes de WhatsApp',
    path='/messages'
)

# Definir modelos usando el namespace
text_message_request = messages_ns.model('TextMessageRequest', TEXT_MESSAGE_FIELDS)
image_message_request = messages_ns.model('ImageMessageRequest', IMAGE_MESSAGE_FIELDS)
location_message_request = messages_ns.model('LocationMessageRequest', LOCATION_MESSAGE_FIELDS)
contacts_message_request = messages_ns.model('ContactsMessageRequest', CONTACTS_MESSAGE_FIELDS)
interactive_buttons_request = messages_ns.model('InteractiveButtonsMessageRequest', INTERACTIVE_BUTTONS_MESSAGE_FIELDS)
interactive_list_request = messages_ns.model('InteractiveListMessageRequest', INTERACTIVE_LIST_MESSAGE_FIELDS)
image_upload_message_request = messages_ns.model('ImageUploadMessageRequest', IMAGE_UPLOAD_MESSAGE_FIELDS)
media_upload_message_request = messages_ns.model('MediaUploadMessageRequest', MEDIA_UPLOAD_MESSAGE_FIELDS)
message_response = messages_ns.model('MessageResponse', MESSAGE_RESPONSE_FIELDS)
update_status_request = messages_ns.model('UpdateMessageStatusRequest', UPDATE_STATUS_FIELDS)
error_response = messages_ns.model('ErrorResponse', ERROR_RESPONSE_FIELDS)
health_response = messages_ns.model('HealthResponse', HEALTH_RESPONSE_FIELDS)

# Modelo simple para lista de mensajes (sin referencias complejas)
message_list_response = messages_ns.model('MessageListResponse', {
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

@messages_ns.route('/text')
class TextMessageResource(Resource):
    """
    Endpoint para envío de mensajes de texto
    """
    
    @messages_ns.doc('send_text_message', security='ApiKeyAuth')
    @messages_ns.expect(text_message_request, validate=True)
    @messages_ns.response(200, 'Mensaje enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
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
                messages_ns.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_text_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/image')
class ImageMessageResource(Resource):
    """
    Endpoint para envío de mensajes de imagen
    """
    
    @messages_ns.doc('send_image_message', security='ApiKeyAuth')
    @messages_ns.expect(image_message_request, validate=True)
    @messages_ns.response(200, 'Mensaje de imagen enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Envía un mensaje de imagen a través de WhatsApp
        
        Envía una imagen a un número de teléfono específico. Puede enviar
        una imagen ya subida (usando media_id) o subir una imagen desde URL.
        Opcionalmente puede incluir un caption con la imagen.
        """
        try:
            # Obtener datos del request
            message_data = request.json
            
            # Validar datos requeridos
            if not message_data:
                messages_ns.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_image_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/location')
class LocationMessageResource(Resource):
    """
    Endpoint para envío de mensajes de ubicación
    """
    
    @messages_ns.doc('send_location_message', security='ApiKeyAuth')
    @messages_ns.expect(location_message_request, validate=True)
    @messages_ns.response(200, 'Mensaje de ubicación enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Envía un mensaje de ubicación a través de WhatsApp
        
        Envía una ubicación geográfica a un número de teléfono específico usando
        coordenadas de latitud y longitud. Opcionalmente puede incluir el nombre
        del lugar y la dirección.
        
        **Formato del mensaje (oficial Meta/WhatsApp):**
        ```json
        {
            "to": "5491123456789",
            "type": "location",
            "location": {
                "latitude": -34.6037,
                "longitude": -58.3816,
                "name": "Obelisco de Buenos Aires",
                "address": "Av. 9 de Julio s/n, C1043 CABA, Argentina"
            },
            "messaging_line_id": 1
        }
        ```
        
        **Campos requeridos:**
        - `to`: Número de teléfono destino en formato internacional
        - `type`: Debe ser "location"
        - `location.latitude`: Latitud (entre -90 y 90)
        - `location.longitude`: Longitud (entre -180 y 180)
        
        **Campos opcionales:**
        - `location.name`: Nombre descriptivo del lugar
        - `location.address`: Dirección completa del lugar
        - `messaging_line_id`: ID de la línea de mensajería (default: 1)
        
        **Ejemplo de uso:**
        ```bash
        curl -X POST "http://localhost:5000/v1/messages/location" \
             -H "X-API-Key: dev-api-key" \
             -H "Content-Type: application/json" \
             -d '{
               "to": "5491123456789",
               "type": "location", 
               "location": {
                 "latitude": -34.6037,
                 "longitude": -58.3816,
                 "name": "Obelisco",
                 "address": "Buenos Aires, Argentina"
               }
             }'
        ```
        """
        try:
            # Obtener datos del request
            message_data = request.json
            
            # Validar datos requeridos
            if not message_data:
                messages_ns.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_location_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/contacts')
class ContactsMessageResource(Resource):
    """
    Endpoint para envío de mensajes de contactos (vCard)
    """
    
    @messages_ns.doc('send_contacts_message', security='ApiKeyAuth')
    @messages_ns.expect(contacts_message_request, validate=True)
    @messages_ns.response(200, 'Mensaje de contactos enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Envía un mensaje de contactos (vCard enriquecida) a través de WhatsApp
        
        Permite enviar una o más tarjetas de contacto con información completa
        como nombre, teléfonos, emails, direcciones, organización, etc.
        
        **Formato del mensaje (oficial Meta/WhatsApp):**
        ```json
        {
            "to": "5491123456789",
            "type": "contacts",
            "contacts": [
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
                            "email": "juan.perez@empresa.com",
                            "type": "WORK"
                        }
                    ],
                    "org": {
                        "company": "Mi Empresa",
                        "department": "Ventas",
                        "title": "Gerente de Ventas"
                    },
                    "addresses": [
                        {
                            "street": "Av. Corrientes 1234",
                            "city": "Buenos Aires",
                            "state": "CABA",
                            "zip": "C1043",
                            "country": "Argentina",
                            "country_code": "AR",
                            "type": "WORK"
                        }
                    ]
                }
            ],
            "messaging_line_id": 1
        }
        ```
        
        **Campos requeridos:**
        - `to`: Número de teléfono destino en formato internacional
        - `type`: Debe ser "contacts"
        - `contacts`: Array con al menos 1 contacto (máximo 20)
        - `contacts[].name`: Objeto con información del nombre
        - `contacts[].name.formatted_name` o `contacts[].name.first_name`: Al menos uno requerido
        
        **Campos opcionales del contacto:**
        - `phones`: Array de teléfonos (máximo 20 por contacto)
        - `emails`: Array de emails (máximo 20 por contacto) 
        - `addresses`: Array de direcciones
        - `urls`: Array de URLs/sitios web
        - `org`: Información de organización (empresa, cargo, departamento)
        - `birthday`: Fecha de nacimiento (formato YYYY-MM-DD)
        - `messaging_line_id`: ID de la línea de mensajería (default: 1)
        
        **Tipos de teléfono/email/dirección:**
        - `CELL`, `MAIN`, `IPHONE`, `HOME`, `WORK`
        
        **Ejemplo de uso:**
        ```bash
        curl -X POST "http://localhost:5000/v1/messages/contacts" \
             -H "X-API-Key: dev-api-key" \
             -H "Content-Type: application/json" \
             -d '{
               "to": "5491123456789",
               "type": "contacts",
               "contacts": [{
                 "name": {
                   "formatted_name": "Juan Pérez",
                   "first_name": "Juan",
                   "last_name": "Pérez"
                 },
                 "phones": [{
                   "phone": "+5491123456789",
                   "type": "CELL",
                   "wa_id": "5491123456789"
                 }],
                 "emails": [{
                   "email": "juan@empresa.com",
                   "type": "WORK"
                 }]
               }]
             }'
        ```
        """
        try:
            # Obtener datos del request
            message_data = request.json
            
            # Validar datos requeridos
            if not message_data:
                messages_ns.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_contacts_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/interactive/buttons')
class InteractiveButtonsMessageResource(Resource):
    """
    Endpoint para envío de mensajes interactivos con botones de respuesta
    """
    
    @messages_ns.doc('send_interactive_buttons_message', security='ApiKeyAuth')
    @messages_ns.expect(interactive_buttons_request, validate=True)
    @messages_ns.response(200, 'Mensaje interactivo con botones enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Envía un mensaje interactivo con botones de respuesta
        
        Permite enviar mensajes con hasta 3 botones clickeables que el usuario
        puede presionar para dar respuestas rápidas. Ideal para encuestas simples,
        confirmaciones, menús de navegación básicos, etc.
        """
        try:
            # Obtener datos del request
            message_data = request.json
            
            # Validar datos requeridos
            if not message_data:
                messages_ns.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_interactive_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/interactive/list')
class InteractiveListMessageResource(Resource):
    """
    Endpoint para envío de mensajes interactivos con lista de opciones
    """
    
    @messages_ns.doc('send_interactive_list_message', security='ApiKeyAuth')
    @messages_ns.expect(interactive_list_request, validate=True)
    @messages_ns.response(200, 'Mensaje interactivo con lista enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Envía un mensaje interactivo con lista de opciones (menú desplegable)
        
        Permite enviar mensajes con un menú desplegable que contiene hasta 10 opciones
        organizadas en secciones. Ideal para menús de servicios, catálogos, opciones
        de soporte, etc.
        """
        try:
            # Obtener datos del request
            message_data = request.json
            
            # Validar datos requeridos
            if not message_data:
                messages_ns.abort(400, 
                    message="Datos del mensaje requeridos",
                    error_code="MISSING_DATA"
                )
            
            # Enviar mensaje usando el servicio
            result = message_service.send_interactive_message(message_data)
            
            # Devolver respuesta exitosa
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/image/upload')
class ImageUploadResource(Resource):
    """
    Endpoint para envío de imágenes con upload de archivo (Caso 2: media_id)
    """
    
    @messages_ns.doc('send_image_with_upload', security='ApiKeyAuth')
    @messages_ns.expect(media_upload_message_request, validate=False)  # No validar porque incluye archivo
    @messages_ns.response(200, 'Mensaje de imagen con upload enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Sube un archivo de imagen y envía mensaje con media_id (Caso 2 oficial Meta)
        
        Este endpoint implementa el flujo oficial de Meta WhatsApp Business API:
        1. Sube el archivo para obtener media_id
        2. Envía el mensaje usando el media_id
        
        Formato multipart/form-data:
        - file: archivo de imagen (JPG/PNG)
        - to: número de teléfono destino
        - type: 'image'
        - caption: texto opcional
        - messaging_line_id: ID de línea (opcional)
        """
        try:
            # Validar que sea multipart/form-data
            if not request.files:
                messages_ns.abort(400, 
                    message="Se requiere archivo de imagen en formato multipart/form-data",
                    error_code="MISSING_FILE"
                )
            
            # Obtener archivo
            if 'file' not in request.files:
                messages_ns.abort(400, 
                    message="Campo 'file' requerido con el archivo de imagen",
                    error_code="MISSING_FILE_FIELD"
                )
                
            file = request.files['file']
            if file.filename == '':
                messages_ns.abort(400, 
                    message="No se seleccionó ningún archivo",
                    error_code="EMPTY_FILE"
                )

            # Validar tipo de archivo
            if not file.content_type or not file.content_type.startswith('image/'):
                messages_ns.abort(400, 
                    message="El archivo debe ser una imagen (JPEG/PNG)",
                    error_code="INVALID_FILE_TYPE"
                )

            # Obtener datos del formulario
            to = request.form.get('to')
            message_type = request.form.get('type', 'image')
            caption = request.form.get('caption', '')
            messaging_line_id = request.form.get('messaging_line_id', 1, type=int)

            # Validar datos requeridos
            if not to:
                messages_ns.abort(400, 
                    message="Campo 'to' requerido con el número de teléfono destino",
                    error_code="MISSING_TO_FIELD"
                )

            # Preparar datos del mensaje
            message_data = {
                'to': to,
                'type': message_type,
                'caption': caption,
                'messaging_line_id': messaging_line_id
            }

            # Leer contenido del archivo
            file_content = file.read()
            filename = file.filename
            content_type = file.content_type

            # Enviar mensaje con upload usando el servicio
            result = message_service.send_image_message_with_upload(
                message_data=message_data,
                file_content=file_content,
                filename=filename,
                content_type=content_type
            )
            
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/video/upload')
class VideoUploadResource(Resource):
    """
    Endpoint para envío de videos con upload de archivo
    """
    
    @messages_ns.doc('send_video_with_upload', security='ApiKeyAuth')
    @messages_ns.response(200, 'Mensaje de video con upload enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Sube un archivo de video y envía mensaje con media_id
        
        ⚠️ **IMPORTANTE: Este endpoint requiere multipart/form-data, NO JSON**
        
        **Proceso:**
        1. Sube el video a servidores de WhatsApp
        2. Obtiene un media_id único
        3. Envía el mensaje usando el media_id
        4. Registra la operación en base de datos
        
        **Content-Type requerido:** multipart/form-data
        
        **Parámetros del formulario:**
        - `file` (archivo, obligatorio): Archivo de video (MP4, 3GPP)
        - `to` (string, obligatorio): Número de teléfono destino (ej: 5491123456789)
        - `type` (string, opcional): Tipo de mensaje, se establece automáticamente como 'video'
        - `caption` (string, opcional): Texto descriptivo del video
        - `messaging_line_id` (integer, opcional): ID de línea de mensajería (default: 1)
        
        **Especificaciones técnicas:**
        - Tamaño máximo: 16MB
        - Formatos: MP4, 3GPP
        - Duración máxima: 6 minutos
        - Resolución recomendada: hasta 1280x720
        
        **Ejemplo en Postman:**
        ```
        POST http://localhost:5000/v1/messages/video/upload
        Headers:
            X-API-Key: dev-api-key
            Content-Type: multipart/form-data
        
        Body (form-data):
            file: [seleccionar archivo video.mp4]
            to: 5491123456789
            type: video
            caption: Mi video de prueba
            messaging_line_id: 1
        ```
        
        **NOTA:** NO usar application/json - debe ser multipart/form-data
        """
        
        return self._handle_media_upload('video', ['video/mp4', 'video/3gpp'])
    
    def _handle_media_upload(self, media_type: str, allowed_content_types: list):
        """Maneja el upload genérico de archivos multimedia"""
        try:
            # Validar que sea multipart/form-data
            if not request.files or 'file' not in request.files:
                messages_ns.abort(400, 
                    message=f"Campo 'file' requerido con el archivo de {media_type}",
                    error_code="MISSING_FILE_FIELD"
                )
            
            file = request.files['file']
            if file.filename == '':
                messages_ns.abort(400, 
                    message="No se seleccionó ningún archivo",
                    error_code="EMPTY_FILE"
                )

            # Validar tipo de archivo
            if not file.content_type or not any(file.content_type.startswith(ct.split('/')[0]) for ct in allowed_content_types):
                messages_ns.abort(400, 
                    message=f"El archivo debe ser de tipo {media_type} ({', '.join(allowed_content_types)})",
                    error_code="INVALID_FILE_TYPE"
                )

            # Obtener datos del formulario
            to = request.form.get('to')
            message_type = request.form.get('type', media_type)
            caption = request.form.get('caption', '')
            messaging_line_id = request.form.get('messaging_line_id', 1, type=int)

            # Validar datos requeridos
            if not to:
                messages_ns.abort(400, 
                    message="Campo 'to' requerido con el número de teléfono destino",
                    error_code="MISSING_TO_FIELD"
                )

            # Preparar datos del mensaje
            message_data = {
                'to': to,
                'type': message_type,
                'caption': caption if caption else '',
                'messaging_line_id': messaging_line_id
            }

            # Leer contenido del archivo
            file_content = file.read()
            filename = file.filename
            content_type = file.content_type

            # Enviar mensaje con upload usando el servicio
            result = message_service.send_media_message_with_upload(
                message_data=message_data,
                file_content=file_content,
                filename=filename,
                content_type=content_type,
                media_type=media_type
            )
            
            return result
            
        except ValidationError as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except (MessageSendError, LineNotFoundError) as e:
            messages_ns.abort(400,
                message=str(e),
                error_code="MESSAGE_SEND_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/audio/upload')
class AudioUploadResource(Resource):
    """
    Endpoint para envío de audios con upload de archivo
    """
    
    @messages_ns.doc('send_audio_with_upload', security='ApiKeyAuth')
    @messages_ns.expect(media_upload_message_request, validate=False)
    @messages_ns.response(200, 'Mensaje de audio con upload enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Sube un archivo de audio y envía mensaje con media_id
        
        Formato multipart/form-data:
        - file: archivo de audio (MP3/OGG/AMR/AAC)
        - to: número de teléfono destino
        - type: 'audio'
        - messaging_line_id: ID de línea (opcional)
        
        Nota: Los audios NO soportan caption
        """
        return VideoUploadResource()._handle_media_upload('audio', ['audio/mpeg', 'audio/ogg', 'audio/amr', 'audio/aac'])

@messages_ns.route('/document/upload')
class DocumentUploadResource(Resource):
    """
    Endpoint para envío de documentos con upload de archivo
    """
    
    @messages_ns.doc('send_document_with_upload', security='ApiKeyAuth')
    @messages_ns.expect(media_upload_message_request, validate=False)
    @messages_ns.response(200, 'Mensaje de documento con upload enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Sube un documento y envía mensaje con media_id
        
        Formato multipart/form-data:
        - file: archivo de documento (PDF/DOC/DOCX/PPT/PPTX/XLS/XLSX/TXT)
        - to: número de teléfono destino
        - type: 'document'
        - caption: texto opcional
        - messaging_line_id: ID de línea (opcional)
        """
        allowed_types = [
            'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain'
        ]
        return VideoUploadResource()._handle_media_upload('document', allowed_types)

@messages_ns.route('/sticker/upload')
class StickerUploadResource(Resource):
    """
    Endpoint para envío de stickers con upload de archivo
    """
    
    @messages_ns.doc('send_sticker_with_upload', security='ApiKeyAuth')
    @messages_ns.expect(media_upload_message_request, validate=False)
    @messages_ns.response(200, 'Mensaje de sticker con upload enviado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
    @require_api_key
    def post(self):
        """
        Sube un sticker y envía mensaje con media_id
        
        Formato multipart/form-data:
        - file: archivo de sticker (WEBP estático)
        - to: número de teléfono destino
        - type: 'sticker'
        - messaging_line_id: ID de línea (opcional)
        
        Nota: Los stickers NO soportan caption y deben ser WEBP estáticos
        """
        return VideoUploadResource()._handle_media_upload('sticker', ['image/webp', 'image/jpeg', 'image/png'])

@messages_ns.route('')
class MessageListResource(Resource):
    """
    Endpoint para listar mensajes con filtros
    """
    
    @messages_ns.doc('get_messages', security='ApiKeyAuth')
    @messages_ns.param('page', 'Número de página', type='integer', default=1)
    @messages_ns.param('per_page', 'Elementos por página', type='integer', default=10)
    @messages_ns.param('phone_number', 'Filtrar por número de teléfono')
    @messages_ns.param('status', 'Filtrar por estado', enum=['pending', 'sent', 'delivered', 'read', 'failed'])
    @messages_ns.param('message_type', 'Filtrar por tipo', enum=['text', 'image', 'location', 'contacts', 'document', 'audio', 'video'])
    @messages_ns.param('direction', 'Filtrar por dirección', enum=['inbound', 'outbound'])
    @messages_ns.param('line_id', 'Filtrar por línea de mensajería')
    @messages_ns.response(200, 'Lista de mensajes obtenida exitosamente', message_list_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(500, 'Error interno del servidor', error_response)
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
            messages_ns.abort(400,
                message=str(e),
                error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            messages_ns.abort(500,
                message="Error interno del servidor",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )

@messages_ns.route('/<string:message_id>')
class MessageResource(Resource):
    """
    Endpoint para operaciones con mensajes específicos
    """
    
    @messages_ns.doc('get_message_by_id', security='ApiKeyAuth')
    @messages_ns.param('message_id', 'ID del mensaje')
    @messages_ns.response(200, 'Mensaje encontrado exitosamente', message_response)
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(404, 'Mensaje no encontrado', error_response)
    @messages_ns.response(500, 'Error interno del servidor', error_response)
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

@messages_ns.route('/whatsapp/<string:whatsapp_message_id>')
class WhatsAppMessageResource(Resource):
    """
    Endpoint para operaciones con mensajes por ID de WhatsApp
    """
    
    @messages_ns.doc('get_message_by_whatsapp_id', security='ApiKeyAuth')
    @messages_ns.param('whatsapp_message_id', 'ID del mensaje en WhatsApp')
    @messages_ns.response(200, 'Mensaje encontrado exitosamente', message_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(404, 'Mensaje no encontrado', error_response)
    @messages_ns.response(500, 'Error interno del servidor', error_response)
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

@messages_ns.route('/whatsapp/<string:whatsapp_message_id>/status')
class MessageStatusResource(Resource):
    """
    Endpoint para actualización de estado de mensajes
    """
    
    @messages_ns.doc('update_message_status', security='ApiKeyAuth')
    @messages_ns.param('whatsapp_message_id', 'ID del mensaje en WhatsApp')
    @messages_ns.expect(update_status_request, validate=True)
    @messages_ns.response(200, 'Estado actualizado exitosamente')
    @messages_ns.response(400, 'Error de validación', error_response)
    @messages_ns.response(401, 'No autorizado')
    @messages_ns.response(404, 'Mensaje no encontrado', error_response)
    @messages_ns.response(500, 'Error interno del servidor', error_response)
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
@messages_ns.route('/test')
class MessageTestResource(Resource):
    """
    Endpoint de prueba para verificar funcionalidad básica
    """
    
    @messages_ns.doc('test_messages_api', security='ApiKeyAuth')
    @messages_ns.response(200, 'API de mensajes funcionando correctamente')
    @messages_ns.response(401, 'No autorizado')
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
                        'POST /v1/messages/text - Enviar mensaje de texto',
                        'POST /v1/messages/image - Enviar mensaje de imagen (URL directa o media_id)',
                        'POST /v1/messages/location - Enviar mensaje de ubicación',
                        'POST /v1/messages/contacts - Enviar mensaje de contactos (vCard)',
                        'POST /v1/messages/interactive/buttons - Enviar mensaje interactivo con botones (hasta 3)',
                        'POST /v1/messages/interactive/list - Enviar mensaje interactivo con lista (hasta 10 opciones)',
                        'POST /v1/messages/image/upload - Subir archivo y enviar imagen (Caso 2: media_id)',
                        'POST /v1/messages/video/upload - Subir archivo y enviar video',
                        'POST /v1/messages/audio/upload - Subir archivo y enviar audio',
                        'POST /v1/messages/document/upload - Subir archivo y enviar documento',
                        'POST /v1/messages/sticker/upload - Subir archivo y enviar sticker',
                        'GET /v1/messages - Listar mensajes con filtros',
                        'GET /v1/messages/{id} - Obtener mensaje por ID',
                        'GET /v1/messages/whatsapp/{whatsapp_id} - Obtener por ID de WhatsApp',
                        'PATCH /v1/messages/whatsapp/{whatsapp_id}/status - Actualizar estado'
                    ]
                }
            }
            
        except Exception as e:
            api.abort(500, 
                message="Error verificando estado del servicio",
                error_code="SERVICE_ERROR",
                details=str(e)
            )
