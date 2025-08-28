# app/services/chatbot_service.py - Nuevo archivo
# filepath: e:\DSW\proyectos\proy04\app\services\chatbot_service.py

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from app.services.rivescript_service import RiveScriptService
from app.repositories.conversation_repository import ConversationRepository, ChatbotInteractionRepository
from app.repositories.flow_repository import FlowRepository
from app.utils.logger import WhatsAppLogger
from config.default import DefaultConfig

class ChatbotService:
    """Servicio principal del chatbot que coordina flujos y respuestas automáticas"""
    
    def __init__(self):
        self.rivescript_service = None
        self.flow_repo = None
        self.context_repo = None
        self.interaction_repo = None
        self.logger = WhatsAppLogger.get_logger('chatbot_service')
        self._initialized = False
    
    def _ensure_initialized(self) -> bool:
        """
        Asegura que el servicio esté inicializado con contexto de aplicación
        """
        from flask import has_app_context
        
        if not has_app_context():
            self.logger.warning("No hay contexto de aplicación disponible para ChatbotService")
            return False
            
        if self._initialized:
            return True
            
        try:
            # Inicializar servicios dentro del contexto de aplicación
            self.rivescript_service = RiveScriptService()
            self.flow_repo = FlowRepository()
            self.context_repo = ConversationRepository()
            self.interaction_repo = ChatbotInteractionRepository()
            
            self._initialized = True
            self.logger.info("ChatbotService inicializado correctamente con contexto de aplicación")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando ChatbotService: {e}")
            return False
    
    def process_message(self, phone_number: str, message: str, 
                       message_record: Optional[Any] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante y genera respuesta automática
        
        Args:
            phone_number: Número de teléfono del usuario
            message: Mensaje entrante
            message_record: Registro del mensaje en BD (opcional)
            
        Returns:
            dict: Respuesta generada con metadata
        """
        # Asegurar inicialización antes de procesar
        if not self._ensure_initialized():
            return {
                'response': "Servicio no disponible temporalmente. Intenta más tarde.",
                'type': 'service_error',
                'error': 'No application context available',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Procesando mensaje de {phone_number}: {message[:50]}...")
            
            # 1. Limpiar número de teléfono
            clean_phone = self._clean_phone_number(phone_number)
            
            # 2. NUEVA LÓGICA: Verificar y manejar timeout de conversación
            context = self.context_repo.get_or_create_context(clean_phone)
            
            if self._is_conversation_expired(context):
                self.logger.info(f"Conversación expirada para {clean_phone}, reiniciando sesión")
                return self._restart_conversation_session(context, message, start_time)
            
            # 3. Verificar comando de cierre explícito
            if self._is_close_command(message):
                self.logger.info(f"Comando de cierre recibido de {clean_phone}")
                return self._close_conversation(context, start_time)
            
            # 4. Intentar respuesta con flujos RiveScript
            flow_response = self.rivescript_service.get_response(clean_phone, message)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            if flow_response:
                self.logger.info(f"Respuesta generada por flujo: {flow_response['type']}")
                
                # Registrar interacción exitosa
                self._log_interaction(
                    phone_number=clean_phone,
                    user_message=message,
                    bot_response=flow_response.get('response'),
                    intent=flow_response.get('type'),
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
                self.logger.info(f"No hay match en flujos para: {message[:30]}...")
                
                default_response = self._get_default_response(message)
                
                # Registrar interacción sin match
                self._log_interaction(
                    phone_number=clean_phone,
                    user_message=message,
                    bot_response=default_response.get('response'),
                    intent=default_response.get('type'),
                    processing_time_ms=processing_time
                )
                
                default_response['processing_time_ms'] = processing_time
                default_response['timestamp'] = datetime.utcnow().isoformat()
                default_response['phone_number'] = clean_phone
                
                return default_response
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Error procesando mensaje de {phone_number}: {e}")
            
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
                user_message=message,
                bot_response=error_response.get('response'),
                intent='error',
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
    
    def _log_interaction(self, phone_number: str, user_message: str, bot_response: str,
                        intent: str, processing_time_ms: int, 
                        flow_id: Optional[str] = None, **kwargs):
        """Registra la interacción del chatbot en la base de datos"""
        try:
            self.interaction_repo.log_interaction(
                phone_number=phone_number,
                user_message=user_message,
                bot_response=bot_response,
                intent=intent,
                processing_time_ms=processing_time_ms,
                flow_id=flow_id,
                **kwargs
            )
            
        except Exception as e:
            self.logger.error(f"Error guardando interacción del chatbot: {e}")
    
    def test_chatbot_response(self, message: str, phone_number: str = "test_user", 
                             flow_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Prueba el chatbot sin afectar contextos reales
        
        Args:
            message: Mensaje de prueba
            phone_number: Número de prueba (debe empezar con "test_")
            flow_id: ID de flujo específico para probar
            
        Returns:
            dict: Respuesta de prueba
        """
        # Asegurar inicialización antes de probar
        if not self._ensure_initialized():
            return {
                'error': 'Servicio no inicializado - sin contexto de aplicación',
                'type': 'test_error'
            }
        
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
            self.logger.error(f"Error en prueba de chatbot: {e}")
            return {
                'error': f'Error en prueba: {str(e)}',
                'type': 'test_error'
            }
    
    def get_user_context(self, phone_number: str) -> Dict[str, Any]:
        """Obtiene el contexto actual de un usuario"""
        if not self._ensure_initialized():
            return {'error': 'Servicio no inicializado - sin contexto de aplicación'}
            
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
            self.logger.error(f"Error obteniendo contexto de usuario {phone_number}: {e}")
            return {'error': str(e)}
    
    def get_user_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene el historial de interacciones de un usuario"""
        if not self._ensure_initialized():
            return []
            
        try:
            clean_phone = self._clean_phone_number(phone_number)
            interactions = self.interaction_repo.get_user_history(clean_phone, limit)
            
            return [interaction.to_dict() for interaction in interactions]
            
        except Exception as e:
            self.logger.error(f"Error obteniendo historial de {phone_number}: {e}")
            return []
    
    def get_chatbot_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Obtiene analíticas del chatbot"""
        if not self._ensure_initialized():
            return {'error': 'Servicio no inicializado - sin contexto de aplicación'}
            
        try:
            analytics = self.interaction_repo.get_analytics(days)
            flow_stats = self.flow_repo.get_flow_statistics()
            
            return {
                'interactions': analytics,
                'flows': flow_stats,
                'period_days': days
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo analíticas del chatbot: {e}")
            return {'error': str(e)}
    
    def is_chatbot_enabled(self) -> bool:
        """Verifica si el chatbot está habilitado globalmente"""
        try:
            # Verificar configuración (se puede implementar en config)
            from config.default import DefaultConfig
            return getattr(DefaultConfig, 'CHATBOT_ENABLED', True)
        except:
            return True  # Por defecto habilitado
    
    # ========================================
    # NUEVOS MÉTODOS DE CONTROL DE CICLO DE VIDA
    # ========================================
    
    def _is_conversation_expired(self, context) -> bool:
        """
        Verifica si una conversación ha expirado por timeout
        
        Args:
            context: Contexto de conversación
            
        Returns:
            bool: True si la conversación ha expirado
        """
        try:
            if not context or not context.last_interaction:
                return False
            
            timeout_hours = DefaultConfig.CHATBOT_SESSION_TIMEOUT_HOURS
            elapsed = datetime.utcnow() - context.last_interaction
            elapsed_hours = elapsed.total_seconds() / 3600
            
            is_expired = elapsed_hours > timeout_hours
            
            if is_expired:
                self.logger.info(f"Conversación expirada: {elapsed_hours:.2f}h > {timeout_hours}h")
            
            return is_expired
            
        except Exception as e:
            self.logger.error(f"Error verificando expiración de conversación: {e}")
            return False
    
    def _restart_conversation_session(self, context, message: str, start_time: float) -> Dict[str, Any]:
        """
        Reinicia una sesión de conversación expirada
        
        Args:
            context: Contexto de conversación
            message: Mensaje que reinicia la conversación
            start_time: Tiempo de inicio del procesamiento
            
        Returns:
            dict: Respuesta de reinicio de sesión
        """
        try:
            # Actualizar contexto para nueva sesión
            context.session_count = context.session_count + 1 if context.session_count else 1
            context.last_interaction = datetime.utcnow()
            context.current_topic = "session_restart"
            context.context_data = {'restarted': True, 'previous_message': message}
            
            # Guardar cambios
            self.context_repo.update_context(context.phone_number, {
                'session_count': context.session_count,
                'current_topic': context.current_topic,
                'context_data': context.context_data
            })
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Generar respuesta de reinicio
            restart_response = {
                'response': f"¡Hola de nuevo! Ha pasado tiempo desde nuestra última conversación. ¿En qué te puedo ayudar hoy?",
                'type': 'session_restart',
                'confidence_score': 1.0,
                'processing_time_ms': processing_time,
                'metadata': {
                    'session_count': context.session_count,
                    'restart_reason': 'timeout',
                    'previous_interaction': context.last_interaction.isoformat() if context.last_interaction else None
                }
            }
            
            # Registrar evento de reinicio
            self.interaction_repo.log_interaction(
                phone_number=context.phone_number,
                user_message=message,
                bot_response=restart_response['response'],
                response_type='session_restart',
                processing_time_ms=processing_time,
                flow_id=context.flow_id,
                confidence_score=1.0
            )
            
            self.logger.info(f"CONVERSATION_RESTARTED: {context.phone_number} - session_{context.session_count}")
            
            return restart_response
            
        except Exception as e:
            self.logger.error(f"Error reiniciando sesión: {e}")
            return self._generate_fallback_response("Error reiniciando conversación", start_time)
    
    def _is_close_command(self, message: str) -> bool:
        """
        Verifica si el mensaje es un comando de cierre de conversación
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            bool: True si es comando de cierre
        """
        close_commands = [
            'cerrar conversacion', 'cerrar', 'terminar', 'salir', 'bye', 'adios', 'adiós',
            'hasta luego', 'nos vemos', 'chau', 'goodbye', 'finish', 'end', 'stop',
            'cerrar conversación', 'finalizar', 'acabar'
        ]
        
        message_lower = message.lower().strip()
        
        return any(command in message_lower for command in close_commands)
    
    def _close_conversation(self, context, start_time: float) -> Dict[str, Any]:
        """
        Cierra explícitamente una conversación
        
        Args:
            context: Contexto de conversación
            start_time: Tiempo de inicio del procesamiento
            
        Returns:
            dict: Respuesta de cierre de conversación
        """
        try:
            processing_time = int((time.time() - start_time) * 1000)
            
            # Respuesta de cierre
            close_response = {
                'response': "¡Hasta luego! Tu conversación ha sido cerrada. ¡Gracias por contactarnos! Para iniciar una nueva conversación, envía cualquier mensaje.",
                'type': 'conversation_closed',
                'confidence_score': 1.0,
                'processing_time_ms': processing_time,
                'metadata': {
                    'session_count': context.session_count if context else 0,
                    'close_reason': 'explicit_command'
                }
            }
            
            # Registrar evento de cierre
            self.interaction_repo.log_interaction(
                phone_number=context.phone_number,
                user_message="[COMANDO_CIERRE]",
                bot_response=close_response['response'],
                response_type='conversation_closed',
                processing_time_ms=processing_time,
                flow_id=context.flow_id if context else None,
                confidence_score=1.0
            )
            
            # Eliminar contexto (conversación cerrada)
            if context:
                self.context_repo.delete_context(context.phone_number)
            
            self.logger.info(f"CONVERSATION_CLOSED: {context.phone_number if context else 'unknown'} - explicit_close")
            
            return close_response
            
        except Exception as e:
            self.logger.error(f"Error cerrando conversación: {e}")
            return self._generate_fallback_response("Conversación cerrada", start_time)
    
    def _generate_fallback_response(self, message: str, start_time: float) -> Dict[str, Any]:
        """
        Genera una respuesta de emergencia cuando hay errores
        
        Args:
            message: Mensaje contextual del error
            start_time: Tiempo de inicio del procesamiento
            
        Returns:
            dict: Respuesta de emergencia
        """
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'response': "Lo siento, ha ocurrido un error procesando tu mensaje. Por favor intenta nuevamente.",
            'type': 'fallback',
            'error_context': message,
            'processing_time_ms': processing_time,
            'timestamp': datetime.utcnow().isoformat(),
            'confidence_score': 0.1
        }