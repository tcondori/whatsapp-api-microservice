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
                'most_used_flow': most_used.name if most_used else None,
                'most_used_count': most_used.usage_count if most_used else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de flujos: {e}")
            return {}
