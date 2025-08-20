"""
Módulo de configuración para el microservicio WhatsApp API
Proporciona configuración multi-entorno (desarrollo, producción)
"""
import os
from config.default import DefaultConfig
from config.dev import DevelopmentConfig  
from config.prod import ProductionConfig

def get_config():
    """
    Obtiene la configuración según la variable de entorno FLASK_ENV
    Returns:
        Clase de configuración correspondiente al entorno
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'dev': DevelopmentConfig,
        'production': ProductionConfig,
        'prod': ProductionConfig,
        'default': DefaultConfig
    }
    
    return configs.get(env, DevelopmentConfig)
