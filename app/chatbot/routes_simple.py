# app/chatbot/routes_simple.py - Rutas simplificadas sin SQLAlchemy
# filepath: e:\DSW\proyectos\proy04\app\chatbot\routes_simple.py

"""
Rutas simplificadas del simulador de chat sin dependencias de SQLAlchemy
Funciona como fallback cuando no están disponibles los servicios enterprise
"""

from flask import render_template, request, jsonify, session
from datetime import datetime
import uuid
import traceback

from . import chatbot_bp

@chatbot_bp.route('/', strict_slashes=False)
@chatbot_bp.route('', strict_slashes=False)
def index():
    """Página principal del simulador de chat"""
    try:
        return render_template('chat_standalone.html')
    except Exception as e:
        return f"Error cargando simulador: {str(e)}", 500

@chatbot_bp.route('/new-session')
def new_session():
    """Crea nueva sesión simple"""
    try:
        # Generar número de teléfono único para simulación web
        phone_base = "+59598"
        session_suffix = str(uuid.uuid4())[:6]
        phone_number = f"{phone_base}{session_suffix}"
        
        # Almacenar en sesión web
        session['phone_number'] = phone_number
        session['session_id'] = str(uuid.uuid4())
        
        return jsonify({
            'status': 'success',
            'session_id': session['session_id'],
            'phone_number': phone_number,
            'message': '¡Hola! Bienvenido al simulador de chat de WhatsApp. ¿En qué puedo ayudarte?'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al crear sesión: {str(e)}'
        }), 500

@chatbot_bp.route('/send-message', methods=['POST'])
def send_message():
    """Procesa mensaje usando respuestas simuladas"""
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
        
        # Generar respuesta simulada
        bot_message = _generate_simulation_response(user_message)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
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
                'type': 'simulation',
                'confidence_score': 0.8,
                'processing_time_ms': round(processing_time, 2),
                'flow_id': None
            },
            'session_info': {
                'session_id': session.get('session_id'),
                'phone_number': phone_number,
                'mode': 'simulation'
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Lo siento, ha ocurrido un error procesando tu mensaje. Por favor intenta nuevamente.',
            'error_details': str(e)
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
            '1': ("**Opción 1 - Problemas de Conexión** 🌐<br><br>"
                  "Vamos a revisar tu conectividad:<br>"
                  "• Verifica que tu WiFi esté conectado<br>"
                  "• Reinicia tu router (30 segundos)<br>"
                  "• Prueba con datos móviles<br><br>"
                  "¿Funcionó? Responde 'si' o 'no'"),
            '2': ("**Opción 2 - Errores de Aplicación** ⚠️<br><br>"
                  "Te ayudo a diagnosticar:<br>"
                  "• Cierra la aplicación completamente<br>"
                  "• Reinicia tu dispositivo<br>"
                  "• Abre la aplicación nuevamente<br><br>"
                  "Si persiste, describe el error específico."),
            '3': ("**Opción 3 - Problemas de Rendimiento** ⚡<br><br>"
                  "Optimicemos tu experiencia:<br>"
                  "• Libera espacio en tu dispositivo<br>"
                  "• Cierra aplicaciones en segundo plano<br>"
                  "• Actualiza la aplicación<br><br>"
                  "¿Notas mejora en el rendimiento?"),
            '4': ("**Opción 4 - Configuración de Cuenta** ⚙️<br><br>"
                  "Te ayudo con:<br>"
                  "• Cambio de contraseña<br>"
                  "• Actualización de datos personales<br>"
                  "• Configuración de privacidad<br>"
                  "• Sincronización de dispositivos<br><br>"
                  "¿Qué necesitas configurar específicamente?"),
            '5': ("**Opción 5 - Hablar con Técnico** 👨‍💻<br><br>"
                  "Te conectaré con nuestro equipo técnico especializado.<br><br>"
                  "**Horario de Atención:**<br>"
                  "• Lunes a Viernes: 8:00 AM - 6:00 PM<br>"
                  "• Sábados: 9:00 AM - 2:00 PM<br><br>"
                  "Un técnico te contactará pronto.<br>"
                  "**Ticket generado:** #ST-12345")
        }
        return responses.get(message_lower, "Opción procesada correctamente.")
    
    elif message_lower in ['si', 'sí', 'yes', 'funciona', 'funcionó']:
        return ("¡Excelente! 😊 Me alegra que haya funcionado.<br><br>"
                "Si necesitas más ayuda, escribe 'soporte tecnico' para volver al menú principal.<br><br>"
                "¡Que tengas un gran día!")
    
    elif message_lower in ['no', 'nada', 'sigue', 'persiste', 'no funciona']:
        return ("Entiendo que el problema persiste. 😔<br><br>"
                "Vamos a intentar otras opciones:<br>"
                "• Reinstala completamente la aplicación<br>"
                "• Contacta con soporte técnico (opción 5)<br>"
                "• Verifica si hay actualizaciones disponibles<br><br>"
                "¿Te conecto directamente con un técnico especializado?")
    
    elif any(word in message_lower for word in ['gracias', 'thanks', 'ok', 'vale', 'perfecto']):
        return ("¡De nada! 😊 Me alegra haberte ayudado.<br><br>"
                "Estoy aquí cuando me necesites.<br>"
                "Escribe 'soporte tecnico' para acceder al menú de soporte técnico.")
    
    else:
        return ("Gracias por contactarnos.<br><br>"
                "Para ayudarte mejor, puedes escribir:<br>"
                "• **'hola'** para ver el menú principal<br>"
                "• **'soporte tecnico'** para ayuda técnica especializada<br>"
                "• **'ventas'** para información comercial<br><br>"
                "¿En qué te puedo ayudar específicamente?")

@chatbot_bp.route('/system-status')
def system_status():
    """Estado del sistema simplificado"""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'mode': 'simulation',
        'message': 'Funcionando en modo simulación',
        'components': {
            'chatbot_simulator': {'status': 'active', 'type': 'simulation'},
            'database': {'status': 'not_available', 'type': 'simulation'},
            'rivescript': {'status': 'not_available', 'type': 'simulation'}
        }
    })

@chatbot_bp.route('/test-commands')
def test_commands():
    """Comandos de prueba para modo simulación"""
    commands = [
        {
            'category': 'Saludos y Navegación',
            'commands': ['hola', 'buenos días', 'menu principal']
        },
        {
            'category': 'Soporte Técnico Completo',
            'commands': ['soporte tecnico', 'ayuda tecnica', 'problema tecnico']
        },
        {
            'category': 'Opciones de Soporte (1-5)',
            'commands': ['1', '2', '3', '4', '5']
        },
        {
            'category': 'Respuestas Interactivas',
            'commands': ['si', 'no', 'gracias', 'no funciona']
        },
        {
            'category': 'Areas Comerciales',
            'commands': ['ventas', 'productos', 'cotizar']
        }
    ]
    
    return jsonify({
        'status': 'success',
        'test_commands': commands,
        'architecture': 'simulation_mode'
    })

@chatbot_bp.route('/get-history')
def get_history():
    """Historial simplificado"""
    return jsonify({
        'status': 'success',
        'messages': [],
        'source': 'simulation',
        'message': 'Historial no disponible en modo simulación'
    })
