"""
Servicio principal del chatbot para pruebas (versión simplificada)
"""
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.services.rivescript_service_test import RiveScriptService
from app.repositories.conversation_repository_test import ConversationRepository, ChatbotInteractionRepository
from app.repositories.flow_repository_test import FlowRepository

class ChatbotService:
    """Servicio principal del chatbot que coordina flujos y respuestas automáticas"""
    
    def __init__(self):
        self.rivescript_service = RiveScriptService()
        self.flow_repo = FlowRepository()
        self.context_repo = ConversationRepository()
        self.interaction_repo = ChatbotInteractionRepository()
    
    def process_message(self, phone_number: str, message: str, 
                       message_record: Optional[Any] = None) -> Dict[str, Any]:
        """Procesa un mensaje entrante y genera respuesta automática"""
        start_time = time.time()
        
        try:
            print(f"Procesando mensaje de {phone_number}: {message[:50]}...")
            
            # 1. Limpiar número de teléfono
            clean_phone = self._clean_phone_number(phone_number)
            
            # 2. Intentar respuesta con flujos RiveScript
            flow_response = self.rivescript_service.get_response(clean_phone, message)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            if flow_response:
                print(f"Respuesta generada por flujo: {flow_response['type']}")
                
                # Registrar interacción exitosa
                self._log_interaction(
                    phone_number=clean_phone,
                    message_in=message,
                    message_out=flow_response.get('response'),
                    response_type=flow_response.get('type'),
                    processing_time_ms=processing_time,
                    flow_id=flow_response.get('flow_id'),
                    confidence_score=flow_response.get('confidence_score')
                )
                
                flow_response['processing_time_ms'] = processing_time
                flow_response['timestamp'] = datetime.utcnow().isoformat()
                flow_response['phone_number'] = clean_phone
                
                return flow_response
            else:
                # 3. Si no hay match en flujos, usar respuesta por defecto
                print(f"No hay match en flujos para: {message[:30]}...")
                
                default_response = self._get_default_response(message)
                
                # Registrar interacción sin match
                self._log_interaction(
                    phone_number=clean_phone,
                    message_in=message,
                    message_out=default_response.get('response'),
                    response_type=default_response.get('type'),
                    processing_time_ms=processing_time
                )
                
                default_response['processing_time_ms'] = processing_time
                default_response['timestamp'] = datetime.utcnow().isoformat()
                default_response['phone_number'] = clean_phone
                
                return default_response
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            print(f"Error procesando mensaje de {phone_number}: {e}")
            
            error_response = {
                'response': "Lo siento, ha ocurrido un error procesando tu mensaje. Por favor intenta nuevamente.",
                'type': 'error',
                'error': str(e),
                'processing_time_ms': processing_time,
                'timestamp': datetime.utcnow().isoformat(),
                'phone_number': self._clean_phone_number(phone_number)
            }
            
            # Registrar error
            self._log_interaction(
                phone_number=self._clean_phone_number(phone_number),
                message_in=message,
                message_out=error_response.get('response'),
                response_type='error',
                processing_time_ms=processing_time
            )
            
            return error_response
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """Limpia el número de teléfono para consistencia"""
        if not phone_number:
            return phone_number
        
        # Remover caracteres no numéricos excepto +
        clean = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Asegurar que empiece con +
        if clean and not clean.startswith('+'):
            clean = '+' + clean
        
        return clean
    
    def _get_default_response(self, message: str) -> Dict[str, Any]:
        """Respuesta por defecto cuando no hay match en flujos"""
        
        # Respuestas basadas en palabras clave simples
        message_lower = message.lower()
        
        # Saludos
        if any(greeting in message_lower for greeting in ['hola', 'hello', 'hi', 'buenos días', 'buenas tardes', 'buenas noches']):
            return {
                'response': '¡Hola! Gracias por contactarnos. En breve un agente te atenderá.',
                'type': 'default_greeting',
                'confidence_score': 0.7
            }
        
        # Despedidas
        if any(goodbye in message_lower for goodbye in ['adiós', 'adios', 'chau', 'bye', 'gracias']):
            return {
                'response': '¡Hasta luego! Si necesitas ayuda adicional, no dudes en contactarnos nuevamente.',
                'type': 'default_goodbye',
                'confidence_score': 0.7
            }
        
        # Preguntas frecuentes
        if any(faq in message_lower for faq in ['horario', 'hora', 'abierto', 'cerrado']):
            return {
                'response': 'Nuestro horario de atención es de lunes a viernes de 9:00 AM a 6:00 PM. ¿En qué más puedo ayudarte?',
                'type': 'default_faq',
                'confidence_score': 0.6
            }
        
        if any(price in message_lower for price in ['precio', 'costo', 'cuanto', 'valor']):
            return {
                'response': 'Para información sobre precios, un agente especializado te contactará pronto con toda la información detallada.',
                'type': 'default_faq',
                'confidence_score': 0.6
            }
        
        # Respuesta genérica por defecto
        default_responses = [
            "Gracias por tu mensaje. Un agente te contactará pronto.",
            "Hemos recibido tu consulta. Te responderemos a la brevedad.",
            "Entendemos tu consulta. Por favor espera mientras te conectamos con soporte."
        ]
        
        # Seleccionar respuesta consistente basada en hash del mensaje
        response_index = abs(hash(message)) % len(default_responses)
        
        return {
            'response': default_responses[response_index],
            'type': 'default_fallback',
            'confidence_score': 0.3
        }
    
    def _log_interaction(self, phone_number: str, message_in: str, message_out: str,
                        response_type: str, processing_time_ms: int, 
                        flow_id: Optional[int] = None, **kwargs):
        """Registra la interacción del chatbot en la base de datos"""
        try:
            self.interaction_repo.log_interaction(
                phone_number=phone_number,
                message_in=message_in,
                message_out=message_out,
                response_type=response_type,
                processing_time_ms=processing_time_ms,
                flow_id=flow_id,
                **kwargs
            )
            
        except Exception as e:
            print(f"Error guardando interacción del chatbot: {e}")
    
    def test_chatbot_response(self, message: str, phone_number: str = "test_user", 
                             flow_id: Optional[int] = None) -> Dict[str, Any]:
        """Prueba el chatbot sin afectar contextos reales"""
        try:
            # Asegurar que es un número de test
            if not phone_number.startswith("test_"):
                phone_number = f"test_{phone_number}"
            
            if flow_id:
                # Probar flujo específico
                flow = self.flow_repo.get_by_id(flow_id)
                if not flow:
                    return {
                        'error': f'Flujo con ID {flow_id} no encontrado',
                        'type': 'test_error'
                    }
                
                test_response = self.rivescript_service.test_flow_response(
                    flow.rivescript_content, 
                    message
                )
                
                test_response['flow_id'] = flow_id
                test_response['flow_name'] = flow.name
                test_response['type'] = 'test_flow'
                
                return test_response
            else:
                # Probar sistema completo en modo test
                response = self.process_message(phone_number, message)
                response['type'] = f"test_{response.get('type', 'unknown')}"
                
                return response
                
        except Exception as e:
            print(f"Error en prueba de chatbot: {e}")
            return {
                'error': f'Error en prueba: {str(e)}',
                'type': 'test_error'
            }
    
    def get_user_context(self, phone_number: str) -> Dict[str, Any]:
        """Obtiene el contexto actual de un usuario"""
        try:
            clean_phone = self._clean_phone_number(phone_number)
            context = self.context_repo.get_by_phone_number(clean_phone)
            
            if context:
                return context.to_dict()
            
            return {
                'phone_number': clean_phone,
                'context_data': {},
                'current_topic': None,
                'last_interaction': None,
                'flow_id': None,
                'session_count': 0
            }
            
        except Exception as e:
            print(f"Error obteniendo contexto de usuario {phone_number}: {e}")
            return {'error': str(e)}
    
    def get_user_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene el historial de interacciones de un usuario"""
        try:
            clean_phone = self._clean_phone_number(phone_number)
            interactions = self.interaction_repo.get_user_history(clean_phone, limit)
            
            return [interaction.to_dict() for interaction in interactions]
            
        except Exception as e:
            print(f"Error obteniendo historial de {phone_number}: {e}")
            return []
    
    def get_chatbot_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Obtiene analíticas del chatbot"""
        try:
            analytics = self.interaction_repo.get_analytics(days)
            flow_stats = self.flow_repo.get_flow_statistics()
            
            return {
                'interactions': analytics,
                'flows': flow_stats,
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error obteniendo analíticas del chatbot: {e}")
            return {'error': str(e)}
