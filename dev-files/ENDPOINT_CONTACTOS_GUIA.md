# 👥 ENDPOINT DE CONTACTOS - Guía de Uso

## 📞 Nuevo Endpoint: POST /v1/messages/contacts

El endpoint de contactos permite enviar tarjetas de contacto (vCard enriquecidas) con información completa como nombres, teléfonos, emails, direcciones, información de empresa, etc., siguiendo el formato oficial de Meta/WhatsApp Business API.

## 📍 URL del Endpoint

```
POST http://localhost:5000/v1/messages/contacts
```

## 🔐 Autenticación

```
Header: X-API-Key: dev-api-key
Content-Type: application/json
```

## 📋 Formato del Mensaje

### Estructura Básica (Solo Nombre y Teléfono)

```json
{
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
```

### Estructura Completa (Información Empresarial)

```json
{
  "to": "5491123456789",
  "type": "contacts",
  "contacts": [
    {
      "name": {
        "formatted_name": "María García",
        "first_name": "María",
        "last_name": "García",
        "middle_name": "Elena",
        "prefix": "Lic.",
        "suffix": "Jr."
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
        },
        {
          "url": "https://www.mariagarcia.com",
          "type": "HOME"
        }
      ],
      "birthday": "1985-03-15"
    }
  ],
  "messaging_line_id": 1
}
```

## 🔧 Campos del Mensaje

### Campos Requeridos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `to` | string | Número de teléfono destino en formato internacional |
| `type` | string | Debe ser "contacts" |
| `contacts` | array | Array de contactos (mínimo 1, máximo 20) |
| `contacts[].name` | object | Información del nombre del contacto |
| `contacts[].name.formatted_name` o `contacts[].name.first_name` | string | Al menos uno requerido |

### Campos Opcionales del Contacto

| Campo | Tipo | Límite | Descripción |
|-------|------|--------|-------------|
| `contacts[].phones` | array | 20 max | Teléfonos del contacto |
| `contacts[].emails` | array | 20 max | Emails del contacto |
| `contacts[].addresses` | array | - | Direcciones del contacto |
| `contacts[].urls` | array | - | URLs/sitios web |
| `contacts[].org` | object | - | Información de empresa/organización |
| `contacts[].birthday` | string | - | Fecha de nacimiento (YYYY-MM-DD) |
| `messaging_line_id` | integer | - | ID de línea de mensajería (default: 1) |

### Tipos Válidos para Teléfonos/Emails/Direcciones

- **Tipos**: `CELL`, `MAIN`, `IPHONE`, `HOME`, `WORK`

### Estructura del Objeto `name`

```json
{
  "formatted_name": "Juan Carlos Pérez Jr.",
  "first_name": "Juan",
  "last_name": "Pérez", 
  "middle_name": "Carlos",
  "prefix": "Dr.",
  "suffix": "Jr."
}
```

### Estructura del Objeto `org`

```json
{
  "company": "Tech Solutions SA",
  "department": "Desarrollo",
  "title": "Gerente de Proyecto"
}
```

## 🌍 Ejemplos de Uso

### Contacto Personal Básico
```bash
curl -X POST "http://localhost:5000/v1/messages/contacts" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
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
               "email": "ana.lopez@gmail.com",
               "type": "HOME"
             }
           ]
         }
       ]
     }'
```

### Contacto Empresarial Completo
```bash
curl -X POST "http://localhost:5000/v1/messages/contacts" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5491123456789",
       "type": "contacts",
       "contacts": [
         {
           "name": {
             "formatted_name": "Dr. Carlos Mendoza",
             "first_name": "Carlos",
             "last_name": "Mendoza",
             "prefix": "Dr."
           },
           "phones": [
             {
               "phone": "+5491177889900",
               "type": "WORK"
             },
             {
               "phone": "+5491188990011",
               "type": "CELL",
               "wa_id": "5491188990011"
             }
           ],
           "emails": [
             {
               "email": "carlos.mendoza@hospital.com",
               "type": "WORK"
             }
           ],
           "org": {
             "company": "Hospital San Juan",
             "department": "Cardiología",
             "title": "Jefe de Cardiología"
           },
           "addresses": [
             {
               "street": "Av. Las Heras 2570",
               "city": "Buenos Aires",
               "state": "CABA",
               "zip": "C1127",
               "country": "Argentina",
               "country_code": "AR",
               "type": "WORK"
             }
           ]
         }
       ]
     }'
```

### Múltiples Contactos (Equipo de Trabajo)
```bash
curl -X POST "http://localhost:5000/v1/messages/contacts" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5491123456789",
       "type": "contacts",
       "contacts": [
         {
           "name": {
             "formatted_name": "Laura Martín",
             "first_name": "Laura",
             "last_name": "Martín"
           },
           "phones": [
             {
               "phone": "+5491199001122",
               "type": "CELL",
               "wa_id": "5491199001122"
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
         },
         {
           "name": {
             "formatted_name": "Roberto Silva",
             "first_name": "Roberto",
             "last_name": "Silva"
           },
           "phones": [
             {
               "phone": "+5491100112233",
               "type": "CELL",
               "wa_id": "5491100112233"
             }
           ],
           "emails": [
             {
               "email": "roberto.silva@empresa.com",
               "type": "WORK"
             }
           ],
           "org": {
             "company": "Tech Solutions SA",
             "title": "DevOps Engineer"
           }
         }
       ]
     }'
```

## ✅ Respuesta Exitosa

```json
{
  "success": true,
  "message": "Mensaje de contactos enviado exitosamente",
  "timestamp": "2025-08-21T23:45:30.123456-04:00",
  "data": {
    "id": "abc123-def456-ghi789",
    "whatsapp_message_id": "wamid.HBgNNTQ5MTEyMzQ1Njc4ORUCABEYEjlFMjk0MUI3M0EwNEE4OTRBQQA=",
    "phone_number": "5491123456789",
    "message_type": "contacts",
    "content": "Contactos enviados (3): María García, Juan Pérez, Ana López",
    "status": "pending",
    "direction": "outbound",
    "line_id": "1",
    "created_at": "2025-08-21T23:45:30.100000-04:00",
    "updated_at": "2025-08-21T23:45:30.100000-04:00",
    "retry_count": 0,
    "error_message": null,
    "contacts_info": {
      "total_contacts": 3,
      "contact_names": ["María García", "Juan Pérez", "Ana López"],
      "contacts_preview": [
        {
          "name": {
            "formatted_name": "María García"
          }
        },
        {
          "name": {
            "formatted_name": "Juan Pérez"
          }
        },
        {
          "preview": "... y 1 contactos más"
        }
      ]
    }
  }
}
```

## ❌ Errores Comunes

### Error: Array de contactos vacío
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "El array 'contacts' debe contener al menos un contacto"
}
```

### Error: Contacto sin nombre
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "El contacto en posición 0 debe incluir el campo 'name'"
}
```

### Error: Nombre incompleto
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "El contacto en posición 0 debe tener 'formatted_name' o 'first_name'"
}
```

### Error: Demasiados contactos
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "WhatsApp permite máximo 20 contactos por mensaje"
}
```

### Error: Demasiados teléfonos
```json
{
  "error_code": "VALIDATION_ERROR", 
  "message": "El contacto en posición 0 puede tener máximo 20 teléfonos"
}
```

### Error: Email inválido
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Email 0 del contacto 0 debe ser una dirección válida"
}
```

## 📱 Uso en Postman

1. **Método:** POST
2. **URL:** `http://localhost:5000/v1/messages/contacts`
3. **Headers:**
   - `X-API-Key: dev-api-key`
   - `Content-Type: application/json`
4. **Body (raw JSON):** Usar cualquiera de los ejemplos de arriba

## 🔍 Validaciones Implementadas

- ✅ Validación de número de teléfono (formato internacional)
- ✅ Validación de tipo de mensaje (debe ser "contacts")
- ✅ Validación de array de contactos (mínimo 1, máximo 20)
- ✅ Validación de estructura de cada contacto
- ✅ Validación de campos nombre (formatted_name o first_name requeridos)
- ✅ Validación de límites de teléfonos/emails (máximo 20 cada uno)
- ✅ Validación de formato de emails (debe contener @)
- ✅ Validación de tipos de datos y estructuras anidadas

## 🏗️ Arquitectura

El endpoint sigue el mismo patrón de arquitectura que los demás endpoints:

- **Endpoint REST:** `app/api/messages/routes.py` - `ContactsMessageResource`
- **Lógica de negocio:** `app/api/messages/services.py` - `send_contacts_message()`
- **Integración WhatsApp:** `app/services/whatsapp_api.py` - `send_contacts_message()`
- **Validaciones:** Validaciones específicas en el servicio y validadores generales
- **Modelos:** `app/api/messages/models.py` - `CONTACTS_MESSAGE_FIELDS`

## 🚀 Estado del Desarrollo

- ✅ Endpoint implementado y funcional
- ✅ Validaciones completas según formato oficial Meta
- ✅ Documentación Swagger automática
- ✅ Manejo de errores detallado
- ✅ Formato oficial Meta/WhatsApp compatible
- ✅ Simulación para desarrollo (cuando no hay credenciales reales)
- ✅ Soporte para múltiples contactos por mensaje
- ✅ Validación de límites de WhatsApp (20 contactos, 20 teléfonos/emails por contacto)

## ⚠️ Importante

**¡Reinicia el servidor!** Si ya tenías el servidor ejecutándose, necesitas reiniciarlo para que tome los nuevos endpoints:

```bash
# Detener el servidor actual (Ctrl+C)
# Luego ejecutar:
python run_server.py
```
