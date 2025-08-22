#!/usr/bin/env python3
"""
Script de pruebas completas para endpoint de contactos - WhatsApp API
Casos de prueba: básico, completo y múltiples contactos
"""

import json
import requests
from pprint import pprint

# Configuración
BASE_URL = "http://127.0.0.1:5000"
ENDPOINT = "/v1/messages/contacts"

def send_contact_request(payload, test_name):
    """Envía una petición de contacto y maneja la respuesta"""
    print(f"\n📤 {test_name}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "dev-api-key"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ¡Éxito!")
            response_data = response.json()
            pprint(response_data)
            return True
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                pprint(error_data)
            except:
                print("Respuesta:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_basic_contact():
    """Prueba contacto básico"""
    payload = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Juan Perez",
                    "first_name": "Juan",
                    "last_name": "Perez"
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "WORK",
                        "wa_id": "5491123456789"
                    }
                ]
            }
        ]
    }
    
    return send_contact_request(payload, "CASO 1: Contacto básico")

def test_complete_contact():
    """Prueba contacto completo con toda la información"""
    payload = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Maria Garcia",
                    "first_name": "Maria",
                    "last_name": "Garcia",
                    "middle_name": "Elena",
                    "suffix": "Ing.",
                    "prefix": "Dra."
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "WORK",
                        "wa_id": "5491123456789"
                    },
                    {
                        "phone": "+5491187654321",
                        "type": "HOME"
                    }
                ],
                "emails": [
                    {
                        "email": "maria.garcia@empresa.com",
                        "type": "WORK"
                    },
                    {
                        "email": "maria.personal@gmail.com",
                        "type": "HOME"
                    }
                ],
                "org": {
                    "company": "Tech Solutions SA",
                    "department": "Desarrollo",
                    "title": "Arquitecta de Software"
                },
                "addresses": [
                    {
                        "street": "Av. Corrientes 1234",
                        "city": "Buenos Aires",
                        "state": "CABA",
                        "zip": "C1043AAZ",
                        "country": "Argentina",
                        "country_code": "AR",
                        "type": "WORK"
                    }
                ],
                "urls": [
                    {
                        "url": "https://www.techsolutions.com.ar",
                        "type": "WORK"
                    },
                    {
                        "url": "https://linkedin.com/in/mariagarcia",
                        "type": "HOME"
                    }
                ]
            }
        ]
    }
    
    return send_contact_request(payload, "CASO 2: Contacto completo")

def test_multiple_contacts():
    """Prueba múltiples contactos (equipo)"""
    payload = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Ana Lopez",
                    "first_name": "Ana",
                    "last_name": "Lopez"
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "WORK",
                        "wa_id": "5491123456789"
                    }
                ],
                "org": {
                    "company": "DevTeam SA",
                    "department": "Frontend",
                    "title": "Desarrolladora Senior"
                }
            },
            {
                "name": {
                    "formatted_name": "Carlos Rodriguez",
                    "first_name": "Carlos",
                    "last_name": "Rodriguez"
                },
                "phones": [
                    {
                        "phone": "+5491187654321",
                        "type": "WORK",
                        "wa_id": "5491187654321"
                    }
                ],
                "org": {
                    "company": "DevTeam SA",
                    "department": "Backend",
                    "title": "Arquitecto de Software"
                }
            },
            {
                "name": {
                    "formatted_name": "Luis Martinez",
                    "first_name": "Luis",
                    "last_name": "Martinez"
                },
                "phones": [
                    {
                        "phone": "+5491155443322",
                        "type": "WORK",
                        "wa_id": "5491155443322"
                    }
                ],
                "org": {
                    "company": "DevTeam SA",
                    "department": "DevOps",
                    "title": "Especialista en Infraestructura"
                }
            }
        ]
    }
    
    return send_contact_request(payload, "CASO 3: Múltiples contactos (equipo)")

def check_server():
    """Verifica que el servidor esté funcionando"""
    print("🌐 Verificando servidor...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Servidor activo en {BASE_URL}")
        return True
    except:
        print(f"❌ Servidor no responde en {BASE_URL}")
        print("   Asegúrate de que esté corriendo: python run_server.py")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBAS ENDPOINT DE CONTACTOS")
    print("=" * 60)
    
    if not check_server():
        exit(1)
    
    # Ejecutar todas las pruebas
    results = []
    results.append(test_basic_contact())
    results.append(test_complete_contact())
    results.append(test_multiple_contacts())
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    successful = sum(results)
    total = len(results)
    print(f"✅ Exitosas: {successful}/{total}")
    print(f"❌ Fallidas: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 ¡Todas las pruebas pasaron!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print(f"\n💡 Para ver endpoints disponibles:")
    print(f"   curl {BASE_URL}")
