#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para solucionar el problema de base de datos bloqueada
"""
import os
import sqlite3
import time
from pathlib import Path

def fix_database_lock():
    """
    Soluciona el problema de base de datos SQLite bloqueada
    """
    print("🔧 Solucionando problema de base de datos bloqueada...")
    
    # Ruta de la base de datos
    db_path = Path("instance/whatsapp_test.db")
    
    if not db_path.exists():
        print("❌ No se encontró la base de datos")
        return False
    
    try:
        # Cerrar todas las conexiones existentes
        print("🔄 Cerrando conexiones existentes...")
        
        # Intentar conectar y cerrar inmediatamente
        conn = sqlite3.connect(str(db_path), timeout=1.0)
        conn.execute("BEGIN IMMEDIATE;")
        conn.rollback()
        conn.close()
        
        print("✅ Base de datos desbloqueada")
        
        # Verificar integridad
        print("🔍 Verificando integridad de la base de datos...")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        
        if result and result[0] == "ok":
            print("✅ Integridad verificada correctamente")
        else:
            print(f"⚠️ Problema de integridad: {result}")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("🔄 Base de datos aún bloqueada, intentando solución alternativa...")
            
            # Esperar un momento
            time.sleep(2)
            
            try:
                # Forzar cierre usando WAL mode
                conn = sqlite3.connect(str(db_path))
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                conn.execute("PRAGMA journal_mode=DELETE;")
                conn.close()
                print("✅ Base de datos desbloqueada usando WAL mode")
                return True
            except Exception as e2:
                print(f"❌ No se pudo desbloquear: {e2}")
                return False
        else:
            print(f"❌ Error inesperado: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def optimize_database():
    """
    Optimiza la base de datos para mejor rendimiento
    """
    print("⚡ Optimizando base de datos...")
    
    db_path = Path("instance/whatsapp_test.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Configuraciones de optimización
        optimizations = [
            "PRAGMA synchronous=NORMAL;",
            "PRAGMA cache_size=10000;",
            "PRAGMA temp_store=MEMORY;",
            "PRAGMA mmap_size=268435456;",  # 256MB
            "PRAGMA journal_mode=WAL;",
        ]
        
        for optimization in optimizations:
            cursor.execute(optimization)
            print(f"✅ {optimization}")
        
        # Limpiar y optimizar
        cursor.execute("VACUUM;")
        cursor.execute("ANALYZE;")
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos optimizada")
        return True
        
    except Exception as e:
        print(f"❌ Error en optimización: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando reparación de base de datos...")
    
    # Solucionar bloqueo
    if fix_database_lock():
        print("\n⚡ Optimizando rendimiento...")
        optimize_database()
        
        print("\n🎉 ¡Base de datos reparada y optimizada!")
        print("\n💡 Recomendaciones:")
        print("   • Reinicia el servidor Flask")
        print("   • Si persiste el problema, considera usar PostgreSQL")
        
    else:
        print("\n❌ No se pudo reparar la base de datos")
        print("\n🔄 Opciones alternativas:")
        print("   • Eliminar instance/whatsapp_api.db y recrear")
        print("   • Usar una base de datos PostgreSQL")
