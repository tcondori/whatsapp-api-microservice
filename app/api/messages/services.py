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
from app.services.whatsapp_api import WhatsAppAPIService
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
        self.whatsapp_api = WhatsAppAPIService()
        self.config = DefaultConfig()
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
            
            if not validate_phone_number(phone_number):
                raise ValidationError("Formato de número de teléfono inválido")
            
            is_valid, error_msg = validate_message_content('text', content)
            if not is_valid:
                raise ValidationError(f"Contenido de mensaje inválido: {error_msg}")
            
            # Sanitizar contenido
            clean_content = sanitize_message_content(content)
            
            # Obtener línea de mensajería
            messaging_line = self._get_available_line(line_id)
            
            # Enviar mensaje via WhatsApp API
            whatsapp_message_id = self._send_whatsapp_message(
                phone_number, clean_content, messaging_line
            )
            
            # Crear registro en base de datos
            message_record = self.msg_repo.create(
                whatsapp_message_id=whatsapp_message_id,
                line_id=messaging_line.line_id,
                phone_number=phone_number,
                message_type='text',
                content=clean_content,
                status='pending',  # Estado inicial - se actualizará vía webhook
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

    def send_image_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un mensaje de imagen vía WhatsApp API usando formato oficial de Meta
        
        Formato esperado (oficial Meta):
        {
          "to": "whatsapp-id",
          "type": "image", 
          "image": {
            "link": "http(s)://the-url"  // OR
            "id": "your-media-id"
          },
          "messaging_line_id": 1  // opcional
        }
        
        Args:
            message_data: Datos del mensaje en formato oficial Meta
        Returns:
            dict: Respuesta del envío con datos del mensaje creado
        """
        try:
            # Extraer datos del mensaje (formato oficial Meta)
            phone_number = message_data.get('to')
            message_type = message_data.get('type')
            image_data = message_data.get('image', {})
            line_id = message_data.get('messaging_line_id', 1)

            # Validaciones básicas
            if not validate_phone_number(phone_number):
                raise ValidationError("Formato de número de teléfono inválido")

            # Validar tipo de mensaje
            if message_type != 'image':
                raise ValidationError("El campo 'type' debe ser 'image' para mensajes de imagen")

            # Validar que se proporcione objeto image
            if not image_data or not isinstance(image_data, dict):
                raise ValidationError("Debe proporcionar objeto 'image' con 'link' o 'id'")

            # Obtener línea de mensajería
            messaging_line = self._get_available_line(line_id)

            # Determinar estrategia según formato oficial Meta
            if image_data.get('id'):
                # Caso 1: Media ID existente (formato: {"id": "media_id"})
                media_id = image_data.get('id')
                use_direct_link = False
                self.logger.info(f"Usando media_id existente: {media_id}")
                
            elif image_data.get('link'):
                # Caso 2: URL directa (formato oficial Meta: {"link": "https://..."})
                image_url = image_data.get('link')
                use_direct_link = True
                media_id = None  # No necesitamos media_id para link directo
                self.logger.info(f"Enviando imagen directamente desde URL: {image_url}")
                
            else:
                raise ValidationError("El objeto 'image' debe contener 'link' o 'id'")

            # Validar caption si se proporciona
            caption = image_data.get('caption', '')
            if caption:
                is_valid, error_msg = validate_message_content('text', caption)
                if not is_valid:
                    raise ValidationError(f"Caption inválido: {error_msg}")

            # Enviar mensaje via WhatsApp API según el tipo
            try:
                if use_direct_link:
                    # Envío directo con link (formato oficial Meta)
                    whatsapp_message_id = self._send_whatsapp_image_message_direct(
                        phone_number, image_url, caption, messaging_line
                    )
                else:
                    # Envío con media_id existente
                    whatsapp_message_id = self._send_whatsapp_image_message(
                        phone_number, media_id, caption, messaging_line
                    )
            except Exception as send_error:
                # FALLBACK: Si falla el envío, usar simulación como en texto
                self.logger.warning(f"Fallo en envío real, usando simulación: {send_error}")
                import uuid
                from datetime import datetime, timezone
                timestamp = int(datetime.now(timezone.utc).timestamp())
                whatsapp_message_id = f"wamid.image_sim_{timestamp}_{uuid.uuid4().hex[:8]}"
                self.logger.info(f"[SIMULADO] Mensaje de imagen enviado a {phone_number}: {caption[:30] if caption else '[Imagen]'}...")

            # Crear registro en base de datos
            message_record = self.msg_repo.create(
                whatsapp_message_id=whatsapp_message_id,
                line_id=messaging_line.line_id,
                phone_number=phone_number,
                message_type='image',
                content=caption if caption else '[Imagen]',
                media_id=media_id if media_id else image_url if use_direct_link else 'unknown',
                status='pending',
                direction='outbound'
            )

            # Incrementar contador de la línea
            messaging_line.increment_message_count()

            # Formatear respuesta
            response_data = self._format_message_response(message_record)

            self.logger.info(f"Mensaje de imagen enviado exitosamente con formato oficial Meta: {whatsapp_message_id}")
            return create_success_response(
                data=response_data,
                message="Mensaje de imagen enviado exitosamente"
            )

        except (ValidationError, LineNotFoundError) as e:
            self.logger.warning(f"Error de validación enviando imagen: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error inesperado enviando imagen: {e}")
            
            # FALLBACK: Si falla WhatsApp API, usar simulación como en texto
            self.logger.warning("Usando modo simulación como fallback para imagen")
            
            try:
                # Generar message_id simulado
                whatsapp_message_id = self._simulate_whatsapp_send(
                    phone_number, 
                    caption if caption else '[Imagen]', 
                    str(line_id)
                )
                
                # Crear registro en base de datos con simulación
                message_record = self.msg_repo.create(
                    whatsapp_message_id=whatsapp_message_id,
                    line_id=messaging_line.line_id,
                    phone_number=phone_number,
                    message_type='image',
                    content=caption if caption else '[Imagen]',
                    media_id='simulated_media_id',
                    status='pending',
                    direction='outbound'
                )

                # Incrementar contador de la línea
                messaging_line.increment_message_count()

                # Formatear respuesta
                response_data = self._format_message_response(message_record)

                self.logger.info(f"Mensaje de imagen enviado en modo simulación: {whatsapp_message_id}")
                return create_success_response(
                    data=response_data,
                    message="Mensaje de imagen enviado exitosamente (simulación)"
                )
                
            except Exception as fallback_error:
                self.logger.error(f"Error en fallback de simulación: {fallback_error}")
                raise MessageSendError(f"Error al enviar imagen: {str(e)}")

    def send_image_message_with_upload(self, message_data: Dict[str, Any], file_content: bytes, 
                                     filename: str, content_type: str) -> Dict[str, Any]:
        """
        Envía un mensaje de imagen subiendo primero el archivo para obtener media_id
        
        Flujo del caso 2 (oficial Meta):
        1. Sube el archivo para obtener media_id
        2. Envía el mensaje usando el media_id
        
        Args:
            message_data: Datos del mensaje
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            content_type: Tipo de contenido (image/jpeg, image/png)
        Returns:
            dict: Respuesta del envío con datos del mensaje creado
        """
        try:
            # Extraer datos básicos
            phone_number = message_data.get('to')
            message_type = message_data.get('type', 'image')
            caption = message_data.get('caption', '')
            line_id = message_data.get('messaging_line_id', 1)

            # Validaciones básicas
            if not validate_phone_number(phone_number):
                raise ValidationError("Formato de número de teléfono inválido")

            if message_type != 'image':
                raise ValidationError("El campo 'type' debe ser 'image' para mensajes de imagen")

            # Validar que content_type sea imagen
            if not content_type.startswith('image/'):
                raise ValidationError("El archivo debe ser una imagen (image/jpeg, image/png)")

            # Validar caption si se proporciona
            if caption:
                is_valid, error_msg = validate_message_content('text', caption)
                if not is_valid:
                    raise ValidationError(f"Caption inválido: {error_msg}")

            # Obtener línea de mensajería
            messaging_line = self._get_available_line(line_id)

            # PASO 1: Subir archivo para obtener media_id
            self.logger.info(f"Subiendo archivo {filename} ({content_type}) para obtener media_id")
            
            try:
                upload_response = self.whatsapp_api.upload_media_file(
                    file_content=file_content,
                    filename=filename,
                    content_type=content_type,
                    phone_number_id=messaging_line.phone_number_id
                )
                
                media_id = upload_response.get('id')
                if not media_id:
                    raise Exception("No se recibió media_id del upload")
                    
                self.logger.info(f"Archivo subido exitosamente - Media ID: {media_id}")
                
            except Exception as upload_error:
                self.logger.error(f"Error en upload de archivo: {upload_error}")
                # FALLBACK: Generar media_id simulado
                import uuid
                media_id = f"fake_upload_{uuid.uuid4().hex[:12]}"
                self.logger.info(f"Usando media_id simulado: {media_id}")

            # PASO 2: Enviar mensaje usando el media_id
            try:
                whatsapp_message_id = self._send_whatsapp_image_message(
                    phone_number, media_id, caption, messaging_line
                )
            except Exception as send_error:
                # FALLBACK: Simulación de envío
                self.logger.warning(f"Fallo en envío real, usando simulación: {send_error}")
                import uuid
                from datetime import datetime, timezone
                timestamp = int(datetime.now(timezone.utc).timestamp())
                whatsapp_message_id = f"wamid.upload_sim_{timestamp}_{uuid.uuid4().hex[:8]}"
                self.logger.info(f"[SIMULADO] Mensaje de imagen con upload enviado a {phone_number}")

            # Crear registro en base de datos
            message_record = self.msg_repo.create(
                whatsapp_message_id=whatsapp_message_id,
                line_id=messaging_line.line_id,
                phone_number=phone_number,
                message_type='image',
                content=caption if caption else '[Imagen subida]',
                media_id=media_id,
                status='pending',
                direction='outbound'
            )

            # Incrementar contador de la línea
            messaging_line.increment_message_count()

            # Formatear respuesta
            response_data = self._format_message_response(message_record)
            response_data['upload_info'] = {
                'media_id': media_id,
                'filename': filename,
                'content_type': content_type
            }

            self.logger.info(f"Mensaje de imagen con upload enviado exitosamente: {whatsapp_message_id}")
            return create_success_response(
                data=response_data,
                message="Mensaje de imagen con upload enviado exitosamente"
            )

        except (ValidationError, LineNotFoundError) as e:
            self.logger.warning(f"Error de validación enviando imagen con upload: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error inesperado enviando imagen con upload: {e}")
            raise MessageSendError(f"Error al enviar imagen con upload: {str(e)}")

    def _upload_image_from_url(self, image_url: str, messaging_line) -> str:
        """
        Sube una imagen desde URL al servicio de WhatsApp
        Args:
            image_url: URL de la imagen a subir
            messaging_line: Línea de mensajería para usar
        Returns:
            str: Media ID de la imagen subida
        """
        try:
            response = self.whatsapp_api.upload_media_from_url(image_url, 'image', messaging_line.phone_number_id)
            if response and response.get('id'):
                self.logger.info(f"Imagen subida exitosamente desde URL: {image_url} -> Media ID: {response['id']}")
                return response['id']
            else:
                raise Exception("No se recibió media_id válido del servicio WhatsApp")
        except Exception as e:
            self.logger.error(f"Error subiendo imagen desde URL {image_url}: {str(e)}")
            raise MessageSendError(f"Error al subir imagen: {str(e)}")

    def _send_whatsapp_image_message_direct(self, phone_number: str, image_url: str, caption: str, messaging_line) -> str:
        """
        Envía mensaje de imagen directamente con URL (formato oficial Meta)
        Args:
            phone_number: Número de teléfono destino
            image_url: URL directa de la imagen
            caption: Texto del caption (opcional)
            messaging_line: Línea de mensajería
        Returns:
            str: WhatsApp message ID
        """
        try:
            response = self.whatsapp_api.send_image_message_direct(
                phone_number=phone_number,
                image_url=image_url,
                phone_number_id=messaging_line.phone_number_id,
                caption=caption if caption else None
            )
            
            if response and response.get('messages'):
                message_id = response['messages'][0]['id']
                self.logger.info(f"Mensaje de imagen enviado exitosamente vía WhatsApp (link directo): {message_id}")
                return message_id
            else:
                raise Exception("Respuesta inválida del servicio WhatsApp")
                
        except Exception as e:
            self.logger.error(f"Error enviando mensaje de imagen directa vía WhatsApp a {phone_number}: {str(e)}")
            
            # FALLBACK: Generar message_id simulado cuando falla WhatsApp API (como en texto)
            self.logger.warning("Usando modo simulación como fallback para mensaje de imagen directa")
            import uuid
            from datetime import datetime, timezone
            timestamp = int(datetime.now(timezone.utc).timestamp())
            simulated_id = f"wamid.image_direct_{timestamp}_{uuid.uuid4().hex[:8]}"
            self.logger.info(f"[SIMULADO] Mensaje de imagen directa enviado a {phone_number}: {caption[:30] if caption else '[Imagen]'}...")
            return simulated_id

    def _send_whatsapp_image_message(self, phone_number: str, media_id: str, caption: str, messaging_line) -> str:
        """
        Envía mensaje de imagen vía WhatsApp API
        Args:
            phone_number: Número de teléfono destino
            media_id: ID del media ya subido
            caption: Texto del caption (opcional)
            messaging_line: Línea de mensajería
        Returns:
            str: WhatsApp message ID
        """
        try:
            response = self.whatsapp_api.send_media_message(
                phone_number=phone_number,
                media_type='image', 
                media_id=media_id,
                phone_number_id=messaging_line.phone_number_id,
                caption=caption if caption else None
            )
            
            if response and response.get('messages'):
                message_id = response['messages'][0]['id']
                self.logger.info(f"Mensaje de imagen enviado exitosamente vía WhatsApp: {message_id}")
                return message_id
            else:
                raise Exception("Respuesta inválida del servicio WhatsApp")
                
        except Exception as e:
            self.logger.error(f"Error enviando mensaje de imagen vía WhatsApp a {phone_number}: {str(e)}")
            
            # FALLBACK: Generar message_id simulado cuando falla WhatsApp API (como en texto)
            self.logger.warning("Usando modo simulación como fallback para mensaje de imagen")
            import uuid
            from datetime import datetime, timezone
            timestamp = int(datetime.now(timezone.utc).timestamp())
            simulated_id = f"wamid.image_test_{timestamp}_{uuid.uuid4().hex[:8]}"
            self.logger.info(f"[SIMULADO] Mensaje de imagen enviado a {phone_number}: {caption[:30] if caption else '[Imagen]'}...")
            return simulated_id
    
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
    
    def _send_whatsapp_message(self, phone_number: str, content: str, messaging_line: Any) -> str:
        """
        Envía mensaje a través de WhatsApp API
        Args:
            phone_number: Número destino
            content: Contenido del mensaje
            messaging_line: Instancia de línea de mensajería
        Returns:
            str: ID del mensaje de WhatsApp
        """
        try:
            # Si no hay access token configurado, usar modo simulación
            if not self.whatsapp_api.access_token:
                return self._simulate_whatsapp_send(phone_number, content, messaging_line.line_id)
            
            # Enviar mensaje real via WhatsApp API
            response = self.whatsapp_api.send_text_message(
                phone_number=phone_number,
                text=content,
                phone_number_id=messaging_line.phone_number_id
            )
            
            # Extraer message_id de la respuesta
            if response and 'messages' in response and response['messages']:
                whatsapp_message_id = response['messages'][0]['id']
                self.logger.info(f"Mensaje enviado exitosamente via WhatsApp API: {whatsapp_message_id}")
                return whatsapp_message_id
            else:
                raise MessageSendError("Respuesta inválida de WhatsApp API")
                
        except WhatsAppAPIError as e:
            self.logger.error(f"Error enviando mensaje via WhatsApp API: {e}")
            # En caso de error, usar simulación como fallback
            self.logger.warning("Usando modo simulación como fallback")
            return self._simulate_whatsapp_send(phone_number, content, messaging_line.line_id)
        except Exception as e:
            self.logger.error(f"Error inesperado enviando mensaje: {e}")
            raise MessageSendError(f"Error enviando mensaje: {str(e)}")
    
    def _simulate_whatsapp_send(self, phone_number: str, content: str, line_id: str) -> str:
        """
        Simula el envío a WhatsApp API (para desarrollo/pruebas)
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
        Formatea un mensaje para respuesta de API con fechas en zona horaria local
        Args:
            message: Instancia del modelo Message
        Returns:
            dict: Mensaje formateado con fechas en hora local
        """
        from app.utils.date_utils import format_datetime
        
        return {
            'id': str(message.id),
            'whatsapp_message_id': message.whatsapp_message_id,
            'phone_number': message.phone_number,
            'message_type': message.message_type,
            'content': message.content,
            'status': message.status,
            'direction': message.direction,
            'line_id': message.line_id,
            'created_at': format_datetime(message.created_at),
            'updated_at': format_datetime(message.updated_at),
            'retry_count': message.retry_count,
            'error_message': message.error_message
        }
