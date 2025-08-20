"""
Repositorio base con operaciones CRUD comunes
Proporciona funcionalidad común para todos los repositorios específicos
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.connection import db, get_db_session, safe_commit, safe_rollback
from app.utils.exceptions import DatabaseError
import logging

class BaseRepository:
    """
    Repositorio base con operaciones CRUD genéricas
    Proporciona funcionalidad común para todos los repositorios
    """
    
    def __init__(self, model_class):
        """
        Inicializa el repositorio base
        Args:
            model_class: Clase del modelo de SQLAlchemy
        """
        self.model_class = model_class
        self.logger = logging.getLogger(f'whatsapp_api.repo.{model_class.__name__.lower()}')
    
    def create(self, **kwargs) -> Optional[Any]:
        """
        Crea una nueva instancia del modelo
        Args:
            **kwargs: Campos del modelo a crear
        Returns:
            Instancia creada o None si falla
        """
        try:
            instance = self.model_class(**kwargs)
            result = instance.save()
            self.logger.info(f"Creado {self.model_class.__name__} con ID: {result.id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error creando {self.model_class.__name__}: {e}")
            raise DatabaseError(f"Error al crear {self.model_class.__name__}", "create")
    
    def get_by_id(self, id: Any) -> Optional[Any]:
        """
        Obtiene instancia por ID
        Args:
            id: ID de la instancia
        Returns:
            Instancia encontrada o None
        """
        try:
            result = self.model_class.query.get(id)
            if result:
                self.logger.debug(f"Encontrado {self.model_class.__name__} con ID: {id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo {self.model_class.__name__} por ID {id}: {e}")
            raise DatabaseError(f"Error al obtener {self.model_class.__name__}", "get_by_id")
    
    def get_all(self, limit: int = None, offset: int = None) -> List[Any]:
        """
        Obtiene todas las instancias con paginación opcional
        Args:
            limit: Límite de resultados
            offset: Offset para paginación
        Returns:
            Lista de instancias
        """
        try:
            query = self.model_class.query
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            self.logger.debug(f"Obtenidos {len(results)} {self.model_class.__name__}s")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo todos los {self.model_class.__name__}s: {e}")
            raise DatabaseError(f"Error al obtener {self.model_class.__name__}s", "get_all")
    
    def update(self, id: Any, **kwargs) -> Optional[Any]:
        """
        Actualiza una instancia por ID
        Args:
            id: ID de la instancia
            **kwargs: Campos a actualizar
        Returns:
            Instancia actualizada o None
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            
            result = instance.update(**kwargs)
            self.logger.info(f"Actualizado {self.model_class.__name__} con ID: {id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error actualizando {self.model_class.__name__} {id}: {e}")
            raise DatabaseError(f"Error al actualizar {self.model_class.__name__}", "update")
    
    def delete(self, id: Any) -> bool:
        """
        Elimina una instancia por ID
        Args:
            id: ID de la instancia
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            instance.delete()
            self.logger.info(f"Eliminado {self.model_class.__name__} con ID: {id}")
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"Error eliminando {self.model_class.__name__} {id}: {e}")
            raise DatabaseError(f"Error al eliminar {self.model_class.__name__}", "delete")
    
    def count(self, **filters) -> int:
        """
        Cuenta instancias con filtros opcionales
        Args:
            **filters: Filtros a aplicar
        Returns:
            int: Número de instancias
        """
        try:
            query = self.model_class.query
            
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)
            
            count = query.count()
            self.logger.debug(f"Contados {count} {self.model_class.__name__}s con filtros: {filters}")
            return count
        except SQLAlchemyError as e:
            self.logger.error(f"Error contando {self.model_class.__name__}s: {e}")
            raise DatabaseError(f"Error al contar {self.model_class.__name__}s", "count")
    
    def find_by(self, **filters) -> List[Any]:
        """
        Busca instancias por filtros
        Args:
            **filters: Filtros a aplicar
        Returns:
            Lista de instancias que cumplen los filtros
        """
        try:
            query = self.model_class.query
            
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)
            
            results = query.all()
            self.logger.debug(f"Encontrados {len(results)} {self.model_class.__name__}s con filtros: {filters}")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error buscando {self.model_class.__name__}s: {e}")
            raise DatabaseError(f"Error al buscar {self.model_class.__name__}s", "find_by")
    
    def exists(self, **filters) -> bool:
        """
        Verifica si existe al menos una instancia con los filtros dados
        Args:
            **filters: Filtros a aplicar
        Returns:
            bool: True si existe al menos una instancia
        """
        try:
            query = self.model_class.query
            
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)
            
            exists = query.first() is not None
            self.logger.debug(f"Existe {self.model_class.__name__} con filtros {filters}: {exists}")
            return exists
        except SQLAlchemyError as e:
            self.logger.error(f"Error verificando existencia de {self.model_class.__name__}: {e}")
            raise DatabaseError(f"Error al verificar {self.model_class.__name__}", "exists")

class MessageRepository(BaseRepository):
    """
    Repositorio específico para mensajes de WhatsApp
    Extiende BaseRepository con funcionalidad específica de mensajes
    """
    
    def __init__(self):
        from database.models import Message
        super().__init__(Message)
    
    def get_by_whatsapp_id(self, whatsapp_message_id: str) -> Optional[Any]:
        """
        Obtiene mensaje por ID de WhatsApp
        Args:
            whatsapp_message_id: ID único de WhatsApp
        Returns:
            Mensaje encontrado o None
        """
        try:
            result = self.model_class.query.filter_by(whatsapp_message_id=whatsapp_message_id).first()
            if result:
                self.logger.debug(f"Encontrado mensaje con WhatsApp ID: {whatsapp_message_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo mensaje por WhatsApp ID {whatsapp_message_id}: {e}")
            raise DatabaseError("Error al obtener mensaje por WhatsApp ID", "get_by_whatsapp_id")
    
    def get_by_phone_number(self, phone_number: str, limit: int = 50) -> List[Any]:
        """
        Obtiene mensajes por número de teléfono
        Args:
            phone_number: Número de teléfono
            limit: Límite de mensajes a retornar
        Returns:
            Lista de mensajes
        """
        try:
            results = (self.model_class.query
                      .filter_by(phone_number=phone_number)
                      .order_by(self.model_class.created_at.desc())
                      .limit(limit)
                      .all())
            
            self.logger.debug(f"Encontrados {len(results)} mensajes para {phone_number}")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo mensajes por teléfono {phone_number}: {e}")
            raise DatabaseError("Error al obtener mensajes por teléfono", "get_by_phone_number")
    
    def get_by_status(self, status: str) -> List[Any]:
        """
        Obtiene mensajes por estado
        Args:
            status: Estado de los mensajes
        Returns:
            Lista de mensajes con el estado especificado
        """
        return self.find_by(status=status)
    
    def update_status(self, whatsapp_message_id: str, new_status: str) -> bool:
        """
        Actualiza el estado de un mensaje
        Args:
            whatsapp_message_id: ID de WhatsApp del mensaje
            new_status: Nuevo estado
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            message = self.get_by_whatsapp_id(whatsapp_message_id)
            if not message:
                return False
            
            message.update(status=new_status)
            self.logger.info(f"Estado de mensaje {whatsapp_message_id} actualizado a: {new_status}")
            return True
        except Exception as e:
            self.logger.error(f"Error actualizando estado de mensaje {whatsapp_message_id}: {e}")
            return False

class ContactRepository(BaseRepository):
    """
    Repositorio específico para contactos de WhatsApp
    """
    
    def __init__(self):
        from database.models import Contact
        super().__init__(Contact)
    
    def get_by_phone_number(self, phone_number: str) -> Optional[Any]:
        """
        Obtiene contacto por número de teléfono
        Args:
            phone_number: Número de teléfono
        Returns:
            Contacto encontrado o None
        """
        try:
            result = self.model_class.query.filter_by(phone_number=phone_number).first()
            if result:
                self.logger.debug(f"Encontrado contacto: {phone_number}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo contacto {phone_number}: {e}")
            raise DatabaseError("Error al obtener contacto", "get_by_phone_number")
    
    def get_blocked_contacts(self) -> List[Any]:
        """
        Obtiene todos los contactos bloqueados
        Returns:
            Lista de contactos bloqueados
        """
        return self.find_by(is_blocked=True)
    
    def block_contact(self, phone_number: str) -> bool:
        """
        Bloquea un contacto
        Args:
            phone_number: Número a bloquear
        Returns:
            bool: True si se bloqueó exitosamente
        """
        try:
            contact = self.get_by_phone_number(phone_number)
            if contact:
                contact.update(is_blocked=True)
                self.logger.info(f"Contacto bloqueado: {phone_number}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error bloqueando contacto {phone_number}: {e}")
            return False

class WebhookRepository(BaseRepository):
    """
    Repositorio específico para eventos de webhook
    """
    
    def __init__(self):
        from database.models import WebhookEvent
        super().__init__(WebhookEvent)
    
    def get_unprocessed_events(self, limit: int = 100) -> List[Any]:
        """
        Obtiene eventos de webhook no procesados
        Args:
            limit: Límite de eventos a retornar
        Returns:
            Lista de eventos no procesados
        """
        try:
            results = (self.model_class.query
                      .filter_by(processed=False)
                      .order_by(self.model_class.created_at.asc())
                      .limit(limit)
                      .all())
            
            self.logger.debug(f"Encontrados {len(results)} eventos no procesados")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo eventos no procesados: {e}")
            raise DatabaseError("Error al obtener eventos no procesados", "get_unprocessed_events")
    
    def mark_as_processed(self, event_id: str, success: bool = True, error_msg: str = None) -> bool:
        """
        Marca un evento como procesado
        Args:
            event_id: ID del evento
            success: Si el procesamiento fue exitoso
            error_msg: Mensaje de error si falló
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            event = self.get_by_id(event_id)
            if not event:
                return False
            
            event.mark_as_processed(success, error_msg)
            self.logger.info(f"Evento {event_id} marcado como procesado: {success}")
            return True
        except Exception as e:
            self.logger.error(f"Error marcando evento {event_id} como procesado: {e}")
            return False

class MessagingLineRepository(BaseRepository):
    """
    Repositorio específico para líneas de mensajería
    """
    
    def __init__(self):
        from database.models import MessagingLine
        super().__init__(MessagingLine)
    
    def get_by_line_id(self, line_id: str) -> Optional[Any]:
        """
        Obtiene línea por line_id
        Args:
            line_id: ID de la línea
        Returns:
            Línea encontrada o None
        """
        try:
            result = self.model_class.query.filter_by(line_id=line_id).first()
            if result:
                self.logger.debug(f"Encontrada línea: {line_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo línea {line_id}: {e}")
            raise DatabaseError("Error al obtener línea", "get_by_line_id")
    
    def get_active_lines(self) -> List[Any]:
        """
        Obtiene todas las líneas activas
        Returns:
            Lista de líneas activas
        """
        return self.find_by(is_active=True)
    
    def get_line_with_capacity(self) -> Optional[Any]:
        """
        Obtiene una línea que tenga capacidad para enviar mensajes
        Returns:
            Línea con capacidad o None
        """
        try:
            active_lines = self.get_active_lines()
            
            for line in active_lines:
                if line.can_send_message():
                    self.logger.debug(f"Línea con capacidad encontrada: {line.line_id}")
                    return line
            
            self.logger.warning("No hay líneas con capacidad disponible")
            return None
        except Exception as e:
            self.logger.error(f"Error buscando línea con capacidad: {e}")
            return None

class MediaRepository(BaseRepository):
    """
    Repositorio específico para archivos multimedia
    """
    
    def __init__(self):
        from database.models import MediaFile
        super().__init__(MediaFile)
    
    def get_by_whatsapp_media_id(self, whatsapp_media_id: str) -> Optional[Any]:
        """
        Obtiene archivo por ID de WhatsApp
        Args:
            whatsapp_media_id: ID de media de WhatsApp
        Returns:
            Archivo encontrado o None
        """
        try:
            result = self.model_class.query.filter_by(whatsapp_media_id=whatsapp_media_id).first()
            if result:
                self.logger.debug(f"Encontrado archivo con WhatsApp ID: {whatsapp_media_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo archivo por WhatsApp ID {whatsapp_media_id}: {e}")
            raise DatabaseError("Error al obtener archivo", "get_by_whatsapp_media_id")
    
    def get_by_file_type(self, file_type: str) -> List[Any]:
        """
        Obtiene archivos por tipo
        Args:
            file_type: Tipo de archivo (image, video, document, audio)
        Returns:
            Lista de archivos del tipo especificado
        """
        return self.find_by(file_type=file_type)
    
    def get_expired_files(self) -> List[Any]:
        """
        Obtiene archivos con URLs expiradas
        Returns:
            Lista de archivos con URLs expiradas
        """
        try:
            from datetime import datetime
            current_time = datetime.utcnow()
            
            results = (self.model_class.query
                      .filter(self.model_class.expires_at < current_time)
                      .filter_by(downloaded=False)
                      .all())
            
            self.logger.debug(f"Encontrados {len(results)} archivos expirados")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo archivos expirados: {e}")
            raise DatabaseError("Error al obtener archivos expirados", "get_expired_files")
