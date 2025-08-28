"""
Sistema de logging estructurado para WhatsApp API Microservice
Proporciona configuración centralizada de logs con formato JSON y manejo de eventos
Soporta logging dual: terminal en tiempo real + persistencia en archivos
"""

import json
import logging
import logging.handlers
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import wraps

from flask import request, g

# Importar colorlog para logs en terminal (desarrollo)
try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


class SimpleTextFormatter(logging.Formatter):
    """
    Formateador simple para logs en terminal - legible y conciso
    Estilo similar a la opción 2 que el usuario prefiere
    """
    
    def __init__(self, include_colors: bool = False):
        self.include_colors = include_colors and COLORLOG_AVAILABLE
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Genera formato de log simple con información útil
        """
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Agregar información extra si está disponible
        extra_info = ""
        if hasattr(record, 'extra_data') and record.extra_data:
            # Extraer información clave del extra_data
            data = record.extra_data
            if 'phone_number' in data:
                extra_info += f" | Phone: {data['phone_number']}"
            if 'message_type' in data:
                extra_info += f" | Type: {data['message_type']}"
            if 'execution_time_ms' in data:
                extra_info += f" | Time: {data['execution_time_ms']:.2f}ms"
            if 'status_code' in data:
                extra_info += f" | Status: {data['status_code']}"
        
        # Formato base: [HH:MM:SS] LEVEL - MESSAGE | Info adicional
        log_line = f"[{timestamp}] {record.levelname:<8} - {record.getMessage()}{extra_info}"
        
        return log_line


class JsonFormatter(logging.Formatter):
    """
    Formateador personalizado para generar logs en formato JSON estructurado
    Facilita el análisis automatizado y la integración con sistemas de monitoreo
    """
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Convierte el registro de log en formato JSON estructurado
        """
        # Información base del log
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información de request si está disponible
        try:
            from flask import has_app_context, g
            if has_app_context() and hasattr(g, 'request_id'):
                log_entry['request_id'] = g.request_id
        except (ImportError, RuntimeError):
            # No hay Flask disponible o no hay contexto activo
            pass
            
        # Agregar información de contexto de Flask si está disponible
        try:
            if request:
                log_entry['request_context'] = {
                    'method': request.method,
                    'url': request.url,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'Unknown')
                }
        except RuntimeError:
            # No hay contexto de request disponible
            pass
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Agregar campos extra si están incluidos
        if self.include_extra and hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)


class WhatsAppLogger:
    """
    Configurador centralizado del sistema de logging para WhatsApp API
    Maneja diferentes tipos de loggers y configuraciones por entorno
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured: bool = False
    
    # Constantes para nombres de loggers
    API_LOGGER = 'whatsapp_api'
    WEBHOOK_LOGGER = 'whatsapp_webhook'  
    SERVICE_LOGGER = 'whatsapp_service'
    DATABASE_LOGGER = 'whatsapp_database'
    SECURITY_LOGGER = 'whatsapp_security'
    PERFORMANCE_LOGGER = 'whatsapp_performance'
    
    @classmethod
    def configure_logging(cls, 
                         log_level: str = 'INFO',
                         log_dir: str = 'logs',
                         environment: str = 'development',
                         max_file_size: int = 10 * 1024 * 1024,  # 10MB
                         backup_count: int = 5,
                         use_date_structure: bool = True,
                         dual_output: bool = True) -> None:
        """
        Configura el sistema de logging dual: terminal en tiempo real + persistencia en archivos
        
        Args:
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directorio base donde almacenar los archivos de log
            environment: Entorno de ejecución (development, production)
            max_file_size: Tamaño máximo de archivo de log antes de rotar
            backup_count: Número de archivos de backup a mantener
            use_date_structure: Si usar estructura organizadas por fechas
            dual_output: Si usar salida dual (terminal + archivos)
        """
        if cls._configured:
            return
        
        # Si se solicita estructura por fechas, usar el nuevo sistema
        if use_date_structure:
            try:
                from app.utils.log_config import initialize_dated_logging
                result = initialize_dated_logging(None, environment, dual_output=dual_output)
                cls._configured = True
                return
            except ImportError:
                # Fallback al sistema anterior si no está disponible
                pass
            
        # Crear directorio de logs si no existe
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Configurar nivel de logging
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configurar formateadores según entorno y salida
        if environment == 'production':
            # Producción: JSON para archivos, texto simple para consola (si dual_output)
            file_formatter = JsonFormatter(include_extra=True)
            console_formatter = SimpleTextFormatter(include_colors=False) if dual_output else JsonFormatter(include_extra=False)
        else:
            # Desarrollo: JSON para archivos, texto con colores para terminal
            file_formatter = JsonFormatter(include_extra=True)
            console_formatter = SimpleTextFormatter(include_colors=True)
        
        # Configurar handler para archivos con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / 'whatsapp_api.log',
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        
        # Configurar handler para terminal (si dual_output habilitado)
        console_handler = None
        if dual_output:
            if COLORLOG_AVAILABLE and environment == 'development':
                # Terminal con colores en desarrollo
                console_handler = colorlog.StreamHandler()
                color_formatter = colorlog.ColoredFormatter(
                    '%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s - %(message)s',
                    datefmt='%H:%M:%S',
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                )
                console_handler.setFormatter(color_formatter)
            else:
                # Terminal simple
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(console_formatter)
            
            console_handler.setLevel(level)
        
        # Configurar handlers específicos por componente
        cls._configure_component_loggers(log_path, file_formatter, console_formatter if dual_output else None, 
                                       level, max_file_size, backup_count, dual_output)
        
        # Configurar logger root
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        
        # Agregar console handler si dual_output habilitado
        if dual_output and console_handler:
            root_logger.addHandler(console_handler)
            
        cls._configured = True
    
    @classmethod
    def _configure_component_loggers(cls, log_path: Path, file_formatter: logging.Formatter,
                                   console_formatter: Optional[logging.Formatter],
                                   level: int, max_file_size: int, backup_count: int,
                                   dual_output: bool = True) -> None:
        """
        Configura loggers específicos para cada componente del sistema con salida dual
        """
        components = {
            cls.API_LOGGER: 'api.log',
            cls.WEBHOOK_LOGGER: 'webhooks.log',
            cls.SERVICE_LOGGER: 'services.log', 
            cls.DATABASE_LOGGER: 'database.log',
            cls.SECURITY_LOGGER: 'security.log',
            cls.PERFORMANCE_LOGGER: 'performance.log'
        }
        
        for logger_name, log_file in components.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            
            # Handler para archivo específico del componente
            file_handler = logging.handlers.RotatingFileHandler(
                log_path / log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)
            
            # Handler para terminal si dual_output habilitado
            if dual_output and console_formatter:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(console_formatter)
                console_handler.setLevel(level)
                logger.addHandler(console_handler)
                
            # Prevenir propagación duplicada
            logger.propagate = False
            
            cls._loggers[logger_name] = logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Obtiene un logger por nombre, lo crea si no existe
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Si no existe, crear logger estándar
        logger = logging.getLogger(name)
        cls._loggers[name] = logger
        return logger


class EventLogger:
    """
    Sistema de logging específico para eventos del sistema WhatsApp
    Maneja eventos estructurados con contexto adicional
    """
    
    def __init__(self, logger_name: str = WhatsAppLogger.API_LOGGER):
        self.logger = WhatsAppLogger.get_logger(logger_name)
    
    def log_whatsapp_request(self, endpoint: str, method: str, payload: Dict[str, Any],
                           phone_number: str = None, message_id: str = None) -> None:
        """
        Registra llamadas a la API de WhatsApp
        """
        event_data = {
            'event_type': 'whatsapp_api_request',
            'endpoint': endpoint,
            'method': method,
            'phone_number': self._sanitize_phone(phone_number),
            'message_id': message_id,
            'payload_size': len(str(payload))
        }
        
        self.logger.info(
            f"WhatsApp API Request: {method} {endpoint}",
            extra={'extra_data': event_data}
        )
    
    def log_whatsapp_response(self, endpoint: str, status_code: int, 
                            response_data: Dict[str, Any], 
                            response_time_ms: float) -> None:
        """
        Registra respuestas de la API de WhatsApp
        """
        event_data = {
            'event_type': 'whatsapp_api_response',
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'response_size': len(str(response_data)),
            'success': 200 <= status_code < 300
        }
        
        level = logging.INFO if event_data['success'] else logging.ERROR
        self.logger.log(
            level,
            f"WhatsApp API Response: {status_code} from {endpoint} ({response_time_ms}ms)",
            extra={'extra_data': event_data}
        )
    
    def log_webhook_received(self, webhook_type: str, phone_number: str,
                           message_id: str = None, payload: Dict[str, Any] = None) -> None:
        """
        Registra webhooks recibidos de WhatsApp
        """
        event_data = {
            'event_type': 'webhook_received',
            'webhook_type': webhook_type,
            'phone_number': self._sanitize_phone(phone_number),
            'message_id': message_id,
            'payload_present': payload is not None
        }
        
        self.logger.info(
            f"Webhook received: {webhook_type} from {self._sanitize_phone(phone_number)}",
            extra={'extra_data': event_data}
        )
    
    def log_message_sent(self, phone_number: str, message_type: str, 
                        message_id: str, template_name: str = None) -> None:
        """
        Registra mensajes enviados a través de WhatsApp
        """
        event_data = {
            'event_type': 'message_sent',
            'phone_number': self._sanitize_phone(phone_number),
            'message_type': message_type,
            'message_id': message_id,
            'template_name': template_name
        }
        
        self.logger.info(
            f"Message sent: {message_type} to {self._sanitize_phone(phone_number)}",
            extra={'extra_data': event_data}
        )
    
    def log_security_event(self, event_type: str, ip_address: str, 
                          user_agent: str = None, details: Dict[str, Any] = None) -> None:
        """
        Registra eventos de seguridad
        """
        security_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SECURITY_LOGGER)
        
        event_data = {
            'event_type': f'security_{event_type}',
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        security_logger.warning(
            f"Security event: {event_type} from {ip_address}",
            extra={'extra_data': event_data}
        )
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             unit: str, tags: Dict[str, str] = None) -> None:
        """
        Registra métricas de performance del sistema
        """
        perf_logger = WhatsAppLogger.get_logger(WhatsAppLogger.PERFORMANCE_LOGGER)
        
        metric_data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {},
            'timestamp': time.time()
        }
        
        perf_logger.info(
            f"Performance metric: {metric_name}={value}{unit}",
            extra={'extra_data': metric_data}
        )
    
    @staticmethod
    def _sanitize_phone(phone_number: str) -> str:
        """
        Sanitiza números de teléfono para logging (mantiene privacidad)
        """
        if not phone_number or phone_number.strip() == '':
            return None if phone_number is None else ''
        
        # Limpiar el número
        clean_phone = phone_number.strip()
        
        # Mostrar solo primeros 3 y últimos 2 dígitos
        if len(clean_phone) > 5:
            return f"{clean_phone[:3]}***{clean_phone[-2:]}"
        return "****"


def log_execution_time(logger_name: str = WhatsAppLogger.PERFORMANCE_LOGGER):
    """
    Decorador para registrar tiempo de ejecución de funciones
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = WhatsAppLogger.get_logger(logger_name)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # en ms
                
                logger.info(
                    f"Function {func.__name__} executed in {execution_time:.2f}ms",
                    extra={'extra_data': {
                        'function_name': func.__name__,
                        'execution_time_ms': execution_time,
                        'success': True
                    }}
                )
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}",
                    extra={'extra_data': {
                        'function_name': func.__name__,
                        'execution_time_ms': execution_time,
                        'success': False,
                        'error': str(e)
                    }},
                    exc_info=True
                )
                raise
                
        return wrapper
    return decorator


def log_api_call(logger_name: str = WhatsAppLogger.API_LOGGER):
    """
    Decorador para registrar llamadas a endpoints de la API
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = WhatsAppLogger.get_logger(logger_name)
            
            # Registrar inicio de llamada
            logger.info(
                f"API call started: {func.__name__}",
                extra={'extra_data': {
                    'endpoint_function': func.__name__,
                    'event_type': 'api_call_start'
                }}
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Registrar éxito
                logger.info(
                    f"API call completed: {func.__name__}",
                    extra={'extra_data': {
                        'endpoint_function': func.__name__,
                        'event_type': 'api_call_success'
                    }}
                )
                
                return result
                
            except Exception as e:
                # Registrar error
                logger.error(
                    f"API call failed: {func.__name__} - {str(e)}",
                    extra={'extra_data': {
                        'endpoint_function': func.__name__,
                        'event_type': 'api_call_error',
                        'error': str(e)
                    }},
                    exc_info=True
                )
                raise
                
        return wrapper
    return decorator