#!/usr/bin/env python3
"""
Test específico para verificar el manejo correcto de timestamps en webhooks
"""
import sys
from pathlib import Path
import json
from datetime import datetime, timezone

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

from entrypoint import create_app
from app.services.webhook_processor import WebhookProcessor
from database.models import Message


def test_timestamp_handling():
    """Prueba que el timestamp del webhook se aplique correctamente"""
    
    # Timestamp específico para testing (22 Agosto 2025, 12:30:45 UTC)
    test_timestamp = "1724330445"
    expected_datetime = datetime.fromtimestamp(int(test_timestamp), timezone.utc)
    
    # Payload con timestamp específico
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "136308692891691",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "59167028778",
                        "phone_number_id": "591497177388140"
                    },
                    "messages": [{
                        "from": "59167028778",
                        "id": f"test_timestamp_{test_timestamp}",  # ID único para este test
                        "timestamp": test_timestamp,
                        "text": {"body": "Test timestamp"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    print("🕐 Prueba de manejo de timestamps en webhooks")
    print(f"Timestamp de prueba: {test_timestamp}")
    print(f"Fecha esperada: {expected_datetime}")
    print()
    
    # Crear aplicación Flask
    app = create_app()
    
    with app.app_context():
        # Procesar webhook
        webhook_processor = WebhookProcessor()
        
        print("📤 Procesando webhook...")
        result = webhook_processor.process_webhook(webhook_payload)
        
        if result:
            print("✅ Webhook procesado exitosamente")
            
            # Verificar que el mensaje se guardó con el timestamp correcto
            message_id = webhook_payload['entry'][0]['changes'][0]['value']['messages'][0]['id']
            
            # Buscar el mensaje en la BD
            message = Message.query.filter_by(whatsapp_message_id=message_id).first()
            
            if message:
                print(f"✅ Mensaje encontrado en BD:")
                print(f"   ID: {message.whatsapp_message_id}")
                print(f"   Created at: {message.created_at}")
                print(f"   Expected:   {expected_datetime}")
                
                # Verificar timestamp (con tolerancia de 1 segundo)
                time_diff = abs((message.created_at.replace(tzinfo=timezone.utc) - expected_datetime).total_seconds())
                
                if time_diff <= 1:
                    print("✅ Timestamp aplicado correctamente")
                    return True
                else:
                    print(f"❌ Timestamp incorrecto - diferencia: {time_diff}s")
                    return False
            else:
                print("❌ Mensaje no encontrado en BD")
                return False
        else:
            print("❌ Error procesando webhook")
            return False


def test_timestamp_edge_cases():
    """Prueba casos extremos de timestamps"""
    
    print("\n🧪 Probando casos extremos de timestamps")
    
    test_cases = [
        ("timestamp_invalido", "invalid_timestamp", "Timestamp inválido"),
        ("timestamp_futuro", "2000000000", "Timestamp futuro"),
        ("timestamp_vacio", "", "Timestamp vacío"),
        ("timestamp_none", None, "Sin timestamp")
    ]
    
    app = create_app()
    
    for i, (test_name, timestamp_val, description) in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {description} ---")
        
        with app.app_context():
            # Crear payload de prueba
            webhook_payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "id": "136308692891691",
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "59167028778",
                                "phone_number_id": "591497177388140"
                            },
                            "messages": [{
                                "from": "59167028778",
                                "id": f"test_{test_name}",
                                "text": {"body": f"Test {description}"},
                                "type": "text"
                            }]
                        },
                        "field": "messages"
                    }]
                }]
            }
            
            # Agregar timestamp si no es None
            if timestamp_val is not None:
                webhook_payload['entry'][0]['changes'][0]['value']['messages'][0]['timestamp'] = timestamp_val
            
            try:
                webhook_processor = WebhookProcessor()
                result = webhook_processor.process_webhook(webhook_payload)
                
                if result:
                    print(f"✅ {description}: Manejado correctamente")
                else:
                    print(f"❌ {description}: Error en procesamiento")
                    
            except Exception as e:
                print(f"🚨 {description}: Excepción - {e}")


if __name__ == "__main__":
    print("🧪 Testing de timestamps en webhooks")
    print("=" * 50)
    
    # Test principal
    success = test_timestamp_handling()
    
    # Tests de casos extremos
    test_timestamp_edge_cases()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Todos los tests principales pasaron")
    else:
        print("❌ Algunos tests fallaron")
