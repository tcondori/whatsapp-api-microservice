"""
🚀 PUNTO DE ENTRADA ÚNICO PARA FLASK CLI
====================================================
Este archivo es el punto de entrada recomendado usando:

    flask run

Incluye TODOS los componentes:
• API REST endpoints (/v1/*)
• Simulador de chat web (/chat)
• Documentación Swagger (/docs)
• Sistema de logging dual
• Configuración completa

RECOMENDADO: flask run
====================================================
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🚀 Iniciando WhatsApp API Microservice...")
print("📁 Variables de entorno cargadas desde .env")

# Importar factory function desde app/__init__.py
from app import create_app

# Crear la instancia de la aplicación usando el factory pattern
# Esta variable DEBE llamarse 'app' para que Flask CLI la encuentre
app = create_app()

print("✅ Aplicación creada con Application Factory Pattern")
print("📦 Componentes incluidos:")
print("  • API REST (/v1/*)")
print("  • Simulador Chat (/chat)")  
print("  • Documentación (/docs)")
print("  • Logging dual")
print("  • Base de datos")

if __name__ == '__main__':
    # Solo para ejecución directa - pero recomendamos usar "flask run"
    port = int(os.getenv('FLASK_RUN_PORT', os.getenv('PORT', 5001)))
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_RUN_DEBUG', 'false').lower() == 'true'
    
    print("=" * 60)
    print("⚠️  EJECUTANDO EN MODO DIRECTO")
    print("   RECOMENDADO: flask run")  
    print("=" * 60)
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"🗨️  Chat: http://{host}:{port}/chat")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print("=" * 60)
    
    app.run(host=host, port=port, debug=debug)