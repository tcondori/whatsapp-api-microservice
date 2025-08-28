#!/usr/bin/env python3
"""
Test para verificar el problema del UUID en get_by_id
"""
import uuid
from app import create_app
from database.connection import db
from database.models import ConversationFlow

def test_uuid_query():
    """Prueba la consulta con UUID"""
    app = create_app()
    
    with app.app_context():
        # UUID de prueba
        flow_id_str = '32561960-1902-495f-af1f-c6157c2d12b0'
        print(f"🔍 UUID de prueba: {flow_id_str}")
        
        # Verificar que el flujo existe en la base de datos
        all_flows = ConversationFlow.query.all()
        print(f"📊 Total de flujos en DB: {len(all_flows)}")
        
        # Mostrar algunos UUIDs de la base de datos
        print("🔢 Primeros 5 UUIDs en DB:")
        for flow in all_flows[:5]:
            print(f"   - {flow.id} ({type(flow.id)})")
            print(f"     Nombre: {flow.name}")
            
        print("\n" + "="*50)
        
        # Intentar diferentes métodos de consulta
        print("🧪 Pruebas de consulta:")
        
        # Método 1: String directo
        print("1️⃣ Consulta con string:")
        try:
            flow1 = ConversationFlow.query.get(flow_id_str)
            print(f"   Resultado: {flow1 is not None}")
            if flow1:
                print(f"   Nombre: {flow1.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        # Método 2: Objeto UUID
        print("2️⃣ Consulta con objeto UUID:")
        try:
            flow_id_uuid = uuid.UUID(flow_id_str)
            flow2 = ConversationFlow.query.get(flow_id_uuid)
            print(f"   Resultado: {flow2 is not None}")
            if flow2:
                print(f"   Nombre: {flow2.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        # Método 3: Filter by
        print("3️⃣ Consulta con filter:")
        try:
            flow3 = ConversationFlow.query.filter(ConversationFlow.id == flow_id_str).first()
            print(f"   Resultado: {flow3 is not None}")
            if flow3:
                print(f"   Nombre: {flow3.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        # Método 4: Filter con UUID object
        print("4️⃣ Consulta con filter + UUID object:")
        try:
            flow_id_uuid = uuid.UUID(flow_id_str)
            flow4 = ConversationFlow.query.filter(ConversationFlow.id == flow_id_uuid).first()
            print(f"   Resultado: {flow4 is not None}")
            if flow4:
                print(f"   Nombre: {flow4.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        # Verificar tipo del campo id
        print("\n🔍 Información del campo ID:")
        try:
            id_column = ConversationFlow.__table__.columns['id']
            print(f"   Tipo de columna: {id_column.type}")
            print(f"   Tipo Python: {id_column.type.python_type}")
        except Exception as e:
            print(f"   ❌ Error al obtener info de columna: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando test de UUID...")
    test_uuid_query()
    print("✅ Test completado")
