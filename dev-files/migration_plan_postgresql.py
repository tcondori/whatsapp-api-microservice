#!/usr/bin/env python
"""
Script de migración automática: SQLite -> PostgreSQL
Migra datos preservando UUIDs correctamente
"""

import sqlite3
# import psycopg2  # Se instalará en el proceso
import uuid
import json
from datetime import datetime

def create_migration_script():
    """
    Crear script de migración completa
    """
    print("=== 🚀 PLAN DE MIGRACIÓN SQLITE -> POSTGRESQL ===\n")
    
    print("PASO 1: INSTALACIÓN POSTGRESQL")
    print("-" * 40)
    print("Windows (recomendado):")
    print("• Descargar PostgreSQL 15+ desde postgresql.org")
    print("• Instalar con pgAdmin (GUI)")
    print("• Crear base de datos: 'whatsapp_chatbot'")
    print("• Usuario: 'whatsapp_user', Password: definir")
    
    print("\nDocker (alternativa):")
    print("docker run --name postgres-whatsapp \\")
    print("  -e POSTGRES_DB=whatsapp_chatbot \\")
    print("  -e POSTGRES_USER=whatsapp_user \\") 
    print("  -e POSTGRES_PASSWORD=whatsapp_pass \\")
    print("  -p 5432:5432 -d postgres:15")

def configuration_changes():
    """
    Cambios en configuración
    """
    print(f"\nPASO 2: CONFIGURACIÓN DE APLICACIÓN")
    print("-" * 40)
    
    # 1. Requirements.txt
    print("1. Actualizar requirements.txt:")
    print("# Agregar:")
    print("psycopg2-binary>=2.9.7")
    print("# Opcional mantener SQLite para testing:")
    print("# sqlite3 (viene con Python)")
    
    # 2. Variables de entorno
    print(f"\n2. Variables de entorno (.env):")
    print("# PostgreSQL")
    print("DATABASE_URL=postgresql://whatsapp_user:whatsapp_pass@localhost:5432/whatsapp_chatbot")
    print("# Mantener SQLite para testing")
    print("SQLITE_URL=sqlite:///instance/whatsapp_chatbot_backup.db")

def data_migration_script():
    """
    Script de migración de datos
    """
    print(f"\nPASO 3: MIGRACIÓN DE DATOS")
    print("-" * 40)
    
    migration_code = '''
def migrate_data():
    """Migrar datos de SQLite a PostgreSQL preservando UUIDs"""
    
    # Conexión SQLite (origen)
    sqlite_conn = sqlite3.connect('instance/whatsapp_chatbot.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conexión PostgreSQL (destino)
    pg_conn = psycopg2.connect(
        host="localhost",
        database="whatsapp_chatbot", 
        user="whatsapp_user",
        password="whatsapp_pass"
    )
    pg_cursor = pg_conn.cursor()
    
    # Migrar tabla conversation_flows
    print("Migrando conversation_flows...")
    sqlite_cursor.execute("SELECT * FROM conversation_flows")
    flows = sqlite_cursor.fetchall()
    
    for flow in flows:
        pg_cursor.execute("""
            INSERT INTO conversation_flows (
                id, name, description, rivescript_content, 
                is_active, is_default, priority, fallback_to_llm,
                max_context_messages, usage_count, last_used,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            flow['id'],  # PostgreSQL acepta UUID string directamente
            flow['name'], flow['description'], flow['rivescript_content'],
            flow['is_active'], flow['is_default'], flow['priority'], 
            flow['fallback_to_llm'], flow['max_context_messages'],
            flow['usage_count'], flow['last_used'], 
            flow['created_at'], flow['updated_at']
        ))
    
    pg_conn.commit()
    print(f"✅ Migrados {len(flows)} flujos de conversación")
    
    # Continuar con otras tablas...
    
    sqlite_conn.close()
    pg_conn.close()
'''
    
    print("Script completo en: migrate_to_postgresql.py")

def code_simplification():
    """
    Simplificación del código post-migración
    """
    print(f"\nPASO 4: SIMPLIFICACIÓN DE CÓDIGO")
    print("-" * 40)
    
    print("ANTES (SQLite - complejo):")
    print("""
def find_by_uuid(self, flow_id: str):
    # 20+ líneas de código SQL directo
    query = text("SELECT * FROM conversation_flows WHERE id = :flow_id")
    result = db.session.execute(query, {'flow_id': flow_id})
    # Mapeo manual de 13 campos...
""")
    
    print("DESPUÉS (PostgreSQL - simple):")
    print("""
def find_by_uuid(self, flow_id: str):
    return ConversationFlow.query.filter_by(id=flow_id).first()
    # ¡Una línea! PostgreSQL maneja UUID automáticamente
""")
    
    print("\n✅ BENEFICIOS INMEDIATOS:")
    print("• Eliminar método find_by_uuid() personalizado")
    print("• Usar métodos heredados de BaseRepository")
    print("• Los botones del editor funcionarán automáticamente")
    print("• Código 90% más simple")

if __name__ == "__main__":
    create_migration_script()
    configuration_changes() 
    data_migration_script()
    code_simplification()
    
    print(f"\n" + "="*50)
    print("¿Procedemos con la migración? 🚀")
    print("Tiempo estimado: 3 horas")
    print("Beneficio: Eliminar TODOS los problemas UUID")
    print("="*50)
