"""
Punto de entrada principal de la aplicación WhatsApp API Microservice
Inicializa la aplicación Flask usando el patrón Factory
"""
import os
import sys
from dotenv import load_dotenv
from flask import Flask

# Cargar variables de entorno desde .env
load_dotenv()
from flask_restx import Api
from app.extensions import init_extensions
from database.connection import init_database
from config import get_config
from app.utils.exceptions import (
    ValidationError, WhatsAppAPIError, AuthenticationError,
    RateLimitError, format_error_response, get_http_status_for_exception
)
import logging

def create_app() -> Flask:
    """
    Crea y configura la aplicación Flask usando el patrón Factory
    Returns:
        Flask: Instancia configurada de la aplicación
    """
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Cargar configuración según el entorno
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Validar configuración crítica
    _validate_configuration(app)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Inicializar base de datos
    init_database(app)
    
    # Crear API con documentación Swagger
    api = _create_api(app)
    
    # Registrar namespaces de la API
    _register_api_namespaces(api)
    
    # Registrar manejadores de errores
    _register_error_handlers(app)
    
    # Registrar comandos CLI
    _register_cli_commands(app)
    
    # Log de inicialización exitosa
    logging.info(f"Aplicación WhatsApp API inicializada correctamente en modo {app.config.get('FLASK_ENV', 'development')}")
    
    return app

def _validate_configuration(app: Flask):
    """
    Valida configuración crítica de la aplicación
    Args:
        app: Instancia de la aplicación Flask
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
        error_msg = f"Configuración faltante: {', '.join(missing_configs)}"
        logging.error(error_msg)
        if not app.config.get('DEBUG'):
            # En producción, fallar si falta configuración crítica
            raise RuntimeError(error_msg)
        else:
            logging.warning("Ejecutando en modo desarrollo con configuración incompleta")

def _create_api(app: Flask) -> Api:
    """
    Crea y configura la API con documentación Swagger
    Args:
        app: Instancia de la aplicación Flask
    Returns:
        Api: Instancia de Flask-RESTX API
    """
    # Configuración de la documentación de la API
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
        ''',
        'doc': '/docs/',
        'authorizations': {
            'apiKey': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key',
                'description': 'API Key para autenticación'
            }
        },
        'security': 'apiKey'
    }
    
    # Agregar información adicional al config antes de crear la API
    api_config['contact'] = {
        'name': 'Equipo de Desarrollo',
        'url': 'https://github.com/tu-org/whatsapp-api-microservice'
    }
    api_config['license'] = {
        'name': 'MIT',
        'url': 'https://opensource.org/licenses/MIT'
    }
    
    # Crear la instancia de API con toda la configuración
    api = Api(app, **api_config)
    
    return api

def _register_api_namespaces(api: Api):
    """
    Registra todos los namespaces de la API
    Args:
        api: Instancia de Flask-RESTX Api
    """
    # Importar todos los namespaces
    from app.api.messages.routes import messages_ns
    from app.api.contacts.routes import contacts_ns
    from app.api.media.routes import media_ns
    from app.api.webhooks.routes import webhook_ns
    
    # Registrar namespaces con sus rutas
    api.add_namespace(messages_ns, path='/v1/messages')
    api.add_namespace(contacts_ns, path='/v1/contacts')
    api.add_namespace(media_ns, path='/v1/media')
    api.add_namespace(webhook_ns, path='/v1/webhooks')
    
    # Health check general (sin autenticación para testing)
    from flask_restx import Resource
    from flask import current_app
    
    @api.route('/health')
    class GeneralHealth(Resource):
        def get(self):
            """Health check general de la aplicación"""
            from app.extensions import is_redis_available
            
            return {
                'status': 'healthy',
                'service': 'WhatsApp API Microservice',
                'version': '1.0.0',
                'environment': current_app.config.get('FLASK_ENV', 'development'),
                'database': 'connected',
                'redis': 'connected' if is_redis_available() else 'disconnected',
                'components': {
                    'messages': 'ready',
                    'contacts': 'ready', 
                    'media': 'ready',
                    'webhooks': 'ready'
                }
            }

def _register_error_handlers(app: Flask):
    """
    Registra manejadores de errores globales
    Args:
        app: Instancia de la aplicación Flask
    """
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Maneja errores de validación"""
        logging.warning(f"Error de validación: {error.message}")
        return format_error_response(error), get_http_status_for_exception(error)
    
    @app.errorhandler(WhatsAppAPIError)
    def handle_whatsapp_error(error):
        """Maneja errores de la API de WhatsApp"""
        logging.error(f"Error de WhatsApp API: {error.message}")
        return format_error_response(error), get_http_status_for_exception(error)
    
    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        """Maneja errores de autenticación"""
        logging.warning(f"Error de autenticación: {error.message}")
        return format_error_response(error), get_http_status_for_exception(error)
    
    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(error):
        """Maneja errores de límite de velocidad"""
        logging.warning(f"Límite de velocidad excedido: {error.message}")
        response = format_error_response(error), get_http_status_for_exception(error)
        if hasattr(error, 'retry_after') and error.retry_after:
            response[1]['Retry-After'] = str(error.retry_after)
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Maneja endpoints no encontrados"""
        return {
            'error': 'NOT_FOUND',
            'message': 'Endpoint no encontrado',
            'timestamp': app.extensions.get('current_timestamp', '')
        }, 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Maneja métodos HTTP no permitidos"""
        return {
            'error': 'METHOD_NOT_ALLOWED',
            'message': 'Método HTTP no permitido para este endpoint',
            'timestamp': app.extensions.get('current_timestamp', '')
        }, 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Maneja errores internos del servidor"""
        logging.error(f"Error interno del servidor: {str(error)}")
        return {
            'error': 'INTERNAL_ERROR',
            'message': 'Error interno del servidor',
            'timestamp': app.extensions.get('current_timestamp', '')
        }, 500

def _register_cli_commands(app: Flask):
    """
    Registra comandos de línea de comandos personalizados
    Args:
        app: Instancia de la aplicación Flask
    """
    from flask.cli import with_appcontext
    import click
    
    @app.cli.command()
    @with_appcontext
    def init_db():
        """Inicializa la base de datos con todas las tablas"""
        from database.connection import db
        db.create_all()
        click.echo('✅ Base de datos inicializada correctamente.')
    
    @app.cli.command()
    @with_appcontext
    def reset_db():
        """Resetea completamente la base de datos"""
        from database.connection import db
        
        click.confirm('⚠️  Esto eliminará todos los datos. ¿Continuar?', abort=True)
        
        db.drop_all()
        db.create_all()
        click.echo('✅ Base de datos reseteada correctamente.')
    
    @app.cli.command()
    @click.option('--line-id', default='line_1', help='ID de la línea a crear')
    @click.option('--display-name', default='Línea Principal', help='Nombre a mostrar')
    @click.option('--phone-number-id', prompt=True, help='Phone Number ID de WhatsApp')
    @with_appcontext
    def create_messaging_line(line_id, display_name, phone_number_id):
        """Crea una nueva línea de mensajería"""
        from database.models import MessagingLine
        from database.connection import db
        
        line = MessagingLine(
            line_id=line_id,
            display_name=display_name,
            phone_number_id=phone_number_id,
            is_active=True
        )
        
        try:
            db.session.add(line)
            db.session.commit()
            click.echo(f'✅ Línea "{line_id}" creada correctamente.')
        except Exception as e:
            db.session.rollback()
            click.echo(f'❌ Error creando línea: {e}')
    
    @app.cli.command()
    @with_appcontext  
    def test_config():
        """Verifica la configuración de la aplicación"""
        click.echo('🔧 Verificando configuración...')
        
        # Verificar configuraciones críticas
        configs_to_check = [
            'SECRET_KEY',
            'WHATSAPP_ACCESS_TOKEN',
            'WEBHOOK_VERIFY_TOKEN', 
            'WEBHOOK_SECRET',
            'SQLALCHEMY_DATABASE_URI',
            'REDIS_URL'
        ]
        
        for config_key in configs_to_check:
            value = app.config.get(config_key)
            status = '✅' if value else '❌'
            masked_value = '***' if value and 'SECRET' in config_key or 'TOKEN' in config_key else value
            click.echo(f'{status} {config_key}: {masked_value}')

# Crear instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Configuración para ejecutar directamente
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    host = '0.0.0.0' if not debug else '127.0.0.1'
    
    print(f"🚀 Iniciando WhatsApp API Microservice en {host}:{port}")
    print(f"📚 Documentación disponible en: http://{host}:{port}/docs/")
    print(f"🏥 Health check en: http://{host}:{port}/health")
    
    app.run(host=host, port=port, debug=debug)
