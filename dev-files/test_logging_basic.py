"""
Prueba simple del log básico en endpoint de mensajes
"""

import requests
import json

def test_basic_log():
    """
    Prueba simple del log básico
    """
    print("� PRUEBA SIMPLE: Log Básico en Mensajes")
    print("=" * 50)
    
    # Datos de prueba
    url = "http://127.0.0.1:5000/v1/messages/text"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-api-key'
    }
    payload = {
        'to': '5491123456789',
        'type': 'text',
        'text': {
            'body': 'Hola! Mensaje de prueba para logging básico'
        }
    }
    
    print(f"🔗 URL: {url}")
    print(f"📤 Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        print(f"\n📥 Response:")
        print(f"Status: {response.status_code}")
        
        if response.content:
            print(f"Body: {response.json()}")
        
        print(f"\n✅ ¡Request enviado! Revisa los logs en:")
        print(f"📁 logs/current/api.log")
        print(f"🔍 Busca: 'Enviando mensaje de texto'")
        
    except requests.ConnectionError:
        print("❌ Error: Servidor no disponible")
        print("Ejecuta: python entrypoint.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_basic_log()
