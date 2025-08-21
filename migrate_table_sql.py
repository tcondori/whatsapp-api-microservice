#!/usr/bin/env python3
"""
Migración SQL directa: Recrear tabla messaging_lines con line_id INTEGER

Esta migración recreará la tabla para que SQLite trate line_id como INTEGER nativo
"""
from entrypoint import create_app
from database.connection import db
from sqlalchemy import text
import logging

def migrate_table_structure():
    """
    Recrear la tabla con estructura correcta de INTEGER
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 MIGRACIÓN SQL: Recreando tabla messaging_lines")
            print("=" * 60)
            
            # PASO 1: Obtener datos actuales
            print("📋 Obteniendo datos actuales...")
            result = db.session.execute(text("""
                SELECT line_id, phone_number_id, display_name, phone_number, 
                       webhook_url, is_active, max_daily_messages, current_daily_count,
                       last_reset_date, api_version, business_id, id, created_at, updated_at
                FROM messaging_lines
            """))
            
            existing_data = []
            for row in result:
                existing_data.append({
                    'line_id': int(row[0]),  # Convertir explícitamente a int
                    'phone_number_id': row[1],
                    'display_name': row[2],
                    'phone_number': row[3],
                    'webhook_url': row[4],
                    'is_active': row[5],
                    'max_daily_messages': row[6],
                    'current_daily_count': row[7],
                    'last_reset_date': row[8],
                    'api_version': row[9],
                    'business_id': row[10],
                    'id': row[11],
                    'created_at': row[12],
                    'updated_at': row[13]
                })
            
            print(f"✅ Datos obtenidos: {len(existing_data)} registros")
            for data in existing_data:
                print(f"  - line_id: {data['line_id']} (será INTEGER)")
            
            # PASO 2: Renombrar tabla actual
            print("🔄 Renombrando tabla actual...")
            db.session.execute(text("ALTER TABLE messaging_lines RENAME TO messaging_lines_backup"))
            
            # PASO 3: Recrear tabla con estructura correcta
            print("🔄 Recreando tabla con line_id INTEGER...")
            db.session.execute(text("""
                CREATE TABLE messaging_lines (
                    line_id INTEGER NOT NULL UNIQUE,
                    phone_number_id VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20),
                    webhook_url TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    max_daily_messages INTEGER DEFAULT 1000,
                    current_daily_count INTEGER DEFAULT 0,
                    last_reset_date DATE,
                    api_version VARCHAR(10) DEFAULT 'v18.0',
                    business_id VARCHAR(255),
                    id CHAR(36) NOT NULL PRIMARY KEY,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))
            
            # PASO 4: Crear índices
            print("🔄 Creando índices...")
            db.session.execute(text("CREATE UNIQUE INDEX ix_messaging_lines_line_id ON messaging_lines (line_id)"))
            db.session.execute(text("CREATE INDEX ix_messaging_lines_is_active ON messaging_lines (is_active)"))
            
            # PASO 5: Insertar datos con line_id como INTEGER
            print("🔄 Insertando datos con line_id INTEGER...")
            for data in existing_data:
                db.session.execute(text("""
                    INSERT INTO messaging_lines 
                    (line_id, phone_number_id, display_name, phone_number, webhook_url, 
                     is_active, max_daily_messages, current_daily_count, last_reset_date,
                     api_version, business_id, id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """), (
                    data['line_id'],  # INTEGER
                    data['phone_number_id'],
                    data['display_name'],
                    data['phone_number'],
                    data['webhook_url'],
                    data['is_active'],
                    data['max_daily_messages'],
                    data['current_daily_count'],
                    data['last_reset_date'],
                    data['api_version'],
                    data['business_id'],
                    data['id'],
                    data['created_at'],
                    data['updated_at']
                ))
            
            # PASO 6: Confirmar cambios
            db.session.commit()
            print("✅ Migración SQL completada")
            
            # PASO 7: Verificar resultado
            print("🔍 Verificando estructura final...")
            result = db.session.execute(text("PRAGMA table_info(messaging_lines)"))
            print("📋 Estructura de tabla:")
            for row in result:
                if row[1] == 'line_id':
                    print(f"  ✅ {row[1]}: {row[2]} (NOT NULL: {row[3]}, PK: {row[5]})")
                else:
                    print(f"     {row[1]}: {row[2]}")
            
            # PASO 8: Verificar datos
            result = db.session.execute(text("SELECT line_id, phone_number_id, display_name FROM messaging_lines"))
            print("📋 Datos finales:")
            for row in result:
                print(f"  - line_id: {row[0]} (tipo en SQLite: INTEGER)")
            
            # PASO 9: Eliminar tabla backup (opcional)
            print("🗑️  Eliminando tabla backup...")
            db.session.execute(text("DROP TABLE messaging_lines_backup"))
            db.session.commit()
            
            print("🎉 MIGRACIÓN COMPLETA!")
            return True
            
        except Exception as e:
            print(f"❌ Error durante migración SQL: {e}")
            db.session.rollback()
            
            # Intentar restaurar desde backup si existe
            try:
                db.session.execute(text("DROP TABLE IF EXISTS messaging_lines"))
                db.session.execute(text("ALTER TABLE messaging_lines_backup RENAME TO messaging_lines"))
                db.session.commit()
                print("🔄 Tabla restaurada desde backup")
            except:
                print("❌ No se pudo restaurar desde backup")
            
            return False

if __name__ == "__main__":
    print("🔄 MIGRACIÓN SQL: line_id como INTEGER nativo")
    print("Recreando tabla con estructura correcta")
    print("=" * 60)
    
    success = migrate_table_structure()
    
    if success:
        print("\n✅ MIGRACIÓN SQL EXITOSA")
        print("- Tabla recreada con line_id INTEGER nativo")
        print("- Datos preservados y convertidos")
        print("- Índices recreados")
    else:
        print("\n❌ MIGRACIÓN SQL FALLÓ")
        print("- Verificar logs para detalles")
        print("- Tabla debe haber sido restaurada desde backup")
