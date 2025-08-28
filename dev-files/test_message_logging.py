"""
Script de prueba para demostrar el logging en endpoint de mensajes
Simula calls al endpoint /v1/messages/text para mostrar los logs
"""

import requests
import json
import time
from datetime import datetime

def test_text_message_logging():
    """
    Prueba el logging del endpoint de mensajes de texto
    """
    print("📝 PRUEBA: Logging en Endpoint de Mensajes de Texto")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    endpoint = "/v1/messages/text"
    full_url = f"{base_url}{endpoint}"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-api-key',
        'User-Agent': 'test-logging-script/1.0'
    }
    
    # Casos de prueba
    test_cases = [
        {
            'name': 'Mensaje de texto exitoso',
            'payload': {
                'to': '5491123456789',
                'type': 'text',
                'text': {
                    'body': 'Hola! Este es un mensaje de prueba para demostrar el sistema de logging.',
                    'preview_url': False
                },
                'messaging_line_id': 1
            },
            'expected_status': 200
        },
        {
            'name': 'Mensaje sin datos (error de validación)',
            'payload': None,
            'expected_status': 400
        },
        {
            'name': 'Mensaje con texto muy largo',
            'payload': {
                'to': '5491987654321',
                'type': 'text',
                'text': {
                    'body': 'Este es un mensaje muy largo para probar cómo el sistema de logging maneja mensajes extensos. ' * 10,
                    'preview_url': True
                },
                'messaging_line_id': 2
            },
            'expected_status': 200
        },
        {
            'name': 'Mensaje con datos inválidos',
            'payload': {
                'to': 'número_inválido',
                'type': 'text',
                'text': {
                    'body': 'Mensaje con número de teléfono inválido'
                }
            },
            'expected_status': 400
        }
    ]
    
    print(f"🔗 Endpoint de prueba: {full_url}")
    print(f"🔑 API Key: {headers['X-API-Key']}")
    print(f"📊 Casos de prueba: {len(test_cases)}")
    print()
    
    # Ejecutar casos de prueba
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} CASO {i}: {test_case['name']} {'='*20}")
        
        start_time = time.time()
        
        try:
            # Hacer request
            response = requests.post(
                full_url,
                json=test_case['payload'],
                headers=headers,
                timeout=10
            )
            
            request_time = (time.time() - start_time) * 1000
            
            # Mostrar resultado
            print(f"📤 Request enviada:")
            if test_case['payload']:
                # Mostrar payload sanitizado
                payload_copy = test_case['payload'].copy()
                if 'to' in payload_copy:
                    payload_copy['to'] = payload_copy['to'][:3] + '***' + payload_copy['to'][-4:]
                print(f"   {json.dumps(payload_copy, indent=2)}")
            else:
                print("   (sin payload)")
            
            print(f"\n📥 Response recibida:")
            print(f"   Status: {response.status_code}")
            print(f"   Tiempo: {request_time:.1f}ms")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    message_id = response_data.get('data', {}).get('whatsapp_message_id', 'N/A')
                    print(f"   ✅ Mensaje enviado - ID: {message_id}")
                else:
                    print(f"   ❌ Error: {response_data.get('message', 'Unknown')}")
            else:
                error_data = response.json() if response.content else {'message': 'Sin contenido'}
                print(f"   ❌ Error: {error_data.get('message', 'Unknown')}")
            
            # Verificar status esperado
            if response.status_code == test_case['expected_status']:
                print(f"   🎯 Status esperado: ✅")
            else:
                print(f"   🎯 Status esperado {test_case['expected_status']}, recibido {response.status_code}: ⚠️")
            
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se pudo conectar al servidor")
            print("   Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:5000")
        except requests.exceptions.Timeout:
            print("❌ Error: Timeout - El servidor tardó demasiado en responder")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        # Pausa entre casos
        if i < len(test_cases):
            print(f"\n⏳ Esperando 2 segundos antes del siguiente caso...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ PRUEBAS COMPLETADAS")
    print()
    print("📋 QUÉ REVISAR EN LOS LOGS:")
    print("1. 📁 Revisar logs/current/ o logs/2025/08/26/")
    print("2. 🔍 Buscar en los archivos:")
    print("   • api_*.log - Logs de API con requests y responses")
    print("   • services_*.log - Logs del servicio de mensajería")
    print("   • performance_*.log - Métricas de tiempo de respuesta")
    print("   • whatsapp_api_*.log - Eventos específicos de WhatsApp")
    print()
    print("📊 PATRONES A BUSCAR:")
    print("• 'Iniciando procesamiento de envío de mensaje de texto'")
    print("• 'Datos del mensaje validados exitosamente'") 
    print("• 'Mensaje de texto enviado exitosamente'")
    print("• 'processing_time_ms' - Tiempos de procesamiento")
    print("• 'phone_number_hash' - Números de teléfono sanitizados")
    print("• 'message_id' - IDs de mensajes generados")
    print()
    
    return True


def show_log_examples():
    """
    Muestra ejemplos de cómo se ven los logs generados
    """
    print("\n📄 EJEMPLOS DE LOGS GENERADOS:")
    print("=" * 60)
    
    examples = [
        {
            'file': 'api_2025-08-26.log',
            'description': 'Log de API con request inicial',
            'example': '''
{
  "timestamp": "2025-08-26T15:47:39.123456",
  "level": "INFO",
  "logger": "whatsapp_api",
  "module": "routes",
  "function": "post",
  "line": 75,
  "message": "Iniciando procesamiento de envío de mensaje de texto",
  "data": {
    "endpoint": "/v1/messages/text",
    "method": "POST",
    "content_type": "application/json",
    "remote_addr": "127.0.0.1",
    "user_agent": "test-logging-script/1.0",
    "content_length": 156
  }
}'''
        },
        {
            'file': 'services_2025-08-26.log',
            'description': 'Log del servicio con datos sanitizados',
            'example': '''
{
  "timestamp": "2025-08-26T15:47:39.234567",
  "level": "INFO", 
  "logger": "whatsapp_service",
  "module": "routes",
  "function": "post",
  "line": 105,
  "message": "Enviando mensaje de texto a través del servicio",
  "data": {
    "service_method": "send_text_message",
    "phone_number_hash": "549***6789",
    "message_type": "text",
    "processing_start": 1724692059.234
  }
}'''
        },
        {
            'file': 'performance_2025-08-26.log',
            'description': 'Métrica de performance',
            'example': '''
{
  "timestamp": "2025-08-26T15:47:39.345678",
  "level": "INFO",
  "logger": "whatsapp_performance", 
  "module": "logger",
  "function": "log_performance_metric",
  "line": 345,
  "message": "Performance metric: text_message_processing_time=145.2ms",
  "data": {
    "metric_name": "text_message_processing_time",
    "value": 145.2,
    "unit": "ms",
    "tags": {
      "endpoint": "/v1/messages/text",
      "status": "success",
      "message_type": "text"
    }
  }
}'''
        }
    ]
    
    for example in examples:
        print(f"\n📄 {example['file']}")
        print(f"   {example['description']}")
        print(f"   {example['example']}")
    
    print("\n💡 VENTAJAS DEL LOGGING ESTRUCTURADO:")
    print("✅ Fácil análisis automático con herramientas como ELK Stack")
    print("✅ Búsqueda eficiente por campos específicos (phone_number, message_id)")
    print("✅ Métricas automáticas de performance y errores")
    print("✅ Trazabilidad completa de requests")
    print("✅ Datos sanitizados para cumplir con privacidad")


def main():
    """
    Función principal
    """
    print("🗓️ DEMOSTRACIÓN: Sistema de Logging en Endpoints")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar pruebas
    success = test_text_message_logging()
    
    # Mostrar ejemplos
    show_log_examples()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡DEMOSTRACIÓN COMPLETADA!")
        print("\n🔍 Para ver los logs generados:")
        print("1. Navega a la carpeta logs/")
        print("2. Abre los archivos .log con cualquier editor de texto")
        print("3. Busca los patrones mencionados arriba")
        print("\n💡 Los logs están organizados por fecha automáticamente")
    else:
        print("⚠️ DEMOSTRACIÓN INCOMPLETA")
        print("Revisa la conexión con el servidor")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
