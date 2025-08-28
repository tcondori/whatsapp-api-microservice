#!/usr/bin/env python3
"""
Verificar datos existentes en la base de datos
"""
import sys
import os
sys.path.append(os.getcwd())

from app import create_app
from database.connection import db
from database.models import ConversationFlow

def check_flows():
    """Verificar flujos existentes"""
    print("🔍 Verificando flujos en la base de datos...")
    
    app = create_app()
    
    with app.app_context():
        try:
            flows = ConversationFlow.query.all()
            print(f"📊 Total flujos encontrados: {len(flows)}")
            
            if flows:
                print("\n🔢 Lista de flujos:")
                for i, flow in enumerate(flows, 1):
                    print(f"   {i}. ID: {flow.id}")
                    print(f"      Nombre: {flow.name}")
                    print(f"      Activo: {flow.is_active}")
                    print(f"      Tipo ID: {type(flow.id)}")
                    print()
                
                # Probar buscar el flujo específico
                test_id = "32561960-1902-495f-af1f-c6157c2d12b0"
                print(f"🎯 Buscando flujo con ID: {test_id}")
                
                # Método directo
                flow_found = None
                for flow in flows:
                    if str(flow.id) == test_id:
                        flow_found = flow
                        break
                
                if flow_found:
                    print("✅ Flujo encontrado en la lista!")
                    print(f"   Nombre: {flow_found.name}")
                else:
                    print("❌ Flujo NO encontrado en la lista")
                    print("🔍 IDs disponibles:")
                    for flow in flows[:3]:
                        print(f"   - {flow.id}")
                
            else:
                print("❌ No hay flujos en la base de datos")
                print("💡 Necesitamos crear datos de prueba")
                
        except Exception as e:
            print(f"❌ Error al consultar la base de datos: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_flows()
