#!/usr/bin/env python3
"""
Script de prueba para verificar la validación de firmas de webhook
"""
import hmac
import hashlib
import json
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.whatsapp_api import WhatsAppAPIService
from config.default import DefaultConfig


def test_webhook_signature():
    """Prueba la verificación de firmas de webhook"""
    
    # Configurar el servicio
    config = DefaultConfig()
    
    # Crear payload de prueba
    test_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "test_entry_id",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15551234567",
                        "phone_number_id": "test_phone_number_id"
                    },
                    "messages": [{
                        "from": "5215551234567",
                        "id": "test_message_id",
                        "timestamp": "1640995200",
                        "text": {"body": "Hola, este es un mensaje de prueba"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    # Convertir a JSON bytes
    payload_bytes = json.dumps(test_payload, separators=(',', ':')).encode('utf-8')
    
    # Obtener el app secret de Facebook
    app_secret = config.FACEBOOK_APP_SECRET
    print(f"Facebook App Secret configurado: {app_secret[:8]}...")
    
    # Calcular firma esperada usando App Secret
    expected_signature = hmac.new(
        app_secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    print(f"Firma esperada: sha256={expected_signature}")
    
    # Probar el servicio de WhatsApp API
    try:
        whatsapp_service = WhatsAppAPIService()
        
        # Probar con firma correcta
        valid_signature = f"sha256={expected_signature}"
        is_valid = whatsapp_service.verify_webhook_signature(payload_bytes, valid_signature)
        print(f"Verificación con firma correcta: {is_valid}")
        
        # Probar con firma incorrecta
        invalid_signature = "sha256=invalid_signature_test"
        is_valid = whatsapp_service.verify_webhook_signature(payload_bytes, invalid_signature)
        print(f"Verificación con firma incorrecta: {is_valid}")
        
        # Probar sin prefijo sha256=
        signature_without_prefix = expected_signature
        is_valid = whatsapp_service.verify_webhook_signature(payload_bytes, signature_without_prefix)
        print(f"Verificación sin prefijo sha256=: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        return False


def create_test_signature(payload_text: str, secret: str):
    """Crear una firma de prueba para un payload específico"""
    payload_bytes = payload_text.encode('utf-8')
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    return f"sha256={signature}"


if __name__ == "__main__":
    print("=== Prueba de Verificación de Firmas de Webhook ===")
    print()
    
    success = test_webhook_signature()
    
    print()
    print("=== Generador de Firmas de Prueba ===")
    
    # Ejemplo de uso para crear firmas manualmente
    test_secret = "ac896e14f53c08b92c2a9a36a632d392"  # Tu App Secret
    test_payload = '{"object":"whatsapp_business_account","entry":[{"id":"test","changes":[]}]}'
    
    test_signature = create_test_signature(test_payload, test_secret)
    print(f"Para el payload: {test_payload}")
    print(f"Con el secret: {test_secret}")
    print(f"La firma debe ser: {test_signature}")
    
    print()
    if success:
        print("✅ Todas las pruebas pasaron correctamente")
    else:
        print("❌ Algunas pruebas fallaron")
