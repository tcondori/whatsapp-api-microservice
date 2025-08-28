# POSTMAN COLLECTION - ENDPOINT DE CONTACTOS
# WhatsApp Business API - Envío de Contactos

## CONFIGURACIÓN BÁSICA PARA POSTMAN

### URL Base:
```
http://127.0.0.1:5000
```

### Headers requeridos:
```
Content-Type: application/json
X-API-Key: dev-api-key
```

### Endpoint:
```
POST /v1/messages/contacts
```

---

## CASO 1: CONTACTO BÁSICO
### Información mínima requerida

```json
{
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
```

---

## CASO 2: CONTACTO COMPLETO
### Con toda la información posible

```json
{
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
```

---

## CASO 3: MÚLTIPLES CONTACTOS (EQUIPO)
### Hasta 20 contactos en un solo mensaje

```json
{
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
```

---

## CASO 4: CONTACTO EMPRESARIAL COMPLETO
### Para empresas con información detallada

```json
{
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
```

---

## PASOS PARA CONFIGURAR EN POSTMAN:

1. **Crear nueva request:**
   - Method: `POST`
   - URL: `http://127.0.0.1:5000/v1/messages/contacts`

2. **Configurar Headers:**
   ```
   Content-Type: application/json
   X-API-Key: dev-api-key
   ```

3. **En Body, seleccionar:**
   - `raw`
   - `JSON`

4. **Copiar y pegar cualquiera de los payloads de arriba**

5. **Click en Send**

---

## RESPUESTA ESPERADA:

```json
{
    "success": true,
    "message": "Mensaje de contactos enviado exitosamente",
    "data": {
        "id": "uuid-del-mensaje",
        "whatsapp_message_id": "wamid.xxxxx",
        "status": "pending",
        "phone_number": "5491123456789",
        "message_type": "contacts",
        "content": "Contactos enviados (1): Juan Perez",
        "contacts_info": {
            "total_contacts": 1,
            "contact_names": ["Juan Perez"],
            "contacts_preview": [...]
        },
        "created_at": "2025-08-22T00:07:22.881330-04:00"
    },
    "timestamp": "2025-08-22T00:07:22.945096-04:00"
}
```

---

## TIPOS DE DATOS SOPORTADOS:

### Tipos de teléfono:
- `WORK` - Trabajo
- `HOME` - Casa  
- `CELL` - Celular
- `MAIN` - Principal
- `IPHONE` - iPhone
- `OTHER` - Otro

### Tipos de email:
- `WORK` - Trabajo
- `HOME` - Personal
- `OTHER` - Otro

### Tipos de dirección:
- `WORK` - Trabajo
- `HOME` - Casa
- `OTHER` - Otro

### Tipos de URL:
- `WORK` - Trabajo
- `HOME` - Personal
- `OTHER` - Otro
