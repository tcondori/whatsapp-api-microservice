"""
Prueba de envío de mensaje con imagen real
Prueba el endpoint POST /v1/messages/image con imagen real disponible públicamente
"""
import sys
import os
import json
import requests
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def test_real_image_message():
    """
    Prueba envío de imagen real usando endpoint directo
    """
    print("=" * 60)
    print("🖼️ PRUEBA DE IMAGEN REAL - WhatsApp API")
    print("=" * 60)
    
    # URL de imagen real pública y accesible
    real_images = [
        {
            "url": "https://httpbin.org/image/jpeg",
            "description": "Imagen JPEG de prueba (httpbin.org)",
            "type": "jpeg"
        },
        {
            "url": "https://httpbin.org/image/png", 
            "description": "Imagen PNG de prueba (httpbin.org)",
            "type": "png"
        },
        {
            "url": "https://picsum.photos/400/300",
            "description": "Imagen aleatoria de Picsum (400x300)",
            "type": "jpg"
        }
    ]
    
    # Configuración de la prueba
    api_url = "http://localhost:5000/v1/messages/image"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-api-key'
    }
    
    # Número de teléfono de prueba (formato internacional)
    test_phone = "5491123456789"  # Número de prueba Argentina
    
    print(f"📱 Número destino: {test_phone}")
    print(f"🔗 Endpoint: {api_url}")
    print()
    
    # Probar cada imagen
    for i, image in enumerate(real_images, 1):
        print(f"{i}️⃣ Probando: {image['description']}")
        print(f"   🔗 URL: {image['url']}")
        
        # Verificar que la imagen sea accesible
        try:
            print("   📡 Verificando accesibilidad de imagen...")
            img_response = requests.head(image['url'], timeout=10)
            print(f"   📊 Status imagen: {img_response.status_code}")
            
            if img_response.status_code == 200:
                print("   ✅ Imagen accesible")
                
                # Preparar payload
                payload = {
                    "to": test_phone,
                    "image_url": image['url'],
                    "caption": f"Imagen de prueba {image['type'].upper()} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "messaging_line_id": 1
                }
                
                print("   📤 Enviando mensaje de imagen...")
                print(f"   💬 Caption: {payload['caption']}")
                
                # Enviar request al endpoint
                try:
                    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                    print(f"   📊 Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print("   ✅ ÉXITO - Mensaje enviado")
                        print(f"      • Message ID: {data.get('data', {}).get('id', 'N/A')}")
                        print(f"      • WhatsApp ID: {data.get('data', {}).get('whatsapp_message_id', 'N/A')}")
                        print(f"      • Status: {data.get('data', {}).get('status', 'N/A')}")
                        print(f"      • Media ID: {data.get('data', {}).get('media_id', 'N/A')}")
                        return True  # Prueba exitosa
                        
                    else:
                        error_data = response.json() if response.content else {}
                        print(f"   ❌ ERROR: {error_data.get('message', 'Error desconocido')}")
                        print(f"      • Código: {error_data.get('error_code', 'N/A')}")
                        if 'details' in error_data:
                            print(f"      • Detalles: {error_data['details']}")
                            
                except Exception as e:
                    print(f"   ❌ ERROR de conexión: {str(e)}")
                    
            else:
                print(f"   ❌ Imagen no accesible: {img_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR verificando imagen: {str(e)}")
        
        print()  # Línea en blanco entre pruebas
    
    return False  # No hubo éxito

def test_with_app_client():
    """
    Prueba usando el cliente de la aplicación Flask directamente
    """
    print("\n" + "=" * 60)
    print("🧪 PRUEBA CON CLIENTE FLASK INTERNO")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        # Imagen de prueba confiable
        test_image = {
            "url": "https://httpbin.org/image/jpeg",
            "description": "Imagen JPEG confiable"
        }
        
        payload = {
            "to": "5491123456789",
            "image_url": test_image['url'],
            "caption": "Prueba directa con Flask client",
            "messaging_line_id": 1
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'dev-api-key'
        }
        
        print(f"📤 Enviando: {test_image['description']}")
        print(f"🔗 URL: {test_image['url']}")
        
        try:
            response = client.post(
                '/v1/messages/image',
                data=json.dumps(payload),
                headers=headers
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print("✅ RESPUESTA EXITOSA:")
                print(f"   • Success: {data.get('success', False)}")
                print(f"   • Message: {data.get('message', 'N/A')}")
                
                if data.get('data'):
                    msg_data = data['data']
                    print("   • Datos del mensaje:")
                    print(f"     - ID: {msg_data.get('id', 'N/A')}")
                    print(f"     - WhatsApp ID: {msg_data.get('whatsapp_message_id', 'N/A')}")
                    print(f"     - Tipo: {msg_data.get('message_type', 'N/A')}")
                    print(f"     - Estado: {msg_data.get('status', 'N/A')}")
                    print(f"     - Media ID: {msg_data.get('media_id', 'N/A')}")
                    print(f"     - Contenido: {msg_data.get('content', 'N/A')}")
                    print(f"     - Fecha: {msg_data.get('created_at', 'N/A')}")
                    
            else:
                error_data = json.loads(response.data) if response.data else {}
                print("❌ ERROR EN RESPUESTA:")
                print(f"   • Mensaje: {error_data.get('message', 'Error desconocido')}")
                print(f"   • Código: {error_data.get('error_code', 'N/A')}")
                if 'details' in error_data:
                    print(f"   • Detalles: {error_data['details']}")
                    
        except Exception as e:
            print(f"❌ ERROR de aplicación: {str(e)}")

def check_whatsapp_service_config():
    """
    Verifica la configuración del servicio WhatsApp
    """
    print("\n" + "=" * 60) 
    print("🔧 VERIFICACIÓN DE CONFIGURACIÓN WHATSAPP")
    print("=" * 60)
    
    try:
        app = create_app()
        
        with app.app_context():
            from app.services.whatsapp_api import WhatsAppAPIService
            
            # Crear instancia del servicio
            wa_service = WhatsAppAPIService()
            
            print("✅ Servicio WhatsApp inicializado correctamente")
            print(f"   • API URL: {getattr(wa_service, 'base_url', 'N/A')}")
            
            # Verificar métodos disponibles
            methods = [method for method in dir(wa_service) if not method.startswith('_')]
            print(f"   • Métodos disponibles: {len(methods)}")
            
            critical_methods = ['send_media_message', 'upload_media']
            for method in critical_methods:
                if hasattr(wa_service, method):
                    print(f"   ✅ {method}: Disponible")
                else:
                    print(f"   ❌ {method}: NO DISPONIBLE")
                    
    except Exception as e:
        print(f"❌ ERROR en configuración: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO PRUEBA DE IMAGEN REAL")
        
        # 1. Verificar configuración
        check_whatsapp_service_config()
        
        # 2. Prueba con requests directo
        success = test_real_image_message()
        
        # 3. Prueba con cliente Flask
        test_with_app_client()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 RESULTADO: Al menos una prueba fue exitosa")
        else:
            print("⚠️ RESULTADO: Todas las pruebas fallaron (esperado en simulación)")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
        
    except Exception as e:
        print(f"\n\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🏁 Fin de las pruebas de imagen real")
