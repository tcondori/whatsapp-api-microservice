#!/usr/bin/env python3
"""
Script simple para revisar estructura completa de messaging_lines
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def check_table_structure():
    """Revisa la estructura completa de messaging_lines"""
    try:
        from app import create_app
        from database.connection import get_db_session
        from sqlalchemy import text
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            session = get_db_session()
            
            try:
                print("🔍 ESTRUCTURA COMPLETA DE messaging_lines:")
                print("=" * 80)
                
                result = session.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'messaging_lines'
                    ORDER BY ordinal_position;
                """))
                
                columns = result.fetchall()
                print(f"{'Columna':<25} {'Tipo':<15} {'Nullable':<8} {'Default':<20}")
                print("-" * 80)
                
                for col_name, data_type, is_nullable, default_val in columns:
                    default_str = str(default_val) if default_val else "None"
                    if len(default_str) > 20:
                        default_str = default_str[:17] + "..."
                    print(f"{col_name:<25} {data_type:<15} {is_nullable:<8} {default_str:<20}")
                
                # Verificar constraints
                print("\n🔒 CONSTRAINTS:")
                result = session.execute(text("""
                    SELECT 
                        tc.constraint_name,
                        tc.constraint_type,
                        kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = 'messaging_lines'
                    ORDER BY tc.constraint_type, kcu.column_name;
                """))
                
                constraints = result.fetchall()
                for constraint_name, constraint_type, column_name in constraints:
                    print(f"  {constraint_type}: {constraint_name} ({column_name})")
                
                # Verificar datos existentes
                print("\n📊 DATOS EXISTENTES:")
                result = session.execute(text("SELECT COUNT(*) FROM messaging_lines;"))
                count = result.scalar()
                print(f"  Total registros: {count}")
                
                if count > 0:
                    result = session.execute(text("""
                        SELECT id, name, phone_number, line_id 
                        FROM messaging_lines 
                        LIMIT 3;
                    """))
                    records = result.fetchall()
                    print("  Primeros registros:")
                    for record in records:
                        print(f"    ID: {record[0]}")
                        print(f"    Name: {record[1]}")
                        print(f"    Phone: {record[2]}")
                        print(f"    Line ID: {record[3]}")
                        print("    ---")
                
                return True
                
            except Exception as e:
                print(f"❌ Error consultando estructura: {str(e)}")
                return False
            finally:
                session.close()
                
    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")
        return False

if __name__ == '__main__':
    check_table_structure()
