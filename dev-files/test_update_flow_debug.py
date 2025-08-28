#!/usr/bin/env python
"""
Test directo para debuggear el método update_flow
"""

from app import create_app
from app.repositories.flow_repository import FlowRepository  

def test_update_flow():
    app = create_app()
    
    with app.app_context():
        flow_repo = FlowRepository()
        
        # Test 1: Verificar que el flujo existe
        flow_id = "32561960-1902-495f-af1f-c6157c2d12b0"
        print(f"=== TEST UPDATE FLOW ===")
        print(f"Flow ID: {flow_id}")
        
        # Verificar que existe usando método personalizado
        existing_flow = flow_repo.find_by_uuid(flow_id)  # Usar método personalizado
        print(f"Flujo existe: {existing_flow is not None}")
        if existing_flow:
            print(f"Nombre: {existing_flow.name}")
            print(f"Estado actual is_active: {existing_flow.is_active}")
            print(f"Tipo de is_active: {type(existing_flow.is_active)}")
        
        # Test 2: Intentar actualizar
        update_data = {"is_active": False}
        print(f"\nIntentando actualizar con: {update_data}")
        
        result = flow_repo.update_flow(flow_id, update_data)
        print(f"Resultado actualización: {result}")
        
        # Test 3: Verificar cambios usando método personalizado
        if result:
            updated_flow = flow_repo.find_by_uuid(flow_id)  # Usar método personalizado
            if updated_flow:
                print(f"✅ Estado después is_active: {updated_flow.is_active}")
                print(f"✅ Tipo de is_active: {type(updated_flow.is_active)}")
                print(f"✅ Nombre: {updated_flow.name}")
            else:
                print("❌ No se pudo obtener flujo después de actualizar")
        else:
            print("❌ La actualización falló")

if __name__ == "__main__":
    test_update_flow()
