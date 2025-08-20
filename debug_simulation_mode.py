"""
Script para diagnosticar por qué los mensajes se envían en modo simulación
"""
import os
from flask import Flask
import sys
sys.path.append('.')

def check_config_loading():
    """Verifica cómo se está cargando la configuración"""
    print("🔍 DIAGNÓSTICO: ¿Por qué está en modo simulación?")
    print("=" * 60)
    
    # 1. Verificar archivo .env
    print("1️⃣ VERIFICANDO ARCHIVO .env:")
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        access_token_line = None
        phone_id_line = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('WHATSAPP_ACCESS_TOKEN='):
                access_token_line = line
            elif line.startswith('LINE_1_PHONE_NUMBER_ID='):
                phone_id_line = line
        
        print(f"✅ Token encontrado: {bool(access_token_line)}")
        if access_token_line:
            token_value = access_token_line.split('=', 1)[1] if '=' in access_token_line else ''
            print(f"   • Longitud del token: {len(token_value)}")
            print(f"   • Empieza con EAA: {token_value.startswith('EAA')}")
            print(f"   • Últimos 10 chars: ...{token_value[-10:] if token_value else 'VACÍO'}")
        
        print(f"✅ Phone Number ID encontrado: {bool(phone_id_line)}")
        if phone_id_line:
            phone_value = phone_id_line.split('=', 1)[1] if '=' in phone_id_line else ''
            print(f"   • Phone Number ID: {phone_value}")
            
    except Exception as e:
        print(f"❌ Error leyendo .env: {e}")
    
    # 2. Verificar carga en Flask
    print(f"\n2️⃣ VERIFICANDO CARGA EN FLASK:")
    try:
        from entrypoint import create_app
        app = create_app()
        
        with app.app_context():
            token_from_config = app.config.get('WHATSAPP_ACCESS_TOKEN')
            phone_from_config = app.config.get('LINE_1_PHONE_NUMBER_ID')
            
            print(f"✅ Token en Flask config: {bool(token_from_config)}")
            if token_from_config:
                print(f"   • Longitud: {len(token_from_config)}")
                print(f"   • Últimos 10: ...{token_from_config[-10:]}")
            else:
                print(f"   ❌ TOKEN NO CARGADO EN FLASK CONFIG")
            
            print(f"✅ Phone ID en Flask config: {bool(phone_from_config)}")
            if phone_from_config:
                print(f"   • Valor: {phone_from_config}")
            else:
                print(f"   ❌ PHONE NUMBER ID NO CARGADO EN FLASK CONFIG")
                
    except Exception as e:
        print(f"❌ Error verificando Flask config: {e}")
    
    # 3. Verificar servicio WhatsApp API
    print(f"\n3️⃣ VERIFICANDO SERVICIO WHATSAPP API:")
    try:
        from app.services.whatsapp_api import WhatsAppAPIService
        from entrypoint import create_app
        
        app = create_app()
        with app.app_context():
            service = WhatsAppAPIService()
            
            print(f"✅ Servicio creado: {bool(service)}")
            print(f"✅ Tiene access_token: {bool(service.access_token)}")
            
            if service.access_token:
                print(f"   • Longitud del token: {len(service.access_token)}")
                print(f"   • Últimos 10: ...{service.access_token[-10:]}")
            else:
                print(f"   ❌ SERVICIO SIN ACCESS TOKEN - USARÁ SIMULACIÓN")
                
            # Verificar método de configuración
            from flask import current_app
            token_direct = current_app.config.get('WHATSAPP_ACCESS_TOKEN')
            print(f"✅ Token desde current_app: {bool(token_direct)}")
            
    except Exception as e:
        print(f"❌ Error verificando servicio WhatsApp: {e}")

def test_manual_api_call():
    """Hacer una llamada manual a WhatsApp API para verificar tokens"""
    print(f"\n4️⃣ PRUEBA MANUAL DE WHATSAPP API:")
    
    # Leer token directamente del archivo
    try:
        with open('.env', 'r') as f:
            config = {}
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value
        
        access_token = config.get('WHATSAPP_ACCESS_TOKEN', '').strip()
        phone_number_id = config.get('LINE_1_PHONE_NUMBER_ID', '').strip()
        
        print(f"✅ Token leído: {len(access_token)} caracteres")
        print(f"✅ Phone ID leído: {phone_number_id}")
        
        if access_token and phone_number_id:
            import requests
            from datetime import datetime
            
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
                    "body": f"🔥 MENSAJE DIRECTO REAL - {datetime.now().strftime('%H:%M:%S')}"
                }
            }
            
            print(f"📤 Enviando a WhatsApp API directamente...")
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ ÉXITO! Respuesta:")
                import json
                print(json.dumps(result, indent=2))
                
                if 'messages' in result:
                    msg_id = result['messages'][0]['id']
                    print(f"🎯 MESSAGE ID REAL: {msg_id}")
                    print(f"🎯 ¿Te llegó este mensaje directo?")
            else:
                print(f"❌ Error: {response.text}")
        else:
            print(f"❌ Faltan tokens en configuración")
            
    except Exception as e:
        print(f"❌ Error en prueba manual: {e}")

if __name__ == "__main__":
    check_config_loading()
    test_manual_api_call()
    
    print(f"\n🎯 DIAGNÓSTICO:")
    print(f"   • Si el servicio no tiene access_token, usará simulación")
    print(f"   • Verifica que los tokens se carguen correctamente en Flask")
    print(f"   • La prueba manual debe mostrar si los tokens funcionan")
    print(f"   • Si la prueba manual funciona, el problema está en el servicio")
