"""
Script para pruebas con tokens reales de WhatsApp Business API
Incluye validaciones y pruebas paso a paso
"""
import os
import requests
import json
from datetime import datetime

# Cargar variables de entorno de producción
def load_production_env():
    """Cargar variables del archivo .env.production"""
    env_vars = {}
    try:
        with open('.env.production', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"Error cargando .env.production: {e}")
        return None
    return env_vars

def test_whatsapp_token_validity(access_token, business_id):
    """Valida que el token de acceso sea válido"""
    print("\n=== VALIDANDO TOKEN DE WHATSAPP ===")
    
    url = f"https://graph.facebook.com/v18.0/{business_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token válido")
            print(f"Business ID: {data.get('id')}")
            print(f"Business Name: {data.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Token inválido: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error validando token: {e}")
        return False

def test_phone_number_validity(access_token, phone_number_id):
    """Valida que el Phone Number ID sea correcto"""
    print(f"\n=== VALIDANDO PHONE NUMBER ID: {phone_number_id} ===")
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Phone Number ID válido")
            print(f"Phone Number: {data.get('display_phone_number')}")
            print(f"Quality Rating: {data.get('quality_rating')}")
            print(f"Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Phone Number ID inválido: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error validando Phone Number ID: {e}")
        return False

def test_local_server_health():
    """Prueba que el servidor local esté funcionando"""
    print("\n=== PROBANDO SERVIDOR LOCAL ===")
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"Health Check Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Servidor local funcionando")
            return True
        else:
            print(f"❌ Servidor local con problemas: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Servidor local no disponible: {e}")
        print("Asegúrate de que el servidor esté corriendo con: python run_simple_server.py")
        return False

def test_send_real_message(phone_number, message_text="🚀 Mensaje de prueba desde API real!"):
    """Envía un mensaje real a través de nuestro microservicio"""
    print(f"\n=== ENVIANDO MENSAJE REAL A: {phone_number} ===")
    
    url = "http://localhost:5000/v1/messages/text"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "dev-api-key"
    }
    
    data = {
        "to": phone_number,
        "text": message_text,
        "line_id": "line_1"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MENSAJE ENVIADO EXITOSAMENTE!")
            print(f"Message ID: {result.get('message_id')}")
            print(f"WhatsApp Message ID: {result.get('whatsapp_message_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Phone Number: {result.get('phone_number')}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def main():
    """Ejecuta todas las pruebas de producción"""
    print("🔥 INICIANDO PRUEBAS CON TOKENS REALES DE WHATSAPP BUSINESS API 🔥")
    print("=" * 70)
    
    # Cargar configuración
    env_vars = load_production_env()
    if not env_vars:
        print("❌ No se pudo cargar la configuración de producción")
        return
    
    access_token = env_vars.get('WHATSAPP_ACCESS_TOKEN')
    business_id = env_vars.get('WHATSAPP_BUSINESS_ID')
    phone_number_id = env_vars.get('LINE_1_PHONE_NUMBER_ID')
    
    if not all([access_token, business_id, phone_number_id]):
        print("❌ Faltan configuraciones necesarias en .env.production")
        return
    
    # Ejecutar pruebas paso a paso
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Validar token
    if test_whatsapp_token_validity(access_token, business_id):
        tests_passed += 1
    
    # Test 2: Validar Phone Number ID
    if test_phone_number_validity(access_token, phone_number_id):
        tests_passed += 1
    
    # Test 3: Verificar servidor local
    if test_local_server_health():
        tests_passed += 1
    
    # Test 4: Enviar mensaje real (solo si todo está bien)
    if tests_passed == 3:
        # Solicitar número de destino
        print("\n" + "=" * 50)
        print("⚠️  ATENCIÓN: Vamos a enviar un mensaje REAL")
        print("Asegúrate de usar TU PROPIO número para la prueba")
        print("=" * 50)
        
        target_phone = input("\nIngresa el número de WhatsApp de destino (con código de país, ej: 59167004011): ").strip()
        
        if target_phone:
            if test_send_real_message(target_phone):
                tests_passed += 1
        else:
            print("❌ No se proporcionó número de destino")
    
    # Resumen final
    print("\n" + "=" * 70)
    print(f"🎯 RESUMEN: {tests_passed}/{total_tests} pruebas exitosas")
    
    if tests_passed == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS! Tu API está lista para producción")
    elif tests_passed >= 3:
        print("✅ API configurada correctamente, lista para enviar mensajes")
    else:
        print("⚠️  Hay problemas en la configuración que necesitas revisar")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
