"""
Test para endpoints de mensajes interactivos de WhatsApp Business API
Prueba los nuevos endpoints para botones de respuesta y listas interactivas
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
API_KEY = "dev-api-key"
TEST_PHONE = "5491123456789"

def test_interactive_endpoints():
    """Función principal para probar todos los casos de mensajes interactivos"""
    
    print("🎯 Iniciando prueba de endpoints interactivos...")
    print(f"📡 URL base: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY}")
    print("-" * 60)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Test 1: Mensaje con botones básico
    print("\n🔘 Caso 1: Mensaje con botones básico")
    payload_buttons_basic = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "¿Te gustó nuestro servicio?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn_si",
                            "title": "✅ Sí"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn_no",
                            "title": "❌ No"
                        }
                    }
                ]
            }
        },
        "messaging_line_id": 1
    }
    
    test_endpoint("/v1/messages/interactive/buttons", payload_buttons_basic, headers, "Botones básico")
    
    # Test 2: Mensaje con botones completo (header, body, footer)
    print("\n🔘 Caso 2: Mensaje con botones completo")
    payload_buttons_complete = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "¿Cómo podemos ayudarte?"
            },
            "body": {
                "text": "Selecciona una de las siguientes opciones para continuar:"
            },
            "footer": {
                "text": "Responde tocando un botón"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn_info",
                            "title": "ℹ️ Información"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn_soporte",
                            "title": "🛠️ Soporte"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn_ventas",
                            "title": "💰 Ventas"
                        }
                    }
                ]
            }
        }
    }
    
    test_endpoint("/v1/messages/interactive/buttons", payload_buttons_complete, headers, "Botones completo")
    
    # Test 3: Lista interactiva básica
    print("\n📋 Caso 3: Lista interactiva básica")
    payload_list_basic = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "¿Qué te gustaría hacer hoy?"
            },
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Acciones Principales",
                        "rows": [
                            {
                                "id": "ver_productos",
                                "title": "Ver Productos",
                                "description": "Explora nuestro catálogo completo"
                            },
                            {
                                "id": "hacer_pedido",
                                "title": "Hacer Pedido",
                                "description": "Realiza tu pedido ahora mismo"
                            },
                            {
                                "id": "seguimiento",
                                "title": "Seguimiento",
                                "description": "Rastrea tu pedido actual"
                            }
                        ]
                    }
                ]
            }
        },
        "messaging_line_id": 1
    }
    
    test_endpoint("/v1/messages/interactive/list", payload_list_basic, headers, "Lista básica")
    
    # Test 4: Lista interactiva completa con múltiples secciones
    print("\n📋 Caso 4: Lista completa con múltiples secciones")
    payload_list_complete = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Nuestros Servicios"
            },
            "body": {
                "text": "Elige el servicio que te interesa para obtener más información detallada:"
            },
            "footer": {
                "text": "Toca para ver las opciones disponibles"
            },
            "action": {
                "button": "Ver Servicios",
                "sections": [
                    {
                        "title": "Servicios Principales",
                        "rows": [
                            {
                                "id": "srv_consulta",
                                "title": "Consulta Gratuita",
                                "description": "Agenda una consulta sin costo inicial"
                            },
                            {
                                "id": "srv_desarrollo",
                                "title": "Desarrollo Web",
                                "description": "Sitios web y aplicaciones personalizadas"
                            },
                            {
                                "id": "srv_marketing",
                                "title": "Marketing Digital",
                                "description": "Campañas y estrategias digitales efectivas"
                            }
                        ]
                    },
                    {
                        "title": "Soporte y Ayuda",
                        "rows": [
                            {
                                "id": "sup_tecnico",
                                "title": "Soporte Técnico",
                                "description": "Ayuda especializada con problemas técnicos"
                            },
                            {
                                "id": "sup_facturacion",
                                "title": "Facturación",
                                "description": "Consultas sobre pagos y facturas"
                            },
                            {
                                "id": "sup_general",
                                "title": "Ayuda General",
                                "description": "Información y consultas generales"
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    test_endpoint("/v1/messages/interactive/list", payload_list_complete, headers, "Lista completa")
    
    # Tests de validación (errores esperados)
    print("\n🔍 Casos de validación (errores esperados):")
    
    # Error 1: Más de 3 botones
    print("\n❌ Error 1: Más de 3 botones")
    payload_error_buttons = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Prueba con 4 botones"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "btn1", "title": "Opción 1"}},
                    {"type": "reply", "reply": {"id": "btn2", "title": "Opción 2"}},
                    {"type": "reply", "reply": {"id": "btn3", "title": "Opción 3"}},
                    {"type": "reply", "reply": {"id": "btn4", "title": "Opción 4"}}
                ]
            }
        }
    }
    
    test_error_endpoint("/v1/messages/interactive/buttons", payload_error_buttons, headers, "Más de 3 botones")
    
    # Error 2: Título de botón muy largo
    print("\n❌ Error 2: Título de botón muy largo")
    payload_error_long_title = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Botón con título largo"},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn_largo",
                            "title": "Este título es muy largo para un botón de WhatsApp"
                        }
                    }
                ]
            }
        }
    }
    
    test_error_endpoint("/v1/messages/interactive/buttons", payload_error_long_title, headers, "Título muy largo")
    
    # Error 3: Lista con más de 10 opciones
    print("\n❌ Error 3: Lista con más de 10 opciones")
    rows_too_many = []
    for i in range(12):  # 12 opciones (excede el límite)
        rows_too_many.append({
            "id": f"option_{i}",
            "title": f"Opción {i+1}",
            "description": f"Descripción de la opción {i+1}"
        })
    
    payload_error_list = {
        "to": TEST_PHONE,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "Lista con demasiadas opciones"},
            "action": {
                "button": "Ver opciones",
                "sections": [{"title": "Muchas Opciones", "rows": rows_too_many}]
            }
        }
    }
    
    test_error_endpoint("/v1/messages/interactive/list", payload_error_list, headers, "Más de 10 opciones")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba de endpoints interactivos completada")
    print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_endpoint(endpoint, payload, headers, test_name):
    """Prueba un endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"📤 Enviando: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📥 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Contenido: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            print(f"✅ Caso {test_name}: EXITOSO")
        else:
            error_data = response.json() if response.content else {}
            print(f"📄 Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            print(f"❌ Caso {test_name}: ERROR HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout - El servidor tardó más de 10 segundos en responder")
        print(f"❌ Caso {test_name}: TIMEOUT")
    except requests.exceptions.RequestException as e:
        print(f"🚫 Error de conexión: {e}")
        print(f"❌ Caso {test_name}: ERROR DE CONEXIÓN")
    except json.JSONDecodeError:
        print(f"📄 Respuesta no JSON: {response.text[:200]}...")
        print(f"❌ Caso {test_name}: RESPUESTA INVÁLIDA")

def test_error_endpoint(endpoint, payload, headers, test_name):
    """Prueba un endpoint esperando un error"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
            error_data = response.json() if response.content else {}
            print(f"📄 Respuesta: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Se esperaba error 400, pero recibió {response.status_code}")
            
    except Exception as e:
        print(f"🚫 Error inesperado: {e}")

if __name__ == "__main__":
    test_interactive_endpoints()
