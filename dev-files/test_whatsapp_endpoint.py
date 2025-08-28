#!/usr/bin/env python3
"""
Script para probar el endpoint de mensajes WhatsApp
"""
import requests
import json

def test_whatsapp_endpoint():
    """Prueba el endpoint de mensajes WhatsApp"""
    url = "http://localhost:5001/v1/messages/text"
    
    headers = {
        "X-API-Key": "dev-api-key",
        "Content-Type": "application/json"
    }
    
    data = {
        "to": "59167028778",
        "text": "¡Hola! Mensaje después de la migración exitosa 🎉",
        "line_id": "line_1"
    }
    
    try:
        print("🚀 Probando endpoint WhatsApp...")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                response_data = response.json()
                print(f"📄 Response JSON:")
                print(json.dumps(response_data, indent=2))
            except json.JSONDecodeError:
                print("❌ Error decodificando JSON response")
                print(f"Raw response: {response.text}")
        else:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ ¡ENDPOINT FUNCIONANDO CORRECTAMENTE!")
        else:
            print(f"\n⚠️  Endpoint respondió con código: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - ¿Está el servidor ejecutándose?")
        print("   Ejecuta: python run_server.py")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == '__main__':
    test_whatsapp_endpoint()
