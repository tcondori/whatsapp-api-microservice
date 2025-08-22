#!/usr/bin/env python3
"""
Test para mensaje de plantilla de cumpleaños con imagen y variable de nombre
"""
import json
import requests
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
PHONE_NUMBER = "5491123456789"  # Cambia por tu número de prueba

def test_template_completo():
    """Test con formato oficial completo de Meta"""
    print("🎂 TESTING: Plantilla de cumpleaños - Formato completo")
    print("=" * 60)
    
    # Payload oficial completo
    payload = {
        "to": PHONE_NUMBER,
        "type": "template",
        "messaging_line_id": 1,
        "template": {
            "name": "cumpleanos_template",  # Cambia por el nombre real de tu plantilla
            "language": {
                "code": "es"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": "https://picsum.photos/800/600?random=birthday"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "María Fernanda"  # Cambia por el nombre que quieras
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/v1/messages/template",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ ¡Plantilla enviada exitosamente!")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_template_simplificado():
    """Test con formato simplificado"""
    print("\n🎂 TESTING: Plantilla de cumpleaños - Formato simplificado")
    print("=" * 60)
    
    # Payload simplificado
    payload = {
        "to": PHONE_NUMBER,
        "template_name": "cumpleanos_template",  # Cambia por el nombre real
        "language_code": "es",
        "messaging_line_id": 1,
        "header_media": {
            "type": "image",
            "image": {
                "link": "https://images.unsplash.com/photo-1464207687429-7505649dae38?w=800&h=600&fit=crop"
            }
        },
        "body_variables": [
            "Carlos Alberto"  # Cambia por el nombre que quieras
        ]
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/v1/messages/template/media",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ ¡Plantilla simplificada enviada exitosamente!")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_diferentes_nombres():
    """Test con diferentes nombres para validar variables"""
    print("\n🎂 TESTING: Diferentes nombres de cumpleañeros")
    print("=" * 60)
    
    nombres = [
        "Ana María",
        "José Luis",
        "Sofía Elena",
        "Roberto Carlos"
    ]
    
    for i, nombre in enumerate(nombres):
        print(f"\n📧 Enviando a: {nombre}")
        
        payload = {
            "to": PHONE_NUMBER,
            "template_name": "cumpleanos_template",
            "language_code": "es",
            "messaging_line_id": 1,
            "header_media": {
                "type": "image",
                "image": {
                    "link": f"https://picsum.photos/800/600?random={i+10}"
                }
            },
            "body_variables": [nombre]
        }
        
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{BASE_URL}/api/v1/messages/template/media",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('data', {}).get('whatsapp_message_id', 'N/A')
                print(f"✅ Enviado a {nombre} - ID: {message_id}")
            else:
                print(f"❌ Error para {nombre}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error enviando a {nombre}: {e}")

def mostrar_ejemplos_json():
    """Muestra ejemplos de JSON para copiar"""
    print("\n📋 EJEMPLOS DE JSON PARA COPIAR")
    print("=" * 60)
    
    print("\n1️⃣ FORMATO OFICIAL COMPLETO:")
    ejemplo_completo = {
        "to": "TU_NUMERO_AQUI",
        "type": "template",
        "messaging_line_id": 1,
        "template": {
            "name": "TU_TEMPLATE_NAME_AQUI",
            "language": {
                "code": "es"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": "https://tu-imagen.com/cumpleanos.jpg"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "NOMBRE_DEL_CUMPLEAÑERO"
                        }
                    ]
                }
            ]
        }
    }
    print(json.dumps(ejemplo_completo, indent=2, ensure_ascii=False))
    
    print("\n2️⃣ FORMATO SIMPLIFICADO:")
    ejemplo_simple = {
        "to": "TU_NUMERO_AQUI",
        "template_name": "TU_TEMPLATE_NAME_AQUI",
        "language_code": "es",
        "messaging_line_id": 1,
        "header_media": {
            "type": "image",
            "image": {
                "link": "https://tu-imagen.com/cumpleanos.jpg"
            }
        },
        "body_variables": [
            "NOMBRE_DEL_CUMPLEAÑERO"
        ]
    }
    print(json.dumps(ejemplo_simple, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print(f"🎂 TEST DE PLANTILLA DE CUMPLEAÑOS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Mostrar ejemplos primero
    mostrar_ejemplos_json()
    
    # Ejecutar tests
    test_template_completo()
    test_template_simplificado() 
    test_diferentes_nombres()
    
    print("\n" + "=" * 60)
    print("🎉 TESTS COMPLETADOS")
    print("\n📝 INSTRUCCIONES:")
    print("1. Cambia 'cumpleanos_template' por el nombre real de tu plantilla")
    print("2. Cambia el número de teléfono por uno real")
    print("3. Cambia la URL de la imagen por una válida")
    print("4. Asegúrate de que tu plantilla esté aprobada en Meta")
