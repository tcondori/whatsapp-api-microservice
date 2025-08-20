#!/usr/bin/env python3
"""
Script para iniciar el servidor Flask de desarrollo
Muestra información útil sobre los endpoints disponibles
"""
import os
from entrypoint import create_app

def main():
    """Función principal para iniciar el servidor"""
    print("=" * 60)
    print("🚀 INICIANDO SERVIDOR FLASK - WhatsApp API Microservice")
    print("=" * 60)
    
    # Crear aplicación
    app = create_app()
    
    # Mostrar información de endpoints
    print("\n📋 ENDPOINTS DE MENSAJES DISPONIBLES:")
    message_routes = [rule for rule in app.url_map.iter_rules() if '/v1/messages' in rule.rule]
    
    for rule in message_routes:
        methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"  • {methods:12} {rule.rule}")
    
    print(f"\n🌐 DOCUMENTACIÓN SWAGGER:")
    print(f"  • Swagger UI:   http://localhost:5000/docs/")
    print(f"  • JSON Schema:  http://localhost:5000/swagger.json")
    
    print(f"\n🔑 AUTENTICACIÓN:")
    print(f"  • Header:       X-API-Key")
    print(f"  • API Keys:     dev-api-key, test-key-123")
    
    print(f"\n📊 HEALTH CHECK:")
    print(f"  • General:      http://localhost:5000/health")
    print(f"  • Messages:     http://localhost:5000/v1/messages/test")
    
    print("\n" + "=" * 60)
    print("✨ Servidor iniciado en http://localhost:5000")
    print("   Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    # Iniciar servidor
    try:
        app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            use_reloader=False  # Evitar doble inicio en modo debug
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")

if __name__ == '__main__':
    main()
