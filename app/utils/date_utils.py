"""
Utilidades para manejo de fechas y zonas horarias
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Union
from flask import current_app


def get_app_timezone() -> timezone:
    """
    Obtiene la zona horaria configurada en la aplicación
    
    Returns:
        timezone: Objeto timezone configurado
    """
    try:
        return current_app.config.get('TIMEZONE', timezone.utc)
    except RuntimeError:
        # Si no hay contexto de aplicación, usar UTC-4 por defecto
        return timezone(timedelta(hours=-4))


def utc_to_local(utc_datetime: Optional[datetime]) -> Optional[datetime]:
    """
    Convierte una fecha UTC a la zona horaria local de la aplicación
    
    Args:
        utc_datetime: Fecha en UTC (puede ser naive o aware)
        
    Returns:
        datetime: Fecha convertida a zona horaria local, o None si la entrada es None
    """
    if utc_datetime is None:
        return None
    
    # Si la fecha no tiene zona horaria, asumir que es UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    
    # Convertir a la zona horaria local
    local_tz = get_app_timezone()
    return utc_datetime.astimezone(local_tz)


def local_to_utc(local_datetime: Optional[datetime]) -> Optional[datetime]:
    """
    Convierte una fecha local a UTC
    
    Args:
        local_datetime: Fecha en zona horaria local
        
    Returns:
        datetime: Fecha convertida a UTC, o None si la entrada es None
    """
    if local_datetime is None:
        return None
    
    # Si la fecha no tiene zona horaria, asumir que es zona horaria local
    if local_datetime.tzinfo is None:
        local_tz = get_app_timezone()
        local_datetime = local_datetime.replace(tzinfo=local_tz)
    
    # Convertir a UTC
    return local_datetime.astimezone(timezone.utc)


def now_local() -> datetime:
    """
    Obtiene la fecha y hora actual en la zona horaria local
    
    Returns:
        datetime: Fecha actual en zona horaria local
    """
    utc_now = datetime.now(timezone.utc)
    return utc_to_local(utc_now)


def now_utc() -> datetime:
    """
    Obtiene la fecha y hora actual en UTC
    
    Returns:
        datetime: Fecha actual en UTC
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: Optional[datetime], include_timezone: bool = True) -> Optional[str]:
    """
    Formatea una fecha para respuestas de API
    
    Args:
        dt: Fecha a formatear
        include_timezone: Si incluir información de zona horaria
        
    Returns:
        str: Fecha formateada como string ISO, o None si la entrada es None
    """
    if dt is None:
        return None
    
    # Convertir a local si es UTC
    if dt.tzinfo == timezone.utc or dt.tzinfo is None:
        dt = utc_to_local(dt)
    
    if include_timezone:
        return dt.isoformat()
    else:
        return dt.strftime('%Y-%m-%dT%H:%M:%S')


def parse_datetime(date_string: Union[str, datetime]) -> Optional[datetime]:
    """
    Parsea un string de fecha o devuelve el datetime si ya es datetime
    
    Args:
        date_string: String de fecha en formato ISO o objeto datetime
        
    Returns:
        datetime: Objeto datetime, o None si no se puede parsear
    """
    if date_string is None:
        return None
    
    if isinstance(date_string, datetime):
        return date_string
    
    if isinstance(date_string, str):
        try:
            # Intentar parsear formato ISO
            if 'T' in date_string:
                if '+' in date_string or date_string.endswith('Z'):
                    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                else:
                    # Asumir UTC si no hay zona horaria
                    return datetime.fromisoformat(date_string).replace(tzinfo=timezone.utc)
            else:
                # Formato simple YYYY-MM-DD
                return datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    return None


def get_timezone_info() -> dict:
    """
    Obtiene información sobre la zona horaria configurada
    
    Returns:
        dict: Información de zona horaria
    """
    local_tz = get_app_timezone()
    now_utc_time = datetime.now(timezone.utc)
    now_local_time = now_utc_time.astimezone(local_tz)
    
    try:
        timezone_name = current_app.config.get('TIMEZONE_NAME', 'America/La_Paz')
    except RuntimeError:
        timezone_name = 'America/La_Paz'
    
    return {
        'timezone_name': timezone_name,
        'offset_hours': local_tz.utcoffset(now_utc_time).total_seconds() / 3600,
        'offset_string': now_local_time.strftime('%z'),
        'current_utc': now_utc_time.isoformat(),
        'current_local': now_local_time.isoformat()
    }
