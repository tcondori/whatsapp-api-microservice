"""
Script de prueba para validar endpoints de mensajes
Prueba todas las funcionalidades implementadas de la API de mensajes
"""
import sys
import os
import json
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def test_messages_api():
    """
    Prueba completa de la API de mensajes
    """
    print("=" * 60)
    print("🧪 INICIANDO PRUEBAS DE API DE MENSAJES")
    print("=" * 60)
    
    # Crear aplicación en modo test
    app = create_app()
    
    # Variables para las pruebas
    base_url = 'http://localhost:5000/v1'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-api-key'  # Clave de prueba válida del .env
    }
    
    with app.app_context():
        # Configurar cliente de pruebas
        client = app.test_client()
        
        print("\n1️⃣ Probando endpoint de salud de mensajes...")
        test_messages_health(client, headers)
        
        print("\n2️⃣ Probando envío de mensaje de texto...")
        message_id = test_send_text_message(client, headers)
        
        print("\n3️⃣ Probando listado de mensajes...")
        test_list_messages(client, headers)
        
        print("\n4️⃣ Probando obtener mensaje por ID...")
        if message_id:
            test_get_message_by_id(client, headers, message_id)
        
        print("\n5️⃣ Probando filtros en listado...")
        test_list_messages_with_filters(client, headers)
        
        print("\n6️⃣ Probando manejo de errores...")
        test_error_handling(client, headers)
        
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)

def test_messages_health(client, headers):
    """
    Prueba el endpoint de salud/test de mensajes
    """
    try:
        response = client.get('/v1/messages/test', headers=headers)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   ✅ Servicio activo: {data.get('data', {}).get('service_status')}")
            print(f"   📊 Total mensajes: {data.get('data', {}).get('total_messages', 0)}")
            print(f"   📱 Líneas disponibles: {data.get('data', {}).get('available_lines', 0)}")
        else:
            if response.content_type == 'application/json':
                error_data = response.get_json()
                print(f"   ❌ Error: {error_data}")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en prueba de salud: {e}")

def test_send_text_message(client, headers):
    """
    Prueba el envío de mensajes de texto
    """
    message_data = {
        "phone_number": "+5491123456789",
        "content": f"Mensaje de prueba enviado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # No especificar line_id para usar línea por defecto
    }
    
    try:
        response = client.post(
            '/v1/messages/text',
            headers=headers,
            json=message_data
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            message_info = data.get('data', {})
            print(f"   ✅ Mensaje enviado exitosamente")
            print(f"   📧 ID: {message_info.get('id')}")
            print(f"   🆔 WhatsApp ID: {message_info.get('whatsapp_message_id')}")
            print(f"   📱 Teléfono: {message_info.get('phone_number')}")
            print(f"   ✉️ Contenido: {message_info.get('content')[:50]}...")
            print(f"   📊 Estado: {message_info.get('status')}")
            return message_info.get('whatsapp_message_id')
        else:
            if response.content_type == 'application/json':
                error_data = response.get_json()
                print(f"   ❌ Error enviando mensaje: {error_data.get('message')}")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Error en envío de mensaje: {e}")
        return None

def test_list_messages(client, headers):
    """
    Prueba el listado de mensajes
    """
    try:
        response = client.get('/v1/messages?page=1&per_page=5', headers=headers)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            messages_data = data.get('data', {})
            messages = messages_data.get('messages', [])
            pagination = messages_data.get('pagination', {})
            
            print(f"   ✅ Mensajes obtenidos: {len(messages)}")
            print(f"   📄 Página actual: {pagination.get('page', 1)}")
            print(f"   📊 Total elementos: {pagination.get('total', 0)}")
            
            if messages:
                print("   📋 Últimos mensajes:")
                for msg in messages[:3]:
                    print(f"      - {msg.get('phone_number')} | {msg.get('status')} | {msg.get('content', '')[:30]}...")
        else:
            if response.content_type == 'application/json':
                error_data = response.get_json()
                print(f"   ❌ Error obteniendo mensajes: {error_data.get('message')}")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en listado de mensajes: {e}")

def test_get_message_by_id(client, headers, whatsapp_message_id):
    """
    Prueba obtener un mensaje específico por ID de WhatsApp
    """
    try:
        response = client.get(
            f'/v1/messages/whatsapp/{whatsapp_message_id}',
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            message_info = data.get('data', {})
            print(f"   ✅ Mensaje encontrado")
            print(f"   🆔 WhatsApp ID: {message_info.get('whatsapp_message_id')}")
            print(f"   📱 Teléfono: {message_info.get('phone_number')}")
            print(f"   📊 Estado: {message_info.get('status')}")
            print(f"   📅 Creado: {message_info.get('created_at')}")
        else:
            error_data = response.get_json()
            print(f"   ❌ Error obteniendo mensaje: {error_data.get('message')}")
    except Exception as e:
        print(f"   ❌ Error obteniendo mensaje por ID: {e}")

def test_list_messages_with_filters(client, headers):
    """
    Prueba el listado con filtros
    """
    try:
        # Filtrar por estado 'sent'
        response = client.get(
            '/v1/messages?status=sent&message_type=text',
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            messages_data = data.get('data', {})
            messages = messages_data.get('messages', [])
            
            print(f"   ✅ Mensajes filtrados (sent + text): {len(messages)}")
            if messages:
                print(f"   📊 Todos tienen estado 'sent': {all(msg.get('status') == 'sent' for msg in messages)}")
                print(f"   📧 Todos son tipo 'text': {all(msg.get('message_type') == 'text' for msg in messages)}")
        else:
            error_data = response.get_json()
            print(f"   ❌ Error con filtros: {error_data.get('message')}")
    except Exception as e:
        print(f"   ❌ Error probando filtros: {e}")

def test_error_handling(client, headers):
    """
    Prueba el manejo de errores
    """
    print("   📋 Probando diferentes casos de error:")
    
    # Error 401 - Sin API key
    try:
        response = client.get('/v1/messages/test')
        print(f"      Sin API key - Status: {response.status_code} ({'✅' if response.status_code == 401 else '❌'})")
    except Exception as e:
        print(f"      ❌ Error probando sin API key: {e}")
    
    # Error 400 - Datos inválidos
    try:
        invalid_data = {"phone_number": "numero-invalido", "content": ""}
        response = client.post(
            '/v1/messages/text',
            headers=headers,
            json=invalid_data
        )
        print(f"      Datos inválidos - Status: {response.status_code} ({'✅' if response.status_code == 400 else '❌'})")
    except Exception as e:
        print(f"      ❌ Error probando datos inválidos: {e}")
    
    # Error 404 - Mensaje no encontrado
    try:
        response = client.get(
            '/v1/messages/whatsapp/mensaje-inexistente',
            headers=headers
        )
        print(f"      Mensaje no encontrado - Status: {response.status_code} ({'✅' if response.status_code == 404 else '❌'})")
    except Exception as e:
        print(f"      ❌ Error probando mensaje inexistente: {e}")

if __name__ == "__main__":
    try:
        test_messages_api()
    except KeyboardInterrupt:
        print("\n\n⚠️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado en las pruebas: {e}")
        import traceback
        traceback.print_exc()
