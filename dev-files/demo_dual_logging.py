"""
Demostración del sistema de logging dual: terminal + archivos
Los logs aparecerán simultáneamente en terminal y se guardarán en archivos
"""

import os
import sys
from pathlib import Path

# Configurar el path para importar las clases
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.logger import WhatsAppLogger

def demo_dual_logging():
    """
    Demuestra el funcionamiento del sistema de logging dual
    """
    print("=" * 60)
    print("DEMO: Sistema de Logging Dual (Terminal + Archivos)")
    print("=" * 60)
    print()
    print("Los logs aparecerán SIMULTÁNEAMENTE en:")
    print("1. Terminal (tiempo real con colores)")
    print("2. Archivos en /logs/ (formato JSON estructurado)")
    print()
    print("Iniciando demo...")
    print("-" * 60)
    
    # Configurar logging dual
    WhatsAppLogger.configure_logging(
        log_level='INFO',
        environment='development',
        use_date_structure=False,  # Usar sistema simple por ahora
        dual_output=True           # HABILITADO: logs en terminal + archivos
    )
    
    # Obtener diferentes loggers
    api_logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
    webhook_logger = WhatsAppLogger.get_logger(WhatsAppLogger.WEBHOOK_LOGGER)
    service_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SERVICE_LOGGER)
    
    print("\n1. Simulando logs de API...")
    api_logger.info("API endpoint called: /send_message", extra={
        'extra_data': {
            'endpoint': '/send_message',
            'method': 'POST',
            'phone_number': '593***99',
            'message_type': 'text',
            'status_code': 200
        }
    })
    
    api_logger.warning("Rate limit approaching for user", extra={
        'extra_data': {
            'phone_number': '593***99',
            'requests_count': 45,
            'limit': 50,
            'time_window': '1_minute'
        }
    })
    
    print("\n2. Simulando logs de webhook...")
    webhook_logger.info("Webhook received from WhatsApp", extra={
        'extra_data': {
            'webhook_type': 'message',
            'phone_number': '593***99',
            'message_id': 'wamid.abc123',
            'message_type': 'text'
        }
    })
    
    print("\n3. Simulando logs de servicios...")
    service_logger.info("Message processing completed", extra={
        'extra_data': {
            'phone_number': '593***99',
            'execution_time_ms': 145.67,
            'chatbot_response': True,
            'template_used': 'greeting'
        }
    })
    
    service_logger.error("WhatsApp API request failed", extra={
        'extra_data': {
            'phone_number': '593***99',
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'retry_attempt': 2,
            'next_retry_in': '30_seconds'
        }
    })
    
    print("\n" + "-" * 60)
    print("Demo completado!")
    print()
    print("Verifica los archivos de log generados en:")
    print("- logs/api.log")
    print("- logs/webhooks.log") 
    print("- logs/services.log")
    print("- logs/whatsapp_api.log (general)")
    print()
    print("Los mismos logs que viste en terminal están guardados en los archivos.")

if __name__ == "__main__":
    demo_dual_logging()
