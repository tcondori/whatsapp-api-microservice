"""
Script de prueba específico para mensajes de imagen
Valida la funcionalidad del endpoint POST /v1/messages/image
"""
import sys
import os
import json
import requests
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def test_image_messages_api():
    """
    Prueba completa del endpoint de mensajes de imagen
    """
    print("=" * 60)
    print("🖼️ INICIANDO PRUEBAS DE MENSAJES DE IMAGEN")
    print("=" * 60)
    
    # Crear aplicación en modo test
    app = create_app()
    
    # Variables para las pruebas
    base_url = 'http://localhost:5000/v1'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-api-key'  # Clave de prueba válida
    }
    
    with app.app_context():
        # Configurar cliente de pruebas
        client = app.test_client()
        
        print("\n1️⃣ Probando envío de imagen con URL...")
        test_send_image_with_url(client, headers)
        
        print("\n2️⃣ Probando envío de imagen con media_id...")
        test_send_image_with_media_id(client, headers)
        
        print("\n3️⃣ Probando envío de imagen con caption...")
        test_send_image_with_caption(client, headers)
        
        print("\n4️⃣ Probando validaciones de imagen...")
        test_image_validations(client, headers)
        
        print("\n5️⃣ Probando filtro de mensajes de imagen...")
        test_filter_image_messages(client, headers)

def test_send_image_with_url(client, headers):
    """
    Prueba envío de imagen usando URL
    """
    try:
        # URL de imagen de prueba (una imagen pública de ejemplo)
        test_image_url = "https://via.placeholder.com/300x200.png?text=Test+Image"
        
        payload = {
            "to": "5491123456789",
            "image_url": test_image_url,
            "messaging_line_id": 1
        }
        
        print(f"   📤 Enviando imagen desde URL: {test_image_url}")
        print(f"   📱 Destino: {payload['to']}")
        
        response = client.post(
            '/v1/messages/image',
            data=json.dumps(payload),
            headers=headers
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Respuesta exitosa:")
            print(f"      • Success: {data.get('success', False)}")
            print(f"      • Message: {data.get('message', 'N/A')}")
            
            if data.get('data'):
                message_data = data['data']
                print(f"      • Message ID: {message_data.get('id', 'N/A')}")
                print(f"      • WhatsApp ID: {message_data.get('whatsapp_message_id', 'N/A')}")
                print(f"      • Status: {message_data.get('status', 'N/A')}")
                print(f"      • Type: {message_data.get('message_type', 'N/A')}")
                print(f"      • Media ID: {message_data.get('media_id', 'N/A')}")
                return message_data.get('whatsapp_message_id')
        else:
            error_data = json.loads(response.data) if response.data else {}
            print(f"   ❌ Error: {error_data.get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    return None

def test_send_image_with_media_id(client, headers):
    """
    Prueba envío de imagen usando media_id (simulado)
    """
    try:
        # Simular un media_id ya subido
        payload = {
            "to": "5491123456789",
            "image": {
                "id": "test_media_id_123456",
                "caption": "Imagen enviada usando media_id"
            },
            "messaging_line_id": 1
        }
        
        print(f"   📤 Enviando imagen con Media ID: {payload['image']['id']}")
        print(f"   📱 Destino: {payload['to']}")
        print(f"   💬 Caption: {payload['image']['caption']}")
        
        response = client.post(
            '/v1/messages/image',
            data=json.dumps(payload),
            headers=headers
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Respuesta exitosa:")
            print(f"      • Success: {data.get('success', False)}")
            print(f"      • Message: {data.get('message', 'N/A')}")
            
            if data.get('data'):
                message_data = data['data']
                print(f"      • Content: {message_data.get('content', 'N/A')}")
                return message_data.get('whatsapp_message_id')
        else:
            error_data = json.loads(response.data) if response.data else {}
            print(f"   ❌ Error: {error_data.get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    return None

def test_send_image_with_caption(client, headers):
    """
    Prueba envío de imagen con caption personalizado
    """
    try:
        test_image_url = "https://picsum.photos/400/300"
        caption_text = "Esta es una imagen de prueba con caption personalizado 📸"
        
        payload = {
            "to": "5491123456789",
            "image_url": test_image_url,
            "caption": caption_text,
            "messaging_line_id": 1
        }
        
        print(f"   📤 Enviando imagen con caption personalizado")
        print(f"   📱 Destino: {payload['to']}")
        print(f"   💬 Caption: {caption_text}")
        
        response = client.post(
            '/v1/messages/image',
            data=json.dumps(payload),
            headers=headers
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Respuesta exitosa - Caption incluido correctamente")
            
            if data.get('data'):
                message_data = data['data']
                print(f"      • Content: {message_data.get('content', 'N/A')}")
        else:
            error_data = json.loads(response.data) if response.data else {}
            print(f"   ❌ Error: {error_data.get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def test_image_validations(client, headers):
    """
    Prueba validaciones del endpoint de imagen
    """
    print("   🔍 Probando validaciones...")
    
    # Test 1: Sin datos de imagen
    try:
        payload = {
            "to": "5491123456789",
            "messaging_line_id": 1
        }
        
        response = client.post(
            '/v1/messages/image',
            data=json.dumps(payload),
            headers=headers
        )
        
        print(f"   📊 Sin imagen - Status: {response.status_code}")
        if response.status_code == 400:
            print("      ✅ Validación correcta: Se requiere imagen")
        else:
            print("      ❌ Debería fallar sin datos de imagen")
            
    except Exception as e:
        print(f"      ❌ Exception: {str(e)}")
    
    # Test 2: Número de teléfono inválido
    try:
        payload = {
            "to": "123",  # Número inválido
            "image_url": "https://via.placeholder.com/150",
            "messaging_line_id": 1
        }
        
        response = client.post(
            '/v1/messages/image',
            data=json.dumps(payload),
            headers=headers
        )
        
        print(f"   📊 Teléfono inválido - Status: {response.status_code}")
        if response.status_code == 400:
            print("      ✅ Validación correcta: Teléfono inválido")
        else:
            print("      ❌ Debería fallar con teléfono inválido")
            
    except Exception as e:
        print(f"      ❌ Exception: {str(e)}")
    
    # Test 3: Sin autorización
    try:
        payload = {
            "to": "5491123456789",
            "image_url": "https://via.placeholder.com/150",
            "messaging_line_id": 1
        }
        
        # Headers sin API key
        headers_no_auth = {'Content-Type': 'application/json'}
        
        response = client.post(
            '/v1/messages/image',
            data=json.dumps(payload),
            headers=headers_no_auth
        )
        
        print(f"   📊 Sin autorización - Status: {response.status_code}")
        if response.status_code == 401:
            print("      ✅ Validación correcta: Autorización requerida")
        else:
            print("      ❌ Debería fallar sin autorización")
            
    except Exception as e:
        print(f"      ❌ Exception: {str(e)}")

def test_filter_image_messages(client, headers):
    """
    Prueba filtro de mensajes por tipo 'image'
    """
    try:
        print("   🔍 Obteniendo mensajes de imagen...")
        
        response = client.get(
            '/v1/messages?message_type=image&per_page=5',
            headers=headers
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Filtro exitoso:")
            print(f"      • Success: {data.get('success', False)}")
            
            if data.get('data') and data['data'].get('messages'):
                messages = data['data']['messages']
                print(f"      • Total mensajes imagen: {len(messages)}")
                
                for i, msg in enumerate(messages[:3]):  # Mostrar solo primeros 3
                    print(f"      • Mensaje {i+1}:")
                    print(f"        - Tipo: {msg.get('message_type', 'N/A')}")
                    print(f"        - Status: {msg.get('status', 'N/A')}")
                    print(f"        - Media ID: {msg.get('media_id', 'N/A')}")
                    print(f"        - Fecha: {msg.get('created_at', 'N/A')}")
            else:
                print("      • No se encontraron mensajes de imagen")
        else:
            error_data = json.loads(response.data) if response.data else {}
            print(f"   ❌ Error: {error_data.get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def print_summary():
    """
    Imprime resumen de las pruebas
    """
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS DE IMAGEN")
    print("=" * 60)
    print("✅ Endpoints probados:")
    print("   • POST /v1/messages/image - Envío con URL")
    print("   • POST /v1/messages/image - Envío con media_id")
    print("   • POST /v1/messages/image - Con caption")
    print("   • GET /v1/messages?message_type=image - Filtro")
    print("\n🔍 Validaciones probadas:")
    print("   • Validación de datos de imagen requeridos")
    print("   • Validación de formato de teléfono")
    print("   • Validación de autorización")
    print("\n📝 Funcionalidades:")
    print("   • Subida de imagen desde URL")
    print("   • Uso de media_id existente")
    print("   • Inclusión de caption")
    print("   • Filtrado por tipo de mensaje")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_image_messages_api()
        print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
        
    except Exception as e:
        print(f"\n\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🏁 Fin de las pruebas de mensajes de imagen")
