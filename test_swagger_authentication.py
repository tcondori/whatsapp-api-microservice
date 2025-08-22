#!/usr/bin/env python3
"""
Script para verificar que los endpoints de Swagger funcionan correctamente
con la autenticación por API Key configurada
"""

import requests
import json
import time

def test_swagger_authentication():
    """
    Prueba la autenticación en Swagger y endpoints
    """
    
    BASE_URL = "http://localhost:5000"
    API_KEY = "dev-api-key"
    
    print("🧪 PRUEBA DE AUTENTICACIÓN EN SWAGGER")
    print("=" * 50)
    
    # Test 1: Health check (sin autenticación)
    print("\n1️⃣  Testing health check (sin autenticación):")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Endpoint sin API Key (debe fallar)
    print("\n2️⃣  Testing endpoint SIN API Key (debe fallar):")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Test sin API Key",
                "line_id": "line_1"
            }
        )
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Error esperado: {response.json()}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Endpoint CON API Key (debe funcionar)
    print("\n3️⃣  Testing endpoint CON API Key (debe funcionar):")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Test con API Key desde script de verificación",
                "line_id": "line_1"
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            }
        )
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Mensaje enviado: {response.json()}")
        else:
            print(f"⚠️  Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Verificar que Swagger está disponible
    print("\n4️⃣  Testing Swagger UI:")
    try:
        response = requests.get(f"{BASE_URL}/docs/")
        if response.status_code == 200:
            print("✅ Swagger UI está disponible")
            print(f"🌐 Accede a: {BASE_URL}/docs/")
        else:
            print(f"❌ Swagger UI no disponible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo a Swagger: {e}")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCCIONES PARA USAR SWAGGER UI:")
    print("1. Ve a http://localhost:5000/docs/")
    print("2. Busca el botón 'Authorize' 🔒 en la parte superior derecha")
    print("3. Haz clic en 'Authorize'")
    print("4. En el campo 'value', ingresa: dev-api-key")
    print("5. Haz clic en 'Authorize' y luego 'Close'")
    print("6. Ahora todos los endpoints 🔒 estarán autenticados")
    print("7. Prueba cualquier endpoint /v1/messages - ¡debería funcionar!")
    
    print("\n✨ API Keys válidas:")
    print("- dev-api-key")
    print("- test-key-123")
    print("- test_key")

if __name__ == "__main__":
    print("🚀 Iniciando verificación de autenticación en Swagger...")
    time.sleep(1)
    test_swagger_authentication()
