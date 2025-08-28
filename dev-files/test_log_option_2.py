"""
Prueba de logs simples con detalles (Opción 2)
"""

import requests
import json

def test_log_option_2():
    """
    Prueba los logs simples con detalles
    """
    print("📝 PRUEBA: Logs Simples con Detalles (Opción 2)")
    print("=" * 60)
    
    url = "http://127.0.0.1:5000/v1/messages/text"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-api-key'
    }
    
    # Casos de prueba
    test_cases = [
        {
            'name': '✅ Mensaje exitoso',
            'payload': {
                'to': '5491123456789',
                'type': 'text',
                'text': {
                    'body': 'Mensaje de prueba para logs simples'
                }
            }
        },
        {
            'name': '❌ Payload vacío (error de validación)',
            'payload': None
        },
        {
            'name': '⚠️ Número inválido',
            'payload': {
                'to': 'numero_invalido',
                'type': 'text',
                'text': {
                    'body': 'Test con número inválido'
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*15} CASO {i}: {test_case['name']} {'='*15}")
        
        try:
            response = requests.post(
                url, 
                json=test_case['payload'], 
                headers=headers, 
                timeout=5
            )
            
            print(f"📤 Payload enviado:")
            if test_case['payload']:
                payload_display = test_case['payload'].copy()
                if 'to' in payload_display:
                    payload_display['to'] = payload_display['to'][:3] + '***' + payload_display['to'][-4:]
                print(f"   {json.dumps(payload_display, indent=2)}")
            else:
                print("   (payload vacío)")
            
            print(f"\n📥 Response recibida:")
            print(f"   Status: {response.status_code}")
            
            if response.content:
                try:
                    response_data = response.json()
                    if response.status_code == 200:
                        message_id = response_data.get('data', {}).get('whatsapp_message_id', 'N/A')
                        print(f"   ✅ Éxito - Message ID: {message_id}")
                    else:
                        print(f"   ❌ Error: {response_data.get('message', 'Unknown')}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            
            print(f"\n🔍 LOGS GENERADOS ESPERADOS:")
            if response.status_code == 200:
                print(f"   📤 'Mensaje de texto enviado a 549***6789 - Estado: iniciando procesamiento'")
                print(f"   ✅ 'Mensaje de texto completado - ID: [message_id] - Destinatario: 549***6789 - Estado: exitoso'")
            else:
                if test_case['payload'] is None:
                    print(f"   ⚠️ 'Error de validación en mensaje de texto - Error: [error_message] - Endpoint: /v1/messages/text'")
                else:
                    print(f"   ❌ 'Error de servicio de mensajería - Error: [error_message] - Destinatario: [phone]'")
                    
        except requests.ConnectionError:
            print("❌ Error: Servidor no disponible")
            print("   Ejecuta: python entrypoint.py")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    print(f"\n{'='*60}")
    print("📁 REVISA LOS LOGS EN:")
    print("   • logs/current/api_*.log")
    print("   • logs/2025/08/26/api_2025-08-26.log")
    print()
    print("🔍 BUSCA ESTAS LÍNEAS:")
    print("   • 'Mensaje de texto enviado a' (log de inicio)")
    print("   • 'Mensaje de texto completado' (log de éxito)")  
    print("   • 'Error de validación en mensaje de texto' (log de error)")
    print("   • 'Error de servicio de mensajería' (log de error de servicio)")
    print()
    print("✨ FORMATO DE LOS LOGS:")
    print("   2025-08-26 15:47:39 - whatsapp_api - INFO - [mensaje_con_detalles]")

if __name__ == "__main__":
    test_log_option_2()
