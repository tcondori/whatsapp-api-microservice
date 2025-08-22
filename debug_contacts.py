#!/usr/bin/env python3
"""
Script de depuración para endpoint de contactos - WhatsApp API
Muestra el JSON generado y prueba el endpoint
"""

import json
import requests
from pprint import pprint

# Configuración
BASE_URL = "http://127.0.0.1:5000"
ENDPOINT = "/v1/messages/contacts"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "dev-api-key"
}

def test_basic_contact():
    print("=" * 60)
    print("🧪 DEPURACIÓN: Contacto básico")
    print("=" * 60)
    
    # Payload de contacto básico
    payload = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Juan Perez",
                    "first_name": "Juan",
                    "last_name": "Perez"
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "WORK",
                        "wa_id": "5491123456789"
                    }
                ]
            }
        ]
    }
    
    # Mostrar JSON generado
    json_payload = json.dumps(payload, indent=2, ensure_ascii=False)
    print(f"📋 JSON generado ({len(json_payload)} caracteres):")
    print(json_payload)
    
    # Verificar carácter en posición 128 si existe
    if len(json_payload) > 128:
        print(f"\n🔍 Carácter en posición 128: '{json_payload[127]}'")
        print(f"🔍 Contexto (posiciones 120-135):")
        print(f"'{json_payload[120:136]}'")
    
    # Enviar request
    print(f"\n📤 Enviando POST a: {BASE_URL}{ENDPOINT}")
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response:")
        
        try:
            response_json = response.json()
            pprint(response_json)
        except json.JSONDecodeError:
            print("⚠️  Respuesta no es JSON válido:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_complete_contact():
    print("\n" + "=" * 60)
    print("🧪 DEPURACIÓN: Contacto completo")
    print("=" * 60)
    
    payload = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Maria Garcia",
                    "first_name": "Maria",
                    "last_name": "Garcia",
                    "middle_name": "Elena",
                    "suffix": "Ing.",
                    "prefix": "Dra."
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "WORK",
                        "wa_id": "5491123456789"
                    },
                    {
                        "phone": "+5491187654321",
                        "type": "HOME"
                    }
                ],
                "emails": [
                    {
                        "email": "maria.garcia@empresa.com",
                        "type": "WORK"
                    },
                    {
                        "email": "maria.personal@gmail.com",
                        "type": "HOME"
                    }
                ],
                "org": {
                    "company": "Tech Solutions SA",
                    "department": "Desarrollo",
                    "title": "Arquitecta de Software"
                },
                "addresses": [
                    {
                        "street": "Av. Corrientes 1234",
                        "city": "Buenos Aires",
                        "state": "CABA",
                        "zip": "C1043AAZ",
                        "country": "Argentina",
                        "country_code": "AR",
                        "type": "WORK"
                    }
                ],
                "urls": [
                    {
                        "url": "https://www.techsolutions.com.ar",
                        "type": "WORK"
                    },
                    {
                        "url": "https://linkedin.com/in/mariagarcia",
                        "type": "HOME"
                    }
                ]
            }
        ]
    }
    
    # Mostrar JSON generado
    json_payload = json.dumps(payload, indent=2, ensure_ascii=False)
    print(f"📋 JSON generado ({len(json_payload)} caracteres):")
    print(json_payload[:500] + "..." if len(json_payload) > 500 else json_payload)
    
    # Enviar request
    print(f"\n📤 Enviando POST a: {BASE_URL}{ENDPOINT}")
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response:")
        
        try:
            response_json = response.json()
            pprint(response_json)
        except json.JSONDecodeError:
            print("⚠️  Respuesta no es JSON válido:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_server_status():
    print("=" * 60)
    print("🌐 VERIFICANDO ESTADO DEL SERVIDOR")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Servidor respondiendo en {BASE_URL}")
        print(f"Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # Verificar endpoint específico
    try:
        response = requests.get(f"{BASE_URL}/v1/messages", timeout=5)
        print(f"✅ Endpoints de mensajes disponibles")
        print(f"Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Endpoint de mensajes: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 DEPURACIÓN ENDPOINT DE CONTACTOS")
    print("Servidor esperado en: http://127.0.0.1:5000")
    
    # Verificar servidor
    if test_server_status():
        # Probar contacto básico
        test_basic_contact()
        
        # Probar contacto completo
        test_complete_contact()
    
    print("\n" + "=" * 60)
    print("🏁 Depuración completada")
    print("=" * 60)
