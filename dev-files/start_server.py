#!/usr/bin/env python3
"""
🚀 SCRIPT PRINCIPAL DE INICIO DEL SERVIDOR
==================================================
Usa el Application Factory Pattern completo con TODOS los componentes:
• API REST endpoints (/v1/*)
• Simulador de chat web (/chat)
• Documentación Swagger (/docs)
• Sistema de logging dual (terminal + archivos)
• Configuración completa (base de datos, Redis, etc.)

RECOMENDACIÓN: Usar este script como punto de entrada único
==================================================
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Función principal para iniciar el servidor completo"""
    print("=" * 80)
    print("🚀 WHATSAPP API MICROSERVICE - SERVIDOR COMPLETO")
    print("=" * 80)
    print()
    print("💡 COMPONENTES INCLUIDOS:")
    print("  📱 API REST completa (/v1/*)")
    print("  🗨️  Simulador de chat (/chat)")
    print("  📚 Documentación Swagger (/docs)")
    print("  📊 Sistema de logging dual")
    print("  🔧 Configuración completa")
    print()
    
    try:
        # Usar la función create_app que incluye TODOS los componentes
        from app import create_app
        
        # Crear aplicación completa
        print("🔧 Inicializando aplicación con todos los componentes...")
        app = create_app('development')
        
        # Información de acceso
        port = 5001
        host = '0.0.0.0'
        
        print(f"\n🌐 ACCESO AL SERVIDOR:")
        print(f"  • URL Principal:   http://localhost:{port}")
        print(f"  • Simulador Chat:  http://localhost:{port}/chat")  
        print(f"  • API Endpoints:   http://localhost:{port}/v1/messages/test")
        print(f"  • Swagger Docs:    http://localhost:{port}/docs")
        print(f"  • Health Check:    http://localhost:{port}/health")
        
        print(f"\n🔑 AUTENTICACIÓN API:")
        print(f"  • Header: X-API-Key: dev-api-key")
        print(f"  • Ejemplo: curl -H 'X-API-Key: dev-api-key' http://localhost:{port}/v1/messages/test")
        
        print(f"\n📁 LOGS:")
        print(f"  • Terminal: Tiempo real con colores")
        print(f"  • Archivos: logs/YYYY/MM/DD/*.log")
        
        print("\n" + "=" * 80)
        print("✨ INICIANDO SERVIDOR COMPLETO...")
        print("   ❤️  Incluye simulador de chat y API completa")
        print("   🛑 Presiona Ctrl+C para detener")
        print("=" * 80)
        
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        print("📁 Los logs fueron guardados en el directorio /logs/")
        return 0

if __name__ == '__main__':
    sys.exit(main())
