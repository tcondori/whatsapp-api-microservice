#!/usr/bin/env python3
"""
Test para el endpoint de envío de mensajes de ubicación
Prueba el endpoint POST /v1/messages/location
"""
import requests
import json
from datetime import datetime

def test_location_endpoint():
    """
    Prueba el endpoint de envío de mensajes de ubicación
    """
    # Configuración de la prueba
    BASE_URL = "http://localhost:5000"
    API_KEY = "dev-api-key"
    
    # Headers para la petición
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("🗺️  Iniciando prueba del endpoint de ubicación...")
    print(f"📡 URL base: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY}")
    print("-" * 60)
    
    # Caso 1: Ubicación básica (solo coordenadas)
    print("\n📍 Caso 1: Ubicación básica (solo coordenadas)")
    location_basic = {
        "to": "5491123456789",
        "type": "location",
        "location": {
            "latitude": -34.6037,
            "longitude": -58.3816
        },
        "messaging_line_id": 1
    }
    
    try:
        print(f"📤 Enviando: {json.dumps(location_basic, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/location",
            headers=headers,
            json=location_basic,
            timeout=10
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Caso 1: EXITOSO - Ubicación básica enviada")
        else:
            print(f"❌ Caso 1: FALLÓ - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Caso 1: ERROR - {str(e)}")
    
    print("\n" + "-" * 60)
    
    # Caso 2: Ubicación completa (con nombre y dirección)
    print("\n🏢 Caso 2: Ubicación completa (con nombre y dirección)")
    location_complete = {
        "to": "5491123456789",
        "type": "location",
        "location": {
            "latitude": -34.6037,
            "longitude": -58.3816,
            "name": "Obelisco de Buenos Aires",
            "address": "Av. 9 de Julio s/n, C1043 CABA, Argentina"
        },
        "messaging_line_id": 1
    }
    
    try:
        print(f"📤 Enviando: {json.dumps(location_complete, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/location",
            headers=headers,
            json=location_complete,
            timeout=10
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Caso 2: EXITOSO - Ubicación completa enviada")
        else:
            print(f"❌ Caso 2: FALLÓ - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Caso 2: ERROR - {str(e)}")
    
    print("\n" + "-" * 60)
    
    # Caso 3: Ubicación de otro país (Nueva York)
    print("\n🗽 Caso 3: Ubicación internacional (Nueva York)")
    location_ny = {
        "to": "5491123456789",
        "type": "location",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "Times Square",
            "address": "Times Square, New York, NY 10036, USA"
        }
    }
    
    try:
        print(f"📤 Enviando: {json.dumps(location_ny, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/location",
            headers=headers,
            json=location_ny,
            timeout=10
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Caso 3: EXITOSO - Ubicación internacional enviada")
        else:
            print(f"❌ Caso 3: FALLÓ - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Caso 3: ERROR - {str(e)}")
    
    print("\n" + "-" * 60)
    
    # Casos de validación (errores esperados)
    print("\n🔍 Casos de validación (errores esperados):")
    
    # Error 1: Falta latitude
    print("\n❌ Error 1: Falta latitude")
    error_case_1 = {
        "to": "5491123456789",
        "type": "location",
        "location": {
            "longitude": -58.3816
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/location",
            headers=headers,
            json=error_case_1,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Error 2: Latitude fuera de rango
    print("\n❌ Error 2: Latitude fuera de rango")
    error_case_2 = {
        "to": "5491123456789",
        "type": "location",
        "location": {
            "latitude": 95.0,  # Fuera del rango válido (-90, 90)
            "longitude": -58.3816
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/location",
            headers=headers,
            json=error_case_2,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Error 3: Tipo de mensaje incorrecto
    print("\n❌ Error 3: Tipo de mensaje incorrecto")
    error_case_3 = {
        "to": "5491123456789",
        "type": "text",  # Tipo incorrecto
        "location": {
            "latitude": -34.6037,
            "longitude": -58.3816
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/location",
            headers=headers,
            json=error_case_3,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba del endpoint de ubicación completada")
    print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_location_endpoint()
