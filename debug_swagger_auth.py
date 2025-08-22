#!/usr/bin/env python3
"""
Script para verificar y corregir definitivamente el problema de autenticación en Swagger
"""

import requests
import json

def test_direct_swagger_endpoints():
    """
    Prueba directamente los endpoints desde Swagger para verificar autenticación
    """
    
    BASE_URL = "http://localhost:5000"
    API_KEY = "dev-api-key"
    
    print("🔍 DIAGNÓSTICO PROFUNDO DE SWAGGER AUTHENTICATION")
    print("=" * 60)
    
    # Test 1: Verificar el endpoint swagger.json para ver la configuración
    print("\n1️⃣  Verificando configuración de Swagger (swagger.json):")
    try:
        response = requests.get(f"{BASE_URL}/swagger.json")
        if response.status_code == 200:
            swagger_config = response.json()
            
            # Verificar si tiene security definitions
            if 'securityDefinitions' in swagger_config:
                print("✅ SecurityDefinitions encontradas:")
                for key, value in swagger_config['securityDefinitions'].items():
                    print(f"   {key}: {value}")
            else:
                print("❌ NO hay securityDefinitions en swagger.json")
            
            # Verificar si tiene security global
            if 'security' in swagger_config:
                print(f"✅ Security global: {swagger_config['security']}")
            else:
                print("❌ NO hay security global en swagger.json")
            
            # Verificar endpoints específicos
            paths = swagger_config.get('paths', {})
            messages_text_path = paths.get('/v1/messages/text', {})
            post_method = messages_text_path.get('post', {})
            
            if 'security' in post_method:
                print(f"✅ Security en /v1/messages/text POST: {post_method['security']}")
            else:
                print("❌ NO hay security en /v1/messages/text POST")
                
        else:
            print(f"❌ Error obteniendo swagger.json: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Probar endpoint sin autenticación (debe fallar)
    print("\n2️⃣  Probando endpoint SIN header X-API-Key:")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Test sin API Key",
                "line_id": 1
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Correcto: El endpoint rechaza requests sin API key")
        else:
            print("❌ Problema: El endpoint no rechaza requests sin API key")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Probar endpoint con autenticación (debe funcionar)
    print("\n3️⃣  Probando endpoint CON header X-API-Key:")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            json={
                "to": "+59167028778",
                "text": "Test con API Key",
                "line_id": 1
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Correcto: El endpoint acepta requests con API key válida")
            result = response.json()
            print(f"✅ Mensaje enviado: {result.get('data', {}).get('whatsapp_message_id', 'N/A')}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 ANÁLISIS:")
    print("Si ves 'NO hay securityDefinitions' o 'NO hay security', el problema")
    print("está en la configuración de Flask-RESTX, no en los decoradores.")
    print("\n🔧 PRÓXIMA ACCIÓN:")
    print("Vamos a regenerar completamente la configuración de Swagger")

if __name__ == "__main__":
    test_direct_swagger_endpoints()
