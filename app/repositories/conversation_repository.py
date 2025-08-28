# app/repositories/conversation_repository.py - Versión corregida
# filepath: e:\DSW\proyectos\proy04\app\repositories\conversation_repository_fixed.py

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from database.models import ConversationContext, ChatbotInteraction
from app.repositories.base_repo import BaseRepository
from app.utils.logger import WhatsAppLogger

class ConversationRepository(BaseRepository):
    """Repositorio para gestión de contextos de conversación"""
    
    def __init__(self):
        super().__init__(ConversationContext)
        self.logger = WhatsAppLogger.get_logger('conversation_repo')
    
    def get_or_create_context(self, phone_number: str) -> ConversationContext:
        """Obtiene o crea un contexto de conversación"""
        try:
            context = self.model_class.query.filter_by(phone_number=phone_number).first()
            
            if context:
                # Actualizar última interacción
                context.last_interaction = datetime.utcnow()
                result = self.update(context.id, last_interaction=context.last_interaction)
                if result:
                    self.logger.info(f"Contexto actualizado para {phone_number}")
                    return result
                return context
            else:
                # Crear nuevo contexto
                new_context = self.create(
                    phone_number=phone_number,
                    current_topic='welcome',
                    context_data={},
                    last_interaction=datetime.utcnow()
                )
                self.logger.info(f"Nuevo contexto creado para {phone_number}")
                return new_context
                
        except Exception as e:
            self.logger.error(f"Error obteniendo/creando contexto para {phone_number}: {e}")
            raise
    
    def update_context(self, phone_number: str, topic: str = None, data: dict = None) -> bool:
        """Actualiza el contexto de conversación"""
        try:
            context = self.model_class.query.filter_by(phone_number=phone_number).first()
            
            if not context:
                return False
            
            updates = {
                'last_interaction': datetime.utcnow()
            }
            
            if topic:
                updates['current_topic'] = topic
                
            if data:
                current_data = context.context_data or {}
                current_data.update(data)
                updates['context_data'] = current_data
            
            result = self.update(context.id, **updates)
            if result:
                self.logger.info(f"Contexto actualizado para {phone_number} - Tema: {topic}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error actualizando contexto para {phone_number}: {e}")
            return False
    
    def update_context_data(self, phone_number: str, data: dict = None) -> bool:
        """Actualiza solo los datos del contexto de conversación"""
        return self.update_context(phone_number, topic=None, data=data)
    
    def set_conversation_timeout(self, phone_number: str, timeout_minutes: int = 60):
        """Establece timeout para una conversación"""
        try:
            timeout_time = datetime.utcnow() + timedelta(minutes=timeout_minutes)
            context = self.model_class.query.filter_by(phone_number=phone_number).first()
            
            if context:
                result = self.update(context.id, timeout_at=timeout_time)
                if result:
                    self.logger.info(f"Timeout establecido para {phone_number}: {timeout_time}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error estableciendo timeout para {phone_number}: {e}")
            return False
    
    def close_conversation(self, phone_number: str) -> bool:
        """Cierra una conversación activa"""
        try:
            context = self.model_class.query.filter_by(phone_number=phone_number).first()
            
            if context:
                result = self.update(context.id, 
                                   current_topic='closed',
                                   last_interaction=datetime.utcnow())
                if result:
                    self.logger.info(f"Conversación cerrada para {phone_number}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cerrando conversación para {phone_number}: {e}")
            return False
    
    def delete_context(self, phone_number: str) -> bool:
        """Elimina completamente un contexto de conversación"""
        try:
            context = self.model_class.query.filter_by(phone_number=phone_number).first()
            
            if context:
                result = self.delete(context.id)
                if result:
                    self.logger.info(f"Contexto eliminado para {phone_number}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando contexto para {phone_number}: {e}")
            return False
    
    def cleanup_expired_contexts(self) -> int:
        """Limpia contextos expirados y retorna el número eliminado"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(hours=24)
            
            old_contexts = self.model_class.query.filter(
                self.model_class.last_interaction < cutoff_date
            ).all()
            
            deleted_count = 0
            for context in old_contexts:
                if self.delete(context.id):
                    deleted_count += 1
            
            self.logger.info(f"Limpiados {deleted_count} contextos expirados")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error limpiando contextos expirados: {e}")
            return 0

class ChatbotInteractionRepository(BaseRepository):
    """Repositorio para gestión de interacciones del chatbot"""
    
    def __init__(self):
        super().__init__(ChatbotInteraction)
        self.logger = WhatsAppLogger.get_logger('interaction_repo')
    
    def save_interaction(self, phone_number: str, user_message: str, bot_response: str, 
                        response_type: str, processing_time_ms: int = None) -> ChatbotInteraction:
        """Guarda una nueva interacción del chatbot"""
        try:
            interaction = self.create(
                phone_number=phone_number,
                message_in=user_message,
                message_out=bot_response,
                response_type=response_type,
                processing_time_ms=processing_time_ms or 0
            )
            
            self.logger.info(f"Interacción guardada para {phone_number} - Tipo: {response_type}")
            return interaction
            
        except Exception as e:
            self.logger.error(f"Error guardando interacción para {phone_number}: {e}")
            raise
    
    def log_interaction(self, phone_number: str, user_message: str, bot_response: str, 
                       response_type: str = "chatbot", processing_time_ms: int = None,
                       flow_id: int = None, confidence_score: float = None) -> ChatbotInteraction:
        """
        Alias mejorado para save_interaction con parámetros adicionales
        
        Args:
            phone_number: Número de teléfono del usuario
            user_message: Mensaje del usuario
            bot_response: Respuesta del bot
            response_type: Tipo de respuesta ('chatbot', 'flow', 'default', etc.)
            processing_time_ms: Tiempo de procesamiento en milisegundos
            flow_id: ID del flujo que generó la respuesta (opcional)
            confidence_score: Puntuación de confianza de la respuesta (opcional)
        """
        return self.save_interaction(phone_number, user_message, bot_response, response_type, processing_time_ms)
    
    def get_user_history(self, phone_number: str, limit: int = 10) -> List[ChatbotInteraction]:
        """Obtiene el historial de interacciones de un usuario"""
        try:
            interactions = self.model_class.query\
                                    .filter_by(phone_number=phone_number)\
                                    .order_by(self.model_class.created_at.desc())\
                                    .limit(limit).all()
            
            self.logger.info(f"Obtenido historial para {phone_number}: {len(interactions)} interacciones")
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error obteniendo historial para {phone_number}: {e}")
            return []
    
    def get_interaction_statistics(self, hours_back: int = 24) -> Dict[str, Any]:
        """Obtiene estadísticas de interacciones"""
        try:
            from sqlalchemy import func
            from database.connection import get_db_session
            
            cutoff_date = datetime.utcnow() - timedelta(hours=hours_back)
            session = get_db_session()
            
            # Estadísticas generales
            general_stats = session.query(
                func.count(self.model_class.id).label('total_interactions'),
                func.avg(self.model_class.processing_time_ms).label('avg_processing_time'),
                func.count(func.distinct(self.model_class.phone_number)).label('unique_users')
            ).filter(self.model_class.created_at >= cutoff_date).first()
            
            # Por tipo de respuesta
            response_types = session.query(
                self.model_class.response_type,
                func.count(self.model_class.id).label('count')
            ).filter(self.model_class.created_at >= cutoff_date)\
             .group_by(self.model_class.response_type)\
             .all()
            
            return {
                'total_interactions': general_stats.total_interactions or 0,
                'avg_processing_time': float(general_stats.avg_processing_time or 0),
                'unique_users': general_stats.unique_users or 0,
                'response_types': {rt.response_type: rt.count for rt in response_types},
                'period_hours': hours_back
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
