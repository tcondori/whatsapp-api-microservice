"""
Ejemplos de logging desde MÁS SIMPLE a más complejo
"""

from app.utils.logger import WhatsAppLogger

# Obtener logger
api_logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)

def ejemplo_logging_simple():
    """
    4 niveles de logging de simple a complejo
    """
    
    phone_number = "5491123456789"
    
    print("🔥 NIVEL 1: ULTRA SIMPLE - Solo texto")
    # ✅ MÁS SIMPLE - Solo texto básico
    api_logger.info(f"Mensaje enviado a {WhatsAppLogger._sanitize_phone(phone_number)}")
    
    
    print("\n📝 NIVEL 2: SIMPLE CON MÁS DATOS")
    # ✅ SIMPLE - Con algunos datos básicos
    api_logger.info(f"Mensaje de texto enviado a {WhatsAppLogger._sanitize_phone(phone_number)} - Estado: exitoso")
    
    
    print("\n📊 NIVEL 3: INTERMEDIO - Con algunos campos")
    # ✅ INTERMEDIO - Con algunos campos útiles
    api_logger.info(
        f"Mensaje enviado a {WhatsAppLogger._sanitize_phone(phone_number)}",
        extra={'extra_data': {
            'tipo': 'text',
            'estado': 'enviado'
        }}
    )
    
    
    print("\n🔬 NIVEL 4: COMPLETO - JSON estructurado")
    # ✅ COMPLETO - JSON completo (como teníamos antes)
    api_logger.info(
        "Mensaje de texto procesado",
        extra={'extra_data': {
            'phone_number_hash': WhatsAppLogger._sanitize_phone(phone_number),
            'message_type': 'text',
            'endpoint': '/v1/messages/text',
            'status': 'sent',
            'processing_time_ms': 145.2
        }}
    )


def logs_en_diferentes_situaciones():
    """
    Ejemplos de logs simples para diferentes casos
    """
    
    print("\n" + "="*50)
    print("📋 LOGS SIMPLES PARA DIFERENTES CASOS")
    print("="*50)
    
    # Caso 1: Éxito
    api_logger.info("✅ Mensaje de texto enviado exitosamente")
    
    # Caso 2: Con número
    api_logger.info("📤 Enviando mensaje a 549***6789")
    
    # Caso 3: Error simple
    api_logger.error("❌ Error: datos del mensaje faltantes")
    
    # Caso 4: Con ID de mensaje
    api_logger.info("📨 Mensaje creado con ID: msg_12345")
    
    # Caso 5: Con tiempo
    api_logger.info("⏱️ Mensaje procesado en 145ms")
    
    # Caso 6: Estado de validación
    api_logger.info("✔️ Datos del mensaje validados correctamente")


# Ejemplos de salida esperada:
"""
SALIDA EN LOS LOGS:

Nivel 1 (Ultra simple):
2025-08-26 15:47:39 - whatsapp_api - INFO - Mensaje enviado a 549***6789

Nivel 2 (Simple con más datos):  
2025-08-26 15:47:39 - whatsapp_api - INFO - Mensaje de texto enviado a 549***6789 - Estado: exitoso

Nivel 3 (Intermedio):
2025-08-26 15:47:39 - whatsapp_api - INFO - Mensaje enviado a 549***6789 | Data: {"tipo": "text", "estado": "enviado"}

Nivel 4 (Completo JSON):
2025-08-26 15:47:39 - whatsapp_api - INFO - Mensaje de texto procesado | Data: {"phone_number_hash": "549***6789", "message_type": "text", "endpoint": "/v1/messages/text", "status": "sent", "processing_time_ms": 145.2}
"""

if __name__ == "__main__":
    ejemplo_logging_simple()
    logs_en_diferentes_situaciones()
    
    print("\n💡 RECOMENDACIÓN:")
    print("Para empezar, usa NIVEL 1 (ultra simple)")
    print("Cuando necesites más información, cambia a NIVEL 2 o 3")
    print("NIVEL 4 solo para casos que requieren análisis automático")
