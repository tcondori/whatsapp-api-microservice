"""
Diagnóstico completo para verificar por qué no llegó el mensaje de WhatsApp
"""
import requests
import json
from datetime import datetime

def check_whatsapp_message_status():
    """Verifica el estado de los mensajes enviados recientemente"""
    print("🔍 DIAGNÓSTICO: ¿Por qué no llegó el mensaje?")
    print("=" * 60)
    
    # 1. Verificar mensajes en nuestra base de datos
    print("\n1️⃣ VERIFICANDO MENSAJES EN NUESTRA BASE DE DATOS:")
    try:
        response = requests.get(
            "http://localhost:5000/v1/messages",
            headers={"X-API-Key": "dev-api-key"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', {}).get('messages', [])
            
            print(f"✅ Encontrados {len(messages)} mensajes en total")
            
            # Mostrar los últimos 3 mensajes
            recent_messages = messages[:3]
            for i, msg in enumerate(recent_messages, 1):
                print(f"\n📨 Mensaje {i}:")
                print(f"   • ID: {msg.get('id')}")
                print(f"   • WhatsApp ID: {msg.get('whatsapp_message_id')}")
                print(f"   • Teléfono: {msg.get('phone_number')}")
                print(f"   • Contenido: {msg.get('content', '')[:50]}...")
                print(f"   • Estado: {msg.get('status')}")
                print(f"   • Dirección: {msg.get('direction')}")
                print(f"   • Creado: {msg.get('created_at')}")
                
        else:
            print(f"❌ Error obteniendo mensajes: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error consultando mensajes: {e}")
    
    # 2. Verificar configuración actual
    print(f"\n2️⃣ VERIFICANDO CONFIGURACIÓN ACTUAL:")
    try:
        with open('.env', 'r') as f:
            config_lines = f.readlines()
            
        for line in config_lines:
            line = line.strip()
            if line.startswith('LINE_1_PHONE_NUMBER'):
                print(f"✅ {line}")
            elif line.startswith('WHATSAPP_ACCESS_TOKEN'):
                token = line.split('=', 1)[1] if '=' in line else ''
                print(f"✅ WHATSAPP_ACCESS_TOKEN={'*' * 50}...{token[-10:] if token else 'VACÍO'}")
            elif line.startswith('WEBHOOK_'):
                print(f"✅ {line}")
                
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")

def test_direct_whatsapp_api():
    """Hace una prueba directa con la API de WhatsApp"""
    print(f"\n3️⃣ PRUEBA DIRECTA CON WHATSAPP API:")
    
    # Cargar configuración
    try:
        with open('.env', 'r') as f:
            config = {}
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value
        
        access_token = config.get('WHATSAPP_ACCESS_TOKEN')
        phone_number_id = config.get('LINE_1_PHONE_NUMBER_ID')
        
        if not access_token or not phone_number_id:
            print("❌ Faltan tokens de configuración")
            return
        
        # Enviar mensaje directo
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        current_time = datetime.now().strftime("%H:%M:%S")
        data = {
            "messaging_product": "whatsapp",
            "to": "59167028778",  # Tu número
            "type": "text",
            "text": {
                "body": f"🔥 PRUEBA DIRECTA - {current_time} - ¿Llegó este mensaje?"
            }
        }
        
        print(f"📤 Enviando mensaje directo a WhatsApp API...")
        print(f"   • URL: {url}")
        print(f"   • Para: {data['to']}")
        print(f"   • Mensaje: {data['text']['body']}")
        
        response = requests.post(url, json=data, headers=headers, timeout=15)
        
        print(f"\n📊 RESPUESTA DE WHATSAPP API:")
        print(f"   • Status: {response.status_code}")
        print(f"   • Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   • Respuesta: {json.dumps(result, indent=2)}")
            
            if 'messages' in result and result['messages']:
                whatsapp_id = result['messages'][0]['id']
                print(f"✅ MENSAJE ENVIADO EXITOSAMENTE!")
                print(f"   • WhatsApp Message ID: {whatsapp_id}")
                print(f"   • ¿Te llegó este mensaje directo?")
            else:
                print(f"⚠️  Respuesta exitosa pero sin mensaje ID")
        else:
            print(f"❌ Error en WhatsApp API:")
            print(f"   • Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")

def check_phone_number_format():
    """Verifica el formato del número de teléfono"""
    print(f"\n4️⃣ VERIFICANDO FORMATO DE NÚMERO:")
    
    test_number = "59167028778"
    print(f"   • Número usado: {test_number}")
    print(f"   • Formato: +{test_number}")
    
    # Validar formato boliviano
    if test_number.startswith('591'):
        if len(test_number) == 11:
            print(f"✅ Formato boliviano válido (591 + 8 dígitos)")
        else:
            print(f"⚠️  Formato boliviano posiblemente incorrecto (debería ser 11 dígitos)")
    else:
        print(f"⚠️  No parece ser número boliviano (debería empezar con 591)")
    
    print(f"   • ¿El número {test_number} está registrado en WhatsApp?")
    print(f"   • ¿Tiene WhatsApp Business o WhatsApp normal?")

def check_whatsapp_business_requirements():
    """Verifica requisitos de WhatsApp Business API"""
    print(f"\n5️⃣ VERIFICANDO REQUISITOS WHATSAPP BUSINESS:")
    print(f"   • ¿El número destino ({59167028778}) acepta mensajes de empresas?")
    print(f"   • ¿Has tenido conversación previa con este número desde el WhatsApp Business?")
    print(f"   • ¿El número está en la lista de números de prueba de Meta?")
    print(f"   • ¿Hay restricciones de país (Bolivia) en tu cuenta de Meta?")
    
    print(f"\n📋 PASOS PARA RESOLVER:")
    print(f"   1. Verificar que el número destino tenga WhatsApp activo")
    print(f"   2. Intentar con un número de prueba oficial de Meta")
    print(f"   3. Revisar el estado de tu cuenta en Meta Business")
    print(f"   4. Verificar límites de envío en tu WhatsApp Business API")

if __name__ == "__main__":
    check_whatsapp_message_status()
    test_direct_whatsapp_api()
    check_phone_number_format()
    check_whatsapp_business_requirements()
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Revisa si te llegó el mensaje directo recién enviado")
    print(f"   2. Si no llegó, el problema puede ser:")
    print(f"      • Número no registrado en WhatsApp")
    print(f"      • Restricciones de WhatsApp Business API")
    print(f"      • Configuración de Meta Business")
    print(f"   3. Intenta con otro número de prueba")
