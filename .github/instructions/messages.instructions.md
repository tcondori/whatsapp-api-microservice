# Messages Instructions
<!-- Instrucciones para manejo de mensajes en WhatsApp API -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar el sistema completo de mensajería WhatsApp con soporte multi-línea, incluyendo:
- API endpoints para todos los tipos de mensajes (texto, imagen, video, documento, plantillas, interactivos)
- Sistema de selección automática de líneas con balanceador de carga
- Gestión completa de líneas de mensajería (CRUD, estadísticas, límites diarios)
- Servicio agregador que detecta automáticamente el tipo de mensaje
- Plantillas de mensajes y componentes interactivos (botones, listas)
- Integración con la API oficial de WhatsApp Business
-->

## Multi-Line Management Endpoints
<!-- Endpoints para gestión de líneas múltiples de mensajería -->

### Messaging Lines Management
```
GET /api/v1/whatsapp/lines              # Listar todas las líneas
POST /api/v1/whatsapp/lines             # Crear nueva línea
PUT /api/v1/whatsapp/lines/{line_id}    # Actualizar línea
DELETE /api/v1/whatsapp/lines/{line_id} # Desactivar línea
GET /api/v1/whatsapp/lines/{line_id}/stats  # Estadísticas de línea
```

### Line Selection Service
```python
# app/services/line_selector_service.py
from database.models import MessagingLine
from flask import current_app
import random

class LineSelector:
    """Servicio para selección automática de líneas de mensajería"""
    
    @staticmethod
    def get_available_line(preferred_line_id=None):
        """
        Obtiene una línea disponible para envío de mensajes
        Args:
            preferred_line_id: ID de línea preferida (opcional)
        Returns:
            MessagingLine: Línea disponible o None
        """
        # Intentar usar línea preferida si se especifica
        if preferred_line_id:
            line = MessagingLine.query.filter_by(
                line_id=preferred_line_id,
                is_active=True
            ).first()
            if line and line.can_send_message():
                return line
        
        # Obtener todas las líneas activas que pueden enviar mensajes
        available_lines = MessagingLine.query.filter_by(is_active=True).all()
        available_lines = [line for line in available_lines if line.can_send_message()]
        
        if not available_lines:
            current_app.logger.warning("No hay líneas disponibles para envío")
            return None
        
        # Selección por balanceador de carga (línea con menos uso)
        return min(available_lines, key=lambda x: x.current_daily_count)
    
    @staticmethod
    def get_line_by_id(line_id):
        """Obtiene una línea específica por ID"""
        return MessagingLine.query.filter_by(
            line_id=line_id,
            is_active=True
        ).first()
```

## API Endpoints Structure
<!-- Estructura de endpoints de la API de mensajes -->

### Main Aggregator Endpoint
```
POST /api/v1/whatsapp/messages
```
Endpoint agregador principal que detecta automáticamente el tipo de mensaje y lo procesa.

### Specific Message Type Endpoints
```
POST /api/v1/whatsapp/messages/text
POST /api/v1/whatsapp/messages/image
POST /api/v1/whatsapp/messages/video
POST /api/v1/whatsapp/messages/document
POST /api/v1/whatsapp/messages/template
POST /api/v1/whatsapp/messages/interactive/buttons
POST /api/v1/whatsapp/messages/interactive/list
```

## Message Types Implementation
<!-- Implementación de tipos de mensajes -->

### Text Messages
```python
def send_text_message(phone_number, message_text, line_id=None):
    """
    Envía un mensaje de texto
    Endpoint: POST /api/v1/whatsapp/messages/text
    Args:
        phone_number: Número de destino
        message_text: Contenido del mensaje
        line_id: ID de línea específica (opcional)
    """
    from app.services.line_selector_service import LineSelector
    
    # Seleccionar línea disponible
    selected_line = LineSelector.get_available_line(line_id)
    if not selected_line:
        raise Exception("No hay líneas disponibles para envío de mensajes")
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    # Enviar mensaje usando la línea seleccionada
    result = send_to_whatsapp_api(payload, selected_line)
    
    # Incrementar contador de mensajes de la línea
    selected_line.increment_message_count()
    
    return result
```

### Image Messages
```python
def send_image_message(phone_number, image_data):
    """
    Envía un mensaje con imagen
    Endpoint: POST /api/v1/whatsapp/messages/image
    Args:
        phone_number: Número de destino
        image_data: Datos de la imagen (ID o URL)
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "image",
        "image": {
            "id": image_data.get('media_id') if image_data.get('media_id') else None,
            "link": image_data.get('url') if image_data.get('url') else None,
            "caption": image_data.get('caption', '')
        }
    }
    return send_to_whatsapp_api(payload)
```

### Video Messages
```python
def send_video_message(phone_number, video_data):
    """
    Envía un mensaje con video
    Endpoint: POST /api/v1/whatsapp/messages/video
    Args:
        phone_number: Número de destino
        video_data: Datos del video (ID o URL)
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "video",
        "video": {
            "id": video_data.get('media_id') if video_data.get('media_id') else None,
            "link": video_data.get('url') if video_data.get('url') else None,
            "caption": video_data.get('caption', '')
        }
    }
    return send_to_whatsapp_api(payload)
```

### Document Messages
```python
def send_document_message(phone_number, document_data):
    """
    Envía un mensaje con documento
    Endpoint: POST /api/v1/whatsapp/messages/document
    Args:
        phone_number: Número de destino
        document_data: Datos del documento
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "document",
        "document": {
            "id": document_data.get('media_id') if document_data.get('media_id') else None,
            "link": document_data.get('url') if document_data.get('url') else None,
            "caption": document_data.get('caption', ''),
            "filename": document_data.get('filename')
        }
    }
    return send_to_whatsapp_api(payload)
```

### Template Messages
```python
def send_template_message(phone_number, template_data):
    """
    Envía un mensaje de plantilla aprobada
    Endpoint: POST /api/v1/whatsapp/messages/template
    Args:
        phone_number: Número de destino
        template_data: Datos de la plantilla
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_data.get('name'),
            "language": {
                "code": template_data.get('language', 'en')
            },
            "components": template_data.get('components', [])
        }
    }
    return send_to_whatsapp_api(payload)
```

### Interactive Messages - Buttons
```python
def send_interactive_buttons(phone_number, button_data):
    """
    Envía un mensaje interactivo con botones
    Endpoint: POST /api/v1/whatsapp/messages/interactive/buttons
    Args:
        phone_number: Número de destino
        button_data: Datos de los botones
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": button_data.get('header'),
            "body": {
                "text": button_data.get('body_text')
            },
            "footer": {
                "text": button_data.get('footer_text', '')
            },
            "action": {
                "buttons": button_data.get('buttons', [])
            }
        }
    }
    return send_to_whatsapp_api(payload)
```

### Interactive Messages - List
```python
def send_interactive_list(phone_number, list_data):
    """
    Envía un mensaje interactivo con lista de opciones
    Endpoint: POST /api/v1/whatsapp/messages/interactive/list
    Args:
        phone_number: Número de destino
        list_data: Datos de la lista
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": list_data.get('header'),
            "body": {
                "text": list_data.get('body_text')
            },
            "footer": {
                "text": list_data.get('footer_text', '')
            },
            "action": {
                "button": list_data.get('button_text', 'Ver opciones'),
                "sections": list_data.get('sections', [])
            }
        }
    }
    return send_to_whatsapp_api(payload)
```

### Main Aggregator Function
```python
def send_message(data):
    """
    Función agregadora que detecta el tipo de mensaje y lo envía
    Endpoint: POST /api/v1/whatsapp/messages
    Args:
        data: Datos del mensaje con tipo autodetectado
    """
    message_type = detect_message_type(data)
    
    if message_type == 'text':
        return send_text_message(data['to'], data['text']['body'])
    elif message_type == 'image':
        return send_image_message(data['to'], data['image'])
    elif message_type == 'video':
        return send_video_message(data['to'], data['video'])
    elif message_type == 'document':
        return send_document_message(data['to'], data['document'])
    elif message_type == 'template':
        return send_template_message(data['to'], data['template'])
    elif message_type == 'interactive':
        if data['interactive']['type'] == 'button':
            return send_interactive_buttons(data['to'], data['interactive'])
        elif data['interactive']['type'] == 'list':
            return send_interactive_list(data['to'], data['interactive'])
    else:
        raise ValueError(f"Tipo de mensaje no soportado: {message_type}")

def detect_message_type(data):
    """
    Detecta automáticamente el tipo de mensaje basado en el payload
    Args:
        data: Payload del mensaje
    Returns:
        str: Tipo de mensaje detectado
    """
    if 'text' in data:
        return 'text'
    elif 'image' in data:
        return 'image'
    elif 'video' in data:
        return 'video'
    elif 'document' in data:
        return 'document'
    elif 'template' in data:
        return 'template'
    elif 'interactive' in data:
        return 'interactive'
    else:
        return 'text'  # Default fallback
```

## Message Status Tracking
<!-- Seguimiento de estado de mensajes -->

### Status Types
- `sent`: Mensaje enviado a WhatsApp
- `delivered`: Mensaje entregado al dispositivo
- `read`: Mensaje leído por el usuario
- `failed`: Error en el envío

### Status Webhook Handler
```python
def handle_msg_status(webhook_data):
    """
    Procesa actualizaciones de estado de mensaje
    Args:
        webhook_data: Datos del webhook de WhatsApp
    """
    pass
```

## Message Processing Pipeline
<!-- Pipeline de procesamiento de mensajes -->

### Incoming Message Flow
1. Webhook receives message
2. Validate webhook signature
3. Parse message content
4. Process business logic
5. Send response (if required)
6. Log message for history

### Outgoing Message Flow
1. Validate recipient and content
2. Check rate limits
3. Format message for WhatsApp API
4. Send via Graph API
5. Handle response and errors
6. Update message status

## Service Layer Implementation
<!-- Implementación de la capa de servicios -->

```python
# app/api/messages/services.py
from app.repositories.msg_repo import MessageRepository
from app.utils.exceptions import ValidationError, WhatsAppAPIError
from app.private.validators import validate_phone_number
import requests
import os

class MessageService:
    """Servicio para manejo de mensajes de WhatsApp"""
    
    def __init__(self):
        self.msg_repo = MessageRepository()
        self.whatsapp_api_url = f"https://graph.facebook.com/{os.getenv('WHATSAPP_API_VERSION')}"
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    def send_message(self, data: dict) -> dict:
        """
        Envía mensaje usando el endpoint agregador
        Detecta automáticamente el tipo y usa el método específico
        """
        if not validate_phone_number(data.get('to')):
            raise ValidationError("Número de teléfono inválido")
        
        message_type = self._detect_message_type(data)
        
        if message_type == 'text':
            return self.send_text_message(data)
        elif message_type == 'image':
            return self.send_image_message(data)
        elif message_type == 'video':
            return self.send_video_message(data)
        elif message_type == 'document':
            return self.send_document_message(data)
        elif message_type == 'template':
            return self.send_template_message(data)
        elif message_type == 'interactive':
            if data['interactive']['type'] == 'button':
                return self.send_interactive_buttons(data)
            elif data['interactive']['type'] == 'list':
                return self.send_interactive_list(data)
        else:
            raise ValidationError(f"Tipo de mensaje no soportado: {message_type}")
    
    def send_text_message(self, data: dict) -> dict:
        """Envía mensaje de texto específicamente"""
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "text",
            "text": {
                "body": data.get('text', {}).get('body', data.get('message', ''))
            }
        }
        return self._send_to_whatsapp_api(payload)
    
    def send_image_message(self, data: dict) -> dict:
        """Envía mensaje con imagen específicamente"""
        image_data = data.get('image', {})
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "image",
            "image": {
                "id": image_data.get('id') if image_data.get('id') else None,
                "link": image_data.get('link') if image_data.get('link') else None,
                "caption": image_data.get('caption', '')
            }
        }
        # Remover campos None
        if payload["image"]["id"] is None:
            del payload["image"]["id"]
        if payload["image"]["link"] is None:
            del payload["image"]["link"]
            
        return self._send_to_whatsapp_api(payload)
    
    def send_video_message(self, data: dict) -> dict:
        """Envía mensaje con video específicamente"""
        video_data = data.get('video', {})
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "video",
            "video": {
                "id": video_data.get('id') if video_data.get('id') else None,
                "link": video_data.get('link') if video_data.get('link') else None,
                "caption": video_data.get('caption', '')
            }
        }
        # Remover campos None
        if payload["video"]["id"] is None:
            del payload["video"]["id"]
        if payload["video"]["link"] is None:
            del payload["video"]["link"]
            
        return self._send_to_whatsapp_api(payload)
    
    def send_document_message(self, data: dict) -> dict:
        """Envía mensaje con documento específicamente"""
        document_data = data.get('document', {})
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "document",
            "document": {
                "id": document_data.get('id') if document_data.get('id') else None,
                "link": document_data.get('link') if document_data.get('link') else None,
                "caption": document_data.get('caption', ''),
                "filename": document_data.get('filename')
            }
        }
        # Remover campos None
        if payload["document"]["id"] is None:
            del payload["document"]["id"]
        if payload["document"]["link"] is None:
            del payload["document"]["link"]
            
        return self._send_to_whatsapp_api(payload)
    
    def send_template_message(self, data: dict) -> dict:
        """Envía mensaje de plantilla específicamente"""
        template_data = data.get('template', {})
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "template",
            "template": {
                "name": template_data.get('name'),
                "language": {
                    "code": template_data.get('language', {}).get('code', 'en')
                },
                "components": template_data.get('components', [])
            }
        }
        return self._send_to_whatsapp_api(payload)
    
    def send_interactive_buttons(self, data: dict) -> dict:
        """Envía mensaje interactivo con botones"""
        interactive_data = data.get('interactive', {})
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "interactive",
            "interactive": interactive_data
        }
        return self._send_to_whatsapp_api(payload)
    
    def send_interactive_list(self, data: dict) -> dict:
        """Envía mensaje interactivo con lista"""
        interactive_data = data.get('interactive', {})
        payload = {
            "messaging_product": "whatsapp",
            "to": data['to'],
            "type": "interactive",
            "interactive": interactive_data
        }
        return self._send_to_whatsapp_api(payload)
    
    def _send_to_whatsapp_api(self, payload: dict) -> dict:
        """
        Envía el payload a la API de WhatsApp
        Args:
            payload: Datos del mensaje formateados para WhatsApp
        Returns:
            dict: Respuesta de la API de WhatsApp
        """
        url = f"{self.whatsapp_api_url}/{self.phone_number_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Guardar mensaje en base de datos
            self._save_message_to_db(payload, result)
            
            return result
            
        except requests.RequestException as e:
            raise WhatsAppAPIError(f"Error enviando mensaje: {str(e)}")
    
    def _detect_message_type(self, data: dict) -> str:
        """Detecta automáticamente el tipo de mensaje"""
        if 'text' in data:
            return 'text'
        elif 'image' in data:
            return 'image'
        elif 'video' in data:
            return 'video'
        elif 'document' in data:
            return 'document'
        elif 'template' in data:
            return 'template'
        elif 'interactive' in data:
            return 'interactive'
        elif 'message' in data:  # Fallback para mensaje de texto simple
            return 'text'
        else:
            return 'text'
    
    def _save_message_to_db(self, payload: dict, whatsapp_response: dict):
        """Guarda el mensaje enviado en la base de datos"""
        message_data = {
            'whatsapp_message_id': whatsapp_response.get('messages', [{}])[0].get('id'),
            'phone_number': payload.get('to'),
            'message_type': payload.get('type'),
            'content': payload,
            'status': 'sent',
            'direction': 'outbound'
        }
        
        self.msg_repo.save_message(message_data)
    
    def get_message_status(self, message_id: str) -> dict:
        """Obtiene el estado actual de un mensaje"""
        return self.msg_repo.get_message_by_whatsapp_id(message_id)
```

## Message Templates Management
<!-- Gestión de plantillas de mensajes -->

### Template Categories
- Marketing messages
- Utility messages  
- Authentication messages

### Template Approval Process
- Submit template for review
- Handle approval/rejection
- Manage template versioning
- Template performance analytics

## Multi-Line Management API
<!-- API para gestión de líneas múltiples -->

### Lines Controller
```python
# app/api/lines.py
from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource, fields
from app.services.line_service import LineService
from app.utils.auth import require_api_key
from app.utils.validators import validate_json

lines_bp = Blueprint('lines', __name__)
api = Namespace('lines', description='Gestión de líneas de mensajería')

# Modelos para Swagger
line_model = api.model('MessagingLine', {
    'line_id': fields.String(required=True, description='ID único de la línea'),
    'phone_number_id': fields.String(required=True, description='ID del número en WhatsApp Business'),
    'display_name': fields.String(required=True, description='Nombre de la línea'),
    'phone_number': fields.String(description='Número de teléfono'),
    'webhook_url': fields.String(description='URL del webhook'),
    'is_active': fields.Boolean(description='Si la línea está activa'),
    'max_daily_messages': fields.Integer(description='Límite diario de mensajes')
})

line_stats_model = api.model('LineStats', {
    'line_id': fields.String(description='ID de la línea'),
    'display_name': fields.String(description='Nombre de la línea'),
    'current_daily_count': fields.Integer(description='Mensajes enviados hoy'),
    'max_daily_messages': fields.Integer(description='Límite diario'),
    'usage_percentage': fields.Float(description='Porcentaje de uso'),
    'is_active': fields.Boolean(description='Si está activa'),
    'last_reset_date': fields.String(description='Última fecha de reinicio')
})

@api.route('/')
class LinesResource(Resource):
    """Gestión de líneas de mensajería"""
    
    @api.marshal_list_with(line_model)
    @require_api_key
    def get(self):
        """Lista todas las líneas de mensajería"""
        line_service = LineService()
        return line_service.get_all_lines()
    
    @api.expect(line_model)
    @api.marshal_with(line_model)
    @require_api_key
    @validate_json
    def post(self):
        """Crea una nueva línea de mensajería"""
        line_service = LineService()
        return line_service.create_line(request.json)

@api.route('/<string:line_id>')
class LineResource(Resource):
    """Gestión de línea específica"""
    
    @api.marshal_with(line_model)
    @require_api_key
    def get(self, line_id):
        """Obtiene información de una línea específica"""
        line_service = LineService()
        return line_service.get_line(line_id)
    
    @api.expect(line_model)
    @api.marshal_with(line_model)
    @require_api_key
    @validate_json
    def put(self, line_id):
        """Actualiza configuración de una línea"""
        line_service = LineService()
        return line_service.update_line(line_id, request.json)
    
    @require_api_key
    def delete(self, line_id):
        """Desactiva una línea de mensajería"""
        line_service = LineService()
        line_service.deactivate_line(line_id)
        return {'message': 'Línea desactivada correctamente'}, 200

@api.route('/<string:line_id>/stats')
class LineStatsResource(Resource):
    """Estadísticas de línea"""
    
    @api.marshal_with(line_stats_model)
    @require_api_key
    def get(self, line_id):
        """Obtiene estadísticas de uso de una línea"""
        line_service = LineService()
        return line_service.get_line_stats(line_id)
```

### Line Service
```python
# app/services/line_service.py
from database.models import MessagingLine, Message
from flask import current_app
from datetime import date

class LineService:
    """Servicio para gestión de líneas de mensajería"""
    
    def get_all_lines(self):
        """Obtiene todas las líneas de mensajería"""
        return MessagingLine.query.all()
    
    def get_line(self, line_id):
        """Obtiene una línea específica"""
        line = MessagingLine.query.filter_by(line_id=line_id).first()
        if not line:
            raise ValueError(f"Línea {line_id} no encontrada")
        return line
    
    def create_line(self, data):
        """Crea una nueva línea de mensajería"""
        line = MessagingLine(
            line_id=data['line_id'],
            phone_number_id=data['phone_number_id'],
            display_name=data['display_name'],
            phone_number=data.get('phone_number'),
            webhook_url=data.get('webhook_url'),
            max_daily_messages=data.get('max_daily_messages', 1000)
        )
        return line.save()
    
    def update_line(self, line_id, data):
        """Actualiza configuración de una línea"""
        line = self.get_line(line_id)
        
        if 'display_name' in data:
            line.display_name = data['display_name']
        if 'webhook_url' in data:
            line.webhook_url = data['webhook_url']
        if 'max_daily_messages' in data:
            line.max_daily_messages = data['max_daily_messages']
        if 'is_active' in data:
            line.is_active = data['is_active']
            
        return line.save()
    
    def deactivate_line(self, line_id):
        """Desactiva una línea de mensajería"""
        line = self.get_line(line_id)
        line.is_active = False
        line.save()
    
    def get_line_stats(self, line_id):
        """Obtiene estadísticas de uso de una línea"""
        line = self.get_line(line_id)
        line.reset_daily_counter_if_needed()
        
        usage_percentage = (line.current_daily_count / line.max_daily_messages) * 100
        
        return {
            'line_id': line.line_id,
            'display_name': line.display_name,
            'current_daily_count': line.current_daily_count,
            'max_daily_messages': line.max_daily_messages,
            'usage_percentage': round(usage_percentage, 2),
            'is_active': line.is_active,
            'last_reset_date': line.last_reset_date.isoformat()
        }
```
