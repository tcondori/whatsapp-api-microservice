"""
Middleware de logging para Flask-RESTX
Intercepta requests y responses para logging automático
"""

import time
import uuid
from flask import Flask, request, g, jsonify
from functools import wraps
from typing import Any, Dict, Optional

from app.utils.logger import WhatsAppLogger, EventLogger
from app.utils.events import event_bus, EventType, Event
from datetime import datetime


class RequestLoggingMiddleware:
    """
    Middleware para logging automático de requests HTTP
    Registra información de entrada y salida de cada request
    """
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        self.event_logger = EventLogger()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """
        Inicializa el middleware con la aplicación Flask
        """
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
    
    def _before_request(self):
        """
        Ejecuta antes de cada request
        """
        # Generar ID único para el request
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Obtener información del request
        request_data = {
            'request_id': g.request_id,
            'method': request.method,
            'url': request.url,
            'endpoint': request.endpoint,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'content_length': request.content_length,
            'content_type': request.content_type
        }
        
        # Log del inicio del request
        self.logger.info(
            f"Request started: {request.method} {request.path}",
            extra={'extra_data': {
                'event_type': 'request_started',
                **request_data
            }}
        )
        
        # Emitir evento asíncrono
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(event_bus.publish(Event(
                event_type=EventType.API_REQUEST_STARTED,
                timestamp=datetime.utcnow(),
                source='api_middleware',
                data=request_data,
                correlation_id=g.request_id
            )))
        except RuntimeError:
            # No hay loop disponible, skip evento asíncrono
            pass
    
    def _after_request(self, response):
        """
        Ejecuta después de cada request
        """
        if hasattr(g, 'request_id') and hasattr(g, 'start_time'):
            # Calcular tiempo de respuesta
            response_time = (time.time() - g.start_time) * 1000  # en ms
            
            # Obtener información de respuesta
            response_data = {
                'request_id': g.request_id,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'content_length': response.content_length,
                'content_type': response.content_type
            }
            
            # Determinar nivel de log según status code
            if 400 <= response.status_code < 500:
                log_level = 'warning'
            elif response.status_code >= 500:
                log_level = 'error'
            else:
                log_level = 'info'
            
            # Log de la respuesta
            getattr(self.logger, log_level)(
                f"Request completed: {request.method} {request.path} - "
                f"{response.status_code} ({response_time:.2f}ms)",
                extra={'extra_data': {
                    'event_type': 'request_completed',
                    **response_data
                }}
            )
            
            # Emitir evento de finalización
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                loop.create_task(event_bus.publish(Event(
                    event_type=EventType.API_REQUEST_COMPLETED,
                    timestamp=datetime.utcnow(),
                    source='api_middleware',
                    data=response_data,
                    correlation_id=g.request_id
                )))
            except RuntimeError:
                pass
        
        return response
    
    def _teardown_request(self, exception):
        """
        Ejecuta al finalizar el contexto del request
        """
        if exception is not None and hasattr(g, 'request_id'):
            # Log de excepción no manejada
            self.logger.error(
                f"Request failed with exception: {str(exception)}",
                extra={'extra_data': {
                    'request_id': g.request_id,
                    'event_type': 'request_exception',
                    'exception': str(exception)
                }},
                exc_info=True
            )


class WhatsAppAPILoggingMiddleware:
    """
    Middleware específico para logging de llamadas a WhatsApp API
    """
    
    def __init__(self):
        self.logger = WhatsAppLogger.get_logger(WhatsAppLogger.SERVICE_LOGGER)
        self.event_logger = EventLogger()
    
    def log_api_call(self, func):
        """
        Decorador para logging de llamadas a WhatsApp API
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            call_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Extraer información de la llamada
            func_name = func.__name__
            
            # Log inicio de llamada
            self.logger.info(
                f"WhatsApp API call started: {func_name}",
                extra={'extra_data': {
                    'call_id': call_id,
                    'function': func_name,
                    'event_type': 'whatsapp_api_call_started'
                }}
            )
            
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                # Log éxito
                self.logger.info(
                    f"WhatsApp API call completed: {func_name} ({response_time:.2f}ms)",
                    extra={'extra_data': {
                        'call_id': call_id,
                        'function': func_name,
                        'response_time_ms': response_time,
                        'success': True,
                        'event_type': 'whatsapp_api_call_completed'
                    }}
                )
                
                return result
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                
                # Log error
                self.logger.error(
                    f"WhatsApp API call failed: {func_name} - {str(e)} ({response_time:.2f}ms)",
                    extra={'extra_data': {
                        'call_id': call_id,
                        'function': func_name,
                        'response_time_ms': response_time,
                        'success': False,
                        'error': str(e),
                        'event_type': 'whatsapp_api_call_failed'
                    }},
                    exc_info=True
                )
                
                raise
        
        return wrapper


class SecurityLoggingMiddleware:
    """
    Middleware para logging de eventos de seguridad
    """
    
    def __init__(self):
        self.security_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SECURITY_LOGGER)
    
    def log_authentication_attempt(self, func):
        """
        Decorador para logging de intentos de autenticación
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = getattr(g, 'request_id', str(uuid.uuid4()))
            
            # Información del intento de autenticación
            auth_data = {
                'request_id': request_id,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'endpoint': request.endpoint,
                'method': request.method
            }
            
            try:
                result = func(*args, **kwargs)
                
                # Autenticación exitosa
                self.security_logger.info(
                    f"Authentication successful from {request.remote_addr}",
                    extra={'extra_data': {
                        **auth_data,
                        'event_type': 'authentication_success',
                        'success': True
                    }}
                )
                
                return result
                
            except Exception as e:
                # Autenticación fallida
                self.security_logger.warning(
                    f"Authentication failed from {request.remote_addr}: {str(e)}",
                    extra={'extra_data': {
                        **auth_data,
                        'event_type': 'authentication_failed',
                        'success': False,
                        'error': str(e)
                    }}
                )
                
                raise
        
        return wrapper
    
    def log_rate_limit_hit(self, ip_address: str, endpoint: str, limit: int):
        """
        Registra cuando se alcanza un límite de rate limiting
        """
        self.security_logger.warning(
            f"Rate limit exceeded for {ip_address} on {endpoint}",
            extra={'extra_data': {
                'event_type': 'rate_limit_exceeded',
                'ip_address': ip_address,
                'endpoint': endpoint,
                'limit': limit,
                'timestamp': datetime.utcnow().isoformat()
            }}
        )
    
    def log_unauthorized_access(self, ip_address: str, endpoint: str, reason: str):
        """
        Registra intentos de acceso no autorizado
        """
        self.security_logger.error(
            f"Unauthorized access attempt from {ip_address} to {endpoint}: {reason}",
            extra={'extra_data': {
                'event_type': 'unauthorized_access',
                'ip_address': ip_address,
                'endpoint': endpoint,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }}
        )


class DatabaseLoggingMiddleware:
    """
    Middleware para logging de operaciones de base de datos
    """
    
    def __init__(self):
        self.db_logger = WhatsAppLogger.get_logger(WhatsAppLogger.DATABASE_LOGGER)
    
    def log_query_execution(self, func):
        """
        Decorador para logging de ejecución de queries
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            query_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Log inicio de query
            self.db_logger.debug(
                f"Database query started: {func.__name__}",
                extra={'extra_data': {
                    'query_id': query_id,
                    'function': func.__name__,
                    'event_type': 'db_query_started'
                }}
            )
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Log éxito
                self.db_logger.info(
                    f"Database query completed: {func.__name__} ({execution_time:.2f}ms)",
                    extra={'extra_data': {
                        'query_id': query_id,
                        'function': func.__name__,
                        'execution_time_ms': execution_time,
                        'success': True,
                        'event_type': 'db_query_completed'
                    }}
                )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                # Log error
                self.db_logger.error(
                    f"Database query failed: {func.__name__} - {str(e)} ({execution_time:.2f}ms)",
                    extra={'extra_data': {
                        'query_id': query_id,
                        'function': func.__name__,
                        'execution_time_ms': execution_time,
                        'success': False,
                        'error': str(e),
                        'event_type': 'db_query_failed'
                    }},
                    exc_info=True
                )
                
                raise
        
        return wrapper


# Instancias globales de middleware
request_logging = RequestLoggingMiddleware()
whatsapp_api_logging = WhatsAppAPILoggingMiddleware()
security_logging = SecurityLoggingMiddleware()
database_logging = DatabaseLoggingMiddleware()


def setup_logging_middleware(app: Flask):
    """
    Configura todos los middlewares de logging para la aplicación Flask
    """
    # Configurar middleware de requests
    request_logging.init_app(app)
    
    # Configurar manejo de errores global
    @app.errorhandler(404)
    def not_found_handler(e):
        logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        logger.warning(
            f"404 Not Found: {request.method} {request.path}",
            extra={'extra_data': {
                'event_type': '404_not_found',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'ip_address': request.remote_addr
            }}
        )
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error_handler(e):
        logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        logger.error(
            f"500 Internal Server Error: {request.method} {request.path}",
            extra={'extra_data': {
                'event_type': '500_internal_error',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'ip_address': request.remote_addr,
                'error': str(e)
            }},
            exc_info=True
        )
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def general_exception_handler(e):
        logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        logger.error(
            f"Unhandled exception: {str(e)}",
            extra={'extra_data': {
                'event_type': 'unhandled_exception',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'exception_type': type(e).__name__,
                'exception_message': str(e)
            }},
            exc_info=True
        )
        return jsonify({'error': 'An unexpected error occurred'}), 500


def init_application_logging(app: Flask, log_level: str = 'INFO', 
                           environment: str = 'development'):
    """
    Inicializa completamente el sistema de logging para la aplicación
    """
    # Configurar sistema de logging
    WhatsAppLogger.configure_logging(
        log_level=log_level,
        environment=environment
    )
    
    # Configurar middleware
    setup_logging_middleware(app)
    
    # Configurar manejadores de eventos por defecto
    from app.utils.events import setup_default_event_handlers
    handlers = setup_default_event_handlers()
    
    # Log de inicio del sistema
    system_logger = WhatsAppLogger.get_logger('system')
    system_logger.info(
        f"WhatsApp API Microservice started - Environment: {environment}",
        extra={'extra_data': {
            'event_type': 'system_startup',
            'environment': environment,
            'log_level': log_level
        }}
    )
    
    return handlers
