"""
Prueba específica para verificar el envío real de mensajes
con validación detallada de la respuesta
"""
import requests
import json

def test_send_real_message_detailed():
    """Envía un mensaje y analiza la respuesta detalladamente"""
    
    # Configuración
    url = "http://localhost:5000/v1/messages/text"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "dev-api-key"
    }
    
    # Datos del mensaje
    data = {
        "to": "59167028778",  # Tu número de prueba
        "text": "🎯 Prueba de mensaje REAL con validación detallada - " + str(__import__('datetime').datetime.now().strftime("%H:%M:%S")),
        "line_id": "line_1"
    }
    
    print("📱 ENVIANDO MENSAJE REAL CON ANÁLISIS DETALLADO")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(data, indent=2)}")
    print("=" * 60)
    
    try:
        # Enviar petición
        response = requests.post(url, json=data, headers=headers, timeout=15)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content-Type: {response.headers.get('content-type')}")
        
        # Analizar respuesta JSON
        try:
            response_data = response.json()
            print(f"✅ Respuesta JSON válida")
            print("\n📋 RESPUESTA COMPLETA:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # Validar estructura esperada
            if 'success' in response_data:
                print(f"\n✅ Success: {response_data['success']}")
                
                if 'message' in response_data:
                    print(f"✅ Message: {response_data['message']}")
                
                if 'data' in response_data and response_data['data']:
                    data_obj = response_data['data']
                    print(f"\n📊 DATOS DEL MENSAJE:")
                    print(f"  • ID interno: {data_obj.get('id', 'N/A')}")
                    print(f"  • WhatsApp ID: {data_obj.get('whatsapp_message_id', 'N/A')}")
                    print(f"  • Teléfono: {data_obj.get('phone_number', 'N/A')}")
                    print(f"  • Estado: {data_obj.get('status', 'N/A')}")
                    print(f"  • Línea: {data_obj.get('line_id', 'N/A')}")
                    print(f"  • Dirección: {data_obj.get('direction', 'N/A')}")
                    print(f"  • Tipo: {data_obj.get('message_type', 'N/A')}")
                    print(f"  • Creado: {data_obj.get('created_at', 'N/A')}")
                else:
                    print("⚠️  Falta el campo 'data' en la respuesta")
            else:
                print("⚠️  Falta el campo 'success' en la respuesta")
                
        except json.JSONDecodeError:
            print(f"❌ Error: Respuesta no es JSON válido")
            print(f"Contenido crudo: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

def test_whatsapp_api_direct():
    """Prueba directa con la API de WhatsApp para comparar"""
    import os
    
    # Cargar token
    access_token = None
    phone_number_id = None
    
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('WHATSAPP_ACCESS_TOKEN='):
                access_token = line.split('=', 1)[1].strip()
            if line.startswith('LINE_1_PHONE_NUMBER_ID='):
                phone_number_id = line.split('=', 1)[1].strip()
    
    # Hacer petición directa a WhatsApp API
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": "59167028778",
        "type": "text",
        "text": {
            "body": "🔥 Mensaje DIRECTO desde WhatsApp API - " + str(__import__('datetime').datetime.now().strftime("%H:%M:%S"))
        }
    }
    
    print("\n🔥 ENVIANDO MENSAJE DIRECTO A WHATSAPP API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=15)
        print(f"✅ Status Code: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 RESPUESTA DIRECTA DE WHATSAPP:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if 'messages' in response_data and response_data['messages']:
            whatsapp_id = response_data['messages'][0]['id']
            print(f"\n🎯 WhatsApp Message ID obtenido: {whatsapp_id}")
            return whatsapp_id
        
    except Exception as e:
        print(f"❌ Error con WhatsApp API directa: {e}")
    
    return None

if __name__ == "__main__":
    # Ejecutar pruebas
    test_send_real_message_detailed()
    
    print("\n" + "="*60)
    
    # Opcional: prueba directa para comparar
    test_whatsapp_api_direct()
