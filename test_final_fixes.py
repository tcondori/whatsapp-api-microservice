#!/usr/bin/env python3
"""
Script de prueba final para verificar que los errores están solucionados
"""

import requests
import json

def test_fixes():
    """
    Prueba las correcciones de line_id y API key
    """
    
    BASE_URL = "http://localhost:5000"
    API_KEY = "dev-api-key"
    
    print("🧪 PRUEBA DE CORRECCIONES")
    print("=" * 50)
    
    # Test 1: Probar con line_id string válido
    print("\n1️⃣  Probando con line_id='1' (string que existe en BD):")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Prueba con line_id string '1'",
                "line_id": "1"  # String que existe en BD
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            }
        )
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Éxito: {response.json()}")
        elif response.status_code == 401:
            print(f"❌ Error de autenticación: {response.json()}")
        else:
            print(f"⚠️  Otro error: {response.json()}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 2: Probar con line_id numérico
    print("\n2️⃣  Probando con line_id=1 (entero):")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Prueba con line_id entero 1",
                "line_id": 1  # Entero
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            }
        )
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Éxito: {response.json()}")
        elif response.status_code == 401:
            print(f"❌ Error de autenticación: {response.json()}")
        else:
            print(f"⚠️  Otro error: {response.json()}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Verificar que el error de line_id='line_1' se maneja mejor
    print("\n3️⃣  Probando con line_id='line_1' (debería dar error claro):")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Prueba con line_id inválido",
                "line_id": "line_1"  # No existe en BD
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            }
        )
        print(f"⚠️  Status: {response.status_code}")
        print(f"⚠️  Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE CORRECCIONES:")
    print("✅ Line ID: Ahora busca como string, no fuerza conversión a int")
    print("✅ API Key: Configuración de seguridad ajustada en Swagger")
    print("✅ Line IDs válidos: '1', '2', 'line_auto_123456789012345', '386149'")
    print("✅ API Key válido: 'dev-api-key'")
    
    print("\n📝 PARA SWAGGER UI:")
    print("1. Ve a http://localhost:5000/docs/")
    print("2. Haz clic en 'Authorize' 🔒")
    print("3. Ingresa: dev-api-key")
    print("4. Usa payloads con line_id válidos:")
    print("   - line_id: '1' o line_id: 1")
    print("   - line_id: '2' o line_id: 2")

if __name__ == "__main__":
    test_fixes()
