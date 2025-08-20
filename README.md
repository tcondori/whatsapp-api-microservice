# WhatsApp API Microservice

🚀 Microservicio completo para integración con WhatsApp Business API construido con Flask-RESTX.

## 🌟 Características

- **Envío de mensajes**: Texto, multimedia, plantillas e interactivos
- **Gestión de contactos**: Perfiles, bloqueo y estadísticas
- **Webhooks en tiempo real**: Procesamiento de eventos de WhatsApp
- **Soporte multi-línea**: Múltiples números de WhatsApp Business
- **Documentación automática**: Swagger/OpenAPI integrado
- **Autenticación por API Key**: Sistema seguro de autenticación
- **Rate limiting**: Control de tráfico y límites de velocidad
- **Base de datos robusta**: SQLAlchemy con SQLite/PostgreSQL
- **Cache con Redis**: Optimización de rendimiento
- **Logging estructurado**: Sistema completo de logs

## 🏗️ Arquitectura

```
├── config/                 # Configuración multi-entorno
├── database/              # Modelos y conexiones de BD
├── app/
│   ├── api/              # Endpoints REST por módulo
│   ├── private/          # Utilidades internas
│   ├── repositories/     # Patrones de repositorio
│   └── utils/            # Utilidades públicas
├── tests/                # Suite de testing
└── entrypoint.py        # Punto de entrada
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- Redis (opcional para cache)
- Base de datos (SQLite para desarrollo, PostgreSQL para producción)

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd whatsapp-api-microservice
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales de WhatsApp Business API
```

5. **Inicializar base de datos**
```bash
python entrypoint.py init-db
```

6. **Ejecutar la aplicación**
```bash
python entrypoint.py
```

La aplicación estará disponible en:
- **API**: http://localhost:5000
- **Documentación**: http://localhost:5000/docs/
- **Health Check**: http://localhost:5000/health

## 📖 Configuración

### Variables de Entorno Principales

```bash
# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=tu-token-de-acceso
WHATSAPP_BUSINESS_ID=tu-business-id
WEBHOOK_VERIFY_TOKEN=tu-webhook-verify-token
WEBHOOK_SECRET=tu-webhook-secret

# Líneas de mensajería
LINE_1_PHONE_NUMBER_ID=tu-phone-number-id
LINE_1_DISPLAY_NAME=Línea Principal

# Base de datos
DATABASE_URL=sqlite:///whatsapp_dev.db  # Desarrollo
# DATABASE_URL=postgresql://user:pass@host:port/db  # Producción

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Seguridad
VALID_API_KEYS=tu-api-key-1,tu-api-key-2
SECRET_KEY=tu-secret-key-super-seguro
```

## 📚 Uso de la API

### Autenticación

Todas las requests deben incluir el header de autenticación:

```bash
X-API-Key: tu-api-key-valida
```

### Endpoints Principales

- `GET /health` - Health check general
- `GET /api/v1/messages/health` - Health check de mensajes
- `GET /api/v1/contacts/health` - Health check de contactos
- `GET /api/v1/media/health` - Health check de medios
- `GET /api/v1/webhooks/health` - Health check de webhooks

### Ejemplos de Uso

```bash
# Health check
curl -X GET "http://localhost:5000/health" \
  -H "X-API-Key: dev-api-key"

# Verificar módulo específico
curl -X GET "http://localhost:5000/api/v1/messages/health" \
  -H "X-API-Key: dev-api-key"
```

## 🛠️ Comandos CLI

```bash
# Inicializar base de datos
python entrypoint.py init-db

# Resetear base de datos
python entrypoint.py reset-db

# Crear línea de mensajería
python entrypoint.py create-messaging-line --line-id line_2 --display-name "Línea Soporte"

# Verificar configuración
python entrypoint.py test-config
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=app

# Tests específicos
pytest tests/unit/
pytest tests/integration/
```

## 🐳 Docker

```bash
# Construir imagen
docker build -t whatsapp-api .

# Ejecutar contenedor
docker run -p 5000:5000 \
  -e WHATSAPP_ACCESS_TOKEN=tu-token \
  -e DATABASE_URL=sqlite:///app.db \
  whatsapp-api
```

## 📁 Estructura del Proyecto

```
whatsapp-api-microservice/
├── 📁 config/                    # Configuración por entornos
│   ├── __init__.py
│   ├── default.py               # Configuración base
│   ├── dev.py                   # Desarrollo
│   └── prod.py                  # Producción
├── 📁 database/                  # Base de datos
│   ├── __init__.py
│   ├── connection.py            # Conexiones y sesiones
│   ├── models.py                # Modelos SQLAlchemy
│   └── 📁 migrations/           # Migraciones Alembic
├── 📁 app/                       # Aplicación principal
│   ├── __init__.py
│   ├── extensions.py            # Extensiones Flask
│   ├── 📁 private/              # Módulos internos
│   │   ├── auth.py              # Autenticación
│   │   ├── validators.py        # Validadores
│   │   └── utils.py             # Utilidades privadas
│   ├── 📁 api/                  # Endpoints REST
│   │   ├── 📁 messages/         # API de mensajes
│   │   ├── 📁 contacts/         # API de contactos
│   │   ├── 📁 media/            # API de medios
│   │   └── 📁 webhooks/         # API de webhooks
│   ├── 📁 repositories/         # Patrones de repositorio
│   │   └── base_repo.py         # Repositorio base + específicos
│   └── 📁 utils/                # Utilidades públicas
│       ├── exceptions.py        # Excepciones personalizadas
│       └── helpers.py           # Funciones auxiliares
├── 📁 tests/                     # Suite de testing
│   ├── 📁 unit/                 # Tests unitarios
│   ├── 📁 integration/          # Tests de integración
│   └── 📁 fixtures/             # Datos de prueba
├── entrypoint.py                # Punto de entrada
├── requirements.txt             # Dependencias Python
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore                  # Archivos ignorados por Git
└── README.md                   # Este archivo
```

## 🔒 Seguridad

- ✅ Autenticación por API Key
- ✅ Verificación de firmas de webhook
- ✅ Rate limiting configurable
- ✅ Validación de entrada
- ✅ Headers de seguridad CORS
- ✅ Logging de eventos de seguridad

## 🚀 Roadmap

- [ ] Implementación completa de APIs REST
- [ ] Sistema de plantillas de mensajes
- [ ] Dashboard web de administración
- [ ] Métricas y monitoreo con Prometheus
- [ ] Sistema de notificaciones
- [ ] Integración con más proveedores de almacenamiento

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-feature`)
3. Commit tus cambios (`git commit -am 'Agregar nueva feature'`)
4. Push a la rama (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- 📧 Email: soporte@tu-empresa.com
- 💬 Discord: [Enlace al servidor]
- 📖 Documentación: [Enlace a docs]

---

⭐ **¡Dale una estrella si este proyecto te fue útil!**
