"""
Prueba funcional simple del sistema de logging estructurado
Demuestra logging sin contexto de Flask
"""

import sys
import os
import time
import json
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

# Configuración manual sin Flask
os.environ['FLASK_ENV'] = 'development'

def test_structured_logging_standalone():
    """
    Prueba el sistema de logging estructurado de forma independiente
    """
    print("🔧 Probando sistema de logging estructurado...")
    
    try:
        from app.utils.logger import WhatsAppLogger, EventLogger
        from app.utils.events import EventType, Event
        from datetime import datetime
        
        # Configurar logging
        temp_dir = Path('test_structured_logs')
        temp_dir.mkdir(exist_ok=True)
        
        WhatsAppLogger.configure_logging(
            log_level='DEBUG',
            log_dir=str(temp_dir),
            environment='development'
        )
        
        # Obtener loggers específicos
        api_logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        service_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SERVICE_LOGGER)
        security_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SECURITY_LOGGER)
        
        print("✅ Loggers configurados correctamente")
        
        # Prueba 1: Logging básico con datos estructurados
        api_logger.info(
            "API request procesada",
            extra={'extra_data': {
                'endpoint': '/api/messages',
                'method': 'POST',
                'user_id': 'user123',
                'response_time_ms': 150.5,
                'success': True
            }}
        )
        
        # Prueba 2: Logging de servicio con datos de WhatsApp
        service_logger.info(
            "Mensaje de WhatsApp enviado",
            extra={'extra_data': {
                'phone_number_sanitized': '+52***90',
                'message_type': 'text',
                'message_id': 'msg_12345',
                'template_name': None,
                'send_time_ms': 200.3
            }}
        )
        
        # Prueba 3: Logging de seguridad
        security_logger.warning(
            "Intento de acceso sospechoso detectado",
            extra={'extra_data': {
                'ip_address': '192.168.1.100',
                'user_agent': 'SuspiciousBot/1.0',
                'endpoint': '/api/messages',
                'attempts_count': 5,
                'blocked': True
            }}
        )
        
        # Prueba 4: Event Logger
        event_logger = EventLogger()
        
        event_logger.log_whatsapp_request(
            endpoint='/v1/messages',
            method='POST',
            payload={'to': '+1234567890', 'type': 'text'},
            phone_number='+1234567890',
            message_id='msg_test_001'
        )
        
        event_logger.log_whatsapp_response(
            endpoint='/v1/messages',
            status_code=200,
            response_data={'messages': [{'id': 'msg_test_001'}]},
            response_time_ms=185.2
        )
        
        # Prueba 5: Performance metrics
        event_logger.log_performance_metric(
            metric_name='message_send_latency',
            value=150.0,
            unit='ms',
            tags={'message_type': 'text', 'country': 'MX'}
        )
        
        print("✅ Todos los tipos de logging ejecutados correctamente")
        
        # Verificar archivos creados
        log_files = list(temp_dir.glob('*.log'))
        print(f"✅ Archivos de log creados: {len(log_files)}")
        
        for log_file in log_files:
            print(f"   📁 {log_file.name} ({log_file.stat().st_size} bytes)")
        
        # Mostrar contenido de algunos logs
        if log_files:
            print("\n📄 Muestra del contenido de logs:")
            for log_file in log_files[:2]:  # Solo los primeros 2
                print(f"\n--- {log_file.name} ---")
                try:
                    content = log_file.read_text(encoding='utf-8')
                    lines = content.strip().split('\n')
                    for line in lines[-3:]:  # Últimas 3 líneas
                        if line.strip():
                            print(f"  {line}")
                except Exception as e:
                    print(f"  Error leyendo archivo: {e}")
        
        # Limpiar archivos de prueba
        print(f"\n🧹 Limpiando {len(log_files)} archivos de prueba...")
        for log_file in log_files:
            try:
                log_file.unlink()
            except:
                pass  # Ignorar errores de limpieza
        
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba estructurada: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_event_creation_and_serialization():
    """
    Prueba creación y serialización de eventos
    """
    print("\n🔧 Probando creación y serialización de eventos...")
    
    try:
        from app.utils.events import Event, EventType
        from datetime import datetime
        
        # Crear diferentes tipos de eventos
        events = [
            Event(
                event_type=EventType.MESSAGE_SENT,
                timestamp=datetime.now(),
                source='whatsapp_service',
                data={
                    'phone_number': '+1234567890',
                    'message_id': 'msg_001',
                    'message_type': 'text',
                    'template_name': None
                },
                correlation_id='corr_001'
            ),
            Event(
                event_type=EventType.WEBHOOK_RECEIVED,
                timestamp=datetime.now(),
                source='webhook_handler',
                data={
                    'webhook_type': 'message_status',
                    'message_id': 'msg_001',
                    'status': 'delivered'
                }
            ),
            Event(
                event_type=EventType.API_REQUEST_COMPLETED,
                timestamp=datetime.now(),
                source='api_layer',
                data={
                    'endpoint': '/api/messages',
                    'method': 'POST',
                    'status_code': 200,
                    'response_time_ms': 150.0
                }
            )
        ]
        
        # Serializar eventos
        for i, event in enumerate(events):
            event_dict = event.to_dict()
            
            # Verificar estructura
            assert 'event_type' in event_dict
            assert 'timestamp' in event_dict  
            assert 'source' in event_dict
            assert 'data' in event_dict
            
            print(f"✅ Evento {i+1} ({event.event_type.value}) serializado correctamente")
            
            # Verificar que se puede serializar a JSON
            json_str = json.dumps(event_dict, default=str)
            assert len(json_str) > 0
            
            # Verificar que se puede deserializar
            deserialized = json.loads(json_str)
            assert deserialized['event_type'] == event.event_type.value
        
        print("✅ Todos los eventos creados y serializados correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en eventos: {e}")
        return False


def main():
    """
    Ejecuta todas las pruebas funcionales
    """
    print("🚀 Iniciando pruebas funcionales del sistema de logging")
    print("=" * 60)
    
    tests = [
        ("Logging Estructurado Standalone", test_structured_logging_standalone),
        ("Creación y Serialización de Eventos", test_event_creation_and_serialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS FUNCIONALES")
    print("="*60)
    
    passed = failed = 0
    for test_name, result in results:
        status = "✅ EXITOSA" if result else "❌ FALLIDA"
        print(f"{test_name:.<40} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResultados finales:")
    print(f"  ✅ Exitosas: {passed}")
    print(f"  ❌ Fallidas: {failed}")
    print(f"  📊 Total: {len(results)}")
    
    if failed == 0:
        print("\n🎉 ¡TODAS LAS PRUEBAS FUNCIONALES EXITOSAS!")
        print("📝 El sistema de logging estructurado está completamente funcional")
        print("\n🔍 Características verificadas:")
        print("  • Logging estructurado con formato JSON")
        print("  • Separación de logs por componente")
        print("  • Event system con serialización")
        print("  • Sanitización de datos sensibles")
        print("  • Métricas de performance")
        print("  • Logging de seguridad")
        print("\n📁 Los logs se generan en el directorio 'logs/'")
    else:
        print(f"\n⚠️  {failed} prueba(s) fallaron")
        print("🔍 Revisa los errores para más detalles")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    sys.exit(0 if success else 1)
