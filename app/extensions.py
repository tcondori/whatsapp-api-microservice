"""
Configuración e inicialización de extensiones Flask
Gestiona CORS, Rate Limiting, Redis, Logging y otras extensiones
"""
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import logging
from logging.handlers import RotatingFileHandler
import os

# Inicializar extensiones sin contexto de aplicación
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Cliente Redis global
redis_client = None

def init_extensions(app):
    """
    Inicializa todas las extensiones Flask con la aplicación
    Args:
        app: Instancia de la aplicación Flask
    """
    # Configurar CORS
    _init_cors(app)
    
    # Configurar Rate Limiting
    _init_rate_limiting(app)
    
    # Configurar Redis
    _init_redis(app)
    
    # Configurar sistema de Logging
    _init_logging(app)
    
    logging.info("Todas las extensiones Flask inicializadas correctamente")

def _init_cors(app):
    """
    Configura CORS (Cross-Origin Resource Sharing)
    Args:
        app: Instancia de la aplicación Flask
    """
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    
    cors.init_app(
        app,
        origins=cors_origins,
        allow_headers=[
            'Content-Type', 
            'Authorization', 
            'X-API-Key', 
            'X-Hub-Signature-256',
            'Accept',
            'Origin',
            'X-Requested-With'
        ],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        supports_credentials=True
    )
    
    logging.info(f"CORS configurado con orígenes: {cors_origins}")

def _init_rate_limiting(app):
    """
    Configura el sistema de Rate Limiting
    Args:
        app: Instancia de la aplicación Flask
    """
    # Configurar el storage backend para rate limiting
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URL')
    
    # Inicializar con la aplicación
    limiter.init_app(app)
    
    # Configurar límites por defecto desde config
    default_limits = app.config.get('RATELIMIT_DEFAULT', "1000 per hour")
    limiter._default_limits = [default_limits]
    
    logging.info(f"Rate limiting configurado: {default_limits}")

def _init_redis(app):
    """
    Configura la conexión a Redis para cache y sesiones
    Args:
        app: Instancia de la aplicación Flask
    """
    global redis_client
    
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379')
    
    try:
        # Crear pool de conexiones Redis
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Probar la conexión
        redis_client.ping()
        
        # Hacer disponible el cliente en la aplicación
        app.redis = redis_client
        
        logging.info(f"Redis conectado correctamente: {redis_url}")
        
    except (redis.RedisError, ConnectionError) as e:
        logging.warning(f"No se pudo conectar a Redis: {e}. Funcionando sin cache.")
        redis_client = None
        app.redis = None

def _init_logging(app):
    """
    Configura el sistema de logging avanzado de la aplicación
    Args:
        app: Instancia de la aplicación Flask
    """
    try:
        # Usar el sistema de logging estructurado
        from app.utils.log_config import initialize_logging
        from app.utils.middleware import init_application_logging
        
        # Obtener entorno desde config o variables de entorno
        environment = app.config.get('FLASK_ENV', os.getenv('FLASK_ENV', 'development'))
        log_level = app.config.get('LOG_LEVEL', 'INFO')
        
        # Inicializar sistema de logging estructurado
        logging_info = initialize_logging(app.config, environment)
        
        # Configurar middleware de logging para la aplicación
        handlers = init_application_logging(app, log_level, environment)
        
        # Hacer disponibles los handlers en el contexto de la app
        app.logging_handlers = handlers
        app.logging_environment = environment
        
        # Configurar logging para bibliotecas externas con el nuevo sistema
        from app.utils.logger import WhatsAppLogger
        
        # Silenciar logs verbosos de bibliotecas externas
        external_loggers = [
            'werkzeug', 'sqlalchemy.engine', 'requests', 
            'urllib3', 'flask_cors', 'flask_limiter'
        ]
        
        for logger_name in external_loggers:
            ext_logger = logging.getLogger(logger_name)
            ext_logger.setLevel(logging.WARNING)
        
        # Log de inicio exitoso
        system_logger = WhatsAppLogger.get_logger('system')
        system_logger.info(
            f"Sistema de logging avanzado inicializado correctamente",
            extra={'extra_data': {
                'environment': environment,
                'log_level': log_level,
                'structured_logging': True,
                'event_system': True,
                'aggregation_enabled': logging_info.get('aggregation_enabled', False)
            }}
        )
        
    except ImportError as e:
        # Fallback al sistema de logging básico si hay problemas
        logging.warning(f"No se pudo cargar sistema de logging avanzado: {e}")
        _init_basic_logging(app)


def _init_basic_logging(app):
    """
    Configura el sistema de logging básico como fallback
    Args:
        app: Instancia de la aplicación Flask
    """
    # Obtener configuración de logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_format = app.config.get('LOG_FORMAT', 
                               '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    
    # Configurar formato de logging
    formatter = logging.Formatter(log_format)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configurar handler para archivo (solo en producción)
    if not app.config.get('DEBUG'):
        # Crear directorio de logs si no existe
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Handler con rotación de archivos
        file_handler = RotatingFileHandler(
            'logs/whatsapp_api.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Agregar handler de archivo
        app.logger.addHandler(file_handler)
    
    # Agregar handler de consola
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Configurar loggers de bibliotecas externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Configurar logging para componentes del microservicio
    logging.getLogger('whatsapp_api').setLevel(log_level)
    
    logging.info(f"Sistema de logging básico configurado - Nivel: {log_level}")

def get_redis_client():
    """
    Obtiene el cliente Redis global
    Returns:
        redis.Redis: Cliente Redis o None si no está disponible
    """
    return redis_client

def is_redis_available() -> bool:
    """
    Verifica si Redis está disponible
    Returns:
        bool: True si Redis está conectado
    """
    if redis_client is None:
        return False
    
    try:
        redis_client.ping()
        return True
    except (redis.RedisError, ConnectionError):
        return False
