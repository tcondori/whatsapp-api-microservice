"""
Repositorio simplificado para gestión de contextos de conversación (versión de prueba)
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from database.models import ConversationContext, ChatbotInteraction
from app.repositories.base_repo import BaseRepository

class ConversationRepository(BaseRepository):
    """Repositorio para gestión de contextos de conversación"""
    
    def __init__(self):
        super().__init__(ConversationContext)
    
    def get_or_create_context(self, phone_number: str) -> ConversationContext:
        """Obtiene o crea el contexto de conversación para un usuario"""
        try:
            # Buscar contexto existente
            context = self.model.query.filter_by(phone_number=phone_number).first()
            
            if context:
                return context
            
            # Crear nuevo contexto
            context = ConversationContext(
                phone_number=phone_number,
                context_data={},
                last_interaction=datetime.utcnow(),
                session_count=1
            )
            
            context = self.create(context)
            return context
        except Exception as e:
            print(f"Error obteniendo/creando contexto para {phone_number}: {e}")
            raise
    
    def get_by_phone_number(self, phone_number: str) -> Optional[ConversationContext]:
        """Obtiene contexto por número de teléfono"""
        try:
            context = self.model.query.filter_by(phone_number=phone_number).first()
            return context
        except Exception as e:
            print(f"Error obteniendo contexto por teléfono {phone_number}: {e}")
            return None
    
    def update_context_data(self, phone_number: str, context_data: Dict[str, Any]) -> bool:
        """Actualiza los datos de contexto de un usuario"""
        try:
            context = self.get_or_create_context(phone_number)
            
            # Merge con datos existentes
            if context.context_data:
                context.context_data.update(context_data)
            else:
                context.context_data = context_data
            
            context.last_interaction = datetime.utcnow()
            
            self.update(context)
            return True
        except Exception as e:
            print(f"Error actualizando contexto para {phone_number}: {e}")
            return False

class ChatbotInteractionRepository(BaseRepository):
    """Repositorio para gestión de interacciones del chatbot"""
    
    def __init__(self):
        super().__init__(ChatbotInteraction)
    
    def log_interaction(self, phone_number: str, message_in: str, message_out: str,
                       response_type: str, processing_time_ms: int, 
                       flow_id: Optional[int] = None, **kwargs) -> ChatbotInteraction:
        """Registra una interacción del chatbot"""
        try:
            interaction = ChatbotInteraction(
                phone_number=phone_number,
                message_in=message_in[:500],  # Limitar tamaño
                message_out=message_out[:500] if message_out else None,
                response_type=response_type,
                processing_time_ms=processing_time_ms,
                flow_id=flow_id,
                confidence_score=kwargs.get('confidence_score'),
                tokens_used=kwargs.get('tokens_used')
            )
            
            interaction = self.create(interaction)
            return interaction
        except Exception as e:
            print(f"Error registrando interacción: {e}")
            raise
    
    def get_user_history(self, phone_number: str, limit: int = 10) -> List[ChatbotInteraction]:
        """Obtiene el historial de interacciones de un usuario"""
        try:
            interactions = self.model.query\
                                    .filter_by(phone_number=phone_number)\
                                    .order_by(self.model.created_at.desc())\
                                    .limit(limit)\
                                    .all()
            return interactions
        except Exception as e:
            print(f"Error obteniendo historial para {phone_number}: {e}")
            return []
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Obtiene analíticas de interacciones del chatbot"""
        try:
            from sqlalchemy import func
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Estadísticas básicas
            stats = self.db.session.query(
                func.count(self.model.id).label('total_interactions'),
                func.avg(self.model.processing_time_ms).label('avg_processing_time'),
                func.count(func.distinct(self.model.phone_number)).label('unique_users')
            ).filter(self.model.created_at >= cutoff_date).first()
            
            # Por tipo de respuesta
            by_type = self.db.session.query(
                self.model.response_type,
                func.count(self.model.id).label('count')
            ).filter(self.model.created_at >= cutoff_date)\
             .group_by(self.model.response_type)\
             .all()
            
            return {
                'period_days': days,
                'total_interactions': stats.total_interactions or 0,
                'avg_processing_time_ms': round(stats.avg_processing_time or 0, 2),
                'unique_users': stats.unique_users or 0,
                'by_response_type': {item.response_type: item.count for item in by_type}
            }
        except Exception as e:
            print(f"Error obteniendo analíticas: {e}")
            return {}
