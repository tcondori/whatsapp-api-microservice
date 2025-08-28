# Endpoint de Mensajes de Ubicación - Guía de Uso

## 🗺️ Nuevo Endpoint: POST /v1/messages/location

El endpoint de ubicación permite enviar mensajes de WhatsApp con coordenadas geográficas, siguiendo el formato oficial de Meta/WhatsApp Business API.

## 📍 URL del Endpoint

```
POST http://localhost:5000/v1/messages/location
```

## 🔐 Autenticación

```
Header: X-API-Key: dev-api-key
Content-Type: application/json
```

## 📋 Formato del Mensaje

### Estructura Básica (Solo Coordenadas)

```json
{
  "to": "5491123456789",
  "type": "location",
  "location": {
    "latitude": -34.6037,
    "longitude": -58.3816
  },
  "messaging_line_id": 1
}
```

### Estructura Completa (Con Nombre y Dirección)

```json
{
  "to": "5491123456789",
  "type": "location",
  "location": {
    "latitude": -34.6037,
    "longitude": -58.3816,
    "name": "Obelisco de Buenos Aires",
    "address": "Av. 9 de Julio s/n, C1043 CABA, Argentina"
  },
  "messaging_line_id": 1
}
```

## 🔧 Campos del Mensaje

### Campos Requeridos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `to` | string | Número de teléfono destino en formato internacional |
| `type` | string | Debe ser "location" |
| `location.latitude` | number | Latitud (entre -90 y 90) |
| `location.longitude` | number | Longitud (entre -180 y 180) |

### Campos Opcionales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `location.name` | string | Nombre descriptivo del lugar (máx. 1000 caracteres) |
| `location.address` | string | Dirección completa del lugar (máx. 1000 caracteres) |
| `messaging_line_id` | integer | ID de la línea de mensajería (default: 1) |

## 🌍 Ejemplos de Ubicaciones

### Buenos Aires, Argentina (Obelisco)
```bash
curl -X POST "http://localhost:5000/v1/messages/location" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5491123456789",
       "type": "location",
       "location": {
         "latitude": -34.6037,
         "longitude": -58.3816,
         "name": "Obelisco de Buenos Aires",
         "address": "Av. 9 de Julio s/n, C1043 CABA, Argentina"
       }
     }'
```

### Nueva York, USA (Times Square)
```bash
curl -X POST "http://localhost:5000/v1/messages/location" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5491123456789",
       "type": "location",
       "location": {
         "latitude": 40.7128,
         "longitude": -74.0060,
         "name": "Times Square",
         "address": "Times Square, New York, NY 10036, USA"
       }
     }'
```

### París, Francia (Torre Eiffel)
```bash
curl -X POST "http://localhost:5000/v1/messages/location" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5491123456789",
       "type": "location",
       "location": {
         "latitude": 48.8584,
         "longitude": 2.2945,
         "name": "Torre Eiffel",
         "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, Francia"
       }
     }'
```

### Tokio, Japón (Torre de Tokio)
```bash
curl -X POST "http://localhost:5000/v1/messages/location" \
     -H "X-API-Key: dev-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5491123456789",
       "type": "location",
       "location": {
         "latitude": 35.6586,
         "longitude": 139.7454,
         "name": "Torre de Tokio",
         "address": "4 Chome-2-8 Shibakoen, Minato City, Tokyo 105-0011, Japón"
       }
     }'
```

## ✅ Respuesta Exitosa

```json
{
  "success": true,
  "message": "Mensaje de ubicación enviado exitosamente",
  "timestamp": "2025-08-21T23:14:46.311147-04:00",
  "data": {
    "id": "733533bb-d291-48e1-a577-d48a95bdefde",
    "whatsapp_message_id": "wamid.HBgNNTQ5MTEyMzQ1Njc4ORUCABEYEjYzRDM4ODlENjM5NzdEQkUxQgA=",
    "phone_number": "5491123456789",
    "message_type": "location",
    "content": "Ubicación: -34.6037, -58.3816 | Nombre: Obelisco | Dirección: Buenos Aires",
    "status": "pending",
    "direction": "outbound",
    "line_id": "1",
    "created_at": "2025-08-21T23:14:46.244316-04:00",
    "updated_at": "2025-08-21T23:14:46.244323-04:00",
    "retry_count": 0,
    "error_message": null,
    "location_info": {
      "latitude": -34.6037,
      "longitude": -58.3816,
      "name": "Obelisco de Buenos Aires",
      "address": "Av. 9 de Julio s/n, C1043 CABA, Argentina"
    }
  }
}
```

## ❌ Errores Comunes

### Error: Latitud faltante
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Los campos 'latitude' y 'longitude' son requeridos en el objeto 'location'"
}
```

### Error: Latitud fuera de rango
```json
{
  "error_code": "VALIDATION_ERROR", 
  "message": "'latitude' debe estar entre -90 y 90 grados"
}
```

### Error: Longitud fuera de rango
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "'longitude' debe estar entre -180 y 180 grados"
}
```

### Error: Tipo de mensaje incorrecto
```json
{
  "errors": {
    "type": "'text' is not one of ['location']"
  },
  "message": "Input payload validation failed"
}
```

### Error: Número de teléfono inválido
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Formato de número de teléfono inválido"
}
```

## 📱 Uso en Postman

1. **Método:** POST
2. **URL:** `http://localhost:5000/v1/messages/location`
3. **Headers:**
   - `X-API-Key: dev-api-key`
   - `Content-Type: application/json`
4. **Body (raw JSON):** Usar cualquiera de los ejemplos de arriba

## 🔍 Validaciones Implementadas

- ✅ Validación de número de teléfono (formato internacional)
- ✅ Validación de tipo de mensaje (debe ser "location")
- ✅ Validación de latitud y longitud (campos requeridos)
- ✅ Validación de rangos de coordenadas (-90 ≤ lat ≤ 90, -180 ≤ lng ≤ 180)
- ✅ Validación de longitud de campos opcionales (máx. 1000 caracteres)
- ✅ Validación de tipos de datos (números para coordenadas)

## 🏗️ Arquitectura

El endpoint sigue el mismo patrón de arquitectura que los demás endpoints:

- **Endpoint REST:** `app/api/messages/routes.py` - `LocationMessageResource`
- **Lógica de negocio:** `app/api/messages/services.py` - `send_location_message()`
- **Integración WhatsApp:** `app/services/whatsapp_api.py` - `send_location_message()`
- **Validaciones:** `app/private/validators.py` - validaciones de ubicación
- **Modelos:** `app/api/messages/models.py` - `LOCATION_MESSAGE_FIELDS`

## 🚀 Estado del Desarrollo

- ✅ Endpoint implementado y funcional
- ✅ Validaciones completas
- ✅ Documentación Swagger automática
- ✅ Tests de integración
- ✅ Manejo de errores
- ✅ Formato oficial Meta/WhatsApp compatible
- ✅ Simulación para desarrollo (cuando no hay credenciales reales)
