#!/usr/bin/env python3
"""
Test para el endpoint de envío de mensajes de contactos (vCard)
Prueba el endpoint POST /v1/messages/contacts
"""
import requests
import json
from datetime import datetime

def test_contacts_endpoint():
    """
    Prueba el endpoint de envío de mensajes de contactos
    """
    # Configuración de la prueba
    BASE_URL = "http://localhost:5000"
    API_KEY = "dev-api-key"
    
    # Headers para la petición
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("👥 Iniciando prueba del endpoint de contactos...")
    print(f"📡 URL base: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY}")
    print("-" * 60)
    
    # Caso 1: Contacto básico (solo nombre y teléfono)
    print("\n📞 Caso 1: Contacto básico (solo nombre y teléfono)")
    contact_basic = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Juan Pérez",
                    "first_name": "Juan",
                    "last_name": "Pérez"
                },
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "CELL",
                        "wa_id": "5491123456789"
                    }
                ]
            }
        ],
        "messaging_line_id": 1
    }
    
    try:
        print(f"📤 Enviando: {json.dumps(contact_basic, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/contacts",
            headers=headers,
            json=contact_basic,
            timeout=10
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Caso 1: EXITOSO - Contacto básico enviado")
        else:
            print(f"❌ Caso 1: FALLÓ - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Caso 1: ERROR - {str(e)}")
    
    print("\n" + "-" * 60)
    
    # Caso 2: Contacto completo (información empresarial)
    print("\n💼 Caso 2: Contacto completo (información empresarial)")
    contact_complete = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "María García",
                    "first_name": "María",
                    "last_name": "García",
                    "prefix": "Lic."
                },
                "phones": [
                    {
                        "phone": "+5491155667788",
                        "type": "CELL",
                        "wa_id": "5491155667788"
                    },
                    {
                        "phone": "+541143334444",
                        "type": "WORK"
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
                    "department": "Marketing Digital",
                    "title": "Gerente de Marketing"
                },
                "addresses": [
                    {
                        "street": "Av. Corrientes 1234, Piso 8",
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
                        "url": "https://www.linkedin.com/in/mariagarcia",
                        "type": "WORK"
                    }
                ]
            }
        ],
        "messaging_line_id": 1
    }
    
    try:
        print(f"📤 Enviando: {json.dumps(contact_complete, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/contacts",
            headers=headers,
            json=contact_complete,
            timeout=10
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Caso 2: EXITOSO - Contacto completo enviado")
        else:
            print(f"❌ Caso 2: FALLÓ - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Caso 2: ERROR - {str(e)}")
    
    print("\n" + "-" * 60)
    
    # Caso 3: Múltiples contactos (equipo de trabajo)
    print("\n👥 Caso 3: Múltiples contactos (equipo de trabajo)")
    multiple_contacts = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "Ana López",
                    "first_name": "Ana",
                    "last_name": "López"
                },
                "phones": [
                    {
                        "phone": "+5491166778899",
                        "type": "CELL",
                        "wa_id": "5491166778899"
                    }
                ],
                "emails": [
                    {
                        "email": "ana.lopez@empresa.com",
                        "type": "WORK"
                    }
                ],
                "org": {
                    "company": "Tech Solutions SA",
                    "title": "Desarrolladora Senior"
                }
            },
            {
                "name": {
                    "formatted_name": "Carlos Ruiz",
                    "first_name": "Carlos",
                    "last_name": "Ruiz"
                },
                "phones": [
                    {
                        "phone": "+5491177889900",
                        "type": "CELL",
                        "wa_id": "5491177889900"
                    }
                ],
                "emails": [
                    {
                        "email": "carlos.ruiz@empresa.com",
                        "type": "WORK"
                    }
                ],
                "org": {
                    "company": "Tech Solutions SA",
                    "title": "Project Manager"
                }
            },
            {
                "name": {
                    "formatted_name": "Laura Martín",
                    "first_name": "Laura",
                    "last_name": "Martín"
                },
                "phones": [
                    {
                        "phone": "+5491188990011",
                        "type": "CELL",
                        "wa_id": "5491188990011"
                    }
                ],
                "emails": [
                    {
                        "email": "laura.martin@empresa.com",
                        "type": "WORK"
                    }
                ],
                "org": {
                    "company": "Tech Solutions SA",
                    "title": "UX Designer"
                }
            }
        ]
    }
    
    try:
        print(f"📤 Enviando: {json.dumps(multiple_contacts, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/contacts",
            headers=headers,
            json=multiple_contacts,
            timeout=10
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Caso 3: EXITOSO - Múltiples contactos enviados")
        else:
            print(f"❌ Caso 3: FALLÓ - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Caso 3: ERROR - {str(e)}")
    
    print("\n" + "-" * 60)
    
    # Casos de validación (errores esperados)
    print("\n🔍 Casos de validación (errores esperados):")
    
    # Error 1: Array de contactos vacío
    print("\n❌ Error 1: Array de contactos vacío")
    error_case_1 = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/contacts",
            headers=headers,
            json=error_case_1,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Error 2: Contacto sin nombre
    print("\n❌ Error 2: Contacto sin nombre")
    error_case_2 = {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "phones": [
                    {
                        "phone": "+5491123456789",
                        "type": "CELL"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/contacts",
            headers=headers,
            json=error_case_2,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Error 3: Tipo de mensaje incorrecto
    print("\n❌ Error 3: Tipo de mensaje incorrecto")
    error_case_3 = {
        "to": "5491123456789",
        "type": "text",  # Tipo incorrecto
        "contacts": [
            {
                "name": {
                    "formatted_name": "Test User"
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/messages/contacts",
            headers=headers,
            json=error_case_3,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error esperado detectado correctamente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba del endpoint de contactos completada")
    print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_contacts_endpoint()
