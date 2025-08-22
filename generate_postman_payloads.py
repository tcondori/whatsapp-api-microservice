#!/usr/bin/env python3
"""
Generador de payloads para Postman - Endpoint de Contactos
Genera JSON limpios listos para copiar y pegar en Postman
"""

import json

def generate_basic_contact():
    return {
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

def generate_complete_contact():
    return {
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

def generate_multiple_contacts():
    return {
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

def generate_business_contact():
    return {
        "to": "5491123456789",
        "type": "contacts",
        "contacts": [
            {
                "name": {
                    "formatted_name": "TechCorp Solutions",
                    "first_name": "TechCorp",
                    "last_name": "Solutions"
                },
                "phones": [
                    {
                        "phone": "+5411044445555",
                        "type": "WORK"
                    },
                    {
                        "phone": "+5411044446666",
                        "type": "WORK"
                    }
                ],
                "emails": [
                    {
                        "email": "contacto@techcorp.com.ar",
                        "type": "WORK"
                    },
                    {
                        "email": "ventas@techcorp.com.ar",
                        "type": "WORK"
                    }
                ],
                "org": {
                    "company": "TechCorp Solutions SA",
                    "department": "Oficina Central",
                    "title": "Empresa de Desarrollo"
                },
                "addresses": [
                    {
                        "street": "Av. Santa Fe 2020, Piso 15",
                        "city": "Buenos Aires",
                        "state": "CABA",
                        "zip": "C1123AAB",
                        "country": "Argentina",
                        "country_code": "AR",
                        "type": "WORK"
                    }
                ],
                "urls": [
                    {
                        "url": "https://www.techcorp.com.ar",
                        "type": "WORK"
                    },
                    {
                        "url": "https://www.linkedin.com/company/techcorp",
                        "type": "WORK"
                    }
                ]
            }
        ]
    }

def print_payload(name, payload):
    print(f"\n{'='*60}")
    print(f"📋 {name}")
    print('='*60)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

def print_postman_config():
    print("🚀 CONFIGURACIÓN PARA POSTMAN")
    print("="*60)
    print("URL: http://127.0.0.1:5000/v1/messages/contacts")
    print("Method: POST")
    print("\nHeaders:")
    print("Content-Type: application/json")
    print("X-API-Key: dev-api-key")
    print("\nBody: raw (JSON)")

if __name__ == "__main__":
    print_postman_config()
    
    # Generar todos los payloads
    payloads = [
        ("CASO 1: Contacto Básico", generate_basic_contact()),
        ("CASO 2: Contacto Completo", generate_complete_contact()),
        ("CASO 3: Múltiples Contactos", generate_multiple_contacts()),
        ("CASO 4: Contacto Empresarial", generate_business_contact())
    ]
    
    for name, payload in payloads:
        print_payload(name, payload)
    
    print(f"\n{'='*60}")
    print("💡 INSTRUCCIONES:")
    print("1. Copia cualquiera de los JSONs de arriba")
    print("2. Pégalo en el Body de Postman (raw/JSON)")
    print("3. Configura los headers mostrados")
    print("4. Envía la request")
    print("="*60)
