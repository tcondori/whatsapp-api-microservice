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
    
    # Base de datos de desarrollo - PostgreSQL por defecto
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'postgresql://whatsapp_user:whatsapp_2024@localhost:5432/whatsapp_chatbot'
    )
    SQLALCHEMY_ECHO = True
    
    # Mantener SQLite como backup para testing
    SQLITE_DATABASE_URI = os.getenv(
        'SQLITE_DATABASE_URL',
        'sqlite:///whatsapp_dev.db'
    )
    
    # CORS usando la configuración del .env
    CORS_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',') + ['http://localhost:5000']
    
    # Configuración de webhooks desde .env
    WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    
    # WhatsApp Business configuración desde .env
    WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ID')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    # Rate limiting más permisivo en desarrollo
    RATELIMIT_DEFAULT = "10000 per hour"
    
    # API Keys desde .env
    VALID_API_KEYS = os.getenv('VALID_API_KEYS', '').split(',')
    
    # Puerto desde .env
    PORT = int(os.getenv('PORT', 5000))
