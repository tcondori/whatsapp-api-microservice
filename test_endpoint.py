#!/usr/bin/env python3
"""
Script para probar el endpoint /test específicamente
"""
import requests
import json

def test_endpoint():
    """Prueba el endpoint /test que está fallando"""
    print("🔍 PROBANDO ENDPOINT /test")
    print("=" * 50)
    
    url = "http://localhost:5000/v1/messages/test"
    headers = {
        "X-API-Key": "dev-api-key",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Enviando GET a: {url}")
        print(f"🔑 Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Headers de respuesta: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ RESPUESTA JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print("❌ ERROR: Respuesta no es JSON válido")
                print(f"Contenido: {response.text[:500]}")
        else:
            print("❌ ERROR EN RESPUESTA:")
            print(f"Contenido: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en localhost:5000")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")

if __name__ == "__main__":
    test_endpoint()
