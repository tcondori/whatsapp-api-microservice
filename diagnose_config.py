"""
Script de diagnóstico para verificar la configuración del servidor
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

print("🔍 Diagnóstico de Configuración")
print("=" * 50)

# Verificar variables de entorno
print("\n📋 Variables de entorno:")
config_vars = [
    'FLASK_ENV',
    'DEBUG', 
    'WEBHOOK_VERIFY_TOKEN',
    'WEBHOOK_SECRET',
    'VALID_API_KEYS',
    'WHATSAPP_ACCESS_TOKEN'
]

for var in config_vars:
    value = os.getenv(var, 'NOT SET')
    if 'TOKEN' in var or 'SECRET' in var or 'KEY' in var:
        display_value = '***HIDDEN***' if value != 'NOT SET' else 'NOT SET'
    else:
        display_value = value
    print(f"  • {var}: {display_value}")

print("\n🧪 Probando configuración en vivo:")

# Test 1: Verificar health check
try:
    response = requests.get("http://localhost:5000/health")
    print(f"✅ Health general: {response.status_code}")
except Exception as e:
    print(f"❌ Health general: {e}")

# Test 2: Verificar webhook health
try:
    response = requests.get("http://localhost:5000/v1/webhooks/health")
    data = response.json()
    print(f"✅ Webhook health: {response.status_code}")
    print(f"   - Verify token configurado: {data['data']['webhook_verify_token_configured']}")
    print(f"   - Webhook secret configurado: {data['data']['webhook_secret_configured']}")
    print(f"   - Access token configurado: {data['data']['access_token_configured']}")
except Exception as e:
    print(f"❌ Webhook health: {e}")

# Test 3: Verificar API keys válidas
try:
    headers = {'X-API-Key': 'test_key', 'Content-Type': 'application/json'}
    response = requests.get("http://localhost:5000/v1/messages/test", headers=headers)
    print(f"✅ API Key 'test_key': {response.status_code} - {response.text[:100]}")
except Exception as e:
    print(f"❌ API Key 'test_key': {e}")

# Test 4: Probar webhook con token correcto
try:
    token = os.getenv('WEBHOOK_VERIFY_TOKEN', 'test_verify_token')
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': token,
        'hub.challenge': 'test123'
    }
    response = requests.get("http://localhost:5000/v1/webhooks", params=params)
    print(f"✅ Webhook verificación con token '{token}': {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Webhook verificación: {e}")

print("\n" + "=" * 50)
