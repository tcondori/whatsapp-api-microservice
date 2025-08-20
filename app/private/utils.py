"""
Utilidades privadas generales para el microservicio
Funciones auxiliares para formateo, conversión y operaciones comunes
"""
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging

def generate_unique_id() -> str:
    """
    Genera un ID único para identificadores internos
    Returns:
        str: UUID4 como string
    """
    return str(uuid.uuid4())

def generate_hash(content: str, algorithm: str = 'sha256') -> str:
    """
    Genera hash de contenido para verificación de integridad
    Args:
        content: Contenido a hashear
        algorithm: Algoritmo de hash (sha256, md5, etc.)
    Returns:
        str: Hash hexadecimal del contenido
    """
    if algorithm == 'sha256':
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"Algoritmo de hash no soportado: {algorithm}")

def normalize_phone_number(phone: str) -> str:
    """
    Normaliza un número de teléfono al formato estándar
    Args:
        phone: Número de teléfono a normalizar
    Returns:
        str: Número normalizado
    """
    if not phone:
        return ""
    
    # Remover espacios y caracteres especiales
    normalized = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Agregar código de país si no está presente
    if not normalized.startswith('+') and not normalized.startswith('1'):
        # Asumir formato internacional sin +
        if len(normalized) > 10:
            normalized = '+' + normalized
        else:
            # Asumir número nacional (por ejemplo, US: +1)
            normalized = '+1' + normalized
    
    # Asegurar que empiece con +
    if not normalized.startswith('+'):
        normalized = '+' + normalized
    
    return normalized

def format_datetime_iso(dt: datetime) -> str:
    """
    Formatea datetime a ISO 8601 con timezone UTC
    Args:
        dt: Datetime a formatear
    Returns:
        str: Datetime en formato ISO
    """
    if dt.tzinfo is None:
        # Asumir UTC si no hay timezone
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()

def parse_iso_datetime(iso_string: str) -> Optional[datetime]:
    """
    Parsea string ISO 8601 a datetime
    Args:
        iso_string: String en formato ISO
    Returns:
        datetime: Objeto datetime o None si falla
    """
    try:
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        logging.warning(f"No se pudo parsear datetime: {iso_string}")
        return None

def safe_get_nested_value(data: Dict[str, Any], keys: list, default: Any = None) -> Any:
    """
    Obtiene valor anidado de un diccionario de forma segura
    Args:
        data: Diccionario fuente
        keys: Lista de claves anidadas
        default: Valor por defecto si no se encuentra
    Returns:
        Any: Valor encontrado o default
    """
    try:
        current = data
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError, IndexError):
        return default

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca string si excede longitud máxima
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
    Returns:
        str: Texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """
    Enmascara datos sensibles manteniendo algunos caracteres visibles
    Args:
        data: Dato a enmascarar
        visible_chars: Caracteres a mantener visibles al final
        mask_char: Carácter para enmascarar
    Returns:
        str: Dato enmascarado
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    masked_length = len(data) - visible_chars
    return mask_char * masked_length + data[-visible_chars:]

def clean_whatsapp_phone_format(phone: str) -> str:
    """
    Limpia formato de teléfono de WhatsApp removiendo sufijos
    Args:
        phone: Número de teléfono de WhatsApp
    Returns:
        str: Número limpio
    """
    if not phone:
        return ""
    
    # WhatsApp a veces agrega @c.us al final
    if phone.endswith('@c.us'):
        phone = phone[:-5]
    
    # Remover otros sufijos comunes
    if phone.endswith('@g.us'):
        phone = phone[:-5]
    
    return phone.strip()

def calculate_retry_delay(retry_count: int, base_delay: int = 1, max_delay: int = 300) -> int:
    """
    Calcula delay exponencial para reintentos
    Args:
        retry_count: Número de reintentos realizados
        base_delay: Delay base en segundos
        max_delay: Delay máximo en segundos
    Returns:
        int: Delay en segundos para el siguiente intento
    """
    delay = base_delay * (2 ** retry_count)
    return min(delay, max_delay)

def extract_error_message(exception: Exception) -> str:
    """
    Extrae mensaje de error limpio de una excepción
    Args:
        exception: Excepción a procesar
    Returns:
        str: Mensaje de error limpio
    """
    if hasattr(exception, 'message'):
        return str(exception.message)
    
    return str(exception)

def is_valid_uuid(uuid_string: str) -> bool:
    """
    Verifica si string es un UUID válido
    Args:
        uuid_string: String a verificar
    Returns:
        bool: True si es UUID válido
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, AttributeError):
        return False

def convert_to_snake_case(camel_case: str) -> str:
    """
    Convierte camelCase a snake_case
    Args:
        camel_case: String en camelCase
    Returns:
        str: String en snake_case
    """
    import re
    
    # Insertar guión bajo antes de letras mayúsculas
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_file_extension_from_mime(mime_type: str) -> str:
    """
    Obtiene extensión de archivo desde tipo MIME
    Args:
        mime_type: Tipo MIME
    Returns:
        str: Extensión de archivo con punto
    """
    mime_to_ext = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp',
        'image/gif': '.gif',
        'video/mp4': '.mp4',
        'video/3gpp': '.3gp',
        'audio/aac': '.aac',
        'audio/mp4': '.m4a',
        'audio/mpeg': '.mp3',
        'audio/ogg': '.ogg',
        'audio/amr': '.amr',
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'text/plain': '.txt'
    }
    
    return mime_to_ext.get(mime_type, '.bin')
