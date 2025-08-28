#!/usr/bin/env python
"""
Test de conexión PostgreSQL
Verifica que la aplicación puede conectar correctamente con PostgreSQL
"""

def test_postgresql_connection():
    """Test de conexión a PostgreSQL"""
    print("=== 🔌 PASO 2: TEST CONEXIÓN POSTGRESQL ===\n")
    
    try:
        from app import create_app
        from database.connection import db
        from database.models import ConversationFlow
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            print("1. ✅ Aplicación creada correctamente")
            print(f"   Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Test conexión básica
            result = db.session.execute(db.text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"2. ✅ Conexión PostgreSQL exitosa (test: {test_value})")
            
            # Test tabla conversation_flows
            count_query = db.text("SELECT COUNT(*) FROM conversation_flows")
            result = db.session.execute(count_query)
            flow_count = result.fetchone()[0]
            print(f"3. ✅ Tabla conversation_flows accesible ({flow_count} registros)")
            
            # Test UUID nativo
            uuid_query = db.text("SELECT uuid_generate_v4() as new_uuid")
            result = db.session.execute(uuid_query)
            new_uuid = result.fetchone()[0]
            print(f"4. ✅ Generación UUID nativa funcional: {new_uuid}")
            
            # Test modelo SQLAlchemy
            flows = ConversationFlow.query.all()
            print(f"5. ✅ SQLAlchemy ORM funcional ({len(flows)} flujos encontrados)")
            
            if flows:
                first_flow = flows[0] 
                print(f"   - Ejemplo: ID={first_flow.id}, Nombre={first_flow.name}")
                print(f"   - Tipo ID: {type(first_flow.id)}")
            
            print(f"\n🎉 POSTGRESQL CONFIGURADO CORRECTAMENTE")
            print("   • Conexión exitosa")
            print("   • Tablas accesibles") 
            print("   • UUID nativo funcionando")
            print("   • SQLAlchemy ORM operativo")
            
            return True
            
    except Exception as e:
        print(f"❌ Error en conexión PostgreSQL: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_postgresql_connection()
    if success:
        print(f"\n🚀 LISTO PARA PASO 3: Migración de datos SQLite -> PostgreSQL")
    else:
        print(f"\n⚠️ Revisar configuración antes de continuar")
