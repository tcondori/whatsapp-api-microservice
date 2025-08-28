"""
Núcleo de la aplicación Flask con patrón Factory
Inicializa y configura todas las extensiones y componentes del microservicio
"""
import os
import sys
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_app(config_name=None):
    """
    Application Factory para crear instancia de Flask
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing')
    Returns:
        Flask: Instancia configurada de la aplicación
    """
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configurar manejo de rutas con barras finales
    app.url_map.strict_slashes = False
    
    # Cargar configuración según el entorno
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    _configure_app(app, config_name)
    _validate_configuration(app)  # Agregar validación
    _initialize_logging_system(app)
    _initialize_extensions(app)
    _initialize_database(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli_commands(app)  # Agregar comandos CLI
    
    return app

def _configure_app(app: Flask, config_name: str):
    """
    Configura la aplicación Flask según el entorno
    """
    if config_name == 'development':
        from config.dev import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from config.prod import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config.default import DefaultConfig
        app.config.from_object(DefaultConfig)
    
    print(f"[OK] Configuración cargada: {config_name}")

def _validate_configuration(app: Flask):
    """
    Valida configuración crítica de la aplicación
    """
    required_configs = [
        'SECRET_KEY',
        'WHATSAPP_ACCESS_TOKEN',
        'WEBHOOK_VERIFY_TOKEN',
        'WEBHOOK_SECRET'
    ]
    
    missing_configs = []
    for config_key in required_configs:
        if not app.config.get(config_key):
            missing_configs.append(config_key)
    
    if missing_configs:
        error_msg = f"[WARNING] Configuración faltante: {', '.join(missing_configs)}"
        print(error_msg)
        
        if not app.config.get('DEBUG'):
            # En producción, fallar si falta configuración crítica
            raise RuntimeError(f"Configuración crítica faltante: {', '.join(missing_configs)}")
        else:
            print("[INFO] Ejecutando en modo desarrollo con configuración incompleta")
    else:
        print("[OK] Configuración crítica validada")

def _initialize_logging_system(app: Flask):
    """
    Inicializa el sistema de logging dual con fechas
    """
    from app.utils.logger import WhatsAppLogger
    
    print("[INFO] Configurando sistema de logging dual con organización por fechas...")
    
    environment = app.config.get('FLASK_ENV', 'development')
    WhatsAppLogger.configure_logging(
        log_level='INFO',
        environment=environment,
        use_date_structure=True,    # logs/2025/08/26/api.log
        dual_output=True           # Terminal + Archivos simultáneamente
    )
    
    print("[OK] Sistema de logging dual con fechas configurado correctamente")

def _initialize_extensions(app: Flask):
    """
    Inicializa extensiones Flask (CORS, Rate Limiting, Redis)
    """
    from app.extensions import _init_cors, _init_rate_limiting, _init_redis
    
    try:
        _init_cors(app)
        _init_rate_limiting(app)
        _init_redis(app)
        print("[OK] Extensiones Flask inicializadas (CORS, Rate Limiting, Redis)")
    except Exception as e:
        print(f"[WARNING] Error inicializando extensiones: {e}")

def _initialize_database(app: Flask):
    """
    Inicializa la base de datos
    """
    try:
        from database.connection import init_database
        init_database(app)
        print("[OK] Base de datos inicializada")
    except Exception as e:
        print(f"[WARNING] Error inicializando base de datos: {e}")

def _register_blueprints(app: Flask):
    """
    Registra blueprints y namespaces de la API
    """
    from flask_restx import Api
    
    # Crear API principal con configuración completa
    api_config = {
        'title': 'WhatsApp API Microservice',
        'version': '1.0.0',
        'description': '''
        API completa para integración con WhatsApp Business API
        
        ## Características principales:
        - Envío de mensajes de texto, multimedia e interactivos
        - Gestión de contactos y perfiles
        - Procesamiento de webhooks en tiempo real
        - Soporte multi-línea para múltiples números de WhatsApp
        - Autenticación por API Key
        - Rate limiting y control de tráfico
        
        ## Autenticación:
        Incluir header `X-API-Key` con tu API key válida en todas las requests.
        
        ### API Keys válidas en desarrollo:
        - dev-api-key
        - test-key-123
        - test_key
        
        ### Ejemplo de uso:
        ```bash
        curl -H "X-API-Key: dev-api-key" http://localhost:5001/v1/messages/test
        ```
        ''',
        'doc': '/docs',
        'authorizations': {
            'ApiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key',
                'description': 'API Key para autenticación. Usar: dev-api-key'
            }
        },
        'security': 'ApiKeyAuth'
    }
    
    # Agregar información adicional
    api_config['contact'] = {
        'name': 'Equipo de Desarrollo',
        'url': 'https://github.com/tcondori/whatsapp-api-microservice'
    }
    api_config['license'] = {
        'name': 'MIT',
        'url': 'https://opensource.org/licenses/MIT'
    }
    
    api = Api(app, **api_config)
    
    # Registrar namespaces principales
    try:
        from app.api.messages.routes import messages_ns
        api.add_namespace(messages_ns, path='/v1/messages')
        print("[OK] Namespace de mensajes registrado")
    except Exception as e:
        print(f"[WARNING] Error registrando mensajes: {e}")
    
    # Intentar registrar otros namespaces si existen
    try:
        from app.api.contacts.routes import contacts_ns
        api.add_namespace(contacts_ns, path='/v1/contacts')
        print("[OK] Namespace de contactos registrado")
    except Exception as e:
        print(f"[WARNING] Error registrando contactos: {e}")
    
    try:
        from app.api.media.routes import media_ns
        api.add_namespace(media_ns, path='/v1/media')
        print("[OK] Namespace de media registrado")
    except Exception as e:
        print(f"[WARNING] Error registrando media: {e}")
    
    try:
        from app.api.webhooks.routes import webhook_ns
        api.add_namespace(webhook_ns, path='/v1/webhooks')
        print("[OK] Namespace de webhooks registrado")
    except Exception as e:
        print(f"[WARNING] Error registrando webhooks: {e}")
    
    # Registrar blueprint del simulador de chat
    try:
        from app.chatbot import chatbot_bp
        app.register_blueprint(chatbot_bp)
        print("[OK] Blueprint de simulador de chat registrado")
    except Exception as e:
        print(f"[WARNING] Error registrando simulador de chat: {e}")
    
    # Registrar blueprint del editor RiveScript
    try:
        from app.api.rivescript_simple import rivescript_simple_bp
        app.register_blueprint(rivescript_simple_bp)
        print("[OK] Blueprint de editor RiveScript registrado")
    except Exception as e:
        print(f"[WARNING] Error registrando editor RiveScript: {e}")
    
    # Health check mejorado con más información
    @app.route('/health')
    def health_check():
        """Health check completo con información del sistema"""
        from app.utils.date_utils import get_timezone_info
        
        # Obtener información de timezone si está disponible
        try:
            timezone_info = get_timezone_info()
        except:
            timezone_info = {
                'timezone_name': 'UTC',
                'offset_string': '+00:00',
                'current_local': 'N/A',
                'current_utc': 'N/A'
            }
        
        # Verificar Redis si está disponible
        redis_status = 'disconnected'
        try:
            from app.extensions import is_redis_available
            redis_status = 'connected' if is_redis_available() else 'disconnected'
        except:
            redis_status = 'not_configured'
        
        return {
            'status': 'healthy',
            'service': 'WhatsApp API Microservice',
            'version': '1.0.0',
            'environment': app.config.get('FLASK_ENV', 'development'),
            'database': 'connected',
            'redis': redis_status,
            'components': {
                'messages': 'ready',
                'contacts': 'ready',
                'media': 'ready', 
                'webhooks': 'ready'
            },
            'timezone': timezone_info,
            'endpoints_info': [
                {"method": "POST", "path": "/v1/messages/text", "description": "Enviar mensaje de texto"},
                {"method": "POST", "path": "/v1/messages/image", "description": "Enviar mensaje de imagen"},
                {"method": "POST", "path": "/v1/messages/location", "description": "Enviar mensaje de ubicación"},
                {"method": "POST", "path": "/v1/messages/contacts", "description": "Enviar mensaje de contactos"},
                {"method": "GET", "path": "/v1/messages/test", "description": "Endpoint de prueba"},
                {"method": "GET", "path": "/docs", "description": "Documentación Swagger"},
                {"method": "GET", "path": "/health", "description": "Health check"}
            ],
            'api_keys': {
                'header_required': 'X-API-Key',
                'valid_keys': app.config.get('VALID_API_KEYS', ['dev-api-key']),
                'example': 'curl -H "X-API-Key: dev-api-key" http://localhost:5001/v1/messages/test'
            }
        }

def _register_error_handlers(app: Flask):
    """
    Registra manejadores de errores globales mejorados
    """
    from app.utils.logger import WhatsAppLogger
    
    # Obtener loggers para errores
    api_logger = WhatsAppLogger.get_logger('api')
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Maneja endpoints no encontrados"""
        api_logger.warning(f"Endpoint no encontrado: {error}")
        return {
            'error': 'NOT_FOUND',
            'message': 'Endpoint no encontrado',
            'available_endpoints': [
                '/docs - Documentación Swagger',
                '/health - Health check',
                '/v1/messages/* - Endpoints de mensajes',
                '/v1/contacts/* - Endpoints de contactos',
                '/v1/media/* - Endpoints de media',
                '/v1/webhooks/* - Endpoints de webhooks'
            ]
        }, 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Maneja métodos HTTP no permitidos"""
        api_logger.warning(f"Método HTTP no permitido: {error}")
        return {
            'error': 'METHOD_NOT_ALLOWED',
            'message': 'Método HTTP no permitido para este endpoint',
            'hint': 'Verifica la documentación en /docs para métodos válidos'
        }, 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Maneja errores internos del servidor"""
        api_logger.error(f"Error interno del servidor: {error}")
        return {
            'error': 'INTERNAL_ERROR',
            'message': 'Error interno del servidor',
            'hint': 'Revisa los logs para más detalles'
        }, 500
    
    # Manejo de errores de autenticación si el módulo existe
    try:
        from app.utils.exceptions import (
            ValidationError, WhatsAppAPIError, AuthenticationError,
            RateLimitError, format_error_response, get_http_status_for_exception
        )
        
        @app.errorhandler(ValidationError)
        def handle_validation_error(error):
            """Maneja errores de validación"""
            api_logger.warning(f"Error de validación: {error.message}")
            return format_error_response(error), get_http_status_for_exception(error)
        
        @app.errorhandler(WhatsAppAPIError)
        def handle_whatsapp_error(error):
            """Maneja errores de la API de WhatsApp"""
            api_logger.error(f"Error de WhatsApp API: {error.message}")
            return format_error_response(error), get_http_status_for_exception(error)
        
        @app.errorhandler(AuthenticationError)
        def handle_auth_error(error):
            """Maneja errores de autenticación"""
            api_logger.warning(f"Error de autenticación: {error.message}")
            return format_error_response(error), get_http_status_for_exception(error)
        
        @app.errorhandler(RateLimitError)
        def handle_rate_limit_error(error):
            """Maneja errores de límite de velocidad"""
            api_logger.warning(f"Límite de velocidad excedido: {error.message}")
            response = format_error_response(error), get_http_status_for_exception(error)
            if hasattr(error, 'retry_after') and error.retry_after:
                response[1]['Retry-After'] = str(error.retry_after)
            return response
            
        print("[OK] Manejadores de errores personalizados registrados")
            
    except ImportError:
        print("[OK] Manejadores de errores básicos registrados (excepciones personalizadas no disponibles)")

def _register_cli_commands(app: Flask):
    """
    Registra comandos de línea de comandos personalizados
    """
    from flask.cli import with_appcontext
    import click
    
    @app.cli.command()
    @with_appcontext
    def init_db():
        """Inicializa la base de datos con todas las tablas"""
        try:
            from database.connection import db
            db.create_all()
            click.echo('[OK] Base de datos inicializada correctamente.')
        except Exception as e:
            click.echo(f'[ERROR] Error inicializando base de datos: {e}')
    
    @app.cli.command()
    @with_appcontext
    def reset_db():
        """Resetea completamente la base de datos"""
        try:
            from database.connection import db
            
            if click.confirm('[WARNING] Esto eliminará todos los datos. ¿Continuar?'):
                db.drop_all()
                db.create_all()
                click.echo('[OK] Base de datos reseteada correctamente.')
            else:
                click.echo('[INFO] Operación cancelada.')
        except Exception as e:
            click.echo(f'[ERROR] Error reseteando base de datos: {e}')
    
    @app.cli.command()
    @click.option('--line-id', default='line_1', help='ID de la línea a crear')
    @click.option('--display-name', default='Línea Principal', help='Nombre a mostrar')
    @click.option('--phone-number-id', prompt=True, help='Phone Number ID de WhatsApp')
    @with_appcontext
    def create_messaging_line(line_id, display_name, phone_number_id):
        """Crea una nueva línea de mensajería"""
        try:
            from database.models import MessagingLine
            from database.connection import db
            
            line = MessagingLine(
                line_id=line_id,
                display_name=display_name,
                phone_number_id=phone_number_id,
                is_active=True
            )
            
            db.session.add(line)
            db.session.commit()
            click.echo(f'[OK] Línea "{line_id}" creada correctamente.')
        except Exception as e:
            try:
                from database.connection import db
                db.session.rollback()
            except:
                pass
            click.echo(f'[ERROR] Error creando línea: {e}')
    
    @app.cli.command()
    @with_appcontext  
    def test_config():
        """Verifica la configuración de la aplicación"""
        click.echo('[INFO] Verificando configuración...')
        
        # Verificar configuraciones críticas
        configs_to_check = [
            'SECRET_KEY',
            'WHATSAPP_ACCESS_TOKEN',
            'WEBHOOK_VERIFY_TOKEN', 
            'WEBHOOK_SECRET',
            'SQLALCHEMY_DATABASE_URI',
            'REDIS_URL',
            'VALID_API_KEYS'
        ]
        
        for config_key in configs_to_check:
            value = app.config.get(config_key)
            status = '[OK]' if value else '[ERROR]'
            
            # Enmascarar valores sensibles
            if value and ('SECRET' in config_key or 'TOKEN' in config_key):
                masked_value = '***'
            elif isinstance(value, list):
                masked_value = f"[{len(value)} items]"
            else:
                masked_value = str(value)[:50] + '...' if value and len(str(value)) > 50 else value
                
            click.echo(f'{status} {config_key}: {masked_value}')
    
    @app.cli.command()
    @with_appcontext
    def show_routes():
        """Muestra todas las rutas disponibles"""
        click.echo('[INFO] RUTAS DISPONIBLES:')
        click.echo('-' * 50)
        
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            click.echo(f'{methods:8} {rule.rule:30} {rule.endpoint}')
    
    print("[OK] Comandos CLI personalizados registrados")
