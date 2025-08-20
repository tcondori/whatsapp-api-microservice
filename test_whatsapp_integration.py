"""
Script de prueba para los webhooks de WhatsApp
"""
import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:5000"

def test_webhook_verification():
    """Prueba la verificación inicial del webhook"""
    print("🔍 Probando verificación de webhook...")
    
    url = f"{BASE_URL}/v1/webhooks"
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': 'test_verify_token',
        'hub.challenge': 'challenge123'
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 and response.text == '"challenge123"':
            print("✅ Verificación de webhook exitosa!")
        else:
            print("❌ Error en verificación de webhook")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_webhook_health():
    """Prueba el health check de webhooks"""
    print("\n🏥 Probando health check de webhooks...")
    
    url = f"{BASE_URL}/v1/webhooks/health"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check de webhooks exitoso!")
        else:
            print("❌ Error en health check de webhooks")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_webhook_message():
    """Prueba el procesamiento de un webhook de mensaje"""
    print("\n📨 Probando procesamiento de webhook de mensaje...")
    
    url = f"{BASE_URL}/v1/webhooks/test"
    headers = {
        "X-API-Key": "test_key",
        "Content-Type": "application/json"
    }
    
    # Webhook de ejemplo simulando un mensaje entrante
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test-business-id",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "test-phone-number-id"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Usuario Prueba"
                                    },
                                    "wa_id": "5491234567890"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5491234567890",
                                    "id": "wamid.test_message_12345",
                                    "timestamp": "1692537600",
                                    "text": {
                                        "body": "Hola! Este es un mensaje de prueba"
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=webhook_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Procesamiento de webhook exitoso!")
        else:
            print("❌ Error procesando webhook")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_message_with_integration():
    """Prueba el envío de mensaje con integración completa"""
    print("\n💬 Probando envío de mensaje con integración de WhatsApp...")
    
    url = f"{BASE_URL}/v1/messages/text"
    headers = {
        "X-API-Key": "test_key",
        "Content-Type": "application/json"
    }
    
    message_data = {
        "to": "+1234567890",
        "text": "Este es un mensaje de prueba con integración de WhatsApp API!",
        "line_id": "line_1"
    }
    
    try:
        response = requests.post(url, headers=headers, json=message_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Mensaje enviado exitosamente!")
        else:
            print("❌ Error enviando mensaje")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de integración de WhatsApp API\n")
    
    test_webhook_verification()
    test_webhook_health()
    test_webhook_message()
    test_message_with_integration()
    
    print("\n✨ Pruebas completadas!")
