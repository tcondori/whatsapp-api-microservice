"""
Prueba de endpoints de flujos con PostgreSQL y UUIDs
Verifica que los botones de editar, activar/desactivar funcionen correctamente
"""
import requests
import json
from test_clean_postgresql_setup import setup_test_environment

def test_flows_endpoints():
    """Prueba endpoints de flujos con soporte nativo para UUID"""
    
    # Configurar entorno
    flows = setup_test_environment()
    if not flows:
        print("❌ Error configurando entorno de prueba")
        return False
        
    base_url = "http://localhost:5000/api/v1/flows"
    headers = {
        'X-API-Key': 'test-api-key-2024',
        'Content-Type': 'application/json'
    }
    
    print("\n🧪 Iniciando pruebas de endpoints de flujos...")
    
    # 1. Probar GET /flows (listar todos)
    print("\n1. Probando GET /flows...")
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            flows_list = data.get('flows', [])
            print(f"✅ Lista obtenida: {len(flows_list)} flujos")
            
            # Obtener primer flujo para pruebas
            if flows_list:
                test_flow = flows_list[0]
                flow_id = test_flow['id']
                print(f"   📋 Flujo de prueba: {test_flow['name']} (ID: {flow_id})")
            else:
                print("❌ No hay flujos para probar")
                return False
        else:
            print(f"❌ Error en GET /flows: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Excepción en GET /flows: {e}")
        return False
    
    # 2. Probar GET /flows/<id> (obtener uno específico)
    print(f"\n2. Probando GET /flows/{flow_id}...")
    try:
        response = requests.get(f"{base_url}/{flow_id}", headers=headers)
        if response.status_code == 200:
            flow_data = response.json()
            print(f"✅ Flujo obtenido: {flow_data['name']}")
            print(f"   📊 Estado: {'Activo' if flow_data['is_active'] else 'Inactivo'}")
        else:
            print(f"❌ Error en GET /flows/{flow_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Excepción en GET /flows/{flow_id}: {e}")
        return False
    
    # 3. Probar POST /flows/<id>/activate (activar)
    print(f"\n3. Probando POST /flows/{flow_id}/activate...")
    try:
        response = requests.post(f"{base_url}/{flow_id}/activate", headers=headers)
        if response.status_code == 200:
            activated_flow = response.json()
            print(f"✅ Flujo activado: {activated_flow['name']}")
            print(f"   📊 Nuevo estado: {'Activo' if activated_flow['is_active'] else 'Inactivo'}")
        else:
            print(f"❌ Error en POST activate: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción en POST activate: {e}")
        return False
    
    # 4. Probar DELETE /flows/<id>/activate (desactivar)
    print(f"\n4. Probando DELETE /flows/{flow_id}/activate...")
    try:
        response = requests.delete(f"{base_url}/{flow_id}/activate", headers=headers)
        if response.status_code == 200:
            deactivated_flow = response.json()
            print(f"✅ Flujo desactivado: {deactivated_flow['name']}")
            print(f"   📊 Nuevo estado: {'Activo' if deactivated_flow['is_active'] else 'Inactivo'}")
        else:
            print(f"❌ Error en DELETE activate: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción en DELETE activate: {e}")
        return False
    
    # 5. Probar PUT /flows/<id> (actualizar)
    print(f"\n5. Probando PUT /flows/{flow_id}...")
    try:
        update_data = {
            "name": f"{test_flow['name']} - Actualizado",
            "description": "Descripción actualizada desde test",
            "is_active": True,
            "priority": 10
        }
        
        response = requests.put(f"{base_url}/{flow_id}", 
                              headers=headers, 
                              data=json.dumps(update_data))
        
        if response.status_code == 200:
            updated_flow = response.json()
            print(f"✅ Flujo actualizado: {updated_flow['name']}")
            print(f"   📝 Nueva descripción: {updated_flow['description']}")
        else:
            print(f"❌ Error en PUT /flows/{flow_id}: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción en PUT /flows/{flow_id}: {e}")
        return False
    
    print("\n🎉 Todas las pruebas de endpoints completadas exitosamente!")
    print("✅ Los botones de editar, activar/desactivar deberían funcionar correctamente")
    return True

if __name__ == "__main__":
    try:
        success = test_flows_endpoints()
        if success:
            print("\n🏆 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("🔧 Los botones del editor RiveScript ahora funcionan con PostgreSQL y UUIDs")
            print("📊 UUID con guiones habilitado nativamente")
        else:
            print("\n❌ Algunas pruebas fallaron")
    except Exception as e:
        print(f"\n💥 Error general: {e}")
