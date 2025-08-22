#!/usr/bin/env python3
"""
Script de prueba específico para verificación de webhook con Meta
Verifica que la respuesta sea texto plano como requiere Meta
"""
import requests
import sys

def test_webhook_verification_plain_text():
    """Prueba que la verificación devuelva texto plano"""
    
    # URLs a probar
    urls = [
        "http://localhost:5000/v1/webhooks",
        "https://193fa34e7248.ngrok-free.app/v1/webhooks"
    ]
    
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': 'Nicole07',
        'hub.challenge': 'meta_verification_test_123'
    }
    
    headers = {
        'ngrok-skip-browser-warning': 'true'
    }
    
    for url in urls:
        print(f"\n🔍 Probando: {url}")
        print("-" * 60)
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
            print(f"Content-Length: {len(response.content)} bytes")
            print(f"Response Text: '{response.text}'")
            print(f"Response Headers: {dict(response.headers)}")
            
            # Verificar que sea texto plano
            content_type = response.headers.get('Content-Type', '')
            is_plain_text = 'text/plain' in content_type
            is_correct_response = response.text == 'meta_verification_test_123'
            is_200_status = response.status_code == 200
            
            print(f"\n✅ Análisis:")
            print(f"  • Status 200: {'✅' if is_200_status else '❌'} {response.status_code}")
            print(f"  • Texto plano: {'✅' if is_plain_text else '❌'} {content_type}")
            print(f"  • Respuesta correcta: {'✅' if is_correct_response else '❌'}")
            
            if is_200_status and is_plain_text and is_correct_response:
                print(f"🎉 ¡PERFECTO! Meta podrá verificar esta URL")
                return True
            else:
                print(f"⚠️  Hay problemas que Meta no aceptará")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ No se puede conectar a {url}")
            if "localhost" in url:
                print(f"   Asegúrate que el servidor esté corriendo")
            continue
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    return False

def test_webhook_health():
    """Prueba rápida del health check"""
    print(f"\n🏥 Probando health check...")
    
    urls = [
        "http://localhost:5000/v1/webhooks/health",
        "https://193fa34e7248.ngrok-free.app/v1/webhooks/health"
    ]
    
    headers = {
        'X-API-Key': 'dev-api-key',
        'ngrok-skip-browser-warning': 'true'
    }
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {url} - OK")
                print(f"   Webhook processor: {data.get('data', {}).get('webhook_processor', 'unknown')}")
                return True
        except:
            continue
    
    print(f"❌ Health check falló")
    return False

if __name__ == "__main__":
    print("🚀 PRUEBA DE VERIFICACIÓN DE WEBHOOK PARA META")
    print("=" * 70)
    
    # Probar health check primero
    health_ok = test_webhook_health()
    
    if not health_ok:
        print("\n❌ El servidor no está disponible")
        print("Asegúrate de ejecutar: python run_server.py")
        sys.exit(1)
    
    # Probar verificación
    verification_ok = test_webhook_verification_plain_text()
    
    print("\n" + "=" * 70)
    if verification_ok:
        print("🎉 ¡WEBHOOK LISTO PARA META!")
        print("\nPuedes usar en Meta Developers:")
        print("📍 URL: https://193fa34e7248.ngrok-free.app/v1/webhooks")
        print("🔑 Token: Nicole07")
    else:
        print("❌ Webhook no está listo para Meta")
        print("\nRevisa:")
        print("• Que el servidor esté ejecutándose")
        print("• Que ngrok esté activo")  
        print("• Que los cambios se hayan aplicado (reiniciar servidor)")
