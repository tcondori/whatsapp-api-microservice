"""
Ejemplo de uso del sistema de logging y eventos
Demuestra cómo utilizar las diferentes funcionalidades implementadas
"""

import asyncio
import time
from datetime import datetime
from app.utils.logger import (
    WhatsAppLogger, EventLogger, log_execution_time, log_api_call
)
from app.utils.events import (
    EventType, Event, event_bus, EventEmitter, 
    log_whatsapp_message_sent, log_webhook_received
)
from app.utils.middleware import (
    whatsapp_api_logging, security_logging, database_logging
)
from app.utils.helpers import (
    log_operation, create_audit_log_entry, log_performance_metric
)


class WhatsAppServiceExample(EventEmitter):
    """
    Ejemplo de servicio que utiliza el sistema de logging y eventos
    """
    
    def __init__(self):
        super().__init__("whatsapp_service_example")
        self.logger = WhatsAppLogger.get_logger(WhatsAppLogger.SERVICE_LOGGER)
        self.event_logger = EventLogger()
    
    @log_execution_time()
    @log_api_call()
    @whatsapp_api_logging.log_api_call
    def send_message_example(self, phone_number: str, message: str, message_type: str = 'text'):
        """
        Ejemplo de envío de mensaje con logging completo
        """
        start_time = time.time()
        
        try:
            # Simular llamada a WhatsApp API
            self.logger.info(
                f"Enviando mensaje a {phone_number}",
                extra={'extra_data': {
                    'phone_number': phone_number,
                    'message_type': message_type,
                    'message_length': len(message)
                }}
            )
            
            # Simular procesamiento
            time.sleep(0.1)
            
            # Generar ID simulado de mensaje
            message_id = f"msg_{int(time.time())}"
            
            # Registrar evento de mensaje enviado
            self.emit_event_sync(
                EventType.MESSAGE_SENT,
                {
                    'phone_number': phone_number,
                    'message_id': message_id,
                    'message_type': message_type,
                    'message_length': len(message)
                },
                correlation_id=message_id
            )
            
            # Log con el EventLogger
            self.event_logger.log_message_sent(
                phone_number, message_type, message_id
            )
            
            # Registrar métrica de performance
            response_time = (time.time() - start_time) * 1000
            log_performance_metric(
                'message_send_time', response_time, 'ms',
                tags={'message_type': message_type}
            )
            
            return {
                'success': True,
                'message_id': message_id,
                'response_time_ms': response_time
            }
            
        except Exception as e:
            # Registrar error
            self.logger.error(
                f"Error enviando mensaje: {str(e)}",
                extra={'extra_data': {
                    'phone_number': phone_number,
                    'error': str(e),
                    'message_type': message_type
                }},
                exc_info=True
            )
            
            # Emitir evento de fallo
            self.emit_event_sync(
                EventType.MESSAGE_FAILED,
                {
                    'phone_number': phone_number,
                    'error': str(e),
                    'message_type': message_type
                }
            )
            
            raise
    
    @database_logging.log_query_execution
    def save_message_to_db_example(self, message_data: dict):
        """
        Ejemplo de guardado en base de datos con logging
        """
        # Simular operación de base de datos
        time.sleep(0.05)
        
        # Log de operación
        log_operation(
            'save_message',
            details={
                'message_id': message_data.get('message_id'),
                'phone_number': message_data.get('phone_number'),
                'operation_type': 'database_insert'
            }
        )
        
        return True
    
    def process_webhook_example(self, webhook_data: dict):
        """
        Ejemplo de procesamiento de webhook con logging
        """
        webhook_type = webhook_data.get('type', 'unknown')
        
        # Registrar recepción del webhook
        self.event_logger.log_webhook_received(
            webhook_type,
            webhook_data.get('phone_number'),
            webhook_data.get('message_id'),
            webhook_data
        )
        
        # Crear entrada de auditoría
        audit_entry = create_audit_log_entry(
            action='webhook_processed',
            resource='webhook',
            changes=webhook_data,
            metadata={'webhook_type': webhook_type}
        )
        
        # Log de auditoría
        audit_logger = WhatsAppLogger.get_logger('audit')
        audit_logger.info(
            f"Webhook procesado: {webhook_type}",
            extra={'extra_data': audit_entry}
        )


class SecurityExample:
    """
    Ejemplo de uso del sistema de logging de seguridad
    """
    
    def __init__(self):
        self.security_middleware = security_logging
    
    @security_logging.log_authentication_attempt
    def authenticate_user(self, api_key: str):
        """
        Ejemplo de autenticación con logging de seguridad
        """
        if not api_key or api_key != "valid_key":
            raise ValueError("Invalid API key")
        
        return {"authenticated": True, "user_id": "user123"}
    
    def log_suspicious_activity(self, ip_address: str, reason: str):
        """
        Ejemplo de logging de actividad sospechosa
        """
        self.security_middleware.log_unauthorized_access(
            ip_address, "/api/messages", reason
        )
    
    def log_rate_limit_exceeded(self, ip_address: str):
        """
        Ejemplo de logging de rate limiting
        """
        self.security_middleware.log_rate_limit_hit(
            ip_address, "/api/messages", 100
        )


async def demonstrate_event_system():
    """
    Demuestra el uso del sistema de eventos
    """
    print("\n=== Demostración del Sistema de Eventos ===")
    
    # Usar helpers para eventos comunes
    await log_whatsapp_message_sent(
        phone_number="+1234567890",
        message_id="msg_demo_001",
        message_type="text",
        template_name=None
    )
    
    await log_webhook_received(
        webhook_type="message_status",
        payload={"status": "delivered", "message_id": "msg_demo_001"}
    )
    
    await log_api_performance(
        endpoint="/api/messages",
        method="POST", 
        response_time_ms=150.5,
        status_code=200
    )
    
    # Esperar a que se procesen los eventos
    await asyncio.sleep(0.1)
    
    print("Eventos publicados y procesados exitosamente")


def demonstrate_structured_logging():
    """
    Demuestra el uso de logging estructurado
    """
    print("\n=== Demostración de Logging Estructurado ===")
    
    # Configurar sistema de logging
    WhatsAppLogger.configure_logging(
        log_level='INFO',
        environment='development'
    )
    
    # Obtener loggers específicos
    api_logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
    webhook_logger = WhatsAppLogger.get_logger(WhatsAppLogger.WEBHOOK_LOGGER)
    security_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SECURITY_LOGGER)
    
    # Ejemplos de logging estructurado
    api_logger.info(
        "API endpoint called",
        extra={'extra_data': {
            'endpoint': '/api/messages',
            'method': 'POST',
            'user_id': 'user123',
            'request_id': 'req_001'
        }}
    )
    
    webhook_logger.info(
        "Webhook processed",
        extra={'extra_data': {
            'webhook_type': 'message_status',
            'processing_time_ms': 45.2,
            'success': True
        }}
    )
    
    security_logger.warning(
        "Multiple failed authentication attempts",
        extra={'extra_data': {
            'ip_address': '192.168.1.100',
            'attempts': 5,
            'time_window': '5_minutes',
            'action_taken': 'rate_limited'
        }}
    )
    
    print("Logging estructurado completado")


def demonstrate_decorators():
    """
    Demuestra el uso de decoradores de logging
    """
    print("\n=== Demostración de Decoradores de Logging ===")
    
    @log_execution_time()
    def slow_operation():
        """Operación simulada lenta"""
        time.sleep(0.1)
        return "Operación completada"
    
    @log_api_call()
    def api_endpoint_simulation():
        """Simulación de endpoint de API"""
        return {"success": True, "data": "response_data"}
    
    # Ejecutar operaciones con decoradores
    result1 = slow_operation()
    result2 = api_endpoint_simulation()
    
    print(f"Operación lenta: {result1}")
    print(f"API endpoint: {result2}")


def demonstrate_complete_workflow():
    """
    Demuestra un flujo completo de trabajo con logging
    """
    print("\n=== Demostración de Flujo Completo ===")
    
    # Crear instancia del servicio de ejemplo
    service = WhatsAppServiceExample()
    security = SecurityExample()
    
    try:
        # 1. Autenticación (con logging de seguridad)
        auth_result = security.authenticate_user("valid_key")
        print(f"Autenticación exitosa: {auth_result}")
        
        # 2. Envío de mensaje (con logging completo)
        message_result = service.send_message_example(
            phone_number="+1234567890",
            message="Hola! Este es un mensaje de prueba",
            message_type="text"
        )
        print(f"Mensaje enviado: {message_result}")
        
        # 3. Guardado en base de datos
        service.save_message_to_db_example({
            'message_id': message_result['message_id'],
            'phone_number': '+1234567890',
            'message': 'Hola! Este es un mensaje de prueba'
        })
        print("Mensaje guardado en base de datos")
        
        # 4. Procesamiento de webhook de confirmación
        service.process_webhook_example({
            'type': 'message_status',
            'message_id': message_result['message_id'],
            'phone_number': '+1234567890',
            'status': 'delivered'
        })
        print("Webhook procesado")
        
    except Exception as e:
        print(f"Error en el flujo: {e}")
        
    # Ejemplo de actividad sospechosa
    security.log_suspicious_activity("192.168.1.100", "Multiple failed requests")
    security.log_rate_limit_exceeded("192.168.1.100")


def main():
    """
    Función principal que ejecuta todos los ejemplos
    """
    print("🔧 Iniciando demostración del sistema de logging y eventos")
    
    # Configurar logging
    demonstrate_structured_logging()
    
    # Demostrar decoradores
    demonstrate_decorators()
    
    # Demostrar flujo completo
    demonstrate_complete_workflow()
    
    # Demostrar sistema de eventos (asíncrono)
    print("\n⚡ Ejecutando demostración de eventos asíncronos...")
    asyncio.run(demonstrate_event_system())
    
    print("\n✅ Demostración completada exitosamente!")
    print("\nRevisa los archivos de log en el directorio 'logs/' para ver los resultados.")


if __name__ == "__main__":
    main()
