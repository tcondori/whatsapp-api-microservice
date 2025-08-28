# app/repositories/chatbot_interaction_repository.py
# filepath: e:\DSW\proyectos\proy04\app\repositories\chatbot_interaction_repository.py

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from database.models import ChatbotInteraction, ConversationContext
from app.repositories.base_repo import BaseRepository
from app.utils.logger import WhatsAppLogger

class ChatbotInteractionRepository(BaseRepository):
    """Repositorio para gestión de interacciones del chatbot"""
    
    def __init__(self):
        super().__init__(ChatbotInteraction)
        self.logger = WhatsAppLogger.get_logger('chatbot_interaction_repo')
    
    def create_interaction(self, phone_number: str, user_message: str, 
                          bot_response: str, context_data: Dict[str, Any] = None) -> Optional[ChatbotInteraction]:
        """Crea una nueva interacción del chatbot"""
        try:
            interaction_data = {
                'phone_number': phone_number,
                'message_in': user_message,
                'message_out': bot_response,
                'response_type': 'text',  # Valor por defecto
                'processing_time_ms': 0   # Valor por defecto
            }
            
            interaction = self.create(interaction_data)
            if interaction:
                self.logger.info(f"Interacción creada para {phone_number}")
            return interaction
            
        except Exception as e:
            self.logger.error(f"Error creando interacción para {phone_number}: {e}")
            return None

    def log_interaction(self, phone_number: str, user_message: str, bot_response: str,
                       response_type: str = 'text', processing_time_ms: int = 0,
                       flow_id: Optional[int] = None, **kwargs) -> Optional[ChatbotInteraction]:
        """Registra una interacción del chatbot con metadatos adicionales"""
        try:
            # Crear datos usando los nombres correctos del modelo
            interaction_data = {
                'phone_number': phone_number,
                'message_in': user_message,
                'message_out': bot_response,
                'response_type': response_type,
                'processing_time_ms': processing_time_ms,
                'flow_id': flow_id,
                # Metadatos adicionales
                'confidence_score': kwargs.get('confidence_score', 0.0),
                'tokens_used': kwargs.get('tokens_used', 0)
            }
            
            interaction = self.create(interaction_data)
            if interaction:
                self.logger.info(f"Interacción registrada para {phone_number} - Tipo: {response_type}")
            return interaction
            
        except Exception as e:
            self.logger.error(f"Error registrando interacción para {phone_number}: {e}")
            return None
    
    def get_recent_interactions(self, phone_number: str, limit: int = 10) -> List[ChatbotInteraction]:
        """Obtiene las interacciones recientes de un usuario"""
        try:
            interactions = (self.model_class.query
                           .filter_by(phone_number=phone_number)
                           .order_by(self.model_class.created_at.desc())
                           .limit(limit)
                           .all())
            
            self.logger.debug(f"Obtenidas {len(interactions)} interacciones para {phone_number}")
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error obteniendo interacciones para {phone_number}: {e}")
            return []
    
    def get_conversation_history(self, phone_number: str, 
                               since: Optional[datetime] = None) -> List[ChatbotInteraction]:
        """Obtiene el historial completo de conversación"""
        try:
            query = self.model_class.query.filter_by(phone_number=phone_number)
            
            if since:
                query = query.filter(self.model_class.created_at >= since)
            
            interactions = query.order_by(self.model_class.created_at.asc()).all()
            
            self.logger.debug(f"Historial obtenido: {len(interactions)} interacciones")
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error obteniendo historial para {phone_number}: {e}")
            return []
    
    def update_response(self, interaction_id: str, new_response: str) -> Optional[ChatbotInteraction]:
        """Actualiza la respuesta de una interacción"""
        try:
            interaction = self.update(interaction_id, bot_response=new_response)
            if interaction:
                self.logger.info(f"Respuesta actualizada para interacción {interaction_id}")
            return interaction
            
        except Exception as e:
            self.logger.error(f"Error actualizando respuesta {interaction_id}: {e}")
            return None
    
    def get_user_stats(self, phone_number: str) -> Dict[str, Any]:
        """Obtiene estadísticas de interacciones del usuario"""
        try:
            total_interactions = (self.model_class.query
                                .filter_by(phone_number=phone_number)
                                .count())
            
            recent_interactions = (self.model_class.query
                                 .filter_by(phone_number=phone_number)
                                 .filter(self.model_class.created_at >= 
                                        datetime.utcnow() - timedelta(days=7))
                                 .count())
            
            last_interaction = (self.model_class.query
                              .filter_by(phone_number=phone_number)
                              .order_by(self.model_class.created_at.desc())
                              .first())
            
            stats = {
                'total_interactions': total_interactions,
                'recent_interactions': recent_interactions,
                'last_interaction': last_interaction.created_at if last_interaction else None,
                'first_interaction': None
            }
            
            # Obtener primera interacción
            first_interaction = (self.model_class.query
                               .filter_by(phone_number=phone_number)
                               .order_by(self.model_class.created_at.asc())
                               .first())
            
            if first_interaction:
                stats['first_interaction'] = first_interaction.created_at
            
            self.logger.debug(f"Estadísticas obtenidas para {phone_number}: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas para {phone_number}: {e}")
            return {
                'total_interactions': 0,
                'recent_interactions': 0,
                'last_interaction': None,
                'first_interaction': None
            }
    
    def cleanup_old_interactions(self, days: int = 30) -> int:
        """Limpia interacciones antiguas"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            old_interactions = (self.model_class.query
                              .filter(self.model_class.created_at < cutoff_date)
                              .all())
            
            count = len(old_interactions)
            
            for interaction in old_interactions:
                self.delete(interaction.id)
            
            self.logger.info(f"Limpiadas {count} interacciones antiguas (>{days} días)")
            return count
            
        except Exception as e:
            self.logger.error(f"Error limpiando interacciones antiguas: {e}")
            return 0
    
    def search_interactions(self, query: str, phone_number: Optional[str] = None,
                           limit: int = 50) -> List[ChatbotInteraction]:
        """Busca interacciones por contenido"""
        try:
            search_query = self.model_class.query
            
            # Filtrar por mensaje del usuario o respuesta del bot usando nombres correctos
            search_filter = (
                self.model_class.message_in.contains(query) |
                self.model_class.message_out.contains(query)
            )
            search_query = search_query.filter(search_filter)
            
            # Filtrar por teléfono si se especifica
            if phone_number:
                search_query = search_query.filter_by(phone_number=phone_number)
            
            # Ordenar por fecha más reciente y limitar resultados
            interactions = (search_query
                           .order_by(self.model_class.created_at.desc())
                           .limit(limit)
                           .all())
            
            self.logger.debug(f"Búsqueda '{query}' encontró {len(interactions)} interacciones")
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error buscando interacciones: {e}")
            return []
