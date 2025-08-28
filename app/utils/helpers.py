"""
Funciones auxiliares y helpers para operaciones comunes
Utilidades para formateo, conversión y procesamiento de datos
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import logging

def create_success_response(data: Any = None, message: str = "Operación exitosa") -> dict:
    """
    Crea respuesta de éxito estándar con timestamp en zona horaria local
    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje descriptivo
    Returns:
        dict: Respuesta estructurada
    """
    try:
        from app.utils.date_utils import now_local
        timestamp = now_local().isoformat()
    except:
        # Fallback a UTC si hay problemas con zona horaria local
        timestamp = datetime.now(timezone.utc).isoformat()
    
    response = {
        'success': True,
        'message': message,
        'timestamp': timestamp
    }
    
    if data is not None:
        response['data'] = data
    
    return response

def create_error_response(error_code: str, message: str, details: dict = None) -> dict:
    """
    Crea respuesta de error estándar
    Args:
        error_code: Código de error
        message: Mensaje descriptivo
        details: Detalles adicionales del error
    Returns:
        dict: Respuesta de error estructurada
    """
    response = {
        'success': False,
        'error': error_code,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response

def paginate_results(items: List[Any], page: int = 1, per_page: int = 10) -> dict:
    """
    Pagina una lista de resultados
    Args:
        items: Lista de elementos a paginar
        page: Número de página (basado en 1)
        per_page: Elementos por página
    Returns:
        dict: Resultados paginados con metadata
    """
    # Validar parámetros
    page = max(1, page)
    per_page = max(1, min(per_page, 100))  # Máximo 100 por página
    
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Calcular índices
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    # Obtener elementos de la página actual
    page_items = items[start_index:end_index]
    
    return {
        'items': page_items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

def filter_dict_keys(data: dict, allowed_keys: List[str]) -> dict:
    """
    Filtra diccionario manteniendo solo las claves permitidas
    Args:
        data: Diccionario a filtrar
        allowed_keys: Lista de claves permitidas
    Returns:
        dict: Diccionario filtrado
    """
    return {key: value for key, value in data.items() if key in allowed_keys}

def merge_dicts(*dicts: dict) -> dict:
    """
    Combina múltiples diccionarios dando prioridad al último
    Args:
        *dicts: Diccionarios a combinar
    Returns:
        dict: Diccionario combinado
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def convert_keys_to_snake_case(data: dict) -> dict:
    """
    Convierte las claves de un diccionario a snake_case
    Args:
        data: Diccionario con claves a convertir
    Returns:
        dict: Diccionario con claves en snake_case
    """
    import re
    
    def to_snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    if isinstance(data, dict):
        return {to_snake_case(k): convert_keys_to_snake_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data

def format_phone_for_display(phone: str) -> str:
    """
    Formatea número de teléfono para visualización
    Args:
        phone: Número de teléfono
    Returns:
        str: Número formateado para mostrar
    """
    if not phone:
        return ""
    
    # Remover prefijo +
    clean_phone = phone.lstrip('+')
    
    # Formatear según longitud (asumiendo formato internacional)
    if len(clean_phone) >= 10:
        # Formato: +XX (XXX) XXX-XXXX para números de 10+ dígitos
        country_code = clean_phone[:-10]
        area_code = clean_phone[-10:-7]
        first_part = clean_phone[-7:-4]
        second_part = clean_phone[-4:]
        
        if country_code:
            return f"+{country_code} ({area_code}) {first_part}-{second_part}"
        else:
            return f"({area_code}) {first_part}-{second_part}"
    
    return phone

def calculate_message_stats(messages: List[dict]) -> dict:
    """
    Calcula estadísticas de una lista de mensajes
    Args:
        messages: Lista de mensajes
    Returns:
        dict: Estadísticas calculadas
    """
    if not messages:
        return {
            'total': 0,
            'by_type': {},
            'by_status': {},
            'by_direction': {}
        }
    
    stats = {
        'total': len(messages),
        'by_type': {},
        'by_status': {},
        'by_direction': {}
    }
    
    for msg in messages:
        # Estadísticas por tipo
        msg_type = msg.get('message_type', 'unknown')
        stats['by_type'][msg_type] = stats['by_type'].get(msg_type, 0) + 1
        
        # Estadísticas por estado
        status = msg.get('status', 'unknown')
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Estadísticas por dirección
        direction = msg.get('direction', 'unknown')
        stats['by_direction'][direction] = stats['by_direction'].get(direction, 0) + 1
    
    return stats

def format_file_size(size_bytes: int) -> str:
    """
    Formatea tamaño de archivo en formato legible
    Args:
        size_bytes: Tamaño en bytes
    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

def extract_mentions_from_text(text: str) -> List[str]:
    """
    Extrae menciones (@usuario) de un texto
    Args:
        text: Texto a analizar
    Returns:
        List[str]: Lista de menciones encontradas
    """
    import re
    
    if not text:
        return []
    
    # Patrón para menciones @usuario
    mention_pattern = r'@([a-zA-Z0-9_]+)'
    mentions = re.findall(mention_pattern, text)
    
    return mentions

def extract_hashtags_from_text(text: str) -> List[str]:
    """
    Extrae hashtags (#etiqueta) de un texto
    Args:
        text: Texto a analizar
    Returns:
        List[str]: Lista de hashtags encontrados
    """
    import re
    
    if not text:
        return []
    
    # Patrón para hashtags #etiqueta
    hashtag_pattern = r'#([a-zA-Z0-9_]+)'
    hashtags = re.findall(hashtag_pattern, text)
    
    return hashtags

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nombre de archivo removiendo caracteres peligrosos
    Args:
        filename: Nombre de archivo a sanitizar
    Returns:
        str: Nombre de archivo sanitizado
    """
    import re
    
    if not filename:
        return "untitled"
    
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remover espacios múltiples y caracteres de control
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'[^\w\-_\.]', '', sanitized)
    
    # Limitar longitud
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        sanitized = name[:max_name_length] + ('.' + ext if ext else '')
    
    return sanitized or "untitled"

def log_operation(operation: str, details: dict = None, level: str = 'info'):
    """
    Registra una operación en el log con formato consistente
    Integrado con el sistema de logging estructurado
    Args:
        operation: Nombre de la operación
        details: Detalles adicionales
        level: Nivel de log (debug, info, warning, error)
    """
    try:
        # Usar el sistema de logging estructurado si está disponible
        from app.utils.logger import WhatsAppLogger
        logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        
        log_data = {
            'operation': operation,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': 'operation_logged'
        }
        
        if details:
            log_data.update(details)
        
        # Usar el nivel apropiado
        if level == 'debug':
            logger.debug(f"Operation: {operation}", extra={'extra_data': log_data})
        elif level == 'warning':
            logger.warning(f"Operation: {operation}", extra={'extra_data': log_data})
        elif level == 'error':
            logger.error(f"Operation: {operation}", extra={'extra_data': log_data})
        else:
            logger.info(f"Operation: {operation}", extra={'extra_data': log_data})
            
    except ImportError:
        # Fallback al logging estándar si el sistema estructurado no está disponible
        logger = logging.getLogger('whatsapp_api.operations')
        
        log_data = {
            'operation': operation,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            log_data.update(details)
        
        if level == 'debug':
            logger.debug(f"Operation: {json.dumps(log_data)}")
        elif level == 'warning':
            logger.warning(f"Operation: {json.dumps(log_data)}")
        elif level == 'error':
            logger.error(f"Operation: {json.dumps(log_data)}")
        else:
            logger.info(f"Operation: {json.dumps(log_data)}")


def setup_request_context_logging():
    """
    Configura logging contextual para requests HTTP
    Debe ser llamado desde Flask app context
    """
    try:
        from flask import g
        from app.utils.logger import WhatsAppLogger
        import uuid
        
        # Generar ID único para el request si no existe
        if not hasattr(g, 'request_id'):
            g.request_id = str(uuid.uuid4())
        
        # Configurar logger con contexto
        logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        
        return logger
        
    except (ImportError, RuntimeError):
        # No hay contexto de Flask disponible
        return logging.getLogger('whatsapp_api')


def get_sanitized_user_data(data: dict, sensitive_fields: List[str] = None) -> dict:
    """
    Sanitiza datos del usuario removiendo campos sensibles para logging
    Args:
        data: Datos a sanitizar
        sensitive_fields: Lista de campos sensibles a remover/ocultar
    Returns:
        dict: Datos sanitizados
    """
    if not data:
        return {}
    
    # Campos sensibles por defecto
    default_sensitive_fields = [
        'password', 'token', 'api_key', 'secret', 'authorization',
        'credit_card', 'ssn', 'phone', 'email'
    ]
    
    sensitive_fields = sensitive_fields or default_sensitive_fields
    sanitized = data.copy()
    
    for field in sensitive_fields:
        if field in sanitized:
            if field == 'phone':
                # Para teléfonos, usar formato sanitizado
                sanitized[field] = format_phone_for_logging(sanitized[field])
            elif field == 'email':
                # Para emails, mostrar solo dominio
                email = sanitized[field]
                if '@' in email:
                    domain = email.split('@')[1]
                    sanitized[field] = f"***@{domain}"
                else:
                    sanitized[field] = "***"
            else:
                # Para otros campos sensibles, ocultar completamente
                sanitized[field] = "***HIDDEN***"
    
    return sanitized


def format_phone_for_logging(phone: str) -> str:
    """
    Formatea número de teléfono para logging seguro (oculta información personal)
    Args:
        phone: Número de teléfono
    Returns:
        str: Número formateado para logging
    """
    if not phone:
        return ""
    
    # Remover caracteres no numéricos
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    if len(clean_phone) > 5:
        # Mostrar solo primeros 3 y últimos 2 dígitos
        return f"{clean_phone[:3]}***{clean_phone[-2:]}"
    else:
        return "****"


def create_audit_log_entry(action: str, resource: str, user_id: str = None, 
                          changes: dict = None, metadata: dict = None) -> dict:
    """
    Crea entrada estructurada para log de auditoría
    Args:
        action: Acción realizada (create, read, update, delete)
        resource: Recurso afectado
        user_id: ID del usuario que realizó la acción
        changes: Cambios realizados
        metadata: Metadatos adicionales
    Returns:
        dict: Entrada de auditoría estructurada
    """
    audit_entry = {
        'audit_type': 'resource_action',
        'action': action,
        'resource': resource,
        'user_id': user_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    
    if changes:
        audit_entry['changes'] = get_sanitized_user_data(changes)
    
    if metadata:
        audit_entry['metadata'] = metadata
    
    return audit_entry


def log_performance_metric(metric_name: str, value: float, unit: str = 'ms',
                          tags: dict = None, threshold: float = None):
    """
    Registra métrica de performance con alertas automáticas
    Args:
        metric_name: Nombre de la métrica
        value: Valor medido
        unit: Unidad de medida
        tags: Tags adicionales para la métrica
        threshold: Umbral para generar alerta
    """
    try:
        from app.utils.logger import WhatsAppLogger
        from app.utils.events import EventType, Event, event_bus
        from datetime import datetime
        import asyncio
        
        perf_logger = WhatsAppLogger.get_logger(WhatsAppLogger.PERFORMANCE_LOGGER)
        
        metric_data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {},
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'performance_metric'
        }
        
        # Determinar nivel de log basado en umbral
        log_level = 'info'
        if threshold and value > threshold:
            log_level = 'warning'
            metric_data['threshold_exceeded'] = True
            metric_data['threshold'] = threshold
        
        # Registrar métrica
        getattr(perf_logger, log_level)(
            f"Performance metric: {metric_name}={value}{unit}",
            extra={'extra_data': metric_data}
        )
        
        # Emitir evento de performance si hay loop disponible
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(event_bus.publish(Event(
                event_type=EventType.API_REQUEST_COMPLETED,
                timestamp=datetime.utcnow(),
                source='performance_monitor',
                data=metric_data
            )))
        except RuntimeError:
            pass
            
    except ImportError:
        # Fallback a logging estándar
        logger = logging.getLogger('performance')
        logger.info(f"Performance: {metric_name}={value}{unit}")


def create_structured_log_context(operation: str, user_id: str = None,
                                 correlation_id: str = None) -> dict:
    """
    Crea contexto estructurado para logging consistente
    Args:
        operation: Operación being performed
        user_id: ID del usuario
        correlation_id: ID para correlacionar eventos relacionados
    Returns:
        dict: Contexto estructurado para logging
    """
    context = {
        'operation': operation,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    
    if user_id:
        context['user_id'] = user_id
    
    if correlation_id:
        context['correlation_id'] = correlation_id
    
    # Agregar información de request si está disponible
    try:
        from flask import g, request
        if hasattr(g, 'request_id'):
            context['request_id'] = g.request_id
        
        if request:
            context['endpoint'] = request.endpoint
            context['method'] = request.method
            
    except (ImportError, RuntimeError):
        pass
    
    return context
