#!/usr/bin/env python3
"""
Test rápido para diagnosticar el error de swagger.json
"""

import requests
import traceback

def test_swagger_json():
    """
    Prueba el endpoint swagger.json para diagnosticar el error
    """
    try:
        print("🔍 Probando acceso a swagger.json...")
        response = requests.get('http://localhost:5000/swagger.json', timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ swagger.json se generó correctamente")
            data = response.json()
            print(f"📋 Paths encontrados: {len(data.get('paths', {}))}")
            print(f"📋 Definiciones encontradas: {len(data.get('definitions', {}))}")
            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text[:500]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_swagger_json()
