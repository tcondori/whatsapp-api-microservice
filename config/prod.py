"""
Configuración específica para el entorno de producción
Incluye configuraciones de seguridad y optimización para producción
"""
import os
from config.default import DefaultConfig

class ProductionConfig(DefaultConfig):
    """Configuración específica para producción"""
    DEBUG = False
    TESTING = False
    
    # Base de datos de producción (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    
    # CORS restrictivo para producción
    CORS_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
    
    # Configuración de seguridad para producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting estricto en producción
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # SSL requerido en producción
    PREFERRED_URL_SCHEME = 'https'
