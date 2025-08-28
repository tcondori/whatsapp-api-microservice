#!/usr/bin/env python3
"""
Script de migración para sincronizar esquema de messaging_lines
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def migrate_messaging_lines():
    """Migra la tabla messaging_lines para que coincida con el modelo"""
    try:
        print("🔧 Migrando esquema de messaging_lines...")
        
        # Importar después de cargar las variables de entorno
        from app import create_app
        from database.connection import get_db_session
        from sqlalchemy import text
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            session = get_db_session()
            
            try:
                # PASO 1: Verificar estructura actual
                print("📊 Verificando estructura actual...")
                result = session.execute(text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'messaging_lines'
                    ORDER BY ordinal_position;
                """))
                
                current_columns = {row[0]: {'type': row[1], 'nullable': row[2]} for row in result}
                print(f"   Columnas actuales: {list(current_columns.keys())}")
                
                # PASO 2: Agregar columna line_id si no existe
                if 'line_id' not in current_columns:
                    print("➕ Agregando columna line_id...")
                    session.execute(text("""
                        ALTER TABLE messaging_lines 
                        ADD COLUMN line_id VARCHAR(50);
                    """))
                    session.commit()
                    print("   ✅ Columna line_id agregada")
                else:
                    print("   ✅ Columna line_id ya existe")
                
                # PASO 3: Agregar/actualizar columnas faltantes
                migrations = [
                    ("phone_number_id", "VARCHAR(255)", False),
                    ("display_name", "VARCHAR(255)", False), 
                    ("webhook_url", "TEXT", True),
                    ("max_daily_messages", "INTEGER", True),
                    ("current_daily_count", "INTEGER", True),
                    ("last_reset_date", "DATE", True),
                    ("api_version", "VARCHAR(10)", True),
                    ("business_id", "VARCHAR(255)", True)
                ]
                
                for col_name, col_type, nullable in migrations:
                    if col_name not in current_columns:
                        print(f"➕ Agregando columna {col_name}...")
                        null_clause = "" if nullable else "NOT NULL DEFAULT ''"
                        if col_name == "max_daily_messages":
                            null_clause = "DEFAULT 1000"
                        elif col_name == "current_daily_count":
                            null_clause = "DEFAULT 0"
                        elif col_name == "last_reset_date":
                            null_clause = "DEFAULT CURRENT_DATE"
                        elif col_name == "api_version":
                            null_clause = "DEFAULT 'v18.0'"
                        
                        session.execute(text(f"""
                            ALTER TABLE messaging_lines 
                            ADD COLUMN {col_name} {col_type} {null_clause};
                        """))
                        session.commit()
                        print(f"   ✅ Columna {col_name} agregada")
                
                # PASO 4: Crear índices únicos y optimizados
                print("🗂️  Creando índices...")
                indices = [
                    ("idx_messaging_lines_line_id", "line_id", True),
                    ("idx_messaging_lines_phone_number_id", "phone_number_id", False),
                    ("idx_messaging_lines_is_active", "is_active", False)
                ]
                
                for idx_name, col_name, unique in indices:
                    try:
                        unique_clause = "UNIQUE" if unique else ""
                        session.execute(text(f"""
                            CREATE {unique_clause} INDEX IF NOT EXISTS {idx_name} 
                            ON messaging_lines ({col_name});
                        """))
                        session.commit()
                        print(f"   ✅ Índice {idx_name} creado")
                    except Exception as e:
                        print(f"   ⚠️  Índice {idx_name} ya existe o error: {str(e)[:50]}...")
                
                # PASO 5: Insertar línea por defecto si la tabla está vacía
                print("📝 Verificando datos...")
                result = session.execute(text("SELECT COUNT(*) FROM messaging_lines;"))
                count = result.scalar()
                
                if count == 0:
                    print("➕ Insertando línea por defecto...")
                    session.execute(text("""
                        INSERT INTO messaging_lines 
                        (line_id, phone_number_id, display_name, phone_number, name, whatsapp_business_id, access_token, is_active, max_daily_messages, current_daily_count, api_version)
                        VALUES 
                        (:line_id, :phone_number_id, :display_name, :phone_number, :name, :whatsapp_business_id, :access_token, :is_active, :max_daily_messages, :current_daily_count, :api_version);
                    """), {
                        'line_id': 'line_1',
                        'phone_number_id': os.getenv('LINE_1_PHONE_NUMBER_ID', '137474306106595'),
                        'display_name': os.getenv('LINE_1_DISPLAY_NAME', 'Mi WhatsApp Business'),
                        'phone_number': os.getenv('LINE_1_PHONE_NUMBER', '+59167028778'),
                        'name': 'Línea Principal',
                        'whatsapp_business_id': os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', 'default_business_id'),
                        'access_token': os.getenv('LINE_1_ACCESS_TOKEN', os.getenv('WHATSAPP_ACCESS_TOKEN', 'default_token')),
                        'is_active': True,
                        'max_daily_messages': 1000,
                        'current_daily_count': 0,
                        'api_version': 'v18.0'
                    })
                    session.commit()
                    print("   ✅ Línea por defecto creada")
                else:
                    print(f"   ✅ Tabla ya tiene {count} línea(s)")
                    
                    # Verificar si alguna línea tiene line_id vacío y asignarlo
                    result = session.execute(text("""
                        SELECT id FROM messaging_lines 
                        WHERE line_id IS NULL OR line_id = '';
                    """))
                    
                    empty_line_ids = result.fetchall()
                    
                    for idx, (uuid_id,) in enumerate(empty_line_ids):
                        line_id = f"line_{idx + 1}"
                        print(f"🔄 Actualizando línea sin line_id: {uuid_id} -> {line_id}")
                        session.execute(text("""
                            UPDATE messaging_lines 
                            SET line_id = :line_id,
                                name = COALESCE(name, :name),
                                phone_number_id = COALESCE(phone_number_id, :phone_number_id),
                                display_name = COALESCE(display_name, :display_name),
                                whatsapp_business_id = COALESCE(whatsapp_business_id, :whatsapp_business_id),
                                access_token = COALESCE(access_token, :access_token),
                                max_daily_messages = COALESCE(max_daily_messages, 1000),
                                current_daily_count = COALESCE(current_daily_count, 0),
                                api_version = COALESCE(api_version, 'v18.0')
                            WHERE id = :uuid_id;
                        """), {
                            'line_id': line_id,
                            'name': f'Línea {idx + 1}',
                            'phone_number_id': os.getenv('LINE_1_PHONE_NUMBER_ID', '137474306106595'),
                            'display_name': f'Línea {idx + 1}',
                            'whatsapp_business_id': os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', 'default_business_id'),
                            'access_token': os.getenv('LINE_1_ACCESS_TOKEN', os.getenv('WHATSAPP_ACCESS_TOKEN', 'default_token')),
                            'uuid_id': uuid_id
                        })
                        session.commit()
                        print(f"   ✅ Línea actualizada: {line_id}")
                
                # PASO 6: Verificar datos finales
                print("🔍 Verificando datos finales...")
                result = session.execute(text("""
                    SELECT line_id, phone_number_id, display_name, phone_number, is_active 
                    FROM messaging_lines 
                    ORDER BY created_at;
                """))
                
                lines = result.fetchall()
                print(f"📊 Total de líneas: {len(lines)}")
                for line in lines:
                    line_id, phone_number_id, display_name, phone_number, is_active = line
                    print(f"   🔗 {line_id}: {display_name} ({phone_number}) - {'Activa' if is_active else 'Inactiva'}")
                
                print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
                return True
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
    except Exception as e:
        print(f"❌ Error en migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_messaging_line_repository():
    """Prueba el repositorio después de la migración"""
    try:
        print("\n🧪 Probando MessagingLineRepository...")
        
        from app import create_app
        from app.repositories.base_repo import MessagingLineRepository
        
        app = create_app()
        
        with app.app_context():
            line_repo = MessagingLineRepository()
            
            # Probar búsqueda por line_id
            line = line_repo.get_by_line_id('line_1')
            
            if line:
                print(f"✅ Línea encontrada:")
                print(f"   🆔 Line ID: {line.line_id}")
                print(f"   📱 Phone Number ID: {line.phone_number_id}")
                print(f"   📞 Número: {line.phone_number}")
                print(f"   📝 Nombre: {line.display_name}")
                print(f"   ✅ Activa: {line.is_active}")
                print(f"   📊 Límite: {line.max_daily_messages}")
                
                # Probar método can_send_message
                can_send = line.can_send_message()
                print(f"   🚀 Puede enviar: {can_send}")
                
                return True
            else:
                print("❌ No se pudo encontrar la línea 'line_1'")
                return False
                
    except Exception as e:
        print(f"❌ Error probando repositorio: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🗃️  MIGRACIÓN DE ESQUEMA MESSAGING_LINES")
    print("=" * 60)
    
    # Paso 1: Migrar esquema
    if migrate_messaging_lines():
        print(f"\n{'='*60}")
        print("🧪 PROBANDO REPOSITORIO")
        print("=" * 60)
        
        # Paso 2: Probar repositorio
        if test_messaging_line_repository():
            print(f"\n{'='*60}")
            print("🎉 ¡MIGRACIÓN Y PRUEBAS COMPLETADAS!")
            print("=" * 60)
            print("\n📝 AHORA PUEDES PROBAR EL ENDPOINT:")
            print("curl -X POST http://localhost:5001/v1/messages/text \\")
            print('     -H "X-API-Key: dev-api-key" \\')
            print('     -H "Content-Type: application/json" \\')
            print('     -d \'{')
            print('       "to": "59167028778",')
            print('       "text": "¡Hola! Mensaje después de la migración",')
            print('       "line_id": "line_1"')
            print('     }\'')
        else:
            print("\n❌ Error en las pruebas del repositorio")
            sys.exit(1)
    else:
        print("\n❌ Error en la migración")
        sys.exit(1)
