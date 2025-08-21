#!/usr/bin/env python3
"""
Test directo del endpoint de upload usando requests multipart
"""
import requests
import io
from PIL import Image

# Crear imagen simple
img = Image.new('RGB', (100, 100), color='red')
img_buffer = io.BytesIO()
img.save(img_buffer, format='JPEG')
img_bytes = img_buffer.getvalue()

# Preparar datos
files = {
    'file': ('test.jpg', img_bytes, 'image/jpeg')
}

data = {
    'to': '5491123456789',
    'type': 'image',
    'caption': 'Test directo',
    'messaging_line_id': '1'
}

headers = {
    'X-API-Key': 'dev-api-key'
}

# Hacer petición
url = 'http://127.0.0.1:5000/v1/messages/image/upload'
print(f"🔍 Probando endpoint: {url}")

try:
    response = requests.post(url, files=files, data=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
