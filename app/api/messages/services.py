"""
Servicios de negocio para manejo de mensajes de WhatsApp
Implementa la lógica de negocio separada de los endpoints REST
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
import logging

from app.repositories.base_repo import MessageRepository, MessagingLineRepository
from app.private.validators import validate_phone_number, validate_message_content, sanitize_message_content
from app.utils.exceptions import (
    ValidationError, MessageSendError, LineNotFoundError, 
    MessageNotFoundError, WhatsAppAPIError
)
from app.utils.helpers import create_success_response, create_error_response, paginate_results
from config.default import DefaultConfig

class MessageService:
    """
    Servicio principal para manejo de mensajes de WhatsApp
    Gestiona el envío, recepción y consulta de mensajes
    """
    
    def __init__(self):
        """
        Inicializa el servicio de mensajes
        """
        self.msg_repo = MessageRepository()
        self.line_repo = MessagingLineRepository()
        self.logger = logging.getLogger('whatsapp_api.services.message')
    
    def send_text_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a través de WhatsApp
        Args:
            message_data: Datos del mensaje a enviar
        Returns:
            dict: Respuesta con información del mensaje enviado
        """
        try:
            # Validar datos de entrada
            phone_number = message_data.get('to')
            content = message_data.get('text')
            line_id = message_data.get('line_id')

            print('hola')
            
            if not validate_phone_number(phone_number):
                raise ValidationError("Formato de número de teléfono inválido")
            
            is_valid, error_msg = validate_message_content('text', content)
            if not is_valid:
                raise ValidationError(f"Contenido de mensaje inválido: {error_msg}")
            
            # Sanitizar contenido
            clean_content = sanitize_message_content(content)
            
            # Obtener línea de mensajería
            messaging_line = self._get_available_line(line_id)
            
            # Simular envío a WhatsApp API (por ahora crear mensaje local)
            whatsapp_message_id = self._simulate_whatsapp_send(
                phone_number, clean_content, messaging_line.line_id
            )
            
            # Crear registro en base de datos
            message_record = self.msg_repo.create(
                whatsapp_message_id=whatsapp_message_id,
                line_id=messaging_line.line_id,
                phone_number=phone_number,
                message_type='text',
                content=clean_content,
                status='sent',  # En implementación real sería 'pending'
                direction='outbound'
            )
            
            # Incrementar contador de la línea
            messaging_line.increment_message_count()
            
            # Formatear respuesta
            response_data = self._format_message_response(message_record)
            
            self.logger.info(f"Mensaje de texto enviado exitosamente: {whatsapp_message_id}")
            return create_success_response(
                data=response_data,
                message="Mensaje de texto enviado exitosamente"
            )
            
        except (ValidationError, LineNotFoundError) as e:
            self.logger.warning(f"Error de validación enviando mensaje: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error inesperado enviando mensaje: {e}")
            raise MessageSendError(f"Error al enviar mensaje: {str(e)}")
    
    def get_messages(self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Obtiene lista de mensajes con filtros y paginación
        Args:
            filters: Filtros a aplicar
            page: Número de página
            per_page: Elementos por página
        Returns:
            dict: Lista paginada de mensajes
        """
        try:
            # Validar parámetros de paginación
            page = max(1, page)
            per_page = max(1, min(per_page, 100))  # Máximo 100 por página
            
            # Aplicar filtros básicos si se proporcionan
            query_filters = {}
            if filters:
                if filters.get('phone_number'):
                    if not validate_phone_number(filters['phone_number']):
                        raise ValidationError("Formato de número de teléfono inválido en filtros")
                    query_filters['phone_number'] = filters['phone_number']
                
                if filters.get('status'):
                    query_filters['status'] = filters['status']
                
                if filters.get('message_type'):
                    query_filters['message_type'] = filters['message_type']
                
                if filters.get('line_id'):
                    query_filters['line_id'] = filters['line_id']
                
                if filters.get('direction'):
                    query_filters['direction'] = filters['direction']
            
            # Obtener mensajes filtrados
            if query_filters:
                messages = self.msg_repo.find_by(**query_filters)
            else:
                messages = self.msg_repo.get_all()
            
            # Ordenar por fecha de creación (más recientes primero)
            messages.sort(key=lambda x: x.created_at, reverse=True)
            
            # Aplicar paginación
            paginated_result = paginate_results(
                [self._format_message_response(msg) for msg in messages],
                page=page,
                per_page=per_page
            )
            
            # Formatear respuesta
            response_data = {
                'messages': paginated_result['items'],
                'pagination': paginated_result['pagination']
            }
            
            self.logger.info(f"Obtenidos {len(paginated_result['items'])} mensajes (página {page})")
            return create_success_response(
                data=response_data,
                message=f"Mensajes obtenidos exitosamente"
            )
            
        except ValidationError as e:
            self.logger.warning(f"Error de validación obteniendo mensajes: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error obteniendo mensajes: {e}")
            raise WhatsAppAPIError(f"Error al obtener mensajes: {str(e)}")
    
    def get_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """
        Obtiene un mensaje específico por su ID
        Args:
            message_id: ID del mensaje
        Returns:
            dict: Datos del mensaje
        """
        try:
            # Buscar mensaje por ID
            message = self.msg_repo.get_by_id(message_id)
            
            if not message:
                raise MessageNotFoundError(message_id)
            
            # Formatear respuesta
            response_data = self._format_message_response(message)
            
            self.logger.info(f"Mensaje obtenido por ID: {message_id}")
            return create_success_response(
                data=response_data,
                message="Mensaje encontrado exitosamente"
            )
            
        except MessageNotFoundError as e:
            self.logger.warning(f"Mensaje no encontrado: {message_id}")
            raise e
        except Exception as e:
            self.logger.error(f"Error obteniendo mensaje por ID {message_id}: {e}")
            raise WhatsAppAPIError(f"Error al obtener mensaje: {str(e)}")
    
    def get_message_by_whatsapp_id(self, whatsapp_message_id: str) -> Dict[str, Any]:
        """
        Obtiene un mensaje por su ID de WhatsApp
        Args:
            whatsapp_message_id: ID del mensaje en WhatsApp
        Returns:
            dict: Datos del mensaje
        """
        try:
            message = self.msg_repo.get_by_whatsapp_id(whatsapp_message_id)
            
            if not message:
                raise MessageNotFoundError(whatsapp_message_id)
            
            response_data = self._format_message_response(message)
            
            self.logger.info(f"Mensaje obtenido por WhatsApp ID: {whatsapp_message_id}")
            return create_success_response(
                data=response_data,
                message="Mensaje encontrado exitosamente"
            )
            
        except MessageNotFoundError as e:
            self.logger.warning(f"Mensaje no encontrado por WhatsApp ID: {whatsapp_message_id}")
            raise e
        except Exception as e:
            self.logger.error(f"Error obteniendo mensaje por WhatsApp ID {whatsapp_message_id}: {e}")
            raise WhatsAppAPIError(f"Error al obtener mensaje: {str(e)}")
    
    def update_message_status(self, whatsapp_message_id: str, new_status: str) -> Dict[str, Any]:
        """
        Actualiza el estado de un mensaje
        Args:
            whatsapp_message_id: ID del mensaje en WhatsApp
            new_status: Nuevo estado
        Returns:
            dict: Respuesta de actualización
        """
        try:
            # Validar estado
            valid_statuses = ['pending', 'sent', 'delivered', 'read', 'failed']
            if new_status not in valid_statuses:
                raise ValidationError(f"Estado inválido: {new_status}. Estados válidos: {valid_statuses}")
            
            # Actualizar estado
            success = self.msg_repo.update_status(whatsapp_message_id, new_status)
            
            if not success:
                raise MessageNotFoundError(whatsapp_message_id)
            
            self.logger.info(f"Estado de mensaje actualizado: {whatsapp_message_id} -> {new_status}")
            return create_success_response(
                message=f"Estado del mensaje actualizado a: {new_status}"
            )
            
        except (ValidationError, MessageNotFoundError) as e:
            self.logger.warning(f"Error actualizando estado de mensaje: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error actualizando estado de mensaje {whatsapp_message_id}: {e}")
            raise WhatsAppAPIError(f"Error al actualizar mensaje: {str(e)}")
    
    def _get_available_line(self, line_id: Optional[str] = None) -> Any:
        """
        Obtiene una línea de mensajería disponible
        Args:
            line_id: ID específico de línea (opcional)
        Returns:
            MessagingLine: Línea disponible
        """
        if line_id:
            # Buscar línea específica
            line = self.line_repo.get_by_line_id(line_id)
            if not line:
                raise LineNotFoundError(line_id)
            if not line.can_send_message():
                raise MessageSendError(f"Línea {line_id} sin capacidad disponible")
            return line
        else:
            # Buscar línea con capacidad disponible
            line = self.line_repo.get_line_with_capacity()
            if not line:
                # Crear línea por defecto si no existe ninguna
                default_line_id = DefaultConfig.get_line_config()['id']
                line = self._ensure_default_line_exists(default_line_id)
            return line
    
    def _ensure_default_line_exists(self, line_id: str) -> Any:
        """
        Asegura que exista una línea por defecto
        Args:
            line_id: ID de la línea por defecto
        Returns:
            MessagingLine: Línea creada o existente
        """
        line = self.line_repo.get_by_line_id(line_id)
        if not line:
            # Crear línea por defecto
            line_config = DefaultConfig.get_line_config(line_id)
            line = self.line_repo.create(
                line_id=line_id,
                phone_number_id=line_config.get('phone_number_id', 'demo-phone-id'),
                display_name=line_config.get('display_name', 'Línea de Prueba'),
                phone_number=line_config.get('phone_number', '+1234567890'),
                is_active=True,
                max_daily_messages=1000
            )
            self.logger.info(f"Línea por defecto creada: {line_id}")
        return line
    
    def _simulate_whatsapp_send(self, phone_number: str, content: str, line_id: str) -> str:
        """
        Simula el envío a WhatsApp API (para pruebas)
        En implementación real, aquí se haría la llamada a Graph API
        Args:
            phone_number: Número destino
            content: Contenido del mensaje
            line_id: ID de la línea
        Returns:
            str: ID simulado del mensaje de WhatsApp
        """
        # Generar ID simulado de WhatsApp
        timestamp = int(datetime.now(timezone.utc).timestamp())
        simulated_id = f"wamid.test_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        # Log de simulación
        self.logger.info(f"[SIMULADO] Mensaje enviado a {phone_number} desde {line_id}: {content[:50]}...")
        
        return simulated_id
    
    def _format_message_response(self, message) -> Dict[str, Any]:
        """
        Formatea un mensaje para respuesta de API
        Args:
            message: Instancia del modelo Message
        Returns:
            dict: Mensaje formateado
        """
        return {
            'id': str(message.id),
            'whatsapp_message_id': message.whatsapp_message_id,
            'phone_number': message.phone_number,
            'message_type': message.message_type,
            'content': message.content,
            'status': message.status,
            'direction': message.direction,
            'line_id': message.line_id,
            'created_at': message.created_at.isoformat() + 'Z',
            'updated_at': message.updated_at.isoformat() + 'Z',
            'retry_count': message.retry_count,
            'error_message': message.error_message
        }
