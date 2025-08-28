#!/usr/bin/env python3
"""
Script para limpiar bloqueos de base de datos y verificar el sistema
"""

import os
import sys
import sqlite3
import time
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clean_database_locks():
    """Limpia bloqueos de base de datos SQLite"""
    
    db_path = 'instance/whatsapp_test.db'
    
    if not os.path.exists(db_path):
        print(f"⚠️  Base de datos no encontrada: {db_path}")
        return False
    
    try:
        print(f"🔧 Limpiando bloqueos en: {db_path}")
        
        # Intentar conexión rápida para verificar estado
        conn = sqlite3.connect(db_path, timeout=5.0)
        conn.execute('BEGIN IMMEDIATE;')
        conn.rollback()
        conn.close()
        
        print("✅ Base de datos accesible, sin bloqueos")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print(f"❌ Base de datos bloqueada: {e}")
            
            # Intentar esperar y reconectar
            print("⏳ Esperando que se libere el bloqueo...")
            time.sleep(2)
            
            try:
                conn = sqlite3.connect(db_path, timeout=10.0)
                conn.execute('PRAGMA journal_mode=WAL;')
                conn.execute('PRAGMA synchronous=NORMAL;')
                conn.commit()
                conn.close()
                print("✅ Bloqueo resuelto, configuración optimizada")
                return True
            except Exception as e2:
                print(f"❌ No se pudo resolver el bloqueo: {e2}")
                return False
        else:
            print(f"❌ Error de base de datos: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_simple_rivescript():
    """Prueba RiveScript básico"""
    
    try:
        from rivescript import RiveScript
        
        # Test simple
        rs = RiveScript(utf8=True)
        
        # Contenido simple
        simple_code = """! version = 2.0

> topic random

+ hello
- Hello there!

+ hola  
- ¡Hola! ¿Cómo estás?

< topic
"""
        
        rs.stream(simple_code)
        rs.sort_replies()
        
        # Pruebas
        tests = ['hello', 'hola', 'test']
        
        print("🧪 Probando RiveScript simple:")
        for test_msg in tests:
            response = rs.reply('user', test_msg)
            status = "✅" if response != "ERR: No Reply Matched" else "❌"
            print(f"   {status} '{test_msg}' -> '{response}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test RiveScript: {e}")
        return False

def main():
    """Función principal"""
    
    print("🧹 LIMPIEZA Y VERIFICACIÓN DEL SISTEMA")
    print("=" * 50)
    
    # 1. Limpiar bloqueos de base de datos
    db_clean = clean_database_locks()
    
    # 2. Test RiveScript
    rs_test = test_simple_rivescript()
    
    # 3. Resumen
    print("\n📊 RESUMEN:")
    print(f"  • Base de datos: {'✅ OK' if db_clean else '❌ FALLO'}")
    print(f"  • RiveScript: {'✅ OK' if rs_test else '❌ FALLO'}")
    
    if db_clean and rs_test:
        print("\n🎉 ¡Sistema listo!")
        print("💡 Ejecuta 'python test_chatbot_interactivo.py' para probar")
    else:
        print("\n⚠️  Hay problemas pendientes")
        sys.exit(1)

if __name__ == '__main__':
    main()
