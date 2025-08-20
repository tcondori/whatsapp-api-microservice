"""
Configuración específica para el entorno de desarrollo
Incluye configuraciones permisivas para testing y debugging
"""
import os
from config.default import DefaultConfig

class DevelopmentConfig(DefaultConfig):
    """Configuración específica para desarrollo"""
    DEBUG = True
    TESTING = False
    
    # Base de datos de desarrollo (SQLite para simplicidad)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'sqlite:///whatsapp_dev.db'
    )
    SQLALCHEMY_ECHO = True
    
    # CORS permisivo para desarrollo
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000']
    
    # Rate limiting más permisivo en desarrollo
    RATELIMIT_DEFAULT = "10000 per hour"
    
    # Configuración de API Keys para desarrollo
    VALID_API_KEYS = ['dev-api-key', 'test-key-123'] + DefaultConfig.VALID_API_KEYS
