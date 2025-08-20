# Project Structure Instructions
<!-- Instrucciones para estructura del proyecto -->

## Directory Structure
# Project Structure Instructions
<!-- Estructura completa del proyecto de microservicio WhatsApp API -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar la estructura completa del proyecto, incluyendo:
- Arquitectura de microservicio con Flask-RESTX y patrón Application Factory
- Configuración multi-entorno (desarrollo, producción) con variables de entorno
- Modelos de base de datos con SQLAlchemy (mensajes, contactos, webhooks, líneas de mensajería)
- Sistema de migración de base de datos con Alembic
- Configuración de conexiones, logging, manejo de errores y extensiones
- Estructura modular con separación de servicios, repositorios y controladores
-->

```
whatsapp-api-microservice/
├── config/
│   ├── __init__.py
│   ├── default.py               # Configuración por defecto
│   ├── dev.py                   # Configuración de desarrollo
│   └── prod.py                  # Configuración de producción
├── database/
│   ├── __init__.py
│   ├── connection.py            # Conexión a base de datos
│   ├── models.py                # Modelos de base de datos
│   └── migrations/              # Migraciones de Alembic
│       ├── versions/
│       └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── extensions.py             # Inicialización de extensiones Flask
│   ├── private/
│   │   ├── __init__.py
│   │   ├── auth.py               # Autenticación y autorización
│   │   ├── validators.py         # Validadores internos
│   │   └── utils.py              # Utilidades privadas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── messages/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py         # Rutas de mensajes
│   │   │   ├── models.py         # Modelos de request/response
│   │   │   └── services.py       # Lógica de negocio de mensajes
│   │   ├── contacts/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py         # Rutas de contactos
│   │   │   ├── models.py         # Modelos de contactos
│   │   │   └── services.py       # Lógica de negocio de contactos
│   │   ├── media/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py         # Rutas de medios
│   │   │   ├── models.py         # Modelos de medios
│   │   │   └── services.py       # Lógica de negocio de medios
│   │   └── webhooks/
│   │       ├── __init__.py
│   │       ├── routes.py         # Rutas de webhooks
│   │       ├── models.py         # Modelos de webhooks
│   │       └── services.py       # Procesamiento de webhooks
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── msg_repo.py           # Repositorio de mensajes
│   │   ├── contact_repo.py       # Repositorio de contactos
│   │   └── media_repo.py         # Repositorio de medios
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py         # Formateadores de mensajes
│       ├── exceptions.py         # Excepciones personalizadas
│       └── helpers.py            # Funciones auxiliares
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_msg_service.py
│   │   ├── test_contact_service.py
│   │   └── test_webhook_service.py
│   ├── integration/
│   │   ├── test_msg_routes.py
│   │   ├── test_webhook_routes.py
│   │   └── test_database.py
│   └── fixtures/
│       ├── webhook_samples.json
│       └── message_samples.json
├── requirements.txt              # Dependencias del proyecto
├── .env                         # Variables de entorno (no versionar)
├── .env.example                 # Ejemplo de variables de entorno
├── README.md                    # Documentación principal
├── entrypoint.py               # Punto de entrada de la aplicación
└── .gitignore
```

## Application Factory Pattern
<!-- Patrón Factory para crear la aplicación -->

```python
# app/__init__.py
from flask import Flask
from flask_restx import Api
from app.extensions import init_extensions
from config.settings import get_config

def create_app(config_name='development'):
    """
    Crea y configura la aplicación Flask
    Args:
        config_name: Nombre del entorno de configuración
    """
    app = Flask(__name__)
    
    # Cargar configuración
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Crear API con documentación Swagger
    api = Api(
        app, 
        doc='/docs/',
        title='WhatsApp API Microservice',
        version='1.0',
        description='API completa para integración con WhatsApp Business'
    )
    
    # Registrar namespaces de la API
    from app.api.messages.routes import messages_ns
    from app.api.contacts.routes import contacts_ns
    from app.api.media.routes import media_ns
    from app.api.webhooks.routes import webhooks_ns
    
    api.add_namespace(messages_ns, path='/api/v1/whatsapp/messages')
    api.add_namespace(contacts_ns, path='/api/v1/whatsapp/contacts')
    api.add_namespace(media_ns, path='/api/v1/whatsapp/media')
    api.add_namespace(webhooks_ns, path='/api/v1/whatsapp/webhooks')
    
    return app
```

## Application Factory Pattern
<!-- Patrón Factory para crear la aplicación -->

```python
# app/__init__.py
from flask import Flask
from flask_restx import Api
from app.extensions import init_extensions
from config import get_config
from database.connection import init_database

def create_app():
    """
    Crea y configura la aplicación Flask usando el patrón Factory
    Returns:
        Flask: Instancia configurada de la aplicación
    """
    app = Flask(__name__)
    
    # Cargar configuración según el entorno
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Inicializar base de datos
    init_database(app)
    
    # Crear API con documentación Swagger
    api = Api(
        app, 
        doc='/docs/',
        title='WhatsApp API Microservice',
        version='1.0',
        description='API completa para integración con WhatsApp Business'
    )
    
    # Registrar namespaces de la API
    register_api_namespaces(api)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    return app

def register_api_namespaces(api):
    """
    Registra todos los namespaces de la API
    Args:
        api: Instancia de Flask-RESTX Api
    """
    from app.api.messages.routes import messages_ns
    from app.api.contacts.routes import contacts_ns
    from app.api.media.routes import media_ns
    from app.api.webhooks.routes import webhooks_ns
    
    api.add_namespace(messages_ns, path='/api/v1/messages')
    api.add_namespace(contacts_ns, path='/api/v1/contacts')
    api.add_namespace(media_ns, path='/api/v1/media')
    api.add_namespace(webhooks_ns, path='/api/v1/webhooks')

def register_error_handlers(app):
    """
    Registra manejadores de errores globales
    Args:
        app: Instancia de la aplicación Flask
    """
    from app.utils.exceptions import ValidationError, WhatsAppAPIError
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return {'error': 'VALIDATION_ERROR', 'message': str(error)}, 400
    
    @app.errorhandler(WhatsAppAPIError)
    def handle_whatsapp_error(error):
        return {'error': 'WHATSAPP_API_ERROR', 'message': str(error)}, 502
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return {'error': 'NOT_FOUND', 'message': 'Endpoint no encontrado'}, 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return {'error': 'INTERNAL_ERROR', 'message': 'Error interno del servidor'}, 500
```

## Extensions Configuration
<!-- Configuración de extensiones Flask -->

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import logging

# Inicializar extensiones (sin app context)
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
redis_client = redis.Redis()

def init_extensions(app):
    """
    Inicializa todas las extensiones Flask
    Args:
        app: Instancia de la aplicación Flask
    """
    # Configurar CORS
    cors.init_app(
        app, 
        origins=app.config.get('CORS_ORIGINS', ['*']),
        allow_headers=['Content-Type', 'Authorization', 'X-API-Key', 'X-Hub-Signature-256']
    )
    
    # Configurar Rate Limiting
    limiter.init_app(app)
    
    # Configurar Redis
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379')
    redis_client.connection_pool = redis.ConnectionPool.from_url(redis_url)
    
    # Configurar Logging
    init_logging(app)

def init_logging(app):
    """
    Configura el sistema de logging
    Args:
        app: Instancia de la aplicación Flask
    """
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_format = app.config.get('LOG_FORMAT')
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log') if not app.config.get('DEBUG') else logging.NullHandler()
        ]
    )
    
    # Configurar loggers específicos
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
```

## Database Configuration
<!-- Configuración de base de datos separada -->

```python
# database/connection.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Inicializar SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """
    Inicializa la conexión a la base de datos
    Args:
        app: Instancia de la aplicación Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Crear tablas si no existen (solo en desarrollo)
    if app.config.get('DEBUG'):
        with app.app_context():
            db.create_all()

def get_db_session():
    """
    Obtiene una sesión de base de datos independiente
    Returns:
        Session: Sesión de SQLAlchemy
    """
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    return Session()

# database/models.py
from database.connection import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class BaseModel(db.Model):
    """Modelo base con campos comunes para todas las tablas"""
    __abstract__ = True
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            column.name: str(getattr(self, column.name)) 
            if isinstance(getattr(self, column.name), (datetime, uuid.UUID))
            else getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def save(self):
        """Guarda el modelo en la base de datos"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Elimina el modelo de la base de datos"""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

class Message(BaseModel):
    """Modelo para mensajes de WhatsApp"""
    __tablename__ = 'messages'
    
    whatsapp_message_id = db.Column(db.String(255), unique=True, nullable=False)
    line_id = db.Column(db.String(50), db.ForeignKey('messaging_lines.line_id'), nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    direction = db.Column(db.String(10), nullable=False)  # 'inbound' o 'outbound'
    media_id = db.Column(db.String(255), nullable=True)
    
    # Relación con la línea de mensajería
    messaging_line = db.relationship('MessagingLine', backref='messages', lazy='select')

class Contact(BaseModel):
    """Modelo para contactos de WhatsApp"""
    __tablename__ = 'contacts'
    
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(255))
    profile_pic_url = db.Column(db.Text)
    last_seen = db.Column(db.DateTime)
    is_blocked = db.Column(db.Boolean, default=False)

class WebhookEvent(BaseModel):
    """Modelo para eventos de webhook"""
    __tablename__ = 'webhook_events'
    
    event_type = db.Column(db.String(100), nullable=False)
    line_id = db.Column(db.String(50), nullable=True)  # Línea que recibió el webhook
    payload = db.Column(db.JSON, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    processed_at = db.Column(db.DateTime)

class MessagingLine(BaseModel):
    """Modelo para líneas de mensajería"""
    __tablename__ = 'messaging_lines'
    
    line_id = db.Column(db.String(50), unique=True, nullable=False)
    phone_number_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    webhook_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    max_daily_messages = db.Column(db.Integer, default=1000)
    current_daily_count = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=db.func.current_date())
    
    def reset_daily_counter_if_needed(self):
        """Resetea el contador diario si ha pasado un día"""
        from datetime import date
        today = date.today()
        
        if self.last_reset_date != today:
            self.current_daily_count = 0
            self.last_reset_date = today
            self.save()
    
    def can_send_message(self) -> bool:
        """Verifica si la línea puede enviar más mensajes hoy"""
        self.reset_daily_counter_if_needed()
        return self.is_active and self.current_daily_count < self.max_daily_messages
    
    def increment_message_count(self):
        """Incrementa el contador de mensajes enviados"""
        self.reset_daily_counter_if_needed()
        self.current_daily_count += 1
        self.save()
```

## Configuration Management
<!-- Gestión de configuración por entornos -->

```python
# config/default.py
import os

class DefaultConfig:
    """Configuración base compartida por todos los entornos"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # WhatsApp API Configuration
    WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v18.0')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ID')
    
    # Multi-line Support Configuration
    # Líneas de mensajería soportadas (JSON string)
    MESSAGING_LINES = os.getenv('MESSAGING_LINES', '[]')
    DEFAULT_LINE_ID = os.getenv('DEFAULT_LINE_ID', 'line_1')
    
    # Configuración de líneas individuales
    # Formato: LINE_{ID}_PHONE_NUMBER_ID, LINE_{ID}_DISPLAY_NAME, etc.
    
    # Webhook Configuration
    WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    
    @staticmethod
    def get_messaging_lines():
        """
        Obtiene las líneas de mensajería configuradas
        Returns:
            dict: Diccionario con las líneas configuradas
        """
        import json
        import os
        
        # Intentar cargar desde JSON
        try:
            lines_json = os.getenv('MESSAGING_LINES', '[]')
            lines = json.loads(lines_json)
            if lines:
                return {line['id']: line for line in lines}
        except json.JSONDecodeError:
            pass
        
        # Fallback: buscar variables de entorno individuales
        lines = {}
        line_id = 1
        while True:
            phone_number_id = os.getenv(f'LINE_{line_id}_PHONE_NUMBER_ID')
            if not phone_number_id:
                break
                
            lines[f'line_{line_id}'] = {
                'id': f'line_{line_id}',
                'phone_number_id': phone_number_id,
                'display_name': os.getenv(f'LINE_{line_id}_DISPLAY_NAME', f'Línea {line_id}'),
                'phone_number': os.getenv(f'LINE_{line_id}_PHONE_NUMBER', ''),
                'webhook_url': os.getenv(f'LINE_{line_id}_WEBHOOK_URL', ''),
                'is_active': os.getenv(f'LINE_{line_id}_IS_ACTIVE', 'true').lower() == 'true',
                'max_daily_messages': int(os.getenv(f'LINE_{line_id}_MAX_DAILY_MESSAGES', '1000'))
            }
            line_id += 1
        
        # Si no hay líneas configuradas, crear una por defecto
        if not lines:
            lines['line_1'] = {
                'id': 'line_1',
                'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID', ''),
                'display_name': 'Línea Principal',
                'phone_number': os.getenv('WHATSAPP_PHONE_NUMBER', ''),
                'webhook_url': os.getenv('WEBHOOK_URL', ''),
                'is_active': True,
                'max_daily_messages': 1000
            }
        
        return lines
    
    @staticmethod
    def get_line_config(line_id: str = None):
        """
        Obtiene la configuración de una línea específica
        Args:
            line_id: ID de la línea (si es None, usa la línea por defecto)
        Returns:
            dict: Configuración de la línea
        """
        lines = DefaultConfig.get_messaging_lines()
        
        if line_id is None:
            line_id = os.getenv('DEFAULT_LINE_ID', 'line_1')
        
        if line_id in lines:
            return lines[line_id]
        
        # Si no encuentra la línea, devolver la primera disponible
        if lines:
            return next(iter(lines.values()))
        
        raise ValueError(f"No se encontró configuración para la línea: {line_id}")

# config/dev.py
from config.default import DefaultConfig

class DevelopmentConfig(DefaultConfig):
    """Configuración específica para desarrollo"""
    DEBUG = True
    TESTING = False
    
    # Base de datos de desarrollo
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'sqlite:///whatsapp_dev.db'
    )
    SQLALCHEMY_ECHO = True
    
    # Configuración de desarrollo para WhatsApp
    WHATSAPP_API_BASE_URL = 'https://graph.facebook.com'
    
    # CORS permisivo para desarrollo
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Rate limiting más permisivo en desarrollo
    RATELIMIT_DEFAULT = "10000 per hour"

# config/prod.py
from config.default import DefaultConfig

class ProductionConfig(DefaultConfig):
    """Configuración específica para producción"""
    DEBUG = False
    TESTING = False
    
    # Base de datos de producción
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    
    # Configuración de producción para WhatsApp
    WHATSAPP_API_BASE_URL = 'https://graph.facebook.com'
    
    # CORS restrictivo para producción
    CORS_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting estricto en producción
    RATELIMIT_DEFAULT = "1000 per hour"

# config/__init__.py
import os
from config.default import DefaultConfig
from config.dev import DevelopmentConfig  
from config.prod import ProductionConfig

def get_config():
    """
    Obtiene la configuración según la variable de entorno FLASK_ENV
    Returns:
        Clase de configuración correspondiente al entorno
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'dev': DevelopmentConfig,
        'production': ProductionConfig,
        'prod': ProductionConfig,
        'default': DefaultConfig
    }
    
    return configs.get(env, DevelopmentConfig)
```

## Database Configuration
<!-- Configuración de base de datos separada -->

```python
# database/connection.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Inicializar SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """
    Inicializa la conexión a la base de datos
    Args:
        app: Instancia de la aplicación Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Crear tablas si no existen (solo en desarrollo)
    if app.config.get('DEBUG'):
        with app.app_context():
            db.create_all()

def get_db_session():
    """
    Obtiene una sesión de base de datos independiente
    Returns:
        Session: Sesión de SQLAlchemy
    """
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    return Session()

## Entry Point
<!-- Punto de entrada de la aplicación -->

```python
# entrypoint.py
import os
from app import create_app
from flask.cli import with_appcontext
import click

# Obtener configuración desde variable de entorno
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

@app.cli.command()
@with_appcontext
def init_db():
    """Inicializa la base de datos"""
    from app.extensions import db
    db.create_all()
    click.echo('Base de datos inicializada.')

@app.cli.command()
@with_appcontext
def reset_db():
    """Resetea la base de datos"""
    from app.extensions import db
    db.drop_all()
    db.create_all()
    click.echo('Base de datos reseteada.')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
```

## Private Module Structure
<!-- Estructura del módulo privado para utilidades internas -->

```python
# app/private/__init__.py
"""
Módulo privado para utilidades internas del microservicio
Contiene funciones y clases que no deben ser expuestas públicamente
"""

# app/private/auth.py
import jwt
import hmac
import hashlib
from functools import wraps
from flask import request, jsonify, current_app

def verify_whatsapp_signature(payload: bytes, signature: str) -> bool:
    """
    Verifica la firma del webhook de WhatsApp
    Args:
        payload: Contenido del webhook
        signature: Firma del header X-Hub-Signature-256
    Returns:
        bool: True si la firma es válida
    """
    if not signature.startswith('sha256='):
        return False
    
    expected_signature = hmac.new(
        current_app.config['WEBHOOK_SECRET'].encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    received_signature = signature[7:]  # Remove 'sha256=' prefix
    return hmac.compare_digest(expected_signature, received_signature)

def require_api_key(f):
    """
    Decorador para requerir API key válida
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'API key inválida'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(api_key: str) -> bool:
    """
    Valida la API key proporcionada
    Args:
        api_key: Clave API a validar
    Returns:
        bool: True si la clave es válida
    """
    # Implementar validación según el sistema de autenticación
    valid_keys = current_app.config.get('VALID_API_KEYS', [])
    return api_key in valid_keys
```

## Entry Point
<!-- Punto de entrada de la aplicación -->

```python
# entrypoint.py
import os
from app import create_app
from flask.cli import with_appcontext
import click

# Obtener configuración desde variable de entorno
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

@app.cli.command()
@with_appcontext
def init_db():
    """Inicializa la base de datos"""
    from app.extensions import db
    db.create_all()
    click.echo('Base de datos inicializada.')

@app.cli.command()
@with_appcontext
def reset_db():
    """Resetea la base de datos"""
    from app.extensions import db
    db.drop_all()
    db.create_all()
    click.echo('Base de datos reseteada.')

if __name__ == '__main__':
    # Ejecutar aplicación directamente
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
```

## API Route Structure
<!-- Estructura de rutas de la API -->

```python
# app/api/messages/routes.py
from flask_restx import Namespace, Resource, fields
from app.api.messages.models import (
    send_message_model, text_message_model, image_message_model, 
    video_message_model, document_message_model, template_message_model,
    interactive_buttons_model, interactive_list_model, message_response_model
)
from app.api.messages.services import MessageService
from app.private.auth import require_api_key

messages_ns = Namespace(
    'messages',
    description='Operaciones de mensajes de WhatsApp',
    decorators=[require_api_key]
)

@messages_ns.route('')
class SendMessage(Resource):
    @messages_ns.expect(send_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_message')
    def post(self):
        """
        Envía un mensaje de WhatsApp (endpoint agregador oficial)
        
        Permite enviar cualquier tipo de mensaje detectando automáticamente
        el tipo basado en el contenido del payload.
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_message(data)
        return result, 201

@messages_ns.route('/text')
class SendTextMessage(Resource):
    @messages_ns.expect(text_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_text_message')
    def post(self):
        """
        Envía un mensaje de texto específicamente
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_text_message(data)
        return result, 201

@messages_ns.route('/image')
class SendImageMessage(Resource):
    @messages_ns.expect(image_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_image_message')
    def post(self):
        """
        Envía un mensaje con imagen
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_image_message(data)
        return result, 201

@messages_ns.route('/video')
class SendVideoMessage(Resource):
    @messages_ns.expect(video_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_video_message')
    def post(self):
        """
        Envía un mensaje con video
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_video_message(data)
        return result, 201

@messages_ns.route('/document')
class SendDocumentMessage(Resource):
    @messages_ns.expect(document_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_document_message')
    def post(self):
        """
        Envía un mensaje con documento
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_document_message(data)
        return result, 201

@messages_ns.route('/template')
class SendTemplateMessage(Resource):
    @messages_ns.expect(template_message_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_template_message')
    def post(self):
        """
        Envía un mensaje de plantilla aprobada
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_template_message(data)
        return result, 201

@messages_ns.route('/interactive/buttons')
class SendInteractiveButtons(Resource):
    @messages_ns.expect(interactive_buttons_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_interactive_buttons')
    def post(self):
        """
        Envía un mensaje interactivo con botones
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_interactive_buttons(data)
        return result, 201

@messages_ns.route('/interactive/list')
class SendInteractiveList(Resource):
    @messages_ns.expect(interactive_list_model)
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('send_interactive_list')
    def post(self):
        """
        Envía un mensaje interactivo con lista de opciones
        """
        data = messages_ns.payload
        service = MessageService()
        result = service.send_interactive_list(data)
        return result, 201

@messages_ns.route('/status/<string:message_id>')
class MessageStatus(Resource):
    @messages_ns.marshal_with(message_response_model)
    @messages_ns.doc('get_message_status')
    def get(self, message_id):
        """
        Obtiene el estado de un mensaje específico
        Args:
            message_id: ID del mensaje de WhatsApp
        """
        service = MessageService()
        result = service.get_message_status(message_id)
        return result, 200
```

## Service Layer Structure
<!-- Estructura de la capa de servicios -->

```python
# app/api/messages/services.py
from app.repositories.msg_repo import MessageRepository
from app.utils.exceptions import ValidationError, WhatsAppAPIError
from app.private.validators import validate_phone_number

class MessageService:
    """Servicio para manejo de mensajes de WhatsApp"""
    
    def __init__(self):
        self.msg_repo = MessageRepository()
    
    def send_message(self, data: dict) -> dict:
        """
        Envía un mensaje a través de WhatsApp API
        Args:
            data: Datos del mensaje a enviar
        Returns:
            dict: Respuesta con información del mensaje enviado
        """
        # Validar datos de entrada
        if not validate_phone_number(data.get('phone_number')):
            raise ValidationError("Número de teléfono inválido")
        
        # Procesar según tipo de mensaje
        message_type = data.get('message_type')
        
        if message_type == 'text':
            return self._send_text_message(data)
        elif message_type == 'template':
            return self._send_template_message(data)
        elif message_type in ['image', 'document', 'audio', 'video']:
            return self._send_media_message(data)
        else:
            raise ValidationError(f"Tipo de mensaje no soportado: {message_type}")
    
    def _send_text_message(self, data: dict) -> dict:
        """Envía mensaje de texto"""
        # Implementar lógica de envío de texto
        pass
    
    def _send_template_message(self, data: dict) -> dict:
        """Envía mensaje de plantilla"""
        # Implementar lógica de envío de plantilla
        pass
    
    def _send_media_message(self, data: dict) -> dict:
        """Envía mensaje multimedia"""
        # Implementar lógica de envío de multimedia
        pass
```

## Dependency Injection
<!-- Inyección de dependencias -->

### Service Layer Pattern
- Services depend on repositories
- Controllers depend on services
- Repositories depend on database connections
- Easy testing with mock dependencies

### Example Service
```python
# app/api/webhooks/services.py
from app.api.messages.services import MessageService
from app.repositories.webhook_repo import WebhookRepository

class WebhookService:
    def __init__(self, message_service=None, webhook_repo=None):
        """
        Inicializa el servicio de webhooks
        Args:
            message_service: Servicio de mensajes (para testing con mocks)
            webhook_repo: Repositorio de webhooks (para testing con mocks)
        """
        self.message_service = message_service or MessageService()
        self.webhook_repo = webhook_repo or WebhookRepository()
    
    def process_webhook(self, webhook_data: dict) -> bool:
        """
        Procesa webhook recibido de WhatsApp
        Args:
            webhook_data: Datos del webhook
        Returns:
            bool: True si se procesó exitosamente
        """
        # Implementar lógica de procesamiento
        pass
```
