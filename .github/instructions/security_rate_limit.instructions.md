# Security and Rate Limiting Instructions
<!-- Instrucciones para seguridad y limitación de velocidad -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar el sistema completo de seguridad y control de tráfico, incluyendo:
- Autenticación con API keys, JWT tokens y verificación de webhooks
- Rate limiting avanzado con Redis y políticas por usuario/endpoint
- Validación exhaustiva de input y sanitización de datos
- Headers de seguridad, CORS y protección contra ataques comunes
- Logging de seguridad, monitoreo de amenazas y alertas
- Encriptación de datos sensibles y gestión segura de credenciales
-->

## Authentication & Authorization
<!-- Autenticación y autorización -->

### WhatsApp API Authentication
```python
def verify_whatsapp_token(token: str) -> bool:
    """
    Verifica el token de acceso de WhatsApp
    Args:
        token: Token de acceso a verificar
    Returns:
        bool: True si el token es válido
    """
    # Verificar token contra WhatsApp Graph API
    pass
```

### Webhook Signature Verification
```python
import hmac
import hashlib

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Verifica la firma del webhook de WhatsApp
    Args:
        payload: Contenido del webhook
        signature: Firma recibida en el header
        secret: Secreto configurado en WhatsApp
    Returns:
        bool: True si la firma es válida
    """
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

### API Key Management
```python
class APIKeyAuth:
    """Manejo de claves API para el microservicio"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    def validate_api_key(self, api_key: str) -> dict:
        """
        Valida clave API y devuelve información del cliente
        Args:
            api_key: Clave API a validar
        Returns:
            dict: Información del cliente o None si inválida
        """
        pass
    
    def generate_api_key(self, client_id: str) -> str:
        """
        Genera nueva clave API para un cliente
        Args:
            client_id: ID del cliente
        Returns:
            str: Nueva clave API generada
        """
        pass
```

## Rate Limiting
<!-- Limitación de velocidad -->

### WhatsApp API Rate Limits
- Business API: 1,000 mensajes por segundo
- Cloud API: 80 mensajes por segundo (por defecto)
- Template messages: límites específicos por plantilla

### Implementation with Redis
```python
import redis
import time
from typing import Optional

class RateLimiter:
    """Implementación de rate limiting con Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, Optional[int]]:
        """
        Verifica si se puede realizar una operación
        Args:
            key: Clave única para el límite (ej: phone_number, api_key)
            limit: Número máximo de operaciones permitidas
            window: Ventana de tiempo en segundos
        Returns:
            tuple: (permitido, tiempo_hasta_reset)
        """
        current_time = int(time.time())
        pipeline = self.redis_client.pipeline()
        
        # Usar sliding window log approach
        pipeline.zremrangebyscore(key, 0, current_time - window)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(current_time): current_time})
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        if current_requests < limit:
            return True, None
        else:
            # Calcular tiempo hasta el reset
            oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_request:
                time_to_reset = int(oldest_request[0][1]) + window - current_time
                return False, max(0, time_to_reset)
            return False, window
```

### Rate Limiting Decorator
```python
from functools import wraps
from flask import request, jsonify

def rate_limit(key_func, limit: int, window: int):
    """
    Decorador para aplicar rate limiting a endpoints
    Args:
        key_func: Función que genera la clave de rate limiting
        limit: Límite de requests
        window: Ventana de tiempo en segundos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = RateLimiter(redis_client)
            key = key_func(request)
            
            allowed, reset_time = limiter.check_rate_limit(key, limit, window)
            
            if not allowed:
                response = jsonify({
                    'error': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Too many requests',
                    'retry_after': reset_time
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(reset_time)
                return response
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso del decorador
@rate_limit(
    key_func=lambda req: f"send_msg:{req.json.get('phone_number')}",
    limit=10,
    window=60
)
def send_message():
    """Endpoint con rate limiting por número de teléfono"""
    pass
```

## Input Validation & Sanitization
<!-- Validación y sanitización de entradas -->

### Phone Number Validation
```python
import re

def validate_phone_number(phone: str) -> bool:
    """
    Valida formato de número telefónico E.164
    Args:
        phone: Número de teléfono a validar
    Returns:
        bool: True si el formato es válido
    """
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))
```

### Content Sanitization
```python
import bleach

def sanitize_message_content(content: str) -> str:
    """
    Sanitiza contenido de mensaje para prevenir XSS
    Args:
        content: Contenido del mensaje
    Returns:
        str: Contenido sanitizado
    """
    # Permitir solo texto plano, sin HTML
    return bleach.clean(content, tags=[], strip=True)
```

### File Upload Security
```python
import magic
import os

ALLOWED_EXTENSIONS = {
    'image': ['image/jpeg', 'image/png', 'image/webp'],
    'video': ['video/mp4', 'video/3gpp'],
    'audio': ['audio/aac', 'audio/mp3', 'audio/ogg'],
    'document': ['application/pdf', 'application/msword']
}

def validate_uploaded_file(file_path: str, expected_type: str) -> tuple[bool, str]:
    """
    Valida tipo y contenido de archivo subido
    Args:
        file_path: Ruta del archivo
        expected_type: Tipo esperado (image, video, audio, document)
    Returns:
        tuple: (válido, mensaje_error)
    """
    # Verificar tipo MIME real del archivo
    mime_type = magic.from_file(file_path, mime=True)
    
    if mime_type not in ALLOWED_EXTENSIONS.get(expected_type, []):
        return False, f"Tipo de archivo no permitido: {mime_type}"
    
    # Verificar tamaño del archivo
    file_size = os.path.getsize(file_path)
    max_sizes = {
        'image': 5 * 1024 * 1024,    # 5MB
        'video': 16 * 1024 * 1024,   # 16MB
        'audio': 16 * 1024 * 1024,   # 16MB
        'document': 100 * 1024 * 1024 # 100MB
    }
    
    if file_size > max_sizes.get(expected_type, 0):
        return False, f"Archivo demasiado grande: {file_size} bytes"
    
    return True, "Archivo válido"
```

## Security Headers & CORS
<!-- Headers de seguridad y CORS -->

### Security Headers
```python
from flask import Flask

def add_security_headers(app: Flask):
    """Agrega headers de seguridad a todas las respuestas"""
    
    @app.after_request
    def set_security_headers(response):
        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevenir XSS
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HTTPS obligatorio
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response
```

### CORS Configuration
```python
from flask_cors import CORS

def configure_cors(app: Flask):
    """Configura CORS para el microservicio"""
    CORS(app, origins=[
        'https://your-frontend-domain.com',
        'https://your-admin-panel.com'
    ])
```
