#!/usr/bin/env python3
"""
Script para probar el webhook con payload simulado
Simula el mensaje duplicado que está causando problemas
"""
import sys
from pathlib import Path
import json
import hmac
import hashlib
import os

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

from entrypoint import create_app
from app.services.webhook_processor import WebhookProcessor
from app.services.whatsapp_api import WhatsAppAPIService


def test_duplicate_message_handling():
    """Prueba el manejo de mensajes duplicados"""
    
    # Payload simulado basado en el error
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "136308692891691",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "59167028778",
                        "phone_number_id": "591497177388140"  # Este es el que aparece en el error
                    },
                    "messages": [{
                        "from": "59167028778",
                        "id": "wamid.HBgLNTkxNjcwMjg3NzgVAgASGCA1NDkyQUVGQTU5NDhENjM4NEY1NjM2MzVFNTlEQUE1MAA=",
                        "timestamp": "1724330827",  # timestamp del error
                        "text": {"body": "Hola"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    print("=== Prueba de manejo de mensajes duplicados ===")
    print(f"Mensaje ID a probar: {webhook_payload['entry'][0]['changes'][0]['value']['messages'][0]['id']}")
    print()
    
    # Crear aplicación Flask y usar su contexto
    app = create_app()
    
    with app.app_context():
        # Inicializar webhook processor
        webhook_processor = WebhookProcessor()
        
        # Procesar el webhook múltiples veces para simular duplicados
        for attempt in range(1, 4):
            print(f"--- Intento {attempt} ---")
            try:
                result = webhook_processor.process_webhook(webhook_payload)
                print(f"Resultado del intento {attempt}: {'✅ Exitoso' if result else '❌ Fallido'}")
            except Exception as e:
                print(f"Error en intento {attempt}: {e}")
            print()
    
    print("=== Fin de la prueba ===")


def test_webhook_signature():
    """Prueba la validación de firmas de webhook"""
    
    print("=== Prueba de validación de firmas ===")
    
    # Obtener App Secret del entorno
    app_secret = os.getenv('FACEBOOK_APP_SECRET')
    
    if not app_secret:
        print("❌ No se encontró FACEBOOK_APP_SECRET en las variables de entorno")
        return
    
    # Payload de prueba
    test_payload = '{"object":"whatsapp_business_account","entry":[]}'
    payload_bytes = test_payload.encode('utf-8')
    
    # Calcular firma esperada
    expected_signature = hmac.new(
        app_secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    print(f"App Secret configurado: {app_secret[:8]}...")
    print(f"Payload de prueba: {test_payload}")
    print(f"Firma calculada: sha256={expected_signature}")
    
    # Crear aplicación Flask y usar su contexto
    app = create_app()
    
    with app.app_context():
        try:
            whatsapp_service = WhatsAppAPIService()
            
            # Probar firma válida
            valid_signature = f"sha256={expected_signature}"
            is_valid = whatsapp_service.verify_webhook_signature(payload_bytes, valid_signature)
            print(f"Verificación con firma válida: {'✅ Válida' if is_valid else '❌ Inválida'}")
            
            # Probar firma inválida
            invalid_signature = "sha256=invalid_signature"
            is_valid = whatsapp_service.verify_webhook_signature(payload_bytes, invalid_signature)
            print(f"Verificación con firma inválida: {'✅ Válida' if is_valid else '❌ Inválida'}")
            
        except Exception as e:
            print(f"Error en prueba de firma: {e}")
    
    print("=== Fin de prueba de firmas ===")


if __name__ == "__main__":
    print("🧪 Iniciando pruebas de webhook...")
    print()
    
    # Probar validación de firmas
    test_webhook_signature()
    print()
    
    # Probar manejo de duplicados
    test_duplicate_message_handling()
    
    print("✅ Pruebas completadas")
