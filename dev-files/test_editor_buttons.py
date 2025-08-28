#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de los botones del editor RiveScript
Verifica que las funciones JavaScript funcionen correctamente
"""

import requests
import json
import time

def test_editor_buttons():
    """Probar funcionalidades del editor"""
    base_url = "http://localhost:5001"
    headers = {"X-API-Key": "dev-api-key"}
    
    print("🧪 PROBANDO BOTONES DEL EDITOR RIVESCRIPT")
    print("=" * 50)
    
    # 1. Verificar que el servidor esté funcionando
    try:
        response = requests.get(f"{base_url}/health", headers=headers)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print(f"❌ Servidor no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # 2. Obtener lista de flujos
    try:
        response = requests.get(f"{base_url}/rivescript/flows", headers=headers)
        data = response.json()
        
        if data["status"] == "success" and data["flows"]:
            print(f"✅ Flujos obtenidos: {data['total']} flujos")
            
            # Buscar un flujo activo para probar
            active_flow = None
            inactive_flow = None
            
            for flow in data["flows"]:
                if flow["is_active"] and not active_flow:
                    active_flow = flow
                elif not flow["is_active"] and not inactive_flow:
                    inactive_flow = flow
                    
                if active_flow and inactive_flow:
                    break
            
            if not active_flow:
                print("❌ No se encontró ningún flujo activo para probar")
                return False
                
            print(f"✅ Flujo activo encontrado: {active_flow['name']}")
            
            # 3. Probar obtener detalles de un flujo (simula loadFlowInEditor)
            flow_id = active_flow["id"]
            response = requests.get(f"{base_url}/rivescript/flows/{flow_id}", headers=headers)
            
            if response.status_code == 200:
                flow_data = response.json()
                if flow_data["status"] == "success":
                    print("✅ Detalles del flujo obtenidos (loadFlowInEditor OK)")
                    print(f"   - Nombre: {flow_data['flow']['name']}")
                    print(f"   - Contenido: {len(flow_data['flow']['rivescript_content'])} caracteres")
                else:
                    print(f"❌ Error obteniendo detalles: {flow_data.get('message', 'Unknown error')}")
            else:
                print(f"❌ Error HTTP obteniendo detalles: {response.status_code}")
            
            # 4. Probar toggle de estado si hay flujo inactivo
            if inactive_flow:
                print(f"✅ Flujo inactivo encontrado: {inactive_flow['name']}")
                
                # Activar el flujo inactivo
                toggle_data = {"is_active": True}
                response = requests.put(
                    f"{base_url}/rivescript/flows/{inactive_flow['id']}", 
                    json=toggle_data, 
                    headers={**headers, "Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result["status"] == "success":
                        print("✅ Toggle de estado funcionando (activación OK)")
                        
                        # Volver a desactivar
                        time.sleep(0.5)
                        toggle_data = {"is_active": False}
                        response = requests.put(
                            f"{base_url}/rivescript/flows/{inactive_flow['id']}", 
                            json=toggle_data, 
                            headers={**headers, "Content-Type": "application/json"}
                        )
                        
                        if response.status_code == 200:
                            print("✅ Toggle de estado funcionando (desactivación OK)")
                        else:
                            print(f"❌ Error desactivando: {response.status_code}")
                    else:
                        print(f"❌ Error en toggle: {result.get('message', 'Unknown error')}")
                else:
                    print(f"❌ Error HTTP en toggle: {response.status_code}")
            else:
                print("⚠️  No hay flujos inactivos para probar toggle")
            
            print("\n🎉 PRUEBAS COMPLETADAS")
            print("\n📋 PASOS PARA PROBAR EN EL NAVEGADOR:")
            print("1. Abrir: http://localhost:5001/chat")
            print("2. Hacer clic en '🔄 Actualizar Flujos'")
            print("3. Hacer clic en '📝' junto a cualquier flujo para editarlo")
            print("4. Hacer clic en '⏸️' o '▶️' para activar/desactivar flujos")
            print("5. Revisar la consola del navegador (F12) para logs detallados")
            
            return True
            
        else:
            print("❌ No se pudieron obtener los flujos")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo flujos: {e}")
        return False

if __name__ == "__main__":
    test_editor_buttons()
