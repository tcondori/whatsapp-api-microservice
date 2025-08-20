"""
Validadores internos para datos del microservicio
Funciones de validación para números de teléfono, mensajes y webhooks
"""
import re
import json
from typing import Dict, Any, Optional
import logging

# Expresiones regulares para validación
PHONE_REGEX = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_phone_number(phone: str) -> bool:
    """
    Valida formato de número de teléfono según estándar E.164
    Args:
        phone: Número de teléfono a validar
    Returns:
        bool: True si el formato es válido
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Limpiar espacios y caracteres especiales comunes
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone.strip())
    
    # Validar con regex E.164
    is_valid = bool(PHONE_REGEX.match(cleaned_phone))
    
    if not is_valid:
        logging.debug(f"Número de teléfono inválido: {phone}")
    
    return is_valid

def validate_email(email: str) -> bool:
    """
    Valida formato de email
    Args:
        email: Email a validar
    Returns:
        bool: True si el formato es válido
    """
    if not email or not isinstance(email, str):
        return False
    
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_message_content(message_type: str, content: Any) -> tuple[bool, str]:
    """
    Valida el contenido de un mensaje según su tipo
    Args:
        message_type: Tipo de mensaje (text, image, video, etc.)
        content: Contenido del mensaje a validar
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    if not message_type:
        return False, "Tipo de mensaje requerido"
    
    message_type = message_type.lower()
    
    # Validar mensaje de texto
    if message_type == 'text':
        if not content or not isinstance(content, str):
            return False, "Contenido de texto requerido"
        
        if len(content.strip()) == 0:
            return False, "El mensaje no puede estar vacío"
        
        # WhatsApp limita mensajes a 4096 caracteres
        if len(content) > 4096:
            return False, "El mensaje excede el límite de 4096 caracteres"
    
    # Validar mensaje de template
    elif message_type == 'template':
        if not isinstance(content, dict):
            return False, "Template debe ser un objeto JSON"
        
        if 'name' not in content:
            return False, "Template debe incluir campo 'name'"
        
        if 'language' not in content:
            return False, "Template debe incluir campo 'language'"
    
    # Validar mensajes multimedia
    elif message_type in ['image', 'video', 'document', 'audio']:
        if not isinstance(content, dict):
            return False, f"Contenido de {message_type} debe ser un objeto"
        
        # Debe tener URL o media_id
        if not content.get('url') and not content.get('id'):
            return False, f"{message_type} debe incluir 'url' o 'id'"
    
    # Validar mensajes interactivos
    elif message_type == 'interactive':
        if not isinstance(content, dict):
            return False, "Mensaje interactivo debe ser un objeto"
        
        if 'type' not in content:
            return False, "Mensaje interactivo debe incluir campo 'type'"
        
        interactive_type = content.get('type')
        if interactive_type not in ['button', 'list']:
            return False, "Tipo interactivo debe ser 'button' o 'list'"
    
    return True, ""

def validate_webhook_payload(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valida la estructura básica de un webhook de WhatsApp
    Args:
        payload: Payload del webhook
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    if not isinstance(payload, dict):
        return False, "Payload debe ser un objeto JSON"
    
    # Verificar campos requeridos
    required_fields = ['object']
    for field in required_fields:
        if field not in payload:
            return False, f"Campo requerido faltante: {field}"
    
    # Verificar que sea un webhook de WhatsApp
    if payload.get('object') != 'whatsapp_business_account':
        return False, "No es un webhook válido de WhatsApp Business"
    
    # Verificar estructura de entry
    if 'entry' not in payload:
        return False, "Webhook debe incluir campo 'entry'"
    
    if not isinstance(payload['entry'], list):
        return False, "Campo 'entry' debe ser una lista"
    
    if len(payload['entry']) == 0:
        return False, "Lista 'entry' no puede estar vacía"
    
    return True, ""

def validate_line_id(line_id: str) -> bool:
    """
    Valida que el line_id sea válido y esté configurado
    Args:
        line_id: ID de la línea a validar
    Returns:
        bool: True si la línea es válida
    """
    if not line_id or not isinstance(line_id, str):
        return False
    
    # Verificar que la línea esté configurada
    try:
        from config.default import DefaultConfig
        lines = DefaultConfig.get_messaging_lines()
        return line_id in lines
    except Exception as e:
        logging.error(f"Error validando line_id {line_id}: {e}")
        return False

def sanitize_message_content(content: str) -> str:
    """
    Sanitiza el contenido de un mensaje removiendo caracteres peligrosos
    Args:
        content: Contenido a sanitizar
    Returns:
        str: Contenido sanitizado
    """
    if not isinstance(content, str):
        return str(content)
    
    # Remover caracteres de control peligrosos
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    
    # Normalizar espacios en blanco
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

def validate_json_structure(json_str: str, required_fields: list = None) -> tuple[bool, dict, str]:
    """
    Valida y parsea una estructura JSON
    Args:
        json_str: String JSON a validar
        required_fields: Lista de campos requeridos
    Returns:
        tuple: (es_válido, datos_parseados, mensaje_error)
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return False, {}, f"JSON inválido: {str(e)}"
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                return False, {}, f"Campo requerido faltante: {field}"
    
    return True, data, ""

def validate_media_file(file_info: dict) -> tuple[bool, str]:
    """
    Valida información de archivo multimedia
    Args:
        file_info: Diccionario con información del archivo
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    if not isinstance(file_info, dict):
        return False, "Información de archivo debe ser un objeto"
    
    # Tipos de archivo soportados por WhatsApp
    supported_image_types = ['image/jpeg', 'image/png', 'image/webp']
    supported_video_types = ['video/mp4', 'video/3gpp']
    supported_audio_types = ['audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg']
    supported_document_types = ['application/pdf', 'application/vnd.ms-powerpoint', 
                               'application/msword', 'application/vnd.ms-excel',
                               'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                               'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                               'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               'text/plain']
    
    all_supported_types = (supported_image_types + supported_video_types + 
                          supported_audio_types + supported_document_types)
    
    # Validar tipo MIME
    mime_type = file_info.get('mime_type')
    if mime_type and mime_type not in all_supported_types:
        return False, f"Tipo de archivo no soportado: {mime_type}"
    
    # Validar tamaño (límites de WhatsApp)
    file_size = file_info.get('file_size', 0)
    if file_size > 100 * 1024 * 1024:  # 100MB
        return False, "Archivo demasiado grande (máximo 100MB)"
    
    return True, ""
