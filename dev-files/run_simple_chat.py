#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de chat simplificado que funciona sin SQLAlchemy
"""
from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def create_simple_chat_app():
    """Crea una aplicación Flask simplificada solo para el chat"""
    app = Flask(__name__)
    app.secret_key = 'dev-secret-key-for-chat'
    
    # Variable en memoria para simular sesiones de chat
    chat_sessions = {}
    
    @app.route('/')
    def index():
        """Página principal del simulador de chat"""
        return render_template('chat_simple.html')
    
    @app.route('/send-message', methods=['POST'])
    def send_message():
        """Procesa mensajes del usuario y devuelve respuesta del bot"""
        try:
            data = request.get_json()
            user_message = data.get('message', '').strip()
            phone_number = data.get('phone_number', '+5959875000')
            
            if not user_message:
                return jsonify({
                    'status': 'error',
                    'message': 'Mensaje vacío'
                }), 400
            
            # Simular respuesta del bot basada en el mensaje
            bot_response = generate_bot_response(user_message)
            
            return jsonify({
                'status': 'success',
                'user_message': {
                    'text': user_message,
                    'timestamp': '15:45',
                    'type': 'user'
                },
                'bot_message': {
                    'text': bot_response,
                    'timestamp': '15:45', 
                    'type': 'bot'
                }
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error procesando mensaje: {str(e)}'
            }), 500
    
    def generate_bot_response(message):
        """Genera respuesta del bot basada en el mensaje"""
        message_lower = message.lower().strip()
        
        # Respuestas del flujo de soporte técnico
        if any(word in message_lower for word in ['soporte tecnico', 'soporte técnico', 'ayuda tecnica', 'ayuda técnica', 'problema tecnico', 'problema técnico', 'no funciona', 'error', 'falla']):
            return """Hola, soy el asistente de **Soporte Técnico** 🛠️

¿Con qué puedo ayudarte hoy?

1️⃣ Problemas de conexión
2️⃣ Errores de la aplicación  
3️⃣ Problemas de rendimiento
4️⃣ Configuración de cuenta
5️⃣ Hablar con un técnico

Escribe el número o describe tu problema."""

        elif message_lower in ['1', 'uno', 'conexion', 'conexión', 'internet', 'red', 'wifi']:
            return """**Problemas de Conexión** 🌐
Vamos a revisar tu conectividad:
1. Verifica que tu WiFi esté conectado
2. Reinicia tu router (30 segundos)
3. Prueba con datos móviles
¿Funcionó? Responde "si" o "no" """

        elif message_lower in ['2', 'dos', 'error', 'errores', 'aplicacion', 'aplicación', 'app', 'falla']:
            return """**Errores de Aplicación** ⚠️
Te ayudo a diagnosticar:
1. Cierra la aplicación completamente
2. Reinicia tu dispositivo
3. Abre la aplicación nuevamente
Si persiste, describe el error."""

        elif message_lower in ['3', 'tres', 'lento', 'rendimiento', 'performance', 'velocidad']:
            return """**Problemas de Rendimiento** ⚡
Optimicemos tu experiencia:
1. Libera espacio en tu dispositivo
2. Cierra aplicaciones en segundo plano  
3. Actualiza la aplicación
¿Notas mejora?"""

        elif message_lower in ['4', 'cuatro', 'cuenta', 'perfil', 'configuracion', 'configuración', 'ajustes']:
            return """**Configuración de Cuenta** ⚙️
Te ayudo con:
• Cambio de contraseña
• Actualización de datos
• Configuración de privacidad  
• Sincronización
¿Qué necesitas configurar?"""

        elif message_lower in ['5', 'cinco', 'tecnico', 'técnico', 'humano', 'persona', 'agente']:
            return """**Conexión con Técnico** 👨‍💻
Te conectaré con nuestro equipo técnico.
**Horario:** Lunes a Viernes 8AM-6PM
**Sábados:** 9AM-2PM
Un técnico te contactará pronto.
**Ticket:** #12345"""

        elif message_lower in ['si', 'sí', 'yes', 'funciona', 'funcionó']:
            return """¡Excelente! 😊 Me alegra que haya funcionado.
Si necesitas más ayuda, escribe "soporte tecnico".
¡Que tengas un gran día!"""

        elif message_lower in ['no', 'nada', 'sigue', 'persiste']:
            return """Entiendo que el problema persiste. 😔
Vamos a intentar otras opciones:
• Reinstala la aplicación
• Contacta soporte técnico (opción 5)
• Verifica actualizaciones
¿Te conecto con un técnico?"""

        elif any(word in message_lower for word in ['hola', 'hello', 'hi', 'hey', 'buenos dias']):
            return """¡Hola! 👋 Bienvenido a nuestro asistente virtual.

¿En qué puedo ayudarte hoy?

1️⃣ Ventas - Información de productos
2️⃣ Soporte - Ayuda técnica  
3️⃣ Recursos Humanos - Consultas

Escribe el número de la opción o describe tu consulta."""

        elif any(word in message_lower for word in ['gracias', 'thanks', 'ok', 'vale']):
            return """¡De nada! 😊 Me alegra haberte ayudado.
Estoy aquí cuando me necesites.
Escribe "soporte tecnico" para el menú de soporte."""

        else:
            return """Gracias por contactarnos.
Para ayudarte mejor, puedes escribir:
• "hola" para ver el menú principal
• "soporte tecnico" para ayuda técnica
¿En qué te puedo ayudar?"""
    
    return app

# Template HTML simplificado
CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Chat Simulator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .chat-header {
            background: #25D366;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f0f0f0;
        }
        .message {
            margin: 10px 0;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background: #DCF8C6;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: white;
            margin-right: auto;
        }
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
        }
        .message-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }
        .send-button {
            background: #25D366;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 20px;
            margin-left: 10px;
            cursor: pointer;
        }
        .send-button:hover {
            background: #20b358;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 WhatsApp Bot</h2>
            <p>Simulador de Chat</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                ¡Hola! Bienvenido al simulador de WhatsApp. 
                Prueba escribir "soporte tecnico" para ver todas las opciones disponibles.
            </div>
        </div>
        <div class="chat-input">
            <input type="text" class="message-input" id="messageInput" placeholder="Escribe tu mensaje..." />
            <button class="send-button" onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Agregar mensaje del usuario
            addMessage(message, 'user');
            input.value = '';
            
            // Enviar al servidor
            fetch('/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    addMessage(data.bot_message.text, 'bot');
                } else {
                    addMessage('Error: ' + data.message, 'bot');
                }
            })
            .catch(error => {
                addMessage('Error de conexión', 'bot');
            });
        }
        
        function addMessage(text, type) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${type}-message`;
            div.innerHTML = text.replace(/\\n/g, '<br>');
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        // Enviar con Enter
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app = create_simple_chat_app()
    
    # Crear directorio de templates si no existe
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Escribir template
    with open(templates_dir / "chat_simple.html", "w", encoding="utf-8") as f:
        f.write(CHAT_TEMPLATE)
    
    print("🚀 Iniciando simulador de chat simplificado...")
    print("🌐 Acceso: http://localhost:5002")
    print("💬 Prueba escribir: 'soporte tecnico'")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
