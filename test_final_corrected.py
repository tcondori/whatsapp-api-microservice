"""
TEST FINAL - Envío de imagen con credenciales corregidas
===============================================================
"""

import requests
import json
from datetime import datetime

def test_final_image_send():
    """
    Prueba final con las credenciales corregidas
    """
    print("🚀 PRUEBA FINAL - ENVÍO DE IMAGEN")
    print("=" * 50)
    
    # Request con formato oficial Meta
    request_data = {
        "to": "59167028778",
        "type": "image", 
        "image": {
            "link": "https://picsum.photos/800/600?random=1",  # Imagen de prueba válida
            "caption": "🎉 ¡PRUEBA FINAL! Imagen enviada con credenciales corregidas"
        },
        "messaging_line_id": 1  # Número, no string
    }
    
    print(f"📤 Enviando request:")
    print(json.dumps(request_data, indent=2))
    
    try:
        # Hacer el request a tu API local
        response = requests.post(
            "http://localhost:5000/api/v1/messages/image",
            json=request_data,
            headers={
                "X-API-Key": "mi-clave-api-secreta-2024",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📊 RESULTADO:")
        print(f"   • Status Code: {response.status_code}")
        print(f"   • Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ ÉXITO! Mensaje enviado:")
            print(f"      • Message ID: {result.get('message_id')}")
            print(f"      • WhatsApp ID: {result.get('whatsapp_id')}")
            print(f"      • Estado: {result.get('status', 'N/A')}")
            
        else:
            print(f"   ❌ Error {response.status_code}:")
            try:
                error_data = response.json()
                print(f"      • Error Code: {error_data.get('error_code')}")
                print(f"      • Message: {error_data.get('message')}")
            except:
                print(f"      • Response: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor local")
        print("   ¿Está ejecutándose el servidor en localhost:5000?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_final_image_send()
    
    print(f"\n" + "="*50)
    if success:
        print("🎉 ¡ÉXITO! El mensaje se envió correctamente")
        print("📱 Revisa si llegó el mensaje al número 59167028778")
    else:
        print("❌ Falló el envío")
        print("🔧 Verifica que el servidor esté ejecutándose")
    print("="*50)
