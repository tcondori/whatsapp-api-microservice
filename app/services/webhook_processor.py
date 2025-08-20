"""
Procesador de webhooks de WhatsApp
Maneja todos los eventos de webhook entrantes de WhatsApp Business API
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.services.whatsapp_api import WhatsAppAPIService
from app.repositories.base_repo import MessageRepository, MessagingLineRepository
from app.utils.exceptions import ValidationError, WhatsAppAPIError
from app.utils.helpers import create_success_response


class WebhookProcessor:
    """Procesador principal de webhooks de WhatsApp"""
    
    def __init__(self):
        """Inicializa el procesador de webhooks"""
        self.logger = logging.getLogger(__name__)
        self.whatsapp_api = WhatsAppAPIService()
        self.msg_repo = MessageRepository()
        self.line_repo = MessagingLineRepository()
        
        # Cache de mensajes procesados para evitar duplicados
        self._processed_messages = set()
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Procesa un webhook de WhatsApp
        Args:
            webhook_data: Datos del webhook
        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            self.logger.info(f"Procesando webhook: {json.dumps(webhook_data, indent=2)}")
            
            # Validar estructura básica del webhook
            if not self._validate_webhook_structure(webhook_data):
                self.logger.warning("Estructura de webhook inválida")
                return False
            
            # Procesar cada entrada del webhook
            for entry in webhook_data.get('entry', []):
                self._process_webhook_entry(entry)
            
            self.logger.info("Webhook procesado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error procesando webhook: {e}")
            return False
    
    def _validate_webhook_structure(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Valida la estructura básica del webhook
        Args:
            webhook_data: Datos del webhook
        Returns:
            bool: True si la estructura es válida
        """
        required_fields = ['object', 'entry']
        
        for field in required_fields:
            if field not in webhook_data:
                self.logger.error(f"Campo requerido faltante en webhook: {field}")
                return False
        
        if webhook_data['object'] != 'whatsapp_business_account':
            self.logger.error(f"Objeto de webhook inválido: {webhook_data['object']}")
            return False
        
        if not isinstance(webhook_data['entry'], list) or not webhook_data['entry']:
            self.logger.error("El campo 'entry' debe ser una lista no vacía")
            return False
        
        return True
    
    def _process_webhook_entry(self, entry: Dict[str, Any]) -> None:
        """
        Procesa una entrada individual del webhook
        Args:
            entry: Entrada del webhook
        """
        try:
            # Obtener cambios
            changes = entry.get('changes', [])
            
            for change in changes:
                field = change.get('field')
                value = change.get('value', {})
                
                if field == 'messages':
                    self._process_messages(value)
                elif field == 'message_status':
                    self._process_message_status(value)
                elif field == 'message_reactions':
                    self._process_message_reactions(value)
                elif field == 'message_template_status_update':
                    self._process_template_status(value)
                else:
                    self.logger.info(f"Tipo de webhook no manejado: {field}")
                    
        except Exception as e:
            self.logger.error(f"Error procesando entrada de webhook: {e}")
            raise
    
    def _process_messages(self, value: Dict[str, Any]) -> None:
        """
        Procesa mensajes entrantes
        Args:
            value: Datos de los mensajes
        """
        try:
            # Obtener metadatos
            metadata = value.get('metadata', {})
            phone_number_id = metadata.get('phone_number_id')
            display_name = metadata.get('display_phone_number')
            
            # Procesar mensajes
            messages = value.get('messages', [])
            
            for message in messages:
                self._process_incoming_message(message, phone_number_id, display_name)
            
            # Procesar contactos
            contacts = value.get('contacts', [])
            for contact in contacts:
                self._process_contact(contact)
                
        except Exception as e:
            self.logger.error(f"Error procesando mensajes: {e}")
            raise
    
    def _process_incoming_message(self, message: Dict[str, Any], phone_number_id: str, display_name: str) -> None:
        """
        Procesa un mensaje entrante individual
        Args:
            message: Datos del mensaje
            phone_number_id: ID del número de WhatsApp Business
            display_name: Nombre visible del número
        """
        try:
            message_id = message.get('id')
            from_number = message.get('from')
            timestamp = message.get('timestamp')
            message_type = message.get('type')
            
            # Verificar si ya procesamos este mensaje
            if message_id in self._processed_messages:
                self.logger.info(f"Mensaje {message_id} ya procesado, saltando")
                return
            
            # Extraer contenido del mensaje
            content = self._extract_message_content(message)
            
            # Buscar línea de mensajería correspondiente
            line = self._find_messaging_line_by_phone_id(phone_number_id)
            
            if not line:
                self.logger.warning(f"No se encontró línea para phone_number_id: {phone_number_id}")
                line = self._create_default_line(phone_number_id, display_name)
            
            # Guardar mensaje en base de datos
            message_record = self.msg_repo.create(
                whatsapp_message_id=message_id,
                line_id=line.line_id,
                phone_number=from_number,
                message_type=message_type,
                content=content,
                status='received',
                direction='inbound',
                timestamp=datetime.fromtimestamp(int(timestamp), timezone.utc) if timestamp else None
            )
            
            # Marcar como procesado
            self._processed_messages.add(message_id)
            
            # Marcar mensaje como leído
            try:
                self.whatsapp_api.mark_message_as_read(message_id, phone_number_id)
            except Exception as e:
                self.logger.warning(f"No se pudo marcar mensaje como leído: {e}")
            
            # Procesar lógica de negocio (respuestas automáticas, etc.)
            self._handle_business_logic(message_record, message)
            
            self.logger.info(f"Mensaje procesado exitosamente: {message_id}")
            
        except Exception as e:
            self.logger.error(f"Error procesando mensaje entrante: {e}")
            raise
    
    def _extract_message_content(self, message: Dict[str, Any]) -> str:
        """
        Extrae el contenido del mensaje según su tipo
        Args:
            message: Datos del mensaje
        Returns:
            str: Contenido extraído
        """
        message_type = message.get('type')
        
        if message_type == 'text':
            return message.get('text', {}).get('body', '')
        
        elif message_type == 'image':
            image_data = message.get('image', {})
            caption = image_data.get('caption', '')
            media_id = image_data.get('id', '')
            return f"[IMAGEN: {media_id}] {caption}".strip()
        
        elif message_type == 'video':
            video_data = message.get('video', {})
            caption = video_data.get('caption', '')
            media_id = video_data.get('id', '')
            return f"[VIDEO: {media_id}] {caption}".strip()
        
        elif message_type == 'audio':
            audio_data = message.get('audio', {})
            media_id = audio_data.get('id', '')
            return f"[AUDIO: {media_id}]"
        
        elif message_type == 'document':
            doc_data = message.get('document', {})
            filename = doc_data.get('filename', 'documento')
            media_id = doc_data.get('id', '')
            caption = doc_data.get('caption', '')
            return f"[DOCUMENTO: {filename} - {media_id}] {caption}".strip()
        
        elif message_type == 'location':
            location_data = message.get('location', {})
            lat = location_data.get('latitude')
            lon = location_data.get('longitude')
            return f"[UBICACIÓN: {lat}, {lon}]"
        
        elif message_type == 'contacts':
            contacts_data = message.get('contacts', [])
            contact_names = [c.get('name', {}).get('formatted_name', 'Contacto') for c in contacts_data]
            return f"[CONTACTOS: {', '.join(contact_names)}]"
        
        elif message_type == 'interactive':
            interactive_data = message.get('interactive', {})
            if interactive_data.get('type') == 'button_reply':
                return f"[BOTÓN: {interactive_data.get('button_reply', {}).get('title', '')}]"
            elif interactive_data.get('type') == 'list_reply':
                return f"[LISTA: {interactive_data.get('list_reply', {}).get('title', '')}]"
        
        elif message_type == 'button':
            button_data = message.get('button', {})
            return f"[BOTÓN: {button_data.get('text', '')}]"
        
        return f"[{message_type.upper()}: Tipo de mensaje no soportado]"
    
    def _process_message_status(self, value: Dict[str, Any]) -> None:
        """
        Procesa actualizaciones de estado de mensajes
        Args:
            value: Datos del estado del mensaje
        """
        try:
            statuses = value.get('statuses', [])
            
            for status in statuses:
                message_id = status.get('id')
                recipient_id = status.get('recipient_id')
                status_value = status.get('status')
                timestamp = status.get('timestamp')
                
                # Actualizar estado en base de datos
                try:
                    message = self.msg_repo.get_by_whatsapp_id(message_id)
                    if message:
                        self.msg_repo.update_status(message.id, status_value)
                        self.logger.info(f"Estado de mensaje actualizado: {message_id} -> {status_value}")
                    else:
                        self.logger.warning(f"Mensaje no encontrado para actualizar estado: {message_id}")
                
                except Exception as e:
                    self.logger.error(f"Error actualizando estado de mensaje {message_id}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error procesando estados de mensaje: {e}")
            raise
    
    def _process_message_reactions(self, value: Dict[str, Any]) -> None:
        """
        Procesa reacciones a mensajes
        Args:
            value: Datos de las reacciones
        """
        try:
            self.logger.info(f"Procesando reacciones: {json.dumps(value, indent=2)}")
            # Implementar lógica de reacciones según necesidad
        except Exception as e:
            self.logger.error(f"Error procesando reacciones: {e}")
            raise
    
    def _process_template_status(self, value: Dict[str, Any]) -> None:
        """
        Procesa actualizaciones de estado de plantillas
        Args:
            value: Datos del estado de plantilla
        """
        try:
            self.logger.info(f"Procesando estado de plantilla: {json.dumps(value, indent=2)}")
            # Implementar lógica de plantillas según necesidad
        except Exception as e:
            self.logger.error(f"Error procesando estado de plantilla: {e}")
            raise
    
    def _process_contact(self, contact: Dict[str, Any]) -> None:
        """
        Procesa información de contacto
        Args:
            contact: Datos del contacto
        """
        try:
            wa_id = contact.get('wa_id')
            profile = contact.get('profile', {})
            name = profile.get('name', '')
            
            self.logger.info(f"Contacto procesado: {wa_id} - {name}")
            # Implementar lógica de contactos según necesidad
            
        except Exception as e:
            self.logger.error(f"Error procesando contacto: {e}")
            raise
    
    def _find_messaging_line_by_phone_id(self, phone_number_id: str) -> Optional[Any]:
        """
        Busca una línea de mensajería por phone_number_id
        Args:
            phone_number_id: ID del número de teléfono
        Returns:
            Línea de mensajería o None
        """
        try:
            return self.line_repo.get_by_phone_number_id(phone_number_id)
        except Exception as e:
            self.logger.error(f"Error buscando línea por phone_number_id {phone_number_id}: {e}")
            return None
    
    def _create_default_line(self, phone_number_id: str, display_name: str) -> Any:
        """
        Crea una línea de mensajería por defecto
        Args:
            phone_number_id: ID del número de teléfono
            display_name: Nombre visible
        Returns:
            Nueva línea de mensajería
        """
        try:
            # Generar line_id único
            line_id = f"line_auto_{phone_number_id}"
            
            line = self.line_repo.create(
                line_id=line_id,
                phone_number_id=phone_number_id,
                display_name=display_name or f"Línea {phone_number_id}",
                phone_number="",
                is_active=True,
                max_daily_messages=1000
            )
            
            self.logger.info(f"Línea de mensajería creada automáticamente: {line_id}")
            return line
            
        except Exception as e:
            self.logger.error(f"Error creando línea por defecto: {e}")
            raise
    
    def _handle_business_logic(self, message_record: Any, webhook_message: Dict[str, Any]) -> None:
        """
        Maneja la lógica de negocio para mensajes entrantes
        Args:
            message_record: Registro del mensaje en BD
            webhook_message: Datos del mensaje del webhook
        """
        try:
            # Aquí puedes implementar lógica de negocio específica:
            # - Respuestas automáticas
            # - Enrutamiento a agentes
            # - Integración con chatbots
            # - Procesamiento de comandos
            
            message_text = message_record.content.lower()
            
            # Ejemplo: respuesta automática a saludo
            if any(greeting in message_text for greeting in ['hola', 'hello', 'hi', 'buenos días']):
                self._send_auto_reply(
                    message_record.phone_number,
                    message_record.line_id,
                    "¡Hola! Gracias por contactarnos. ¿En qué podemos ayudarte?"
                )
            
            # Ejemplo: respuesta a comando de ayuda
            elif 'ayuda' in message_text or 'help' in message_text:
                self._send_auto_reply(
                    message_record.phone_number,
                    message_record.line_id,
                    "Comandos disponibles:\n- /info: Información del servicio\n- /contacto: Información de contacto"
                )
            
            self.logger.info(f"Lógica de negocio procesada para mensaje: {message_record.whatsapp_message_id}")
            
        except Exception as e:
            self.logger.error(f"Error en lógica de negocio: {e}")
            # No re-lanzar la excepción para no fallar el procesamiento del webhook
    
    def _send_auto_reply(self, phone_number: str, line_id: str, text: str) -> None:
        """
        Envía una respuesta automática
        Args:
            phone_number: Número de destino
            line_id: ID de la línea
            text: Texto de la respuesta
        """
        try:
            # Obtener configuración de la línea
            line = self.line_repo.get_by_line_id(line_id)
            if not line or not line.phone_number_id:
                self.logger.warning(f"No se puede enviar respuesta automática: línea {line_id} no válida")
                return
            
            # Enviar mensaje vía WhatsApp API
            response = self.whatsapp_api.send_text_message(
                phone_number=phone_number,
                text=text,
                phone_number_id=line.phone_number_id
            )
            
            # Guardar respuesta automática en BD
            if response and 'messages' in response:
                whatsapp_message_id = response['messages'][0]['id']
                
                self.msg_repo.create(
                    whatsapp_message_id=whatsapp_message_id,
                    line_id=line_id,
                    phone_number=phone_number,
                    message_type='text',
                    content=text,
                    status='sent',
                    direction='outbound'
                )
                
            self.logger.info(f"Respuesta automática enviada a {phone_number}")
            
        except Exception as e:
            self.logger.error(f"Error enviando respuesta automática: {e}")
