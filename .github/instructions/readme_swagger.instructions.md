# README and Swagger Instructions
<!-- Instrucciones para documentación README y Swagger -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar la documentación completa del proyecto, incluyendo:
- README detallado con instalación, configuración y ejemplos de uso
- Documentación Swagger/OpenAPI automática con Flask-RESTX
- Ejemplos completos de requests/responses para todos los endpoints
- Guías de deployment en Docker, Kubernetes y servicios cloud
- Documentación técnica de arquitectura y patrones implementados
- Changelog, roadmap y guías de contribución al proyecto
-->

## README.md Structure
<!-- Estructura del archivo README principal -->

```markdown
# WhatsApp API Microservice

## Descripción
Microservicio independiente para integración con WhatsApp Business API usando Flask-RESTX.

## Características Principales
- ✅ API REST completa con documentación Swagger automática
- ✅ Manejo completo de webhooks de WhatsApp
- ✅ Soporte para todos los tipos de mensajes (texto, multimedia, plantillas)
- ✅ Gestión de contactos y archivos multimedia
- ✅ Validación de firmas de webhook
- ✅ Rate limiting y manejo de errores robusto
- ✅ Logging estructurado y monitoreo

## Instalación Rápida

### Con Docker
```bash
docker-compose up -d
```

### Desarrollo Local
```bash
pip install -r requirements/development.txt
export FLASK_ENV=development
python run.py
```

## Configuración
Copiar `.env.example` a `.env` y configurar:
- `WHATSAPP_ACCESS_TOKEN`: Token de acceso de WhatsApp Business API
- `WEBHOOK_VERIFY_TOKEN`: Token para verificación de webhooks
- `DATABASE_URL`: URL de conexión a la base de datos

## Endpoints Principales
- `POST /api/v1/whatsapp/messages` - Enviar mensaje (endpoint agregador)
- `POST /api/v1/whatsapp/messages/text` - Enviar mensaje de texto
- `POST /api/v1/whatsapp/messages/image` - Enviar mensaje con imagen
- `POST /api/v1/whatsapp/messages/video` - Enviar mensaje con video
- `POST /api/v1/whatsapp/messages/document` - Enviar documento
- `POST /api/v1/whatsapp/messages/template` - Enviar plantilla
- `POST /api/v1/whatsapp/messages/interactive/buttons` - Mensaje con botones
- `POST /api/v1/whatsapp/messages/interactive/list` - Mensaje con lista
- `POST /api/v1/whatsapp/webhooks` - Recibir webhooks de WhatsApp
- `GET /api/v1/whatsapp/contacts/{phone}` - Obtener información de contacto
- `POST /api/v1/whatsapp/media/upload` - Subir archivo multimedia

## Documentación API
Swagger UI disponible en: `http://localhost:5000/docs/`
```

## Swagger Documentation Standards
<!-- Estándares para documentación Swagger -->

### Namespace Configuration
```python
# Configuración de namespace con descripción en español
messages_ns = Namespace(
    'messages',
    description='Operaciones de mensajes de WhatsApp',
    path='/api/v1/whatsapp/messages'
)
```

### Endpoint Documentation Examples
```python
@messages_ns.route('')
class SendMessage(Resource):
    @messages_ns.doc('send_message_aggregator')
    @messages_ns.expect(send_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.response(200, 'Mensaje enviado exitosamente')
    @messages_ns.response(400, 'Error en los datos del mensaje')
    @messages_ns.response(401, 'Token de acceso inválido')
    def post(self):
        """
        Envía un mensaje de WhatsApp (endpoint agregador)
        
        Detecta automáticamente el tipo de mensaje basado en el payload
        y lo envía usando la API oficial de WhatsApp.
        """
        pass

@messages_ns.route('/text')
class SendTextMessage(Resource):
    @messages_ns.doc('send_text_message')
    @messages_ns.expect(text_message_model)
    @messages_ns.marshal_with(message_response_model)
    def post(self):
        """
        Envía un mensaje de texto específicamente
        
        Envía un mensaje de texto plano a un número de WhatsApp.
        """
        pass

@messages_ns.route('/interactive/buttons')
class SendInteractiveButtons(Resource):
    @messages_ns.doc('send_interactive_buttons')
    @messages_ns.expect(interactive_buttons_model)
    @messages_ns.marshal_with(message_response_model)
    def post(self):
        """
        Envía un mensaje interactivo con botones
        
        Permite al usuario seleccionar una opción de una lista de botones.
        """
        pass
```

### Model Documentation
```python
# Modelos Swagger con descripciones en español

# Modelo agregador principal
send_message_model = messages_ns.model('SendMessage', {
    'to': fields.String(
        required=True,
        description='Número de teléfono en formato E.164',
        example='+1234567890'
    ),
    'type': fields.String(
        description='Tipo de mensaje (autodetectado si no se especifica)',
        enum=['text', 'image', 'video', 'document', 'template', 'interactive'],
        example='text'
    ),
    'text': fields.Nested(text_content_model, description='Contenido de texto'),
    'image': fields.Nested(image_content_model, description='Contenido de imagen'),
    'video': fields.Nested(video_content_model, description='Contenido de video'),
    'document': fields.Nested(document_content_model, description='Contenido de documento'),
    'template': fields.Nested(template_content_model, description='Contenido de plantilla'),
    'interactive': fields.Nested(interactive_content_model, description='Contenido interactivo')
})

# Modelo específico para texto
text_message_model = messages_ns.model('TextMessage', {
    'to': fields.String(
        required=True,
        description='Número de teléfono en formato E.164',
        example='+1234567890'
    ),
    'text': fields.Nested(messages_ns.model('TextContent', {
        'body': fields.String(
            required=True,
            description='Contenido del mensaje de texto',
            example='Hola, este es un mensaje de prueba'
        )
    }), required=True)
})

# Modelo específico para imagen
image_message_model = messages_ns.model('ImageMessage', {
    'to': fields.String(required=True, description='Número de destino'),
    'image': fields.Nested(messages_ns.model('ImageContent', {
        'id': fields.String(description='ID del medio subido a WhatsApp'),
        'link': fields.String(description='URL pública de la imagen'),
        'caption': fields.String(description='Leyenda de la imagen')
    }), required=True)
})

# Modelo para botones interactivos
interactive_buttons_model = messages_ns.model('InteractiveButtons', {
    'to': fields.String(required=True, description='Número de destino'),
    'interactive': fields.Nested(messages_ns.model('ButtonsContent', {
        'type': fields.String(required=True, enum=['button'], example='button'),
        'header': fields.Nested(messages_ns.model('Header', {
            'type': fields.String(enum=['text'], example='text'),
            'text': fields.String(example='Título del mensaje')
        })),
        'body': fields.Nested(messages_ns.model('Body', {
            'text': fields.String(required=True, example='Selecciona una opción:')
        })),
        'action': fields.Nested(messages_ns.model('ButtonAction', {
            'buttons': fields.List(fields.Nested(messages_ns.model('Button', {
                'type': fields.String(enum=['reply'], example='reply'),
                'reply': fields.Nested(messages_ns.model('ButtonReply', {
                    'id': fields.String(required=True, example='btn_1'),
                    'title': fields.String(required=True, example='Opción 1')
                }))
            })))
        }))
    }), required=True)
})

# Modelo para lista interactiva
interactive_list_model = messages_ns.model('InteractiveList', {
    'to': fields.String(required=True, description='Número de destino'),
    'interactive': fields.Nested(messages_ns.model('ListContent', {
        'type': fields.String(required=True, enum=['list'], example='list'),
        'body': fields.Nested(messages_ns.model('ListBody', {
            'text': fields.String(required=True, example='Elige una opción de la lista:')
        })),
        'action': fields.Nested(messages_ns.model('ListAction', {
            'button': fields.String(required=True, example='Ver opciones'),
            'sections': fields.List(fields.Nested(messages_ns.model('ListSection', {
                'title': fields.String(example='Categoría 1'),
                'rows': fields.List(fields.Nested(messages_ns.model('ListRow', {
                    'id': fields.String(required=True, example='row_1'),
                    'title': fields.String(required=True, example='Opción A'),
                    'description': fields.String(example='Descripción de la opción A')
                })))
            })))
        }))
    }), required=True)
})
```

### Error Response Models
```python
# Modelo de respuesta de error estándar
error_model = api.model('Error', {
    'error': fields.String(description='Código de error'),
    'message': fields.String(description='Descripción del error'),
    'details': fields.Raw(description='Detalles adicionales del error')
})
```

## API Examples Section
<!-- Sección de ejemplos de uso de la API -->

### Request Examples
```python
# Ejemplos de requests para cada endpoint
webhook_example = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "15551234567",
                    "phone_number_id": "123456789"
                },
                "messages": [{
                    "from": "16315551234",
                    "id": "wamid.ABGGFlA5Fpa",
                    "timestamp": "1664827504",
                    "text": {
                        "body": "Hola mundo"
                    },
                    "type": "text"
                }]
            },
            "field": "messages"
        }]
    }]
}
```

### Response Examples  
```python
# Ejemplos de respuestas para documentación
message_response_example = {
    "id": "uuid-generated-id",
    "whatsapp_message_id": "wamid.ABGGFlA5Fpa",
    "status": "sent",
    "phone_number": "+1234567890",
    "created_at": "2025-01-15T10:30:00Z"
}
```

## Interactive Documentation Features
<!-- Funcionalidades de documentación interactiva -->

### Try It Out Functionality
- All endpoints should be testable from Swagger UI
- Include authentication setup instructions
- Provide sample data for testing

### API Versioning in Swagger
```python
# Configuración de versionado en Swagger
api = Api(
    app,
    version='1.0',
    title='WhatsApp API Microservice',
    description='API completa para integración con WhatsApp Business',
    doc='/docs/',
    prefix='/api/v1'
)
```

### Tags and Organization
```python
# Organización por tags
@messages_ns.route('/send')
class SendMessage(Resource):
    @messages_ns.doc(
        'send_message',
        tags=['Messaging'],
        security='apikey'
    )
```

## Development Documentation
<!-- Documentación para desarrollo -->

### Setup Instructions in README
- Prerequisites (Python version, dependencies)
- Environment variable setup
- Database migration commands
- Testing instructions
- Docker setup for development

### API Testing Examples
```bash
# Ejemplo 1: Enviar mensaje de texto usando endpoint agregador
curl -X POST "http://localhost:5000/api/v1/whatsapp/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "to": "+1234567890",
    "text": {
      "body": "Hola! Este es un mensaje de prueba."
    }
  }'

# Ejemplo 2: Enviar mensaje de texto usando endpoint específico
curl -X POST "http://localhost:5000/api/v1/whatsapp/messages/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "to": "+1234567890",
    "text": {
      "body": "Mensaje enviado usando endpoint específico de texto"
    }
  }'

# Ejemplo 3: Enviar imagen con leyenda
curl -X POST "http://localhost:5000/api/v1/whatsapp/messages/image" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "to": "+1234567890",
    "image": {
      "id": "MEDIA_ID_FROM_WHATSAPP",
      "caption": "Descripción de la imagen"
    }
  }'

# Ejemplo 4: Enviar botones interactivos
curl -X POST "http://localhost:5000/api/v1/whatsapp/messages/interactive/buttons" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "to": "+1234567890",
    "interactive": {
      "type": "button",
      "header": {
        "type": "text",
        "text": "¿Cómo podemos ayudarte?"
      },
      "body": {
        "text": "Selecciona una de las siguientes opciones:"
      },
      "action": {
        "buttons": [
          {
            "type": "reply",
            "reply": {
              "id": "support_tech",
              "title": "Soporte Técnico"
            }
          },
          {
            "type": "reply", 
            "reply": {
              "id": "info_product",
              "title": "Información"
            }
          }
        ]
      }
    }
  }'

# Ejemplo 5: Enviar plantilla
curl -X POST "http://localhost:5000/api/v1/whatsapp/messages/template" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "to": "+1234567890",
    "template": {
      "name": "hello_world",
      "language": {
        "code": "en_US"
      },
      "components": []
    }
  }'
```
