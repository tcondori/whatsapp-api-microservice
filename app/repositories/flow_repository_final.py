"""
Repositorio de flujos de conversación - Versión final PostgreSQL
Manejo nativo de UUIDs con SQLAlchemy
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.connection import db, get_db_session
from app.utils.exceptions import DatabaseError
import logging


class FlowRepository:
    """Repositorio para gestión de flujos de conversación con UUIDs nativos"""
    
    def __init__(self):
        self.logger = logging.getLogger('repo.flows')
    
    def get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return get_db_session()
    
    def create_flow(self, name: str, description: str = "", 
                    rivescript_content: str = "", **kwargs) -> Any:
        """
        Crea un nuevo flujo de conversación
        Args:
            name: Nombre del flujo
            description: Descripción del flujo
            rivescript_content: Contenido RiveScript
            **kwargs: Otros campos opcionales
        Returns:
            Nuevo flujo creado
        """
        try:
            from database.models import ConversationFlow
            
            # PostgreSQL generará automáticamente el UUID
            flow_data = {
                'name': name,
                'description': description,
                'rivescript_content': rivescript_content,
                'is_active': kwargs.get('is_active', True),
                'is_default': kwargs.get('is_default', False),
                'priority': kwargs.get('priority', 1),
                'fallback_to_llm': kwargs.get('fallback_to_llm', True),
                'max_context_messages': kwargs.get('max_context_messages', 5),
            }
            
            session = self.get_session()
            flow = ConversationFlow(**flow_data)
            session.add(flow)
            session.commit()
            
            self.logger.info(f"Flujo creado: {flow.name} ({flow.id})")
            return flow
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Error creando flujo: {e}")
            raise DatabaseError("Error al crear flujo", "create")
    
    def get_by_id(self, flow_id: str) -> Optional[Any]:
        """
        Obtiene un flujo por su UUID
        Args:
            flow_id: UUID del flujo (string)
        Returns:
            Flujo encontrado o None
        """
        try:
            from database.models import ConversationFlow
            
            # Convertir string a UUID si es necesario
            if isinstance(flow_id, str):
                flow_uuid = uuid.UUID(flow_id)
            else:
                flow_uuid = flow_id
            
            session = self.get_session()
            flow = session.query(ConversationFlow).filter(
                ConversationFlow.id == flow_uuid
            ).first()
            
            if flow:
                self.logger.debug(f"Flujo encontrado: {flow.name} ({flow.id})")
            return flow
        except (ValueError, SQLAlchemyError) as e:
            self.logger.error(f"Error obteniendo flujo {flow_id}: {e}")
            return None
    
    def get_all_flows(self) -> List[Any]:
        """
        Obtiene todos los flujos
        Returns:
            Lista de flujos
        """
        try:
            from database.models import ConversationFlow
            
            session = self.get_session()
            flows = session.query(ConversationFlow).order_by(
                ConversationFlow.priority.asc()
            ).all()
            
            self.logger.debug(f"Obtenidos {len(flows)} flujos")
            return flows
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo flujos: {e}")
            return []
    
    def get_active_flows(self) -> List[Any]:
        """
        Obtiene solo los flujos activos
        Returns:
            Lista de flujos activos
        """
        try:
            from database.models import ConversationFlow
            
            session = self.get_session()
            flows = session.query(ConversationFlow).filter(
                ConversationFlow.is_active == True
            ).order_by(
                ConversationFlow.priority.asc()
            ).all()
            
            self.logger.debug(f"Obtenidos {len(flows)} flujos activos")
            return flows
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo flujos activos: {e}")
            return []
    
    def get_default_flow(self) -> Optional[Any]:
        """
        Obtiene el flujo por defecto
        Returns:
            Flujo por defecto o None
        """
        try:
            from database.models import ConversationFlow
            
            session = self.get_session()
            flow = session.query(ConversationFlow).filter(
                ConversationFlow.is_default == True,
                ConversationFlow.is_active == True
            ).first()
            
            if flow:
                self.logger.debug(f"Flujo por defecto: {flow.name}")
            return flow
        except SQLAlchemyError as e:
            self.logger.error(f"Error obteniendo flujo por defecto: {e}")
            return None
    
    def update_flow(self, flow_id: str, **updates) -> Optional[Any]:
        """
        Actualiza un flujo
        Args:
            flow_id: UUID del flujo
            **updates: Campos a actualizar
        Returns:
            Flujo actualizado o None
        """
        try:
            from database.models import ConversationFlow
            
            # Convertir string a UUID
            if isinstance(flow_id, str):
                flow_uuid = uuid.UUID(flow_id)
            else:
                flow_uuid = flow_id
            
            session = self.get_session()
            flow = session.query(ConversationFlow).filter(
                ConversationFlow.id == flow_uuid
            ).first()
            
            if not flow:
                self.logger.warning(f"Flujo no encontrado para actualizar: {flow_id}")
                return None
            
            # Actualizar campos
            for key, value in updates.items():
                if hasattr(flow, key):
                    setattr(flow, key, value)
            
            session.commit()
            
            self.logger.info(f"Flujo actualizado: {flow.name} ({flow.id})")
            return flow
        except (ValueError, SQLAlchemyError) as e:
            session.rollback()
            self.logger.error(f"Error actualizando flujo {flow_id}: {e}")
            return None
    
    def activate_flow(self, flow_id: str) -> bool:
        """
        Activa un flujo
        Args:
            flow_id: UUID del flujo
        Returns:
            bool: True si se activó exitosamente
        """
        result = self.update_flow(flow_id, is_active=True)
        return result is not None
    
    def deactivate_flow(self, flow_id: str) -> bool:
        """
        Desactiva un flujo
        Args:
            flow_id: UUID del flujo
        Returns:
            bool: True si se desactivó exitosamente
        """
        result = self.update_flow(flow_id, is_active=False)
        return result is not None
    
    def set_as_default(self, flow_id: str) -> bool:
        """
        Establece un flujo como predeterminado
        Args:
            flow_id: UUID del flujo
        Returns:
            bool: True si se estableció exitosamente
        """
        try:
            from database.models import ConversationFlow
            
            session = self.get_session()
            
            # Primero quitar el default de todos
            session.query(ConversationFlow).update(
                {ConversationFlow.is_default: False}
            )
            
            # Luego establecer el nuevo default
            if isinstance(flow_id, str):
                flow_uuid = uuid.UUID(flow_id)
            else:
                flow_uuid = flow_id
            
            updated = session.query(ConversationFlow).filter(
                ConversationFlow.id == flow_uuid
            ).update({
                ConversationFlow.is_default: True,
                ConversationFlow.is_active: True  # También activarlo
            })
            
            session.commit()
            
            if updated > 0:
                self.logger.info(f"Flujo establecido como predeterminado: {flow_id}")
                return True
            return False
        except (ValueError, SQLAlchemyError) as e:
            session.rollback()
            self.logger.error(f"Error estableciendo flujo como predeterminado {flow_id}: {e}")
            return False
    
    def delete_flow(self, flow_id: str) -> bool:
        """
        Elimina un flujo
        Args:
            flow_id: UUID del flujo
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            from database.models import ConversationFlow
            
            if isinstance(flow_id, str):
                flow_uuid = uuid.UUID(flow_id)
            else:
                flow_uuid = flow_id
            
            session = self.get_session()
            deleted = session.query(ConversationFlow).filter(
                ConversationFlow.id == flow_uuid
            ).delete()
            
            session.commit()
            
            if deleted > 0:
                self.logger.info(f"Flujo eliminado: {flow_id}")
                return True
            return False
        except (ValueError, SQLAlchemyError) as e:
            session.rollback()
            self.logger.error(f"Error eliminando flujo {flow_id}: {e}")
            return False
    
    def search_flows(self, query: str) -> List[Any]:
        """
        Busca flujos por nombre o descripción
        Args:
            query: Texto a buscar
        Returns:
            Lista de flujos que coinciden
        """
        try:
            from database.models import ConversationFlow
            
            session = self.get_session()
            flows = session.query(ConversationFlow).filter(
                (ConversationFlow.name.contains(query)) |
                (ConversationFlow.description.contains(query))
            ).order_by(
                ConversationFlow.priority.asc()
            ).all()
            
            self.logger.debug(f"Encontrados {len(flows)} flujos con query: {query}")
            return flows
        except SQLAlchemyError as e:
            self.logger.error(f"Error buscando flujos: {e}")
            return []
    
    def count_flows(self) -> int:
        """
        Cuenta el total de flujos
        Returns:
            Número total de flujos
        """
        try:
            from database.models import ConversationFlow
            
            session = self.get_session()
            count = session.query(ConversationFlow).count()
            
            self.logger.debug(f"Total de flujos: {count}")
            return count
        except SQLAlchemyError as e:
            self.logger.error(f"Error contando flujos: {e}")
            return 0


# Instancia singleton del repositorio
flow_repository = FlowRepository()
