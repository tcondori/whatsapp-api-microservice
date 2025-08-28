"""
Repositorio de flujos de conversación para PostgreSQL
Versión simplificada usando SQLAlchemy ORM nativo con UUIDs
"""
from typing import List, Optional, Dict, Any
from database.models import ConversationFlow
from database.connection import db
import logging


class FlowRepository:
    """
    Repositorio simplificado para gestión de flujos de conversación
    Usa SQLAlchemy ORM nativo con soporte completo para UUID PostgreSQL
    """
    
    def __init__(self):
        self.logger = logging.getLogger('repo.flows')
        
    def get_all_flows(self) -> List[ConversationFlow]:
        """Obtiene todos los flujos de conversación"""
        return ConversationFlow.query.all()
        
    def get_by_id(self, flow_id: str) -> Optional[ConversationFlow]:
        """Obtiene un flujo por su UUID"""
        return ConversationFlow.query.get(flow_id)
        
    def get_by_name(self, name: str) -> Optional[ConversationFlow]:
        """Obtiene un flujo por su nombre"""
        return ConversationFlow.query.filter_by(name=name).first()
        
    def get_default_flow(self) -> Optional[ConversationFlow]:
        """Obtiene el flujo marcado como por defecto"""
        return ConversationFlow.query.filter_by(is_default=True).first()
        
    def get_active_flows(self) -> List[ConversationFlow]:
        """Obtiene todos los flujos activos ordenados por prioridad"""
        return ConversationFlow.query.filter_by(is_active=True).order_by(ConversationFlow.priority).all()
        
    def update_flow(self, flow_id: str, update_data: dict) -> bool:
        """Actualiza un flujo por UUID"""
        try:
            flow = ConversationFlow.query.get(flow_id)
            if not flow:
                self.logger.warning(f"Flujo no encontrado: {flow_id}")
                return False
                
            # Actualizar campos
            for key, value in update_data.items():
                if hasattr(flow, key):
                    setattr(flow, key, value)
                    
            db.session.commit()
            self.logger.info(f"Flujo {flow_id} actualizado correctamente")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error actualizando flujo {flow_id}: {e}")
            return False
            
    def create_flow(self, flow_data: Dict[str, Any]) -> Optional[ConversationFlow]:
        """Crea un nuevo flujo"""
        try:
            flow = ConversationFlow(**flow_data)
            db.session.add(flow)
            db.session.commit()
            self.logger.info(f"Flujo creado: {flow.name}")
            return flow
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando flujo: {e}")
            return None
            
    def delete_flow(self, flow_id: str) -> bool:
        """Elimina un flujo por UUID"""
        try:
            flow = ConversationFlow.query.get(flow_id)
            if not flow:
                return False
                
            db.session.delete(flow)
            db.session.commit()
            self.logger.info(f"Flujo {flow_id} eliminado")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error eliminando flujo {flow_id}: {e}")
            return False
