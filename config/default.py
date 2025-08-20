"""
Configuración base compartida por todos los entornos
Incluye configuración de WhatsApp API, base de datos, Redis y seguridad
"""
import os
import json

class DefaultConfig:
    """Configuración base compartida por todos los entornos"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de WhatsApp API
    WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v18.0')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ID')
    WHATSAPP_API_BASE_URL = 'https://graph.facebook.com'
    
    # Configuración de líneas individuales (para compatibilidad)
    LINE_1_PHONE_NUMBER_ID = os.getenv('LINE_1_PHONE_NUMBER_ID')
    LINE_1_DISPLAY_NAME = os.getenv('LINE_1_DISPLAY_NAME', 'Línea Principal')
    LINE_1_PHONE_NUMBER = os.getenv('LINE_1_PHONE_NUMBER')
    LINE_1_IS_ACTIVE = os.getenv('LINE_1_IS_ACTIVE', 'true').lower() == 'true'
    LINE_1_MAX_DAILY_MESSAGES = int(os.getenv('LINE_1_MAX_DAILY_MESSAGES', '1000'))
    
    # Configuración de soporte multi-línea
    # Líneas de mensajería soportadas (JSON string)
    MESSAGING_LINES = os.getenv('MESSAGING_LINES', '[]')
    DEFAULT_LINE_ID = os.getenv('DEFAULT_LINE_ID', 'line_1')
    
    # Configuración de Webhooks
    WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    
    # Configuración de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Configuración de Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Configuración de Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Configuración de Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    
    # Configuración de API Keys válidas
    VALID_API_KEYS = os.getenv('VALID_API_KEYS', '').split(',')
    
    @staticmethod
    def get_messaging_lines():
        """
        Obtiene las líneas de mensajería configuradas
        Returns:
            dict: Diccionario con las líneas configuradas
        """
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
