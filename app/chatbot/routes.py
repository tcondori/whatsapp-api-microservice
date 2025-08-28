# app/chatbot/routes.py - Rutas del simulador de chat
# filepath: e:\DSW\proyectos\proy04\app\chatbot\routes.py

"""
Rutas integradas del simulador de chat con arquitectura enterprise completa
Integra el simulador web con los servicios principales del sistema
"""

from flask import render_template, request, jsonify, session, current_app
from datetime import datetime
import uuid
import traceback

from . import chatbot_bp
from app.services.chatbot_service import ChatbotService
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.chatbot_interaction_repository import ChatbotInteractionRepository
from app.utils.logger import WhatsAppLogger

# Configurar logger
logger = WhatsAppLogger.get_logger('chatbot_simulator_integrated')

@chatbot_bp.route('/', strict_slashes=False)
@chatbot_bp.route('', strict_slashes=False)
def index():
    """Página principal del simulador de chat"""
    try:
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error cargando template chat: {e}")
        return f"Error cargando simulador: {str(e)}", 500

@chatbot_bp.route('/new-session')
def new_session():
    """Crea nueva sesión usando arquitectura enterprise"""
    try:
        # Generar número de teléfono único para simulación web
        phone_base = "+59598"
        session_suffix = str(uuid.uuid4())[:6]
        phone_number = f"{phone_base}{session_suffix}"
        
        # Almacenar en sesión web
        session['phone_number'] = phone_number
        session['session_id'] = str(uuid.uuid4())
        
        logger.info(f"Nueva sesión simulador creada: {phone_number}")
        
        # Inicializar contexto en repositorio si tenemos BD disponible
        try:
            with current_app.app_context():
                conversation_repo = ConversationRepository()
                context = conversation_repo.get_or_create_context(phone_number)
                logger.info(f"Contexto inicializado para {phone_number}")
        except Exception as db_error:
            logger.warning(f"BD no disponible, funcionando en modo simulación: {db_error}")
        
        return jsonify({
            'status': 'success',
            'session_id': session['session_id'],
            'phone_number': phone_number,
            'message': '¡Hola! Bienvenido al simulador de chat de WhatsApp. ¿En qué puedo ayudarte?'
        })
    
    except Exception as e:
        logger.error(f"Error creando nueva sesión: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error al crear sesión: {str(e)}'
        }), 500

@chatbot_bp.route('/send-message', methods=['POST'])
def send_message():
    """Procesa mensaje usando ChatbotService enterprise completo"""
    start_time = datetime.now()
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Mensaje requerido'
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Mensaje no puede estar vacío'
            }), 400
        
        # Obtener número de teléfono de la sesión
        phone_number = session.get('phone_number')
        if not phone_number:
            # Crear nueva sesión si no existe
            phone_base = "+59598"
            session_suffix = str(uuid.uuid4())[:6]
            phone_number = f"{phone_base}{session_suffix}"
            session['phone_number'] = phone_number
            session['session_id'] = str(uuid.uuid4())
        
        logger.info(f"Procesando mensaje de {phone_number}: {user_message}")
        
        # USAR EL SERVICIO ENTERPRISE COMPLETO
        try:
            with current_app.app_context():
                chatbot_service = ChatbotService()
                bot_response = chatbot_service.process_message(phone_number, user_message)
            
            # Procesar respuesta del servicio enterprise
            if isinstance(bot_response, dict):
                bot_message = bot_response.get('response', 'Error procesando mensaje')
                bot_type = bot_response.get('type', 'response')
                processing_time = bot_response.get('processing_time_ms', 0)
                confidence_score = bot_response.get('confidence_score', 0)
                flow_id = bot_response.get('flow_id')
                
                logger.info(f"Respuesta generada por servicio enterprise - Tipo: {bot_type}, Tiempo: {processing_time}ms")
                
            else:
                # Fallback para respuestas simples
                bot_message = str(bot_response) if bot_response else "Error procesando mensaje"
                bot_type = 'fallback'
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                confidence_score = 0.5
                flow_id = None
                
                logger.info(f"Respuesta fallback generada")
                
        except Exception as service_error:
            logger.error(f"Error en servicio enterprise: {service_error}")
            
            # Modo simulación cuando el servicio no está disponible
            bot_message = _generate_simulation_response(user_message)
            bot_type = 'simulation'
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            confidence_score = 0.3
            flow_id = None
            
            logger.info("Funcionando en modo simulación")
        
        # Logging seguro con encoding
        safe_message = user_message.encode('utf-8', errors='replace').decode('utf-8')
        safe_response = bot_message[:100].encode('utf-8', errors='replace').decode('utf-8')
        
        logger.info(f"Mensaje procesado - Usuario: {safe_message} | Bot: {safe_response}...")
        
        # Preparar respuesta completa
        response_data = {
            'status': 'success',
            'user_message': {
                'text': user_message,
                'timestamp': start_time.isoformat(),
                'sender': 'user',
                'phone_number': phone_number
            },
            'bot_message': {
                'text': bot_message,
                'timestamp': datetime.now().isoformat(),
                'sender': 'bot',
                'type': bot_type,
                'confidence_score': confidence_score,
                'processing_time_ms': round(processing_time, 2),
                'flow_id': flow_id
            },
            'session_info': {
                'session_id': session.get('session_id'),
                'phone_number': phone_number,
                'mode': 'enterprise' if 'service_error' not in locals() else 'simulation'
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error crítico procesando mensaje: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'status': 'error',
            'message': 'Lo siento, ha ocurrido un error procesando tu mensaje. Por favor intenta nuevamente.',
            'error_details': str(e) if current_app.debug else None
        }), 500

def _generate_simulation_response(message: str) -> str:
    """Genera respuesta simulada cuando los servicios no están disponibles"""
    message_lower = message.lower()
    
    # Respuestas específicas para testing
    if any(word in message_lower for word in ['hola', 'hello', 'hi', 'buenos']):
        return ("¡Hola! Bienvenido al simulador de chat de WhatsApp.<br><br>"
                "¿En qué puedo ayudarte hoy?<br><br>"
                "1. Ventas - Información de productos<br>"
                "2. Soporte Técnico - Ayuda especializada<br>"
                "3. Recursos Humanos - Consultas de empleados<br><br>"
                "Escribe el número o describe tu consulta.")
    
    elif any(word in message_lower for word in ['soporte', 'tecnico', 'technical', 'ayuda', 'problema']):
        return ("Hola, soy el asistente de **Soporte Técnico** 🛠️<br><br>"
                "¿Con qué puedo ayudarte hoy?<br><br>"
                "1️⃣ Problemas de conexión<br>"
                "2️⃣ Errores de la aplicación<br>"
                "3️⃣ Problemas de rendimiento<br>"
                "4️⃣ Configuración de cuenta<br>"
                "5️⃣ Hablar con un técnico<br><br>"
                "Escribe el número o describe tu problema.")
    
    elif any(word in message_lower for word in ['ventas', 'productos', 'comprar', 'cotizar']):
        return ("¡Perfecto! Te conectamos con nuestro equipo de **Ventas** 💼<br><br>"
                "¿Qué te interesa?<br><br>"
                "1️⃣ Consultar precios<br>"
                "2️⃣ Información de productos<br>"
                "3️⃣ Solicitar cotización<br>"
                "4️⃣ Hablar con ejecutivo<br><br>"
                "Escribe el número de tu opción.")
    
    elif message_lower in ['1', '2', '3', '4', '5']:
        responses = {
            '1': "Perfecto, para la opción 1. Te ayudo con eso inmediatamente.",
            '2': "Excelente elección, opción 2. Procesando tu solicitud...",
            '3': "Opción 3 seleccionada. Te proporciono la información correspondiente.",
            '4': "Has elegido la opción 4. Te conecto con el área especializada.",
            '5': "Opción 5 confirmada. Te transfiero con un agente humano."
        }
        return responses.get(message_lower, "Opción procesada correctamente.")
    
    else:
        return ("Gracias por tu mensaje. He registrado tu consulta.<br><br>"
                "Para ayudarte mejor, puedes escribir:<br>"
                "• 'soporte tecnico' para ayuda especializada<br>"
                "• 'ventas' para información comercial<br>"
                "• 'menu' para ver todas las opciones<br><br>"
                "¿En qué más puedo ayudarte?")

@chatbot_bp.route('/get-history')
def get_history():
    """Obtiene historial usando ConversationRepository"""
    try:
        phone_number = session.get('phone_number')
        if not phone_number:
            return jsonify({
                'status': 'no_session',
                'message': 'No hay sesión activa'
            })
        
        try:
            # Intentar obtener historial de la BD
            with current_app.app_context():
                interaction_repo = ChatbotInteractionRepository()
                history = interaction_repo.get_recent_interactions(phone_number, limit=20)
                
                interactions = []
                for interaction in history:
                    interactions.extend([
                        {
                            'text': interaction.message_in,
                            'sender': 'user',
                            'timestamp': interaction.created_at.isoformat(),
                            'type': 'user_message'
                        },
                        {
                            'text': interaction.message_out,
                            'sender': 'bot', 
                            'timestamp': interaction.created_at.isoformat(),
                            'type': interaction.response_type,
                            'processing_time_ms': interaction.processing_time_ms
                        }
                    ])
                
                return jsonify({
                    'status': 'success',
                    'messages': interactions[-20:],  # Últimos 20 mensajes
                    'source': 'database',
                    'phone_number': phone_number
                })
                
        except Exception as db_error:
            logger.warning(f"No se puede acceder al historial de BD: {db_error}")
            return jsonify({
                'status': 'success',
                'messages': [],
                'source': 'simulation',
                'message': 'Historial no disponible en modo simulación'
            })
    
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@chatbot_bp.route('/clear-chat', methods=['POST'])
def clear_chat():
    """Limpia el historial de chat usando enterprise repository"""
    try:
        phone_number = session.get('phone_number')
        if not phone_number:
            return jsonify({
                'status': 'error',
                'message': 'No hay sesión activa'
            }), 400
        
        try:
            with current_app.app_context():
                conversation_repo = ConversationRepository()
                conversation_repo.delete_context(phone_number)
                logger.info(f"Historial limpiado para {phone_number}")
                
                return jsonify({
                    'status': 'success',
                    'message': 'Historial limpiado exitosamente'
                })
        except Exception as db_error:
            logger.warning(f"No se puede limpiar historial de BD: {db_error}")
            return jsonify({
                'status': 'success',
                'message': 'Historial limpiado (modo simulación)'
            })
    
    except Exception as e:
        logger.error(f"Error limpiando chat: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error limpiando chat: {str(e)}'
        }), 500

@chatbot_bp.route('/close-session', methods=['POST'])
def close_session():
    """Cierra la sesión usando enterprise repository"""
    try:
        phone_number = session.get('phone_number')
        if not phone_number:
            return jsonify({
                'status': 'error',
                'message': 'No hay sesión activa'
            }), 400
        
        try:
            with current_app.app_context():
                conversation_repo = ConversationRepository()
                conversation_repo.close_conversation(phone_number)
                
                # Limpiar sesión web
                session.clear()
                
                logger.info(f"Sesión cerrada: {phone_number}")
                
                return jsonify({
                    'status': 'success',
                    'message': 'Sesión cerrada exitosamente'
                })
        except Exception as db_error:
            logger.warning(f"No se puede cerrar sesión en BD: {db_error}")
            # Limpiar sesión web de todos modos
            session.clear()
            return jsonify({
                'status': 'success',
                'message': 'Sesión cerrada (modo simulación)'
            })
    
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error cerrando sesión: {str(e)}'
        }), 500

@chatbot_bp.route('/session-info')
def session_info():
    """Obtiene información de la sesión enterprise"""
    try:
        phone_number = session.get('phone_number')
        session_id = session.get('session_id')
        
        if not phone_number:
            return jsonify({
                'status': 'no_session',
                'message': 'No hay sesión activa'
            })
        
        try:
            with current_app.app_context():
                conversation_repo = ConversationRepository()
                context = conversation_repo.get_context(phone_number)
                
                session_data = {
                    'session_id': session_id,
                    'phone_number': phone_number,
                    'status': 'active' if context else 'not_found',
                    'mode': 'enterprise'
                }
                
                if context:
                    session_data.update({
                        'context_data': context.context_data,
                        'last_flow_id': context.last_flow_id,
                        'created_at': context.created_at.isoformat() if context.created_at else None,
                        'updated_at': context.updated_at.isoformat() if context.updated_at else None
                    })
                
                return jsonify({
                    'status': 'success',
                    'session': session_data
                })
                
        except Exception as db_error:
            logger.warning(f"No se puede obtener info de BD: {db_error}")
            return jsonify({
                'status': 'success',
                'session': {
                    'session_id': session_id,
                    'phone_number': phone_number,
                    'mode': 'simulation'
                }
            })
    
    except Exception as e:
        logger.error(f"Error obteniendo info de sesión: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@chatbot_bp.route('/system-status')
def system_status():
    """Verifica el estado de los componentes enterprise"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'components': {}
    }
    
    # Verificar base de datos
    try:
        with current_app.app_context():
            conversation_repo = ConversationRepository()
            # Test simple query
            conversation_repo.session.execute("SELECT 1").fetchone()
            status['components']['database'] = {'status': 'connected', 'type': 'enterprise'}
    except Exception as e:
        status['components']['database'] = {'status': 'disconnected', 'error': str(e)}
    
    # Verificar ChatbotService
    try:
        with current_app.app_context():
            chatbot_service = ChatbotService()
            status['components']['chatbot_service'] = {'status': 'available', 'type': 'enterprise'}
    except Exception as e:
        status['components']['chatbot_service'] = {'status': 'unavailable', 'error': str(e)}
    
    # Verificar RiveScript
    try:
        with current_app.app_context():
            from app.services.rivescript_service import RiveScriptService
            rs_service = RiveScriptService()
            test_response = rs_service.get_response("+test", "hola")
            if test_response:
                status['components']['rivescript'] = {'status': 'functional', 'type': 'enterprise'}
            else:
                status['components']['rivescript'] = {'status': 'loaded_no_response'}
    except Exception as e:
        status['components']['rivescript'] = {'status': 'error', 'error': str(e)}
    
    # Determinar modo general
    if all(comp.get('status') in ['connected', 'available', 'functional'] 
           for comp in status['components'].values()):
        status['mode'] = 'enterprise'
        status['message'] = 'Todos los servicios enterprise funcionando'
    else:
        status['mode'] = 'hybrid'
        status['message'] = 'Funcionando en modo híbrido con simulación'
    
    return jsonify(status)

@chatbot_bp.route('/stats')
def stats():
    """Obtiene estadísticas enterprise del sistema"""
    try:
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'sessions': {},
            'interactions': {},
            'system': {}
        }
        
        # Estadísticas de sesiones activas web
        active_sessions = len([s for s in session.keys() if s.startswith('phone_number')])
        stats_data['sessions']['web_active'] = active_sessions
        
        # Intentar obtener estadísticas de BD
        try:
            with current_app.app_context():
                interaction_repo = ChatbotInteractionRepository()
                total_interactions = interaction_repo.count_total_interactions()
                stats_data['interactions']['total'] = total_interactions
                
                today_interactions = interaction_repo.count_interactions_today()
                stats_data['interactions']['today'] = today_interactions
                
        except Exception as db_error:
            stats_data['interactions']['error'] = str(db_error)
        
        stats_data['system']['mode'] = 'enterprise_hybrid'
        
        return jsonify({
            'status': 'success',
            'stats': stats_data
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }), 500

# Comandos de prueba predefinidos
@chatbot_bp.route('/test-commands')
def test_commands():
    """Comandos de prueba optimizados para arquitectura enterprise"""
    commands = [
        {
            'category': 'Flujos RiveScript Enterprise',
            'commands': ['hola', 'soporte tecnico', 'ayuda tecnica', 'problema tecnico']
        },
        {
            'category': 'Navegación de Flujos',
            'commands': ['1', '2', '3', '4', '5', 'menu principal', 'volver']
        },
        {
            'category': 'Areas Especializadas',
            'commands': ['ventas', 'recursos humanos', 'facturacion', 'soporte']
        },
        {
            'category': 'Testing de Contexto',
            'commands': ['si', 'no', 'gracias', 'no funciona', 'problema resuelto']
        },
        {
            'category': 'Control de Sesión',
            'commands': ['cerrar conversacion', 'nueva sesion', 'transferir agente']
        }
    ]
    
    return jsonify({
        'status': 'success',
        'test_commands': commands,
        'architecture': 'enterprise'
    })
