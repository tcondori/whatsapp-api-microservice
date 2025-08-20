"""
Script simple para probar configuración
"""
import os
from dotenv import load_dotenv
load_dotenv()

from config import get_config

# Crear configuración
config = get_config()
print("🔧 Configuración actual:")
print(f"Clase: {config.__name__}")
print(f"DEBUG: {config.DEBUG if hasattr(config, 'DEBUG') else 'NO DEFINIDO'}")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")

# Verificar API keys
if hasattr(config, 'VALID_API_KEYS'):
    print(f"API Keys válidas: {config.VALID_API_KEYS}")
else:
    print("❌ VALID_API_KEYS no definido en configuración")

# Verificar tokens
if hasattr(config, 'WEBHOOK_VERIFY_TOKEN'):
    print(f"Webhook verify token: {config.WEBHOOK_VERIFY_TOKEN}")
else:
    print("❌ WEBHOOK_VERIFY_TOKEN no definido en configuración")

# Variables de entorno directas
print(f"\n📋 Variables de entorno directas:")
print(f"VALID_API_KEYS: {os.getenv('VALID_API_KEYS')}")
print(f"WEBHOOK_VERIFY_TOKEN: {os.getenv('WEBHOOK_VERIFY_TOKEN')}")
