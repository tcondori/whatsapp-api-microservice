#!/usr/bin/env python3
"""
Script para corregir el schema de la base de datos añadiendo las columnas faltantes
"""

import sqlite3
import os

def fix_database_schema():
    """Corrige el schema de la base de datos añadiendo columnas faltantes"""
    # Ubicación de la base de datos
    db_path = "instance/whatsapp_test.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return
    
    print("🔧 Corrigiendo schema de base de datos...")
    print(f"📍 Archivo: {db_path}")
    
    try:
        # Conectar directamente a SQLite
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        print("📝 Añadiendo columnas faltantes...")
        
        # Añadir columnas a conversation_contexts
        try:
            cursor.execute("ALTER TABLE conversation_contexts ADD COLUMN context_data TEXT")
            print("   ✅ context_data añadido a conversation_contexts")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ⚠️  context_data ya existe en conversation_contexts")
            else:
                print(f"   ❌ Error añadiendo context_data: {e}")
        
        try:
            cursor.execute("ALTER TABLE conversation_contexts ADD COLUMN flow_id VARCHAR(36)")
            print("   ✅ flow_id añadido a conversation_contexts")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ⚠️  flow_id ya existe en conversation_contexts")
            else:
                print(f"   ❌ Error añadiendo flow_id: {e}")
        
        try:
            cursor.execute("ALTER TABLE conversation_contexts ADD COLUMN session_count INTEGER DEFAULT 1")
            print("   ✅ session_count añadido a conversation_contexts")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ⚠️  session_count ya existe en conversation_contexts")
            else:
                print(f"   ❌ Error añadiendo session_count: {e}")
        
        # Verificar y modificar chatbot_interactions
        try:
            # Verificar estructura actual
            cursor.execute("PRAGMA table_info(chatbot_interactions)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"   📋 Columnas actuales en chatbot_interactions: {column_names}")
            
            if 'llm_tokens_used' in column_names:
                print("   🔄 Recreando tabla chatbot_interactions...")
                # Crear tabla temporal
                cursor.execute("""
                    CREATE TABLE chatbot_interactions_temp AS 
                    SELECT id, phone_number, message_in, message_out, response_type, 
                           processing_time_ms, confidence_score, created_at, updated_at 
                    FROM chatbot_interactions
                """)
                
                # Eliminar tabla original
                cursor.execute("DROP TABLE chatbot_interactions")
                
                # Recrear tabla con estructura correcta
                cursor.execute("""
                    CREATE TABLE chatbot_interactions (
                        id VARCHAR(36) PRIMARY KEY,
                        phone_number VARCHAR(20) NOT NULL,
                        message_in TEXT NOT NULL,
                        message_out TEXT NOT NULL,
                        response_type VARCHAR(50) NOT NULL,
                        processing_time_ms INTEGER DEFAULT 0,
                        flow_id VARCHAR(36),
                        confidence_score FLOAT DEFAULT 0.0,
                        tokens_used INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copiar datos de vuelta
                cursor.execute("""
                    INSERT INTO chatbot_interactions 
                    (id, phone_number, message_in, message_out, response_type, 
                     processing_time_ms, confidence_score, created_at, updated_at)
                    SELECT id, phone_number, message_in, message_out, response_type,
                           processing_time_ms, confidence_score, created_at, updated_at
                    FROM chatbot_interactions_temp
                """)
                
                # Eliminar tabla temporal
                cursor.execute("DROP TABLE chatbot_interactions_temp")
                print("   ✅ Tabla chatbot_interactions recreada correctamente")
            else:
                # Solo añadir las columnas faltantes
                if 'flow_id' not in column_names:
                    cursor.execute("ALTER TABLE chatbot_interactions ADD COLUMN flow_id VARCHAR(36)")
                    print("   ✅ flow_id añadido a chatbot_interactions")
                
                if 'tokens_used' not in column_names:
                    cursor.execute("ALTER TABLE chatbot_interactions ADD COLUMN tokens_used INTEGER DEFAULT 0")
                    print("   ✅ tokens_used añadido a chatbot_interactions")
                    
        except sqlite3.OperationalError as e:
            print(f"   ❌ Error modificando chatbot_interactions: {e}")
        
        # Commit los cambios
        connection.commit()
        
        print("\n✅ Schema de base de datos corregido exitosamente")
        
        # Verificar los cambios
        print("\n🔍 Verificando cambios...")
        
        cursor.execute("PRAGMA table_info(conversation_contexts)")
        columns = cursor.fetchall()
        print(f"   📋 conversation_contexts tiene {len(columns)} columnas:")
        for col in columns:
            print(f"      - {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(chatbot_interactions)")
        columns = cursor.fetchall()
        print(f"   📋 chatbot_interactions tiene {len(columns)} columnas:")
        for col in columns:
            print(f"      - {col[1]} ({col[2]})")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        raise

if __name__ == "__main__":
    fix_database_schema()
