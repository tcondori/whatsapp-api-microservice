# app/chatbot/__init__.py - Blueprint del simulador de chat
# filepath: e:\DSW\proyectos\proy04\app\chatbot\__init__.py

from flask import Blueprint

# Crear blueprint del simulador de chat
chatbot_bp = Blueprint(
    'chatbot', 
    __name__, 
    template_folder='templates',
    static_folder='static',
    url_prefix='/chat'
)

# Las rutas del blueprint se configurarán con strict_slashes=False individualmente

# Importar las rutas después de crear el blueprint para evitar imports circulares
# Usar rutas simplificadas para evitar problemas con SQLAlchemy
try:
    # Intentar importar rutas enterprise completas
    from . import routes
    print("[DEBUG] Rutas enterprise cargadas exitosamente")
except ImportError as e:
    print(f"[DEBUG] Error cargando rutas enterprise: {e}")
    try:
        # Fallback a rutas simplificadas
        from . import routes_simple
        print("[DEBUG] Rutas simplificadas cargadas como fallback")
    except ImportError as e2:
        print(f"[ERROR] Error cargando rutas simplificadas: {e2}")
        raise
except Exception as e:
    print(f"[DEBUG] Error general cargando rutas enterprise: {e}")
    try:
        # Fallback a rutas simplificadas
        from . import routes_simple
        print("[DEBUG] Rutas simplificadas cargadas como fallback")
    except Exception as e2:
        print(f"[ERROR] Error cargando rutas simplificadas: {e2}")
        raise
