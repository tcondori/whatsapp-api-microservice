#!/usr/bin/env python3
"""
Script para iniciar el servidor Flask de desarrollo con Sistema de Logging Dual
Terminal en tiempo real + Archivos persistentes
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from flask_restx import Api
from app.utils.logger import WhatsAppLogger

def create_server_app():
    """
    Crea aplicación Flask usando el factory pattern completo
    """
    # Usar la función create_app del módulo app que incluye TODOS los blueprints
    from app import create_app
    
    print("🔧 Creando aplicación usando Application Factory Pattern...")
    app = create_app('development')
    
    print("✅ Aplicación creada con todos los blueprints registrados:")
    print("  • API namespaces: /v1/messages, /v1/contacts, /v1/media, /v1/webhooks")
    print("  • Simulador de chat: /chat")
    print("  • Documentación: /docs")
    print("  • Health check: /health")
    
    return app

def main():
    """Función principal para iniciar el servidor con logging dual"""
    print("=" * 70)
    print("🚀 SERVIDOR FLASK - WhatsApp API con Sistema de Logging Dual")
    print("=" * 70)
    print()
    print("💡 CARACTERÍSTICAS DEL LOGGING DUAL:")
    print("  📺 Terminal: Logs en tiempo real con colores")  
    print("  📁 Archivos: JSON estructurado en /logs/")
    print("  ⚡ Simultáneo: Mismos logs en ambos destinos")
    print()
    
    # Crear aplicación con logging dual
    try:
        app = create_server_app()
        
        # Mostrar información de endpoints disponibles
        print("📋 ENDPOINTS PRINCIPALES:")
        endpoints_info = [
            ("POST", "/v1/messages/text", "Enviar mensaje de texto"),
            ("POST", "/v1/messages/image", "Enviar mensaje de imagen"),
            ("POST", "/v1/messages/location", "Enviar mensaje de ubicación"), 
            ("POST", "/v1/messages/contacts", "Enviar mensaje de contactos"),
            ("GET", "/v1/messages/test", "Endpoint de prueba"),
            ("GET", "/chat", "Simulador de chat interactivo"),
            ("GET", "/docs", "Documentación Swagger"),
            ("GET", "/health", "Health check")
        ]
        
        for method, endpoint, description in endpoints_info:
            print(f"  • {method:4} {endpoint:25} - {description}")
        
        print(f"\n🌐 ACCESO AL SERVIDOR:")
        print(f"  • URL Principal:  http://localhost:5001")
        print(f"  • Simulador Chat: http://localhost:5001/chat")
        print(f"  • Swagger Docs:   http://localhost:5001/docs")
        print(f"  • Health Check:   http://localhost:5001/health")
        
        print(f"\n🔑 AUTENTICACIÓN:")
        print(f"  • Header requerido:  X-API-Key: dev-api-key")
        print(f"  • API Keys válidas: {', '.join(app.config.get('VALID_API_KEYS', []))}")
        print(f"  • Ejemplo curl: curl -H 'X-API-Key: dev-api-key' http://localhost:5001/v1/messages/test")
        
        print(f"\n📊 LOGS EN VIVO:")
        print(f"  • Terminal: Los logs aparecerán aquí en tiempo real")
        print(f"  • Archivos: logs/api.log, logs/services.log, etc.")
        
        print("\n" + "=" * 70)
        print("✨ Iniciando servidor con logging dual...")
        print("   Presiona Ctrl+C para detener")
        print("=" * 70)
        
        # Iniciar servidor
        app.run(
            host='0.0.0.0', 
            port=5001, 
            debug=True,
            use_reloader=False  # Evitar problemas con logging dual
        )
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        print("📁 Los logs fueron guardados en el directorio /logs/")

if __name__ == '__main__':
    main()
