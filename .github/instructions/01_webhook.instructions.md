# Webhook Instructions
<!-- Instrucciones para manejo completo de webhooks de WhatsApp -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar el sistema completo de webhooks de WhatsApp con soporte multi-línea, incluyendo:
- Verificación de webhooks y validación de firmas de seguridad
- Procesamiento de todos los tipos de eventos (mensajes, estados, reacciones)
- Manejo de múltiples líneas de mensajería con identificación automática
- Procesamiento asíncrono con Celery para alto rendimiento
- Gestión de errores, reintentos y logging estructurado
- Endpoints específicos por línea y webhook unificado
-->

## Multi-Line Webhook Processing
<!-- Procesamiento de webhooks para múltiples líneas -->

### Webhook Route Identification
```python
def identify_webhook_line(webhook_payload):
    """
    Identifica qué línea de mensajería corresponde al webhook
    Args:
        webhook_payload: Payload del webhook
    Returns:
        str: line_id de la línea correspondiente
    """
    # WhatsApp incluye el phone_number_id en los webhooks
    phone_number_id = webhook_payload.get('entry', [{}])[0].get('id')
    
    if not phone_number_id:
        return None
    
    # Buscar línea por phone_number_id
    from database.models import MessagingLine
    line = MessagingLine.query.filter_by(
        phone_number_id=phone_number_id,
        is_active=True
    ).first()
    
    return line.line_id if line else None
```

### Multi-Line Webhook Handler
```python
from flask import Blueprint, request, current_app
from app.services.webhook_processor import WebhookProcessor

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    """
    Maneja webhooks de todas las líneas de mensajería
    GET: Verificación de webhook
    POST: Procesamiento de eventos
    """
    if request.method == 'GET':
        return verify_webhook_subscription(request)
    
    # Validar firma del webhook
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_webhook_signature(request.get_data(), signature):
        current_app.logger.warning("Firma de webhook inválida")
        return 'Unauthorized', 401
    
    payload = request.json
    
    # Identificar línea correspondiente
    line_id = identify_webhook_line(payload)
    if not line_id:
        current_app.logger.warning(f"Línea no identificada para webhook: {payload}")
        return 'OK', 200  # Responder OK para evitar reenvíos
    
    # Procesar webhook con información de línea
    processor = WebhookProcessor(line_id)
    try:
        processor.process_webhook(payload)
        return 'OK', 200
    except Exception as e:
        current_app.logger.error(f"Error procesando webhook línea {line_id}: {str(e)}")
        return 'Error', 500

@webhook_bp.route('/webhook/<string:line_id>', methods=['POST'])
def handle_line_specific_webhook(line_id):
    """
    Webhook específico para una línea (URL personalizada)
    Útil cuando se configuran webhooks específicos por línea
    """
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_webhook_signature(request.get_data(), signature):
        return 'Unauthorized', 401
    
    processor = WebhookProcessor(line_id)
    try:
        processor.process_webhook(request.json)
        return 'OK', 200
    except Exception as e:
        current_app.logger.error(f"Error en webhook línea {line_id}: {str(e)}")
        return 'Error', 500
```

## Webhook Verification
<!-- Verificación de webhooks -->

### Initial Webhook Setup
```python
def verify_webhook_subscription(request):
    """
    Verifica la suscripción inicial del webhook
    WhatsApp envía un GET request para verificar el endpoint
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        return challenge, 200
    else:
        return 'Forbidden', 403
```

### Signature Verification
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verifica la firma del webhook para autenticar que viene de WhatsApp
    Args:
        payload: Contenido del webhook en bytes
        signature: Firma del header X-Hub-Signature-256
    Returns:
        bool: True si la firma es válida
    """
    if not signature.startswith('sha256='):
        return False
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    received_signature = signature[7:]  # Remove 'sha256=' prefix
    return hmac.compare_digest(expected_signature, received_signature)
```

## Webhook Event Types
<!-- Tipos de eventos de webhook -->

### Message Events
```python
def process_message_event(message_data: dict):
    """
    Procesa eventos de mensajes entrantes
    Args:
        message_data: Datos del mensaje desde el webhook
    """
    message_type = message_data.get('type')
    
    if message_type == 'text':
        process_text_message(message_data)
    elif message_type == 'image':
        process_image_message(message_data)
    elif message_type == 'document':
        process_document_message(message_data)
    elif message_type == 'audio':
        process_audio_message(message_data)
    elif message_type == 'video':
        process_video_message(message_data)
    elif message_type == 'location':
        process_location_message(message_data)
    elif message_type == 'contacts':
        process_contact_message(message_data)
    elif message_type == 'interactive':
        process_interactive_message(message_data)
    else:
        log_unsupported_message_type(message_type, message_data)
```

### Status Update Events
```python
def process_status_event(status_data: dict):
    """
    Procesa actualizaciones de estado de mensajes
    Args:
        status_data: Datos del estado desde el webhook
    """
    message_id = status_data.get('id')
    status = status_data.get('status')
    timestamp = status_data.get('timestamp')
    recipient_id = status_data.get('recipient_id')
    
    # Estados posibles: sent, delivered, read, failed
    if status in ['sent', 'delivered', 'read']:
        update_message_status_success(message_id, status, timestamp)
    elif status == 'failed':
        error_data = status_data.get('errors', [])
        update_message_status_failed(message_id, error_data, timestamp)
```

### Message Reaction Events
```python
def process_reaction_event(reaction_data: dict):
    """
    Procesa eventos de reacciones a mensajes
    Args:
        reaction_data: Datos de la reacción desde el webhook
    """
    message_id = reaction_data.get('message_id')
    emoji = reaction_data.get('emoji')
    from_user = reaction_data.get('from')
    
    # Guardar reacción en base de datos
    save_message_reaction(message_id, from_user, emoji)
```

## Webhook Processing Pipeline
<!-- Pipeline de procesamiento de webhooks -->

### Main Webhook Handler
```python
from typing import Dict, Any
import json
import logging

class WebhookProcessor:
    """Procesador principal de webhooks de WhatsApp con soporte multi-línea"""
    
    def __init__(self, line_id=None, msg_service=None, contact_service=None, media_service=None):
        self.line_id = line_id
        self.msg_service = msg_service
        self.contact_service = contact_service
        self.media_service = media_service
        self.logger = logging.getLogger(__name__)
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Procesa webhook de WhatsApp para una línea específica
        Args:
            webhook_data: Datos del webhook
        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            # Validar estructura del webhook
            if not self._validate_webhook_structure(webhook_data):
                self.logger.error("Estructura de webhook inválida")
                return False
            
            # Procesar cada entrada del webhook
            for entry in webhook_data.get('entry', []):
                self._process_entry(entry)
            
            # Guardar evento de webhook con información de línea
            self._save_webhook_event(webhook_data, self.line_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error procesando webhook línea {self.line_id}: {e}")
            raise e
            return False
    
    def _process_entry(self, entry: Dict[str, Any]):
        """Procesa una entrada específica del webhook"""
        changes = entry.get('changes', [])
        
        for change in changes:
            field = change.get('field')
            value = change.get('value', {})
            
            if field == 'messages':
                self._process_messages(value)
            elif field == 'message_template_status_update':
                self._process_template_status(value)
    
    def _process_messages(self, value: Dict[str, Any]):
        """Procesa mensajes y estados desde el webhook"""
        # Procesar mensajes entrantes
        messages = value.get('messages', [])
        for message in messages:
            self._process_incoming_message(message)
        
        # Procesar actualizaciones de estado
        statuses = value.get('statuses', [])
        for status in statuses:
            self._process_status_update(status)
    
    def _process_incoming_message(self, message: Dict[str, Any]):
        """Procesa un mensaje entrante específico"""
        message_id = message.get('id')
        from_number = message.get('from')
        message_type = message.get('type')
        timestamp = message.get('timestamp')
        
        # Evitar procesar mensajes duplicados
        if self.msg_service.message_exists(message_id):
            self.logger.info(f"Mensaje {message_id} ya procesado")
            return
        
        # Guardar mensaje en base de datos
        self.msg_service.save_incoming_message({
            'whatsapp_message_id': message_id,
            'phone_number': from_number,
            'message_type': message_type,
            'content': self._extract_message_content(message),
            'timestamp': timestamp,
            'direction': 'inbound'
        })
        
        # Procesar lógica de negocio específica
        self._handle_business_logic(message)
```

### Message Content Extraction
```python
def _extract_message_content(self, message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae el contenido específico según el tipo de mensaje
    Args:
        message: Datos del mensaje
    Returns:
        dict: Contenido extraído del mensaje
    """
    message_type = message.get('type')
    
    if message_type == 'text':
        return {'text': message.get('text', {}).get('body', '')}
    
    elif message_type == 'image':
        image_data = message.get('image', {})
        return {
            'media_id': image_data.get('id'),
            'caption': image_data.get('caption', ''),
            'mime_type': image_data.get('mime_type'),
            'sha256': image_data.get('sha256')
        }
    
    elif message_type == 'document':
        doc_data = message.get('document', {})
        return {
            'media_id': doc_data.get('id'),
            'filename': doc_data.get('filename'),
            'caption': doc_data.get('caption', ''),
            'mime_type': doc_data.get('mime_type'),
            'sha256': doc_data.get('sha256')
        }
    
    elif message_type == 'location':
        location_data = message.get('location', {})
        return {
            'latitude': location_data.get('latitude'),
            'longitude': location_data.get('longitude'),
            'name': location_data.get('name', ''),
            'address': location_data.get('address', '')
        }
    
    elif message_type == 'interactive':
        interactive_data = message.get('interactive', {})
        return {
            'type': interactive_data.get('type'),
            'button_reply': interactive_data.get('button_reply'),
            'list_reply': interactive_data.get('list_reply')
        }
    
    return {}
```

## Error Handling & Retries
<!-- Manejo de errores y reintentos -->

### Retry Mechanism
```python
import time
from typing import Callable

def retry_webhook_processing(func: Callable, max_retries: int = 3, delay: int = 1):
    """
    Reintenta procesamiento de webhook en caso de error
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        delay: Delay inicial entre reintentos (exponential backoff)
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                # Último intento fallido, registrar error
                logger.error(f"Webhook processing failed after {max_retries} retries: {e}")
                raise
            
            # Exponential backoff
            wait_time = delay * (2 ** attempt)
            logger.warning(f"Webhook processing attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
```

### Dead Letter Queue
```python
def send_to_dead_letter_queue(webhook_data: Dict[str, Any], error: str):
    """
    Envía webhooks no procesables a una cola de mensajes muertos
    Args:
        webhook_data: Datos del webhook original
        error: Descripción del error
    """
    dead_letter_entry = {
        'webhook_data': webhook_data,
        'error': error,
        'timestamp': int(time.time()),
        'retry_count': 0
    }
    
    # Guardar en base de datos o sistema de colas
    save_failed_webhook(dead_letter_entry)
```

## Webhook Endpoint Implementation
<!-- Implementación del endpoint de webhook -->

```python
from flask import request, jsonify
from flask_restx import Resource, Namespace

webhook_ns = Namespace('webhooks', description='Endpoints de webhook de WhatsApp')

@webhook_ns.route('')
class WebhookEndpoint(Resource):
    """Endpoint principal para webhooks de WhatsApp"""
    
    def get(self):
        """Verificación inicial del webhook"""
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            return challenge, 200
        else:
            return {'error': 'Forbidden'}, 403
    
    def post(self):
        """Procesa webhooks de WhatsApp"""
        try:
            # Verificar firma del webhook
            signature = request.headers.get('X-Hub-Signature-256')
            if not verify_webhook_signature(request.get_data(), signature):
                return {'error': 'Invalid signature'}, 401
            
            # Obtener datos del webhook
            webhook_data = request.get_json()
            
            # Procesar webhook de forma asíncrona
            process_webhook_async.delay(webhook_data)
            
            # Respuesta inmediata a WhatsApp
            return {'status': 'received'}, 200
            
        except Exception as e:
            logger.error(f"Error en endpoint de webhook: {e}")
            return {'error': 'Internal server error'}, 500
```

## Asynchronous Processing
<!-- Procesamiento asíncrono de webhooks -->

```python
from celery import Celery

# Configurar Celery para procesamiento asíncrono
celery_app = Celery('webhook_processor')

@celery_app.task
def process_webhook_async(webhook_data: Dict[str, Any]):
    """
    Procesa webhook de forma asíncrona
    Args:
        webhook_data: Datos del webhook a procesar
    """
    processor = WebhookProcessor(msg_service, contact_service, media_service)
    
    try:
        success = processor.process_webhook(webhook_data)
        if not success:
            # Reintentar o enviar a DLQ
            raise Exception("Failed to process webhook")
            
    except Exception as e:
        # Manejar error y posible reintento
        logger.error(f"Async webhook processing failed: {e}")
        raise
```
