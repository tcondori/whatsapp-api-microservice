"""
Test específico para el formato de Swagger exacto
Prueba con el payload exacto que se muestra en la documentación
"""
import sys
import os
import json
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def test_swagger_exact_format():
    """
    Prueba con el formato exacto mostrado en Swagger
    """
    print("=" * 60)
    print("🧪 PRUEBA CON FORMATO SWAGGER EXACTO")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        # Headers exactos
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'dev-api-key'
        }
        
        # Payload exacto de Swagger
        payload = {
            "to": "5491123456789",
            "image": {
                "id": "media_id_12345",
                "link": "https://example.com/image.jpg",
                "caption": "Descripción opcional de la imagen"
            },
            "messaging_line_id": 1
        }
        
        print(f"📤 Enviando request exacto de Swagger:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = client.post(
                '/v1/messages/image',
                data=json.dumps(payload),
                headers=headers
            )
            
            print(f"\n📥 RESPUESTA:")
            print(f"Status Code: {response.status_code}")
            
            if response.data:
                try:
                    response_data = json.loads(response.data)
                    print("Response JSON:")
                    print(json.dumps(response_data, indent=2))
                    
                    if response.status_code == 200:
                        print("\n✅ ÉXITO - Endpoint funcionando!")
                        data = response_data.get('data', {})
                        print(f"   • Message ID: {data.get('id', 'N/A')}")
                        print(f"   • WhatsApp ID: {data.get('whatsapp_message_id', 'N/A')}")
                        print(f"   • Tipo: {data.get('message_type', 'N/A')}")
                        print(f"   • Estado: {data.get('status', 'N/A')}")
                        print(f"   • Contenido: {data.get('content', 'N/A')}")
                        return True
                    else:
                        print(f"\n⚠️ Error (esperado en simulación):")
                        print(f"   • Mensaje: {response_data.get('message', 'N/A')}")
                        print(f"   • Código: {response_data.get('error_code', 'N/A')}")
                        
                except json.JSONDecodeError:
                    print("Response (no JSON):")
                    print(response.data.decode('utf-8'))
            else:
                print("No response data")
                
        except Exception as e:
            print(f"❌ Error en test: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return False

def test_alternative_formats():
    """
    Prueba formatos alternativos para verificar flexibilidad
    """
    print("\n" + "=" * 60)
    print("🔄 PRUEBA DE FORMATOS ALTERNATIVOS")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'dev-api-key'
        }
        
        # Formato 1: Solo con image.id
        print("\n1️⃣ TEST: Solo con media_id existente")
        payload1 = {
            "to": "5491123456789",
            "image": {
                "id": "existing_media_123"
            },
            "messaging_line_id": 1
        }
        
        try:
            response = client.post('/v1/messages/image', data=json.dumps(payload1), headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 400]:
                data = json.loads(response.data) if response.data else {}
                print(f"   Resultado: {data.get('message', data.get('success', 'N/A'))}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Formato 2: Solo con image.link
        print("\n2️⃣ TEST: Solo con link para upload")
        payload2 = {
            "to": "5491123456789",
            "image": {
                "link": "https://httpbin.org/image/jpeg"
            },
            "messaging_line_id": 1
        }
        
        try:
            response = client.post('/v1/messages/image', data=json.dumps(payload2), headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 400]:
                data = json.loads(response.data) if response.data else {}
                print(f"   Resultado: {data.get('message', data.get('success', 'N/A'))}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Formato 3: Con image_url (formato simple)
        print("\n3️⃣ TEST: Con image_url directo")
        payload3 = {
            "to": "5491123456789",
            "image_url": "https://httpbin.org/image/png",
            "caption": "Imagen con URL directa",
            "messaging_line_id": 1
        }
        
        try:
            response = client.post('/v1/messages/image', data=json.dumps(payload3), headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 400]:
                data = json.loads(response.data) if response.data else {}
                print(f"   Resultado: {data.get('message', data.get('success', 'N/A'))}")
        except Exception as e:
            print(f"   Error: {e}")

def show_debugging_info():
    """
    Muestra información de debugging útil
    """
    print("\n" + "=" * 60)
    print("🔍 INFORMACIÓN DE DEBUGGING")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.api.messages.services import MessageService
            from app.services.whatsapp_api import WhatsAppAPIService
            
            # Verificar inicialización de servicios
            msg_service = MessageService()
            print(f"✅ MessageService inicializado correctamente")
            print(f"   • whatsapp_api disponible: {hasattr(msg_service, 'whatsapp_api')}")
            
            # Verificar métodos de WhatsApp service
            wa_service = WhatsAppAPIService()
            print(f"✅ WhatsAppAPIService inicializado correctamente")
            
            methods_check = [
                'upload_media_from_url',
                'send_media_message',
                'send_text_message'
            ]
            
            for method in methods_check:
                available = hasattr(wa_service, method)
                print(f"   • {method}: {'✅ Disponible' if available else '❌ NO disponible'}")
                
        except Exception as e:
            print(f"❌ Error en debugging: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO PRUEBAS DE FORMATO SWAGGER")
        
        # Información de debugging
        show_debugging_info()
        
        # Prueba formato exacto
        success = test_swagger_exact_format()
        
        # Pruebas alternativas
        test_alternative_formats()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 RESULTADO: Endpoint funcionando correctamente!")
        else:
            print("⚠️ RESULTADO: Errores encontrados (pueden ser esperados en simulación)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🏁 Pruebas completadas")
