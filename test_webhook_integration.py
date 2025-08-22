#!/usr/bin/env python3
"""
Script de prueba para integración de webhooks de WhatsApp
Simula eventos de webhook para verificar que el procesamiento funciona correctamente
"""
import json
import requests
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
API_KEY = "dev-api-key"

def test_webhook_verification():
    """Prueba la verificación del webhook (GET)"""
    print("🔍 Probando verificación de webhook...")
    
    url = f"{BASE_URL}/v1/webhooks"
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': 'Nicole07',  # Token correcto del .env
        'hub.challenge': 'test_challenge_123'
    }
    
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200 and response.text == 'test_challenge_123':
        print("✅ Verificación de webhook exitosa")
        return True
    else:
        print("❌ Verificación de webhook falló")
        return False

def test_webhook_message_received():
    """Prueba procesamiento de mensaje entrante"""
    print("\n📨 Probando mensaje entrante...")
    
    # Payload de ejemplo de WhatsApp (mensaje entrante)
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "123456789012345"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Usuario Test"
                                    },
                                    "wa_id": "5491123456789"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5491123456789",
                                    "id": f"wamid.test_{int(time.time())}",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {
                                        "body": "Hola, este es un mensaje de prueba"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    url = f"{BASE_URL}/v1/webhooks/test"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    response = requests.post(url, json=webhook_payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Mensaje entrante procesado exitosamente")
        return True
    else:
        print("❌ Error procesando mensaje entrante")
        return False

def test_webhook_message_status():
    """Prueba actualización de estado de mensaje"""
    print("\n📊 Probando actualización de estado de mensaje...")
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "field": "message_status",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "123456789012345"
                            },
                            "statuses": [
                                {
                                    "id": f"wamid.test_{int(time.time())}",
                                    "status": "delivered",
                                    "timestamp": str(int(time.time())),
                                    "recipient_id": "5491123456789"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    url = f"{BASE_URL}/v1/webhooks/test"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    response = requests.post(url, json=webhook_payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Estado de mensaje actualizado exitosamente")
        return True
    else:
        print("❌ Error actualizando estado de mensaje")
        return False

def test_webhook_interactive_response():
    """Prueba respuesta a mensaje interactivo"""
    print("\n🔘 Probando respuesta interactiva...")
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "123456789012345"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Usuario Test"
                                    },
                                    "wa_id": "5491123456789"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5491123456789",
                                    "id": f"wamid.interactive_{int(time.time())}",
                                    "timestamp": str(int(time.time())),
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "btn_help",
                                            "title": "Ayuda"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    url = f"{BASE_URL}/v1/webhooks/test"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    response = requests.post(url, json=webhook_payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Respuesta interactiva procesada exitosamente")
        return True
    else:
        print("❌ Error procesando respuesta interactiva")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN DE WEBHOOKS")
    print("=" * 60)
    
    tests = [
        test_webhook_verification,
        test_webhook_message_received, 
        test_webhook_message_status,
        test_webhook_interactive_response
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
            time.sleep(1)  # Esperar entre pruebas
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"✅ Exitosas: {sum(results)}/{len(results)}")
    print(f"❌ Fallidas: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar logs del servidor.")

if __name__ == "__main__":
    main()
