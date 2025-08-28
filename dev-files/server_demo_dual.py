"""
Servidor Flask independiente para demo de logging dual
Sin dependencias del entrypoint original
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from flask_restx import Api
from app.utils.logger import WhatsAppLogger

def create_demo_app():
    """
    Crea una aplicación Flask independiente para probar logging dual
    """
    # Crear app Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-for-testing'
    
    # Configurar logging dual ANTES de hacer cualquier otra cosa
    print("🔧 Configurando sistema de logging dual...")
    WhatsAppLogger.configure_logging(
        log_level='INFO',
        environment='development',
        use_date_structure=False,  # Sin fechas complicadas
        dual_output=True          # HABILITADO: terminal + archivos
    )
    
    print("✅ Logging dual configurado correctamente")
    
    # Crear API
    api = Api(
        app,
        version='1.0',
        title='WhatsApp API - Logging Dual Demo',
        description='Demo del sistema de logging dual: terminal + archivos',
        doc='/docs'
    )
    
    # Registrar namespace de mensajes manualmente 
    from app.api.messages.routes import messages_ns
    try:
        api.add_namespace(messages_ns, path='/v1/messages')
        print("✅ Namespace de mensajes registrado")
    except Exception as e:
        print(f"⚠️  Error registrando namespace: {e}")
        print("Continuando sin namespace...")
    
    return app

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask con Logging Dual...")
    print("📱 Endpoints disponibles:")
    print("   • http://localhost:5000/docs - Documentación Swagger")
    print("   • http://localhost:5000/v1/messages/text - Endpoint de texto")
    print("   • http://localhost:5000/v1/messages/test - Test endpoint")
    print()
    print("💡 Los logs aparecerán en TIEMPO REAL en esta terminal")
    print("📁 Y también se guardarán en archivos logs/*.log")
    print("=" * 60)
    
    try:
        app = create_demo_app()
        
        # Ejecutar servidor
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Evitar problemas con logging dual
        )
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
