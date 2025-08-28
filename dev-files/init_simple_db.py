#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para inicializar base de datos limpia
"""

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def init_clean_database():
    """Inicializa una base de datos limpia"""
    try:
        print("🔧 Inicializando base de datos limpia...")
        
        # Configurar variables de entorno
        os.environ['FLASK_ENV'] = 'development'
        
        # Importar después de configurar el entorno
        from app import create_app
        from sqlalchemy import create_engine, text
        from app.models.base import Base
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            print("📋 Creando tablas...")
            
            # Obtener la URL de la base de datos
            database_url = 'sqlite:///instance/whatsapp_test.db'
            
            # Crear engine y tablas
            engine = create_engine(database_url)
            Base.metadata.create_all(engine)
            
            # Configurar SQLite
            with engine.connect() as conn:
                conn.execute(text("PRAGMA synchronous=NORMAL"))
                conn.execute(text("PRAGMA cache_size=10000"))
                conn.execute(text("PRAGMA temp_store=MEMORY"))
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.commit()
            
            print("✅ Base de datos inicializada correctamente")
            print("🎉 ¡Listo para usar!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_clean_database()
    
    if success:
        print("\n🚀 Base de datos lista. Puedes iniciar el servidor ahora.")
    else:
        print("\n⚠️ Hubo errores en la inicialización.")
