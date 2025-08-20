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
    
    # Configuración de desarrollo para webhooks
    WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN', 'test_verify_token')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'test_webhook_secret')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', 'test_access_token')
    
    # Rate limiting más permisivo en desarrollo
    RATELIMIT_DEFAULT = "10000 per hour"
    
    # Configuración de API Keys para desarrollo
    VALID_API_KEYS = ['dev-api-key', 'test-key-123', 'test_key'] + DefaultConfig.VALID_API_KEYS
