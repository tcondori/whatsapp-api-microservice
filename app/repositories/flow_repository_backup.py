# app/repositories/flow_repository.py - Versión corregida
# filepath: e:\DSW\proyectos\proy04\app\repositories\flow_repository_fixed.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from database.models import ConversationFlow
from app.repositories.base_repo import BaseRepository
from app.utils.logger import WhatsAppLogger

class FlowRepository(BaseRepository):
    """Repositorio para gestión de flujos de conversación"""
    
    def __init__(self):
        super().__init__(ConversationFlow)
        self.logger = WhatsAppLogger.get_logger('flow_repo')
    
    def get_active_flows(self) -> List[ConversationFlow]:
        """Obtiene todos los flujos activos ordenados por prioridad"""
        try:
            flows = self.model_class.query.filter_by(is_active=True)\
                                   .order_by(self.model_class.priority.asc())\
                                   .all()
            
            self.logger.info(f"Obtenidos {len(flows)} flujos activos")
            return flows
            
        except Exception as e:
            self.logger.error(f"Error obteniendo flujos activos: {e}")
            return []
    
    def find_by_uuid(self, flow_id: str) -> Optional[ConversationFlow]:
        """
        MÉTODO PERSONALIZADO: Obtiene un flujo por UUID (sin conflicto de herencia)
        Args:
            flow_id: UUID del flujo como string
        Returns:
            Flujo encontrado o None
        """
        try:
            import uuid
            
            self.logger.debug(f"🚀 FIND_BY_UUID PERSONALIZADO - Llamado con: {flow_id}")
            
            # Convertir string a UUID object
            if isinstance(flow_id, str):
                uuid_obj = uuid.UUID(flow_id)
                self.logger.debug(f"🚀 FIND_BY_UUID - UUID convertido a objeto: {uuid_obj} (tipo: {type(uuid_obj)})")
            else:
                uuid_obj = flow_id
                self.logger.debug(f"🚀 FIND_BY_UUID - UUID recibido como objeto: {uuid_obj}")
            
            # SOLUCIÓN FINAL: usar SQL directo para evitar conversiones automáticas de SQLAlchemy
            from sqlalchemy import text
            from database.connection import db
            
            self.logger.debug(f"🚀 FIND_BY_UUID - Usando SQL directo con: {flow_id}")
            
            # Consulta SQL directa con el UUID como string literal
            sql = text("SELECT * FROM conversation_flows WHERE id = :flow_id")
            result = db.session.execute(sql, {"flow_id": flow_id}).fetchone()
            
            if result:
                # Convertir el resultado a objeto ConversationFlow manualmente
                flow = self.model_class()
                
                # Obtener columnas desde la metadata de la tabla
                table_columns = self.model_class.__table__.columns.keys()
                
                # Asignar valores por índice (result es una tupla)
                for i, column_name in enumerate(table_columns):
                    if i < len(result):
                        setattr(flow, column_name, result[i])
                
                self.logger.debug(f"✅ FIND_BY_UUID - Flujo encontrado con SQL directo: {flow.name}")
                return flow
            else:
                self.logger.warning(f"❌ FIND_BY_UUID - No se encontró flujo con ID: {flow_id}")
                # Debug info
                total_flows = self.model_class.query.count()
                self.logger.debug(f"Total de flujos en DB: {total_flows}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error buscando flujo por UUID {flow_id}: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def get_by_id(self, flow_id: str) -> Optional[ConversationFlow]:
        """
        OVERRIDE: Obtiene un flujo específico por ID (UUID) - versión personalizada para UUID
        Args:
            flow_id: UUID del flujo como string o UUID object
        Returns:
            Flujo encontrado o None
        """
        try:
            import uuid
            
            self.logger.debug(f"🔧 FLOW REPOSITORY CUSTOM - get_by_id llamado con: {flow_id}")
            
            # Convertir string a UUID object (SQLAlchemy NECESITA el objeto UUID, no string)
            if isinstance(flow_id, str):
                uuid_obj = uuid.UUID(flow_id)
                self.logger.debug(f"🔧 FLOW REPOSITORY CUSTOM - UUID convertido a objeto: {uuid_obj} (tipo: {type(uuid_obj)})")
            else:
                uuid_obj = flow_id
                self.logger.debug(f"🔧 FLOW REPOSITORY CUSTOM - UUID recibido como objeto: {uuid_obj}")
            
            # CLAVE: usar query.get() con objeto UUID - esto SÍ funciona
            self.logger.debug(f"🔧 FLOW REPOSITORY CUSTOM - Usando query.get() con objeto UUID")
            result = self.model_class.query.get(uuid_obj)
            
            if result:
                self.logger.debug(f"✅ Flujo encontrado: {result.name}")
                return result
            else:
                self.logger.warning(f"❌ No se encontró flujo con ID: {flow_id}")
                # Debug info
                total_flows = self.model_class.query.count()
                self.logger.debug(f"Total de flujos en DB: {total_flows}")
            
            return None
        except ValueError as e:
            self.logger.error(f"ID inválido: {flow_id} - {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo flujo {flow_id}: {e}")
            return None
            return None

    def get_default_flow(self) -> Optional[ConversationFlow]:
        """Obtiene el flujo por defecto"""
        try:
            flow = self.model_class.query.filter_by(is_default=True, is_active=True).first()
            
            if flow:
                self.logger.info(f"Flujo por defecto obtenido: {flow.name}")
            else:
                self.logger.warning("No se encontró flujo por defecto activo")
            
            return flow
            
        except Exception as e:
            self.logger.error(f"Error obteniendo flujo por defecto: {e}")
            return None
    
    def get_by_name(self, name: str) -> Optional[ConversationFlow]:
        """Obtiene un flujo por su nombre"""
        try:
            flow = self.model_class.query.filter_by(name=name).first()
            
            if flow:
                self.logger.info(f"Flujo encontrado por nombre: {name}")
            
            return flow
            
        except Exception as e:
            self.logger.error(f"Error buscando flujo por nombre '{name}': {e}")
            return None
    
    def increment_usage(self, flow_id: int) -> bool:
        """Incrementa el contador de uso de un flujo"""
        try:
            flow = self.get_by_id(flow_id)
            if flow:
                flow.usage_count = (flow.usage_count or 0) + 1
                flow.last_used = datetime.utcnow()
                
                # Usar el método update del BaseRepository
                result = self.update(flow.id, usage_count=flow.usage_count, last_used=flow.last_used)
                if result:
                    self.logger.info(f"Uso incrementado para flujo {flow_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error incrementando uso del flujo {flow_id}: {e}")
            return False
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de flujos"""
        try:
            from sqlalchemy import func
            from database.connection import get_db_session
            
            session = get_db_session()
            
            stats = session.query(
                func.count(self.model_class.id).label('total_flows'),
                func.sum(self.model_class.usage_count).label('total_usage'),
                func.count(self.model_class.id).filter(self.model_class.is_active == True).label('active_flows')
            ).first()
            
            most_used = self.model_class.query.order_by(self.model_class.usage_count.desc()).first()
            
            return {
                'total_flows': stats.total_flows or 0,
                'total_usage': stats.total_usage or 0,
                'active_flows': stats.active_flows or 0,
                'most_used_flow': most_used.name if most_used else None
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de flujos: {e}")
            return {
                'total_flows': 0,
                'total_usage': 0, 
                'active_flows': 0,
                'most_used_flow': None
            }
    
    # ========================================
    # MÉTODOS ADICIONALES PARA EL EDITOR
    # ========================================
    
    def create_flow(self, flow_data: Dict[str, Any]) -> Optional[ConversationFlow]:
        """
        Crea un nuevo flujo RiveScript
        
        Args:
            flow_data: Datos del flujo a crear
            
        Returns:
            ConversationFlow: Flujo creado o None si hay error
        """
        try:
            # Usar método create del BaseRepository
            flow = self.create(**flow_data)
            
            if flow:
                self.logger.info(f"Flujo '{flow.name}' creado con ID {flow.id}")
                return flow
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creando flujo: {e}")
            return None
    
    def update_flow(self, flow_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Actualiza un flujo existente
        
        Args:
            flow_id: ID del flujo a actualizar (UUID como string)
            update_data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # CAMBIO: Usar nuestro método personalizado find_by_uuid() que SÍ funciona
            self.logger.debug(f"🔧 UPDATE_FLOW - Usando find_by_uuid() personalizado")
            flow = self.find_by_uuid(flow_id)  # Usar nuestro método personalizado
            
            if not flow:
                self.logger.warning(f"Flujo no encontrado: {flow_id}")
                return False
            
            # Agregar timestamp de actualización
            update_data['updated_at'] = datetime.utcnow()
            
            # Actualizar los campos manualmente
            for key, value in update_data.items():
                if hasattr(flow, key):
                    setattr(flow, key, value)
                    self.logger.debug(f"Actualizando {key}: {value}")
            
            # Confirmar cambios usando la sesión de base de datos
            from database.connection import db, safe_commit
            
            try:
                safe_commit(db.session)
                self.logger.info(f"Flujo {flow_id} actualizado correctamente")
                return True
            except Exception as commit_error:
                db.session.rollback()
                self.logger.error(f"Error confirmando actualización: {commit_error}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error actualizando flujo {flow_id}: {e}")
            return False
    
    def delete_flow(self, flow_id: int) -> bool:
        """
        Elimina un flujo
        
        Args:
            flow_id: ID del flujo a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            # Usar método delete del BaseRepository
            result = self.delete(flow_id)
            
            if result:
                self.logger.info(f"Flujo {flow_id} eliminado correctamente")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando flujo {flow_id}: {e}")
            return False
    
    def get_all_flows(self) -> List[ConversationFlow]:
        """
        Obtiene todos los flujos (activos e inactivos)
        
        Returns:
            List[ConversationFlow]: Lista de todos los flujos
        """
        try:
            flows = self.model_class.query.order_by(
                self.model_class.is_active.desc(),
                self.model_class.priority.asc(),
                self.model_class.name.asc()
            ).all()
            
            self.logger.info(f"Obtenidos {len(flows)} flujos totales")
            return flows
            
        except Exception as e:
            self.logger.error(f"Error obteniendo todos los flujos: {e}")
            return []
    
    def get_flows_by_category(self, category: str) -> List[ConversationFlow]:
        """
        Obtiene flujos por categoría
        
        Args:
            category: Categoría a filtrar
            
        Returns:
            List[ConversationFlow]: Flujos de la categoría
        """
        try:
            flows = self.model_class.query.filter_by(category=category)\
                                   .filter_by(is_active=True)\
                                   .order_by(self.model_class.priority.asc())\
                                   .all()
            
            self.logger.info(f"Obtenidos {len(flows)} flujos de categoría '{category}'")
            return flows
            
        except Exception as e:
            self.logger.error(f"Error obteniendo flujos de categoría '{category}': {e}")
            return []
    
    def get_flow_statistics(self):
        """
        Obtiene estadísticas generales de los flujos
        
        Returns:
            Dict: Estadísticas de flujos
        """
        try:
            total_flows = self.model_class.query.count()
            active_flows = self.model_class.query.filter_by(is_active=True).count()
            
            # Flujo más utilizado (si tienes campo usage_count)
            most_used = self.model_class.query.order_by(
                self.model_class.id.desc()  # Temporalmente usar ID como proxy
            ).first()
            
            return {
                'total_flows': total_flows,
                'active_flows': active_flows,
                'inactive_flows': total_flows - active_flows,
                'most_used_flow': most_used.name if most_used else None,
                'most_used_count': 1 if most_used else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de flujos: {e}")
            return {}
