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
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, model_class):
        """
        Inicializa el repositorio base
        Args:
            model_class: Clase del modelo SQLAlchemy
        """
        self.model_class = model_class
        self.logger = logging.getLogger(f'repo.{model_class.__name__.lower()}')
    
    def get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return get_db_session()
    
    def create(self, **kwargs) -> Any:
        """
        Crea una nueva instancia
        Args:
            **kwargs: Datos para la nueva instancia
        Returns:
            Nueva instancia creada
        """
        try:
            session = self.get_session()
            instance = self.model_class(**kwargs)
            session.add(instance)
            safe_commit(session)
            
            self.logger.debug(f"Creado nuevo {self.model_class.__name__}: {instance.id if hasattr(instance, 'id') else 'N/A'}")
            return instance
        except SQLAlchemyError as e:
            safe_rollback(session)
            self.logger.error(f"Error creando {self.model_class.__name__}: {e}")
            raise DatabaseError(f"Error al crear {self.model_class.__name__}", "create")
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """
        Obtiene una instancia por ID
        Args:
            id: ID de la instancia
        Returns:
            Instancia encontrada o None
        """
        try:
            result = self.model_class.query.get(id)
            if result:
                self.logger.debug(f"Encontrado {self.model_class.__name__}: {id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo {self.model_class.__name__} {id}: {e}")
            raise DatabaseError(f"Error al obtener {self.model_class.__name__}", "get_by_id")
    
    def get_all(self, limit: int = None, offset: int = None) -> List[Any]:
        """
        Obtiene todas las instancias
        Args:
            limit: Límite de resultados (opcional)
            offset: Offset para paginación (opcional)
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
            self.logger.error(f"Error obteniendo {self.model_class.__name__}s: {e}")
            raise DatabaseError(f"Error al obtener {self.model_class.__name__}s", "get_all")
    
    def update(self, id: int, **kwargs) -> Optional[Any]:
        """
        Actualiza una instancia por ID
        Args:
            id: ID de la instancia
            **kwargs: Campos a actualizar
        Returns:
            Instancia actualizada o None
        """
        try:
            session = self.get_session()
            instance = self.get_by_id(id)
            
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            safe_commit(session)
            
            self.logger.debug(f"Actualizado {self.model_class.__name__}: {id}")
            return instance
        except SQLAlchemyError as e:
            safe_rollback(session)
            self.logger.error(f"Error actualizando {self.model_class.__name__} {id}: {e}")
            raise DatabaseError(f"Error al actualizar {self.model_class.__name__}", "update")
    
    def delete(self, id: int) -> bool:
        """
        Elimina una instancia por ID
        Args:
            id: ID de la instancia
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            session = self.get_session()
            instance = self.get_by_id(id)
            
            if not instance:
                return False
            
            session.delete(instance)
            safe_commit(session)
            
            self.logger.debug(f"Eliminado {self.model_class.__name__}: {id}")
            return True
        except SQLAlchemyError as e:
            safe_rollback(session)
            self.logger.error(f"Error eliminando {self.model_class.__name__} {id}: {e}")
            raise DatabaseError(f"Error al eliminar {self.model_class.__name__}", "delete")
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        Cuenta instancias con filtros opcionales
        Args:
            filters: Filtros a aplicar (opcional)
        Returns:
            Número de instancias
        """
        try:
            query = self.model_class.query
            
            if filters:
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


class MessageRepository(BaseRepository):
    """
    Repositorio específico para mensajes
    """
    
    def __init__(self):
        from database.models import Message
        super().__init__(Message)
    
    def get_by_whatsapp_id(self, whatsapp_message_id: str) -> Optional[Any]:
        """
        Obtiene mensaje por ID de WhatsApp
        Args:
            whatsapp_message_id: ID del mensaje en WhatsApp
        Returns:
            Mensaje encontrado o None
        """
        try:
            result = self.model_class.query.filter_by(whatsapp_message_id=whatsapp_message_id).first()
            if result:
                self.logger.debug(f"Encontrado mensaje: {whatsapp_message_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo mensaje {whatsapp_message_id}: {e}")
            raise DatabaseError("Error al obtener mensaje", "get_by_whatsapp_id")
    
    def get_by_phone_number(self, phone_number: str, limit: int = 10) -> List[Any]:
        """
        Obtiene mensajes de un número específico
        Args:
            phone_number: Número de teléfono
            limit: Límite de mensajes
        Returns:
            Lista de mensajes
        """
        try:
            results = self.model_class.query.filter_by(
                phone_number=phone_number
            ).order_by(
                self.model_class.created_at.desc()
            ).limit(limit).all()
            
            self.logger.debug(f"Encontrados {len(results)} mensajes para {phone_number}")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo mensajes de {phone_number}: {e}")
            raise DatabaseError("Error al obtener mensajes por teléfono", "get_by_phone_number")
    
    def get_by_line_id(self, line_id: str) -> List[Any]:
        """
        Obtiene mensajes de una línea específica
        Args:
            line_id: ID de la línea
        Returns:
            Lista de mensajes
        """
        return self.find_by(line_id=line_id)
    
    def get_recent_messages(self, hours: int = 24) -> List[Any]:
        """
        Obtiene mensajes recientes
        Args:
            hours: Horas hacia atrás
        Returns:
            Lista de mensajes recientes
        """
        try:
            from datetime import datetime, timedelta
            
            since_time = datetime.utcnow() - timedelta(hours=hours)
            results = self.model_class.query.filter(
                self.model_class.created_at >= since_time
            ).order_by(
                self.model_class.created_at.desc()
            ).all()
            
            self.logger.debug(f"Encontrados {len(results)} mensajes recientes")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo mensajes recientes: {e}")
            raise DatabaseError("Error al obtener mensajes recientes", "get_recent_messages")
    
    def update_status(self, message_id: int, new_status: str) -> bool:
        """
        Actualiza el estado de un mensaje
        Args:
            message_id: ID del mensaje
            new_status: Nuevo estado
        Returns:
            bool: True si se actualizó exitosamente
        """
        updated = self.update(message_id, status=new_status)
        return updated is not None


class MessagingLineRepository(BaseRepository):
    """
    Repositorio específico para líneas de mensajería
    """
    
    def __init__(self):
        from database.models import MessagingLine
        super().__init__(MessagingLine)
    
    def get_by_line_id(self, line_id) -> Optional[Any]:
        """
        Obtiene línea por ID
        Args:
            line_id: ID de la línea (puede ser int o str)
        Returns:
            Línea encontrada o None
        """
        try:
            # Buscar directamente como string (las line_ids en BD son strings)
            # Si line_id es int, convertir a string para la búsqueda
            if isinstance(line_id, int):
                line_id_str = str(line_id)
            else:
                line_id_str = str(line_id)
            
            result = self.model_class.query.filter_by(line_id=line_id_str).first()
            if result:
                self.logger.debug(f"Encontrada línea: {line_id_str}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo línea {line_id}: {e}")
            raise DatabaseError("Error al obtener línea", "get_by_line_id")
    
    def get_by_phone_number_id(self, phone_number_id: str) -> Optional[Any]:
        """
        Obtiene línea por phone_number_id de WhatsApp
        Args:
            phone_number_id: ID del número de teléfono de WhatsApp Business
        Returns:
            Línea encontrada o None
        """
        try:
            result = self.model_class.query.filter_by(phone_number_id=phone_number_id).first()
            if result:
                self.logger.debug(f"Encontrada línea con phone_number_id: {phone_number_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo línea con phone_number_id {phone_number_id}: {e}")
            raise DatabaseError("Error al obtener línea por phone_number_id", "get_by_phone_number_id")
    
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
                if hasattr(line, 'can_send_message') and line.can_send_message():
                    self.logger.debug(f"Línea con capacidad encontrada: {line.line_id}")
                    return line
            
            self.logger.warning("No hay líneas con capacidad disponible")
            return None
        except Exception as e:
            self.logger.error(f"Error buscando línea con capacidad: {e}")
            return None


class ContactRepository(BaseRepository):
    """
    Repositorio específico para contactos
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
                self.update(contact.id, is_blocked=True)
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
    
    def get_by_webhook_id(self, webhook_id: str) -> Optional[Any]:
        """
        Obtiene evento por ID de webhook
        Args:
            webhook_id: ID del webhook
        Returns:
            Evento encontrado o None
        """
        try:
            result = self.model_class.query.filter_by(webhook_id=webhook_id).first()
            if result:
                self.logger.debug(f"Encontrado evento de webhook: {webhook_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo evento {webhook_id}: {e}")
            raise DatabaseError("Error al obtener evento de webhook", "get_by_webhook_id")
    
    def get_unprocessed_events(self) -> List[Any]:
        """
        Obtiene eventos no procesados
        Returns:
            Lista de eventos no procesados
        """
        return self.find_by(status='pending')


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
                self.logger.debug(f"Encontrado archivo: {whatsapp_media_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo archivo {whatsapp_media_id}: {e}")
            raise DatabaseError("Error al obtener archivo multimedia", "get_by_whatsapp_media_id")
    
    def get_by_file_path(self, file_path: str) -> Optional[Any]:
        """
        Obtiene archivo por ruta
        Args:
            file_path: Ruta del archivo
        Returns:
            Archivo encontrado o None
        """
        try:
            result = self.model_class.query.filter_by(file_path=file_path).first()
            if result:
                self.logger.debug(f"Encontrado archivo por ruta: {file_path}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo archivo por ruta {file_path}: {e}")
            raise DatabaseError("Error al obtener archivo por ruta", "get_by_file_path")
