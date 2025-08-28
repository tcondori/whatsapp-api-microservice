# WhatsApp API Microservice - Copilot Instructions
<!-- Instrucciones para agentes AI sobre microservicio de WhatsApp API con Flask-RESTX -->

## Project Overview
<!-- Resumen del proyecto: microservicio independiente para integración con WhatsApp Business API -->
This is a Flask-RESTX microservice providing WhatsApp Business API integration with comprehensive webhook handling, Swagger documentation, and enterprise chatbot capabilities powered by RiveScript and LLM integration for intelligent response management.



## Detailed Instructions by Component
For specific implementation details, refer to these specialized instruction files:

- **`.github/instructions/project_structure.instructions.md`** - Complete project structure, directory organization, and application factory pattern


- **`.github/instructions/messages.instructions.md`** - Message handling, templates, status tracking, and processing pipeline
  <!-- Sistema completo de mensajería WhatsApp con soporte multi-línea, API endpoints para todos los tipos de mensajes, selección automática de líneas con balanceador de carga, gestión CRUD de líneas de mensajería, y integración con WhatsApp Business API -->

- **`media_contacts.instructions.md`** - Media upload/download, contact management, and file storage integration
  <!-- Gestión completa de archivos multimedia y contactos, incluyendo upload/download de medios, validación de archivos, gestión de contactos con perfiles y bloqueo, integración con servicios de almacenamiento, y APIs CRUD para contactos y medios -->

- **`webhook.instructions.md`** - Complete webhook handling, signature verification, and event processing
  <!-- Sistema completo de webhooks WhatsApp con soporte multi-línea, verificación de firmas de seguridad, procesamiento de todos los tipos de eventos, manejo asíncrono con Celery, gestión de errores y reintentos, y endpoints específicos por línea -->

- **`persistence.instructions.md`** - Database schema, models, repositories, and caching strategies
  <!-- Sistema de persistencia completo con SQLAlchemy y PostgreSQL, patrones de repositorio, migración con Alembic, cache con Redis para alto rendimiento, conexiones múltiples a base de datos, y consultas optimizadas con indexación -->

- **`security_rate_limit.instructions.md`** - Authentication, rate limiting, input validation, and security headers
  <!-- Sistema integral de seguridad con autenticación por API keys y JWT, rate limiting avanzado con Redis, validación exhaustiva de input, headers de seguridad, protección contra ataques, logging de seguridad y encriptación de datos sensibles -->

- **`tests.instructions`** - Testing strategy, unit tests, integration tests, and mock implementations
  <!-- Framework completo de testing con pytest, tests unitarios para todos los componentes, tests de integración para APIs y webhooks, mocking de servicios externos, tests de carga y rendimiento, coverage completo y pipeline CI/CD automatizado -->

- **`readme_swagger.instructions.md`** - Documentation standards, Swagger setup, and API examples
  <!-- Documentación completa del proyecto con README detallado, documentación Swagger/OpenAPI automática con Flask-RESTX, ejemplos de requests/responses, guías de deployment en Docker y cloud, documentación técnica de arquitectura y guías de contribución -->

- **`logs.instructions.md`** - Logging strategy, log formats, and log management
  <!-- Estrategia de logging completa con formatos de log, gestión de logs, integración con sistemas de monitoreo y alertas, y mejores prácticas para logging en producción -->

## Architecture & Key Components
<!-- Arquitectura y componentes principales del microservicio -->

### Core Structure
<!-- Estructura principal: capas de API, webhooks, servicios y modelos -->
- **API Layer**: Flask-RESTX with automatic Swagger documentation
- **Webhook Handler**: Complete WhatsApp webhook processing system
- **Service Layer**: Business logic for WhatsApp operations (send messages, handle media, manage contacts)
- **Models**: Data models for webhook payloads, message types, and API responses

### Key Directories (when created)
<!-- Directorios clave cuando se cree la estructura del proyecto -->
- `app/api/` - REST endpoints organized by WhatsApp API categories
- `app/` - Blueprint and application factory
- `app/webhooks/` - Webhook handlers for incoming WhatsApp events
- `app/services/` - Business logic layer
- `app/models/` - Pydantic models for request/response validation
- `app/utils/` - Utilities for WhatsApp API authentication, media handling

## Development Patterns
<!-- Patrones de desarrollo específicos para el microservicio -->

### Code Documentation Standards
<!-- Estándares de documentación del código -->
- All code comments must be written in Spanish
- Use clear, descriptive Spanish comments for functions, classes, and complex logic
- Document API endpoints and webhook handlers with Spanish descriptions
- Include Spanish docstrings for all public methods and classes

### Naming Conventions
<!-- Convenciones de nomenclatura para archivos y funciones -->
- All file names must be in abbreviated English (e.g., `msg_handler.py`, `webhook_proc.py`)
- Function and method names should use abbreviated English (e.g., `send_msg()`, `proc_webhook()`, `validate_req()`)
- Class names in abbreviated English with PascalCase (e.g., `MsgService`, `WebhookHandler`)
- Variable names can be abbreviated English or descriptive short forms

### API Endpoint Structure
<!-- Estructura de endpoints: usar namespaces, documentación Swagger, validación -->
- Use Flask-RESTX namespaces to group related endpoints (messages, media, contacts, webhooks)
- All endpoints should have proper Swagger documentation with examples
- Implement request validation using Pydantic models or Flask-RESTX expect decorators
- Follow WhatsApp API naming conventions for consistency

### Webhook Implementation
<!-- Implementación de webhooks: verificación, manejo de eventos, procesamiento asíncrono -->
- Webhook verification must validate WhatsApp signatures
- Handle all webhook event types: messages, message_status, message_reactions, etc.
- Implement proper error handling and retry mechanisms
- Use background tasks for heavy processing to avoid webhook timeouts

### Error Handling
<!-- Manejo de errores: respuestas estándar, logging, circuit breaker, rate limiting -->
- Return standardized error responses matching WhatsApp API format
- Log all webhook events and API calls for debugging
- Implement circuit breaker patterns for external API calls
- Handle WhatsApp API rate limiting with exponential backoff

## Key Dependencies & Integration Points
<!-- Dependencias clave y puntos de integración externos -->
- WhatsApp Business API (Graph API endpoints)
- Media storage service (for handling images, videos, documents)
- Database for message history and webhook event logging
- Authentication service for API key management

## Development Workflow
<!-- Flujo de trabajo de desarrollo: variables de entorno, testing, mocks, Docker -->
- Use environment variables for WhatsApp API credentials and webhook secrets
- Implement comprehensive unit tests for webhook handlers and API endpoints
- Use mock responses for WhatsApp API during development
- Docker containerization for consistent deployment

## Specific Implementation Notes
<!-- Notas específicas de implementación para WhatsApp API -->
- Always verify webhook signatures before processing
- Implement idempotency for message sending to prevent duplicates
- Handle WhatsApp message templates and interactive components properly
- Implement proper media upload/download flows with validation
- Support both text and rich media message types

## Configuration Management
<!-- Gestión de configuración: entornos, secretos, feature flags -->
- Separate configs for development, staging, and production environments
- Secure storage of WhatsApp API tokens and webhook secrets
- Feature flags for enabling/disabling specific WhatsApp features

## Test y pruebas
- Crear los scripts de prueba en /test/[modulo]


## Logging, Monitoring & Observability
<!-- Monitoreo y observabilidad: logs estructurados, health checks, métricas -->
- Log all webhook events with structured logging
- Implement health checks for WhatsApp API connectivity
- Track message delivery rates and webhook processing times
- Monitor API rate limits and usage patterns
- Implement gestión de logs para asegurar la trazabilidad y el análisis de eventos

When implementing features, always consider WhatsApp's API limitations, webhook delivery requirements, and the need for reliable message processing.
