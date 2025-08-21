#!/usr/bin/env python3
"""
Test específico para probar el endpoint de video
"""
import requests
import io

# Crear contenido de video simulado
video_content = b"FAKE_MP4_CONTENT_FOR_TESTING_" + b"0" * 1000

# Preparar datos
files = {
    'file': ('test_video.mp4', video_content, 'video/mp4')
}

data = {
    'to': '5491123456789',
    'type': 'video',
    'caption': 'Test de video directo',
    'messaging_line_id': '1'
}

headers = {
    'X-API-Key': 'dev-api-key'
}

# Hacer petición
url = 'http://127.0.0.1:5000/v1/messages/video/upload'
print(f"🔍 Probando endpoint de video: {url}")

try:
    response = requests.post(url, files=files, data=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
