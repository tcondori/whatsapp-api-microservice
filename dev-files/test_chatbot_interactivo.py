# test_chatbot_interactivo.py - Prueba interactiva del chatbot
# filepath: e:\DSW\proyectos\proy04\test_chatbot_interactivo.py

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.services.chatbot_service import ChatbotService
import time

def test_chatbot_interactive():
    """Test interactivo del chatbot"""
    
    # Configurar la aplicación
    app = create_app()
    
    with app.app_context():
        # Inicializar el servicio de chatbot
        chatbot = ChatbotService()
        
        print("=" * 70)
        print("🤖 CHATBOT WHATSAPP - PRUEBA INTERACTIVA")
        print("=" * 70)
        print("💡 Escribe 'salir' para terminar")
        print("🎯 Comandos de prueba:")
        print("   • hola, menu, ayuda")
        print("   • ventas, soporte, recursos humanos, facturacion")
        print("   • 1, 2, 3, 4, 5 (opciones del menú)")
        print("   • cerrar conversacion")
        print("-" * 70)
        
        # Simular número de teléfono de prueba
        test_phone = "+595987000999"
        
        while True:
            try:
                # Solicitar mensaje del usuario
                user_input = input("\n👤 Tú: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if not user_input:
                    continue
                
                # Procesar mensaje con el chatbot
                print("🤔 Procesando...", end="")
                start_time = time.time()
                
                response = chatbot.process_message(test_phone, user_input)
                
                processing_time = (time.time() - start_time) * 1000
                print(f"\r⏱️  Procesado en {processing_time:.1f}ms")
                
                # Mostrar respuesta del bot
                print(f"🤖 Bot: {response}")
                
                # Mostrar línea separadora
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupción del usuario. ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("🔧 Continuando con la siguiente pregunta...")

if __name__ == "__main__":
    test_chatbot_interactive()
