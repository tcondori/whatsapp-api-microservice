"""
Script de diagnóstico para identificar problemas en la inicialización
"""
import os
from dotenv import load_dotenv

print("🔍 Iniciando diagnóstico...")

# Cargar variables de entorno
load_dotenv()
print("✅ Variables de entorno cargadas")

try:
    from flask import Flask
    print("✅ Flask importado correctamente")
except Exception as e:
    print(f"❌ Error importando Flask: {e}")
    exit(1)

try:
    from app.extensions import init_extensions
    print("✅ Extensions importadas correctamente")
except Exception as e:
    print(f"❌ Error importando extensions: {e}")
    exit(1)

try:
    from database.connection import init_database
    print("✅ Database connection importada correctamente")
except Exception as e:
    print(f"❌ Error importando database: {e}")
    exit(1)

try:
    from config import get_config
    print("✅ Config importada correctamente")
except Exception as e:
    print(f"❌ Error importando config: {e}")
    exit(1)

# Crear aplicación paso a paso
try:
    app = Flask(__name__)
    print("✅ Flask app creada")
    
    config_class = get_config()
    app.config.from_object(config_class)
    print("✅ Configuración cargada")
    
    init_extensions(app)
    print("✅ Extensions inicializadas")
    
    init_database(app)
    print("✅ Database inicializada")
    
    print("✅ Aplicación creada exitosamente!")
    print(f"📊 Rutas registradas: {len(list(app.url_map.iter_rules()))}")
    
    # Mostrar algunas rutas para verificar
    print("\n📋 Algunas rutas registradas:")
    for rule in list(app.url_map.iter_rules())[:10]:
        print(f"  • {rule.rule} ({', '.join(rule.methods)})")
    
except Exception as e:
    print(f"❌ Error creando aplicación: {e}")
    import traceback
    traceback.print_exc()
