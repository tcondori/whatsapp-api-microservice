"""
Módulo de autenticación y autorización para el microservicio
Gestiona verificación de webhooks, API keys y tokens de seguridad
"""
# import jwt  # Temporalmente comentado para pruebas
import hmac
import hashlib
from functools import wraps
from flask import request, jsonify, current_app
import logging

def verify_whatsapp_signature(payload: bytes, signature: str) -> bool:
    """
    Verifica la firma del webhook de WhatsApp usando HMAC-SHA256
    Args:
        payload: Contenido del webhook en bytes
        signature: Firma del header X-Hub-Signature-256
    Returns:
        bool: True si la firma es válida
    """
    webhook_secret = current_app.config.get('WEBHOOK_SECRET')
    
    if not webhook_secret:
        logging.error("WEBHOOK_SECRET no configurado")
        return False
    
    if not signature:
        logging.warning("Signature no proporcionada en webhook")
        return False
    
    # La firma debe empezar con 'sha256='
    if not signature.startswith('sha256='):
        logging.warning("Formato de firma inválido")
        return False
    
    # Calcular la firma esperada
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Extraer la firma recibida (sin el prefijo 'sha256=')
    received_signature = signature[7:]
    
    # Comparación segura
    is_valid = hmac.compare_digest(expected_signature, received_signature)
    
    if not is_valid:
        logging.warning(f"Firma de webhook inválida. Esperada: {expected_signature[:10]}...")
    
    return is_valid

def require_api_key(f):
    """
    Decorador para requerir API key válida en endpoints protegidos
    Args:
        f: Función a proteger
    Returns:
        Función decorada que verifica API key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_restx import abort  # Import local para evitar circular imports
        
        # Buscar API key en headers
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            logging.warning(f"API key faltante desde IP: {request.remote_addr}")
            abort(401, 
                error='AUTHENTICATION_REQUIRED',
                message='API key requerida en header X-API-Key'
            )
        
        if not validate_api_key(api_key):
            logging.warning(f"API key inválida desde IP: {request.remote_addr}")
            abort(401,
                error='INVALID_API_KEY',
                message='API key inválida o expirada'
            )
        
        # Agregar información de autenticación al contexto de la request
        request.api_key = api_key
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_api_key(api_key: str) -> bool:
    """
    Valida la API key proporcionada contra la lista de claves válidas
    Args:
        api_key: Clave API a validar
    Returns:
        bool: True si la clave es válida
    """
    valid_keys = current_app.config.get('VALID_API_KEYS', [])
    
    # Filtrar claves vacías
    valid_keys = [key for key in valid_keys if key and key.strip()]
    
    if not valid_keys:
        logging.warning("No hay API keys válidas configuradas")
        return False
    
    return api_key in valid_keys

def require_webhook_signature(f):
    """
    Decorador para verificar firma de webhook de WhatsApp
    Args:
        f: Función del endpoint de webhook
    Returns:
        Función decorada que verifica firma
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_restx import abort  # Import local para evitar circular imports
        
        # Obtener el payload raw del request
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        
        if not verify_whatsapp_signature(payload, signature):
            logging.error(f"Webhook con firma inválida desde IP: {request.remote_addr}")
            abort(401,
                error='INVALID_SIGNATURE',
                message='Firma de webhook inválida'
            )
        
        return f(*args, **kwargs)
    
    return decorated_function

def extract_line_id_from_webhook(webhook_data: dict) -> str:
    """
    Extrae el ID de línea desde los datos del webhook
    Args:
        webhook_data: Datos del webhook de WhatsApp
    Returns:
        str: ID de la línea o línea por defecto
    """
    try:
        # Intentar extraer desde la estructura del webhook
        if 'entry' in webhook_data and webhook_data['entry']:
            entry = webhook_data['entry'][0]
            if 'id' in entry:
                # El ID del entry corresponde al phone_number_id
                phone_number_id = entry['id']
                
                # Buscar qué línea corresponde a este phone_number_id
                from config.default import DefaultConfig
                lines = DefaultConfig.get_messaging_lines()
                
                for line_id, line_config in lines.items():
                    if line_config.get('phone_number_id') == phone_number_id:
                        return line_id
        
    except (KeyError, IndexError, TypeError) as e:
        logging.warning(f"Error al extraer line_id del webhook: {e}")
    
    # Fallback a línea por defecto
    default_line = current_app.config.get('DEFAULT_LINE_ID', 'line_1')
    logging.info(f"Usando línea por defecto: {default_line}")
    return default_line

def get_whatsapp_access_token(line_id: str = None) -> str:
    """
    Obtiene el token de acceso de WhatsApp para una línea específica
    Args:
        line_id: ID de la línea (opcional)
    Returns:
        str: Token de acceso de WhatsApp
    """
    # Por ahora usar el token global, en futuras versiones podría ser por línea
    token = current_app.config.get('WHATSAPP_ACCESS_TOKEN')
    
    if not token:
        logging.error(f"Token de WhatsApp no configurado para línea: {line_id}")
        raise ValueError("Token de WhatsApp no configurado")
    
    return token

def log_security_event(event_type: str, details: dict, level: str = 'info'):
    """
    Registra eventos de seguridad para auditoría
    Args:
        event_type: Tipo de evento de seguridad
        details: Detalles del evento
        level: Nivel de logging (info, warning, error)
    """
    # Agregar información del request actual
    request_info = {
        'ip': request.remote_addr if request else 'unknown',
        'user_agent': request.headers.get('User-Agent') if request else 'unknown',
        'endpoint': request.endpoint if request else 'unknown',
        'method': request.method if request else 'unknown'
    }
    
    log_data = {
        'event_type': event_type,
        'details': details,
        'request_info': request_info
    }
    
    # Log según el nivel especificado
    logger = logging.getLogger('whatsapp_api.security')
    
    if level == 'error':
        logger.error(f"Security Event: {log_data}")
    elif level == 'warning':
        logger.warning(f"Security Event: {log_data}")
    else:
        logger.info(f"Security Event: {log_data}")
