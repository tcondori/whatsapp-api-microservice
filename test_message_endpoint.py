#!/usr/bin/env python3
"""
Script para probar el endpoint de envío de mensajes de texto
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:5000"
API_KEY = "dev-api-key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    """Probar el endpoint de health check"""
    print("🔍 Probando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Health Check OK\n")
        return True
    except Exception as e:
        print(f"❌ Error en Health Check: {e}\n")
        return False

def test_messages_health():
    """Probar el endpoint de health de mensajes"""
    print("🔍 Probando Messages Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/v1/messages/test", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Messages Health Check OK\n")
        return True
    except Exception as e:
        print(f"❌ Error en Messages Health Check: {e}\n")
        return False

def test_send_message(to, text, messaging_line_id=1):
    """Probar el envío de un mensaje de texto"""
    print(f"📱 Enviando mensaje a {to}...")
    
    payload = {
        "to": to,
        "text": text,
        "messaging_line_id": messaging_line_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            headers=HEADERS,
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Request Payload: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Mensaje enviado exitosamente\n")
            return response.json()
        else:
            print("❌ Error al enviar mensaje\n")
            return None
            
    except Exception as e:
        print(f"❌ Error en envío de mensaje: {e}\n")
        return None

def test_get_messages():
    """Probar la obtención de mensajes"""
    print("📋 Obteniendo lista de mensajes...")
    try:
        response = requests.get(f"{BASE_URL}/v1/messages", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"Total de mensajes: {len(messages)}")
            if messages:
                print("Últimos 3 mensajes:")
                for msg in messages[:3]:
                    print(f"  - ID: {msg.get('id')}, To: {msg.get('to')}, Text: {msg.get('text')[:50]}...")
            print("✅ Lista de mensajes obtenida\n")
            return messages
        else:
            print(f"❌ Error al obtener mensajes: {response.text}\n")
            return None
            
    except Exception as e:
        print(f"❌ Error al obtener mensajes: {e}\n")
        return None

def test_invalid_requests():
    """Probar requests inválidos para verificar validaciones"""
    print("🧪 Probando requests inválidos...")
    
    # Test 1: Sin API Key
    print("Test 1: Sin API Key")
    try:
        payload = {"to": "+51987654321", "text": "Test sin API key"}
        response = requests.post(f"{BASE_URL}/v1/messages/text", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Test 2: Datos faltantes
    print("Test 2: Datos faltantes (sin 'to')")
    try:
        payload = {"text": "Test sin numero de destino"}
        response = requests.post(f"{BASE_URL}/v1/messages/text", headers=HEADERS, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Test 3: Número inválido
    print("Test 3: Número de teléfono inválido")
    try:
        payload = {"to": "123", "text": "Test con numero invalido"}
        response = requests.post(f"{BASE_URL}/v1/messages/text", headers=HEADERS, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("=" * 60)
    print("🚀 PRUEBAS DEL ENDPOINT DE MENSAJES DE TEXTO")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health():
        print("❌ El servidor no está funcionando correctamente")
        return
    
    # Test 2: Messages Health Check
    if not test_messages_health():
        print("❌ El servicio de mensajes no está funcionando")
        return
    
    # Test 3: Envío de mensajes válidos
    test_cases = [
        {
            "to": "+51987654321", 
            "text": "¡Hola! Este es un mensaje de prueba desde Python 🐍",
            "messaging_line_id": 1
        },
        {
            "to": "+51912345678", 
            "text": "Segundo mensaje de prueba con emojis 😄📱💬",
            "messaging_line_id": 1
        },
        {
            "to": "+51999888777", 
            "text": "Mensaje de prueba con texto más largo para verificar que se maneja correctamente el contenido extenso en el sistema de mensajería",
            "messaging_line_id": 1
        }
    ]
    
    sent_messages = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"📤 Caso de prueba {i}:")
        result = test_send_message(**test_case)
        if result:
            sent_messages.append(result)
        time.sleep(1)  # Esperar 1 segundo entre envíos
    
    # Test 4: Obtener mensajes
    test_get_messages()
    
    # Test 5: Requests inválidos
    test_invalid_requests()
    
    print("=" * 60)
    print(f"✅ Pruebas completadas. Se enviaron {len(sent_messages)} mensajes exitosamente.")
    print("=" * 60)

if __name__ == "__main__":
    main()
