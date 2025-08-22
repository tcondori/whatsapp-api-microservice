#!/usr/bin/env python3
"""
Test rápido: Inicia servidor temporal en puerto 5001 para verificar endpoint de contactos
"""

from entrypoint import create_app
import requests
import json
import threading
import time

def test_contacts_endpoint():
    # Esperar que el servidor inicie
    time.sleep(2)
    
    payload = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Test User",
                    "first_name": "Test",
                    "last_name": "User"
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
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/v1/messages/contacts",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "dev-api-key"
            },
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        if response.status_code == 200:
            print("🎉 ¡ENDPOINT DE CONTACTOS FUNCIONANDO!")
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)[:200]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🧪 INICIANDO SERVIDOR TEMPORAL PARA PRUEBA")
    print("Puerto: 5001 (para no interferir con tu servidor en 5000)")
    print("=" * 60)
    
    # Crear y configurar la aplicación
    app = create_app()
    
    # Iniciar prueba en hilo separado
    test_thread = threading.Thread(target=test_contacts_endpoint)
    test_thread.start()
    
    # Iniciar servidor temporal
    print("🚀 Servidor iniciando en puerto 5001...")
    app.run(host='127.0.0.1', port=5001, debug=False)
