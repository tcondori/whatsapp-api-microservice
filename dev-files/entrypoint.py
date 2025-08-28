"""
Punto de entrada principal de la aplicación WhatsApp API Microservice
Usa el patrón Application Factory desde app/__init__.py
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importar factory function desde app/__init__.py
from app import create_app

# Crear instancia de la aplicación usando el patrón factory
app = create_app()

if __name__ == '__main__':
    # Configuración para ejecutar directamente
    port = int(os.getenv('FLASK_RUN_PORT', os.getenv('PORT', 5000)))
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_RUN_DEBUG', 'false').lower() == 'true'
    
    print("=" * 70)
    print("🚀 WhatsApp API Microservice - Sistema de Logging Dual")
    print("=" * 70)
    print()
    print("💡 CARACTERÍSTICAS DEL LOGGING DUAL:")
    print("  📺 Terminal: Logs en tiempo real con colores")
    print("  📁 Archivos: JSON estructurado organizados por fechas")
    print("  ⚡ Simultáneo: Mismos logs en ambos destinos")
    print()
    print(f"🌐 ACCESO AL SERVIDOR:")
    print(f"  • URL Principal:  http://{host}:{port}")
    print(f"  • Swagger Docs:   http://{host}:{port}/docs")
    print(f"  • Health Check:   http://{host}:{port}/health")
    print()
    print(f"🔑 AUTENTICACIÓN:")
    print(f"  • Header requerido: X-API-Key")
    print(f"  • API Keys válidas: {', '.join(app.config.get('VALID_API_KEYS', ['dev-api-key']))}")
    print()
    print(f"📊 LOGS EN VIVO:")
    print(f"  • Terminal: Los logs aparecerán aquí en tiempo real")
    print(f"  • Archivos: logs/YYYY/MM/DD/api.log, services.log, etc.")
    print()
    print("🚀 COMANDOS DISPONIBLES:")
    print("  • flask run              (recomendado)")
    print("  • python entrypoint.py   (alternativo)")
    print()
    print("=" * 70)
    print("✨ Iniciando servidor con logging dual...")
    print("   Presiona Ctrl+C para detener")
    print("=" * 70)
    
    app.run(host=host, port=port, debug=debug)
