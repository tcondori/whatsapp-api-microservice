"""
DIAGNÓSTICO COMPARATIVO - Text vs Image Payload
===============================================
Comparar exactamente qué payloads se envían en cada caso
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_text_endpoint():
    """
    Probar endpoint de texto para ver el payload que funciona
    """
    print("📤 PROBANDO ENDPOINT TEXT (QUE FUNCIONA)")
    print("=" * 50)
    
    request_data = {
        "to": "59167028778",
        "text": "Mensaje de texto de prueba",
        "line_id": "1"  # Usando string como en imagen
    }
    
    print(f"Request enviado:")
    print(json.dumps(request_data, indent=2))
    
    try:
        response = requests.post(
            "http://localhost:5000/api/v1/messages/text",
            json=request_data,
            headers={
                "X-API-Key": "mi-clave-api-secreta-2024",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"\n📊 RESULTADO TEXT:")
        print(f"   • Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ ÉXITO!")
            print(f"      • Message ID: {result.get('data', {}).get('id')}")
            return True
        else:
            print(f"   ❌ Error {response.status_code}:")
            try:
                error_data = response.json()
                print(f"      • Error: {error_data}")
            except:
                print(f"      • Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_image_endpoint():
    """
    Probar endpoint de imagen que está fallando
    """
    print("\n📤 PROBANDO ENDPOINT IMAGE (QUE FALLA)")
    print("=" * 50)
    
    request_data = {
        "to": "59167028778",
        "type": "image",
        "image": {
            "link": "https://picsum.photos/400/300?random=1",
            "caption": "Imagen de prueba"
        },
        "messaging_line_id": 1  # Usando número como corrección
    }
    
    print(f"Request enviado:")
    print(json.dumps(request_data, indent=2))
    
    try:
        response = requests.post(
            "http://localhost:5000/api/v1/messages/image",
            json=request_data,
            headers={
                "X-API-Key": "mi-clave-api-secreta-2024",
                "Content-Type": "application/json"
            },
            timeout=30  # Más tiempo para upload de imagen
        )
        
        print(f"\n📊 RESULTADO IMAGE:")
        print(f"   • Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ ÉXITO!")
            print(f"      • Message ID: {result.get('data', {}).get('id')}")
            return True
        else:
            print(f"   ❌ Error {response.status_code}:")
            try:
                error_data = response.json()
                print(f"      • Error Code: {error_data.get('error_code')}")
                print(f"      • Message: {error_data.get('message')}")
            except:
                print(f"      • Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def debug_whatsapp_payload():
    """
    Crear un mock del servicio para ver exactamente qué payload genera
    """
    print(f"\n🔍 DEBUGGING PAYLOAD GENERATION")
    print("=" * 40)
    
    from entrypoint import create_app
    app = create_app()
    
    with app.app_context():
        try:
            from app.services.whatsapp_api import WhatsAppAPIService
            
            service = WhatsAppAPIService()
            
            print("📋 PAYLOAD PARA TEXT MESSAGE:")
            text_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "59167028778",
                "type": "text",
                "text": {
                    "body": "Mensaje de prueba"
                }
            }
            print(json.dumps(text_payload, indent=2))
            
            print(f"\n📋 PAYLOAD PARA IMAGE MESSAGE:")
            image_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "59167028778",
                "type": "image",
                "image": {
                    "id": "fake_media_123"
                }
            }
            print(json.dumps(image_payload, indent=2))
            
            print(f"\n📋 PAYLOAD PARA IMAGE MESSAGE CON CAPTION:")
            image_caption_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "59167028778",
                "type": "image",
                "image": {
                    "id": "fake_media_123",
                    "caption": "Caption de prueba"
                }
            }
            print(json.dumps(image_caption_payload, indent=2))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_with_fake_media_id():
    """
    Probar directamente con un media_id falso para aislar el problema
    """
    print(f"\n🧪 PRUEBA CON MEDIA_ID FALSO")
    print("=" * 40)
    
    # Simular el payload que genera send_media_message
    fake_media_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual", 
        "to": "59167028778",
        "type": "image",
        "image": {
            "id": "fake_media_test_123"
        }
    }
    
    print("📤 Payload que se enviaría a WhatsApp API:")
    print(json.dumps(fake_media_payload, indent=2))
    
    # Simular la URL que se usaría
    phone_number_id = "136308692891691"  # De las credenciales actuales
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    print(f"\n📍 URL que se usaría: {url}")
    print("⚠️ Este es el mismo formato que usa send_text_message")
    print("⚠️ La diferencia está solo en el payload")

if __name__ == "__main__":
    print("🕐 DIAGNÓSTICO COMPARATIVO TEXT vs IMAGE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Probar endpoint que funciona (text)
    text_works = test_text_endpoint()
    
    # Probar endpoint que falla (image) 
    image_works = test_image_endpoint()
    
    # Debug de payloads
    debug_whatsapp_payload()
    
    # Prueba con media_id falso
    test_with_fake_media_id()
    
    print(f"\n" + "=" * 60)
    print("📋 RESUMEN:")
    print(f"   • TEXT endpoint: {'✅ Funciona' if text_works else '❌ Falla'}")
    print(f"   • IMAGE endpoint: {'✅ Funciona' if image_works else '❌ Falla'}")
    print()
    
    if text_works and not image_works:
        print("🎯 CONCLUSIÓN: El problema NO son las credenciales")
        print("   • Las credenciales están bien (text funciona)")
        print("   • El problema está en el payload de imagen o el media_id")
        print("   • Revisar: upload_media_from_url y send_media_message")
    elif not text_works and not image_works:
        print("🎯 CONCLUSIÓN: Problema de credenciales o servidor")
    elif text_works and image_works:
        print("🎯 CONCLUSIÓN: ¡Ambos funcionan! Problema resuelto")
    
    print("=" * 60)
