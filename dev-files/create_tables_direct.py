#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear las tablas necesarias usando SQLAlchemy directamente
"""
import sqlite3
import os
from pathlib import Path

def create_tables_direct():
    """
    Crea las tablas directamente en SQLite
    """
    print("🔧 Creando tablas directamente en SQLite...")
    
    # Ruta de la base de datos
    db_path = Path("instance/whatsapp_test.db")
    
    # Crear directorio instance si no existe
    db_path.parent.mkdir(exist_ok=True)
    
    # Conectar a SQLite
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Tabla conversation_flows
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_flows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            rivescript_content TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_default BOOLEAN DEFAULT 0,
            priority INTEGER DEFAULT 1,
            fallback_to_llm BOOLEAN DEFAULT 0,
            max_context_messages INTEGER DEFAULT 10,
            usage_count INTEGER DEFAULT 0,
            last_used DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla conversation_contexts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_contexts (
            id TEXT PRIMARY KEY,
            phone_number TEXT NOT NULL UNIQUE,
            current_topic TEXT,
            context_data TEXT,
            last_interaction DATETIME,
            flow_id TEXT,
            session_count INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flow_id) REFERENCES conversation_flows (id)
        )
        """)
        
        # Tabla chatbot_interactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_interactions (
            id TEXT PRIMARY KEY,
            phone_number TEXT NOT NULL,
            message_in TEXT NOT NULL,
            message_out TEXT NOT NULL,
            response_type TEXT DEFAULT 'flow',
            processing_time_ms INTEGER,
            flow_id TEXT,
            confidence_score REAL,
            tokens_used INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flow_id) REFERENCES conversation_flows (id)
        )
        """)
        
        # Tabla messaging_lines (para mensajes)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messaging_lines (
            id TEXT PRIMARY KEY,
            line_name TEXT NOT NULL UNIQUE,
            phone_number_id TEXT NOT NULL,
            access_token TEXT NOT NULL,
            webhook_verify_token TEXT,
            business_account_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_default BOOLEAN DEFAULT 0,
            daily_limit INTEGER DEFAULT 1000,
            current_usage INTEGER DEFAULT 0,
            last_reset_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla messages
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            messaging_line_id TEXT NOT NULL,
            whatsapp_message_id TEXT UNIQUE,
            phone_number TEXT NOT NULL,
            message_type TEXT NOT NULL,
            content TEXT,
            media_url TEXT,
            status TEXT DEFAULT 'sent',
            timestamp_sent DATETIME,
            timestamp_delivered DATETIME,
            timestamp_read DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (messaging_line_id) REFERENCES messaging_lines (id)
        )
        """)
        
        # Tabla contacts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            phone_number TEXT NOT NULL UNIQUE,
            name TEXT,
            profile_name TEXT,
            is_blocked BOOLEAN DEFAULT 0,
            last_interaction DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla webhook_events
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_events (
            id TEXT PRIMARY KEY,
            messaging_line_id TEXT,
            webhook_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            processed BOOLEAN DEFAULT 0,
            processing_attempts INTEGER DEFAULT 0,
            last_attempt DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (messaging_line_id) REFERENCES messaging_lines (id)
        )
        """)
        
        # Tabla media_files
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS media_files (
            id TEXT PRIMARY KEY,
            whatsapp_media_id TEXT UNIQUE,
            file_type TEXT NOT NULL,
            file_size INTEGER,
            file_path TEXT,
            original_filename TEXT,
            mime_type TEXT,
            upload_status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Configurar SQLite para mejor rendimiento
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Commit cambios
        conn.commit()
        
        print("✅ Todas las tablas creadas correctamente")
        
        # Insertar flujo básico de prueba
        import uuid
        from datetime import datetime
        
        flow_id = str(uuid.uuid4())
        basic_flow = """! version = 2.0

// Flujo básico de saludo
> topic random

+ hola
- ¡Hola! 👋 Bienvenido a nuestro asistente virtual.
- ¿En qué puedo ayudarte hoy?
- 1️⃣ Ventas - Información de productos  
- 2️⃣ Soporte - Ayuda técnica
- 3️⃣ Recursos Humanos - Consultas
- Escribe el número de la opción o describe tu consulta.

+ (hello|hi|hey)
- Hello! 👋 Welcome to our virtual assistant.
- How can I help you today?

+ (1|uno|ventas|productos)
- ¡Perfecto! Te ayudo con información de ventas.
- ¿Qué productos te interesan?

+ (2|dos|soporte|ayuda|problema)
- Te ayudo con soporte técnico.
- Por favor describe tu problema.

+ (3|tres|recursos humanos|rrhh|empleado)
- ¡Hola! Soy tu asistente de Recursos Humanos.
- ¿En qué puedo ayudarte?

+ *
- Gracias por contactarnos.
- Para ayudarte mejor, puedes escribir "hola" para ver el menú.
- ¿En qué te puedo ayudar?

< topic"""

        cursor.execute("""
        INSERT OR REPLACE INTO conversation_flows 
        (id, name, description, rivescript_content, is_active, is_default, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flow_id,
            "Flujo Básico WhatsApp",
            "Flujo de conversación básico con menú principal",
            basic_flow,
            1,  # is_active
            1,  # is_default
            1,  # priority
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Flujo básico insertado")
        
        # Verificar que las tablas se crearon
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tablas creadas ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  • {table[0]} ({count} registros)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    if create_tables_direct():
        print("\n🎉 ¡Base de datos lista!")
        print("🚀 Reinicia el servidor para aplicar los cambios.")
    else:
        print("\n⚠️ Error creando las tablas.")
