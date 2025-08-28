"""
Repositorio simplificado para gestión de flujos de conversación (versión de prueba)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from database.models import ConversationFlow
from app.repositories.base_repo import BaseRepository

class FlowRepository(BaseRepository):
    """Repositorio para gestión de flujos de conversación"""
    
    def __init__(self):
        super().__init__(ConversationFlow)
    
    def get_active_flows(self) -> List[ConversationFlow]:
        """Obtiene todos los flujos activos ordenados por prioridad"""
        try:
            flows = self.model.query.filter_by(is_active=True)\
                                   .order_by(self.model.priority.asc())\
                                   .all()
            return flows
        except Exception as e:
            print(f"Error obteniendo flujos activos: {e}")
            return []
    
    def get_default_flow(self) -> Optional[ConversationFlow]:
        """Obtiene el flujo por defecto"""
        try:
            flow = self.model.query.filter_by(is_default=True, is_active=True).first()
            return flow
        except Exception as e:
            print(f"Error obteniendo flujo por defecto: {e}")
            return None
    
    def get_by_name(self, name: str) -> Optional[ConversationFlow]:
        """Obtiene un flujo por su nombre"""
        try:
            flow = self.model.query.filter_by(name=name).first()
            return flow
        except Exception as e:
            print(f"Error buscando flujo por nombre '{name}': {e}")
            return None
    
    def increment_usage(self, flow_id: int) -> bool:
        """Incrementa el contador de uso de un flujo"""
        try:
            flow = self.get_by_id(flow_id)
            if flow:
                flow.usage_count = (flow.usage_count or 0) + 1
                flow.last_used = datetime.utcnow()
                self.update(flow)
                return True
            return False
        except Exception as e:
            print(f"Error incrementando uso del flujo {flow_id}: {e}")
            return False
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de flujos"""
        try:
            from sqlalchemy import func
            
            stats = self.db.session.query(
                func.count(self.model.id).label('total_flows'),
                func.sum(self.model.usage_count).label('total_usage'),
                func.count(self.model.id).filter(self.model.is_active == True).label('active_flows')
            ).first()
            
            most_used = self.model.query.order_by(self.model.usage_count.desc()).first()
            
            return {
                'total_flows': stats.total_flows or 0,
                'total_usage': stats.total_usage or 0,
                'active_flows': stats.active_flows or 0,
                'most_used_flow': most_used.name if most_used else None,
                'most_used_count': most_used.usage_count if most_used else 0
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas de flujos: {e}")
            return {}
