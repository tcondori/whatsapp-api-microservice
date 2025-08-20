# 🔥 Guía Completa para Probar los Endpoints de WhatsApp API

## 🌐 URLs Principales

### **Documentación Swagger**
- **Swagger UI**: http://localhost:5000/docs/
- **JSON Schema**: http://localhost:5000/swagger.json

### **Health Check**
- **General**: http://localhost:5000/health
- **Messages**: http://localhost:5000/v1/messages/test

---

## 🔑 Autenticación

**IMPORTANTE**: Todos los endpoints requieren autenticación con API Key.

```
Header: X-API-Key
Valores válidos: dev-api-key, test-key-123
```

---

## 📋 Endpoints Disponibles

### 1. 🧪 **Test/Health Check**
```
GET http://localhost:5000/v1/messages/test
Headers: X-API-Key: dev-api-key
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "API de mensajes funcionando correctamente",
  "data": {
    "service_status": "active",
    "total_messages": 1,
    "available_lines": 1,
    "supported_endpoints": [...]
  }
}
```

### 2. 📤 **Enviar Mensaje de Texto**
```
POST http://localhost:5000/v1/messages/text
Headers: 
  Content-Type: application/json
  X-API-Key: dev-api-key

Body:
{
  "phone_number": "+5491123456789",
  "content": "Hola, este es un mensaje de prueba desde la API"
}
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Mensaje de texto enviado exitosamente",
  "data": {
    "id": "uuid-del-mensaje",
    "whatsapp_message_id": "wamid.test_timestamp_hash",
    "phone_number": "+5491123456789",
    "message_type": "text",
    "content": "Hola, este es un mensaje de prueba desde la API",
    "status": "sent",
    "direction": "outbound",
    "line_id": "line_1",
    "created_at": "2025-08-20T12:56:00.059002Z",
    "updated_at": "2025-08-20T12:56:00.059006Z"
  }
}
```

### 3. 📋 **Listar Mensajes**
```
GET http://localhost:5000/v1/messages?page=1&per_page=10
Headers: X-API-Key: dev-api-key
```

**Con filtros:**
```
GET http://localhost:5000/v1/messages?status=sent&message_type=text&phone_number=+5491123456789
Headers: X-API-Key: dev-api-key
```

### 4. 🔍 **Obtener Mensaje por WhatsApp ID**
```
GET http://localhost:5000/v1/messages/whatsapp/wamid.test_1755694560_22d1775e
Headers: X-API-Key: dev-api-key
```

### 5. 🔄 **Actualizar Estado de Mensaje**
```
PATCH http://localhost:5000/v1/messages/whatsapp/wamid.test_1755694560_22d1775e/status
Headers: 
  Content-Type: application/json
  X-API-Key: dev-api-key

Body:
{
  "status": "delivered"
}
```

---

## 🧪 Métodos de Prueba

### **Opción 1: Swagger UI (Más Fácil)**
1. Ve a http://localhost:5000/docs/
2. Expande el endpoint que quieres probar
3. Click en "Try it out"
4. Agrega la API Key en el header: `dev-api-key`
5. Completa los parámetros
6. Click en "Execute"

### **Opción 2: cURL**
```bash
# Health Check
curl -X GET "http://localhost:5000/v1/messages/test" \
  -H "X-API-Key: dev-api-key"

# Enviar mensaje
curl -X POST "http://localhost:5000/v1/messages/text" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "phone_number": "+5491123456789",
    "content": "Mensaje desde cURL"
  }'

# Listar mensajes
curl -X GET "http://localhost:5000/v1/messages" \
  -H "X-API-Key: dev-api-key"
```

### **Opción 3: Postman**
1. Crea una nueva colección
2. Agrega requests con las URLs de arriba
3. En Headers agrega: `X-API-Key: dev-api-key`
4. Para POST, configura Body como JSON

### **Opción 4: Python requests**
```python
import requests

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'dev-api-key'
}

# Health check
response = requests.get('http://localhost:5000/v1/messages/test', headers=headers)
print(response.json())

# Enviar mensaje
data = {
    "phone_number": "+5491123456789",
    "content": "Mensaje desde Python"
}
response = requests.post('http://localhost:5000/v1/messages/text', headers=headers, json=data)
print(response.json())
```

---

## ❌ Códigos de Error Comunes

- **401 Unauthorized**: API Key faltante o inválida
- **400 Bad Request**: Datos de entrada inválidos
- **404 Not Found**: Mensaje no encontrado
- **500 Internal Server Error**: Error interno del servidor

---

## 🎯 Datos de Ejemplo para Pruebas

### **Números de teléfono válidos:**
```
+5491123456789  (Argentina)
+1234567890     (US)
+34612345678    (España)
```

### **Contenido de mensajes:**
```
"Hola, este es un mensaje de prueba"
"¡Bienvenido a nuestra API de WhatsApp!"
"Mensaje con emojis 🚀 📱 ✅"
```

### **Estados válidos:**
```
pending, sent, delivered, read, failed
```

---

## 🔧 Troubleshooting

### **Si no funciona Swagger:**
1. Verifica que el servidor esté funcionando en http://localhost:5000
2. Prueba http://localhost:5000/swagger.json para ver el schema
3. Recarga la página de Swagger

### **Si obtienes 401 Unauthorized:**
1. Verifica que incluiste el header `X-API-Key`
2. Usa uno de estos valores: `dev-api-key` o `test-key-123`

### **Si obtienes 400 Bad Request:**
1. Verifica el formato del número de teléfono (debe empezar con +)
2. Asegúrate de que el contenido no esté vacío
3. Revisa que el JSON esté bien formateado

---

¡Ya puedes probar todos los endpoints! 🎉
