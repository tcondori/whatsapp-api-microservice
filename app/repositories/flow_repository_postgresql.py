"""
Repository para gestionar flujos de conversación RiveScript
¡VERSIÓN SIMPLIFICADA PARA POSTGRESQL!
Los métodos heredados funcionan perfectamente con UUID nativo
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from database.models import ConversationFlow
from app.repositories.base_repo import BaseRepository


class FlowRepository(BaseRepository):
    """Repository simplificado para PostgreSQL - sin métodos personalizados complejos"""
    
    def __init__(self):
        super().__init__(ConversationFlow)
    
    # ===== MÉTODOS ESPECÍFICOS DE FLUJOS =====
    # Los métodos heredados get_by_id(), update(), etc. funcionan perfectamente con PostgreSQL
    
    def get_active_flows(self) -> List[ConversationFlow]:
        """Obtiene todos los flujos activos ordenados por prioridad"""
        try:
            flows = self.model_class.query.filter_by(is_active=True).order_by(
                self.model_class.priority.asc()
            ).all()
            
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
    
    def increment_usage(self, flow_id: str) -> bool:
        """Incrementa el contador de uso de un flujo"""
        try:
            flow = self.get_by_id(flow_id)
            if flow:
                usage_count = (flow.usage_count or 0) + 1
                last_used = datetime.utcnow()
                
                # Usar el método update heredado que funciona perfecto con PostgreSQL
                success = self.update(flow_id, usage_count=usage_count, last_used=last_used)
                if success:
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
            
            # Estadísticas básicas usando query directo
            total_flows = self.model_class.query.count()
            active_flows = self.model_class.query.filter_by(is_active=True).count()
            
            # Flujo más usado
            most_used = self.model_class.query.order_by(
                self.model_class.usage_count.desc()
            ).first()
            
            stats = {
                'total_flows': total_flows,
                'active_flows': active_flows,
                'inactive_flows': total_flows - active_flows,
                'most_used_flow': {
                    'name': most_used.name if most_used else None,
                    'usage_count': most_used.usage_count if most_used else 0
                }
            }
            
            self.logger.info("Estadísticas de flujos obtenidas")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def create_flow(self, flow_data: Dict[str, Any]) -> Optional[ConversationFlow]:
        """
        Crear un nuevo flujo de conversación
        
        Args:
            flow_data: Diccionario con los datos del flujo
            
        Returns:
            ConversationFlow: Flujo creado o None si hay error
        """
        try:
            # Usar el método create heredado que funciona perfecto
            flow = self.create(**flow_data)
            
            if flow:
                self.logger.info(f"Flujo creado: {flow.name} (ID: {flow.id})")
                return flow
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creando flujo: {e}")
            return None
    
    # ===== MÉTODOS SIMPLIFICADOS =====
    # Usar métodos heredados que funcionan perfectamente con PostgreSQL
    
    def update_flow(self, flow_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Actualizar un flujo - VERSIÓN SIMPLIFICADA PARA POSTGRESQL
        """
        try:
            # Con PostgreSQL, el método heredado update() funciona perfectamente
            success = self.update(flow_id, **update_data)
            
            if success:
                self.logger.info(f"Flujo {flow_id} actualizado correctamente")
                return True
            else:
                self.logger.warning(f"No se pudo actualizar flujo {flow_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error actualizando flujo {flow_id}: {e}")
            return False
    
    def delete_flow(self, flow_id: str) -> bool:
        """
        Eliminar un flujo - VERSIÓN SIMPLIFICADA
        """
        try:
            success = self.delete(flow_id)
            
            if success:
                self.logger.info(f"Flujo {flow_id} eliminado correctamente")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando flujo {flow_id}: {e}")
            return False
    
    def get_all_flows(self) -> List[ConversationFlow]:
        """Obtener todos los flujos"""
        try:
            flows = self.get_all()
            self.logger.info(f"Obtenidos {len(flows)} flujos totales")
            return flows
        except Exception as e:
            self.logger.error(f"Error obteniendo todos los flujos: {e}")
            return []
    
    def activate_flow(self, flow_id: str) -> bool:
        """Activar un flujo"""
        return self.update_flow(flow_id, {'is_active': True})
    
    def deactivate_flow(self, flow_id: str) -> bool:
        """Desactivar un flujo"""
        return self.update_flow(flow_id, {'is_active': False})
    
    def set_as_default(self, flow_id: str) -> bool:
        """Establecer un flujo como por defecto"""
        try:
            # Primero, quitar default de todos los flujos
            all_flows = self.get_all()
            for flow in all_flows:
                if flow.is_default:
                    self.update(flow.id, is_default=False)
            
            # Luego, establecer el nuevo como default
            success = self.update_flow(flow_id, {'is_default': True, 'is_active': True})
            
            if success:
                self.logger.info(f"Flujo {flow_id} establecido como por defecto")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error estableciendo flujo por defecto {flow_id}: {e}")
            return False
