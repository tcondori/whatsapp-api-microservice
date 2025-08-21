#!/usr/bin/env python3
"""
Test simplificado para todos los tipos multimedia
"""
import requests
import io
from PIL import Image

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "dev-api-key"
PHONE_NUMBER = "5491123456789"

def test_media_type(media_type: str, filename: str, content: bytes, content_type: str, caption: str = None):
    """Test para un tipo específico de multimedia"""
    
    print(f"\n🧪 TESTING {media_type.upper()}")
    print("=" * 40)
    
    # Preparar datos
    files = {'file': (filename, content, content_type)}
    data = {
        'to': PHONE_NUMBER,
        'type': media_type,
        'messaging_line_id': '1'
    }
    
    if caption:
        data['caption'] = caption
    
    headers = {'X-API-Key': API_KEY}
    
    # URL del endpoint
    url = f"{BASE_URL}/v1/messages/{media_type}/upload"
    
    print(f"📤 Endpoint: {url}")
    print(f"📄 Archivo: {filename} ({len(content)} bytes)")
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {media_type}")
            print(f"📨 Message ID: {result['data']['whatsapp_message_id']}")
            print(f"📤 Media ID: {result['data']['upload_info']['media_id']}")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🧪 TEST SIMPLIFICADO: Mensajes Multimedia")
    print("="*50)
    
    # Verificar API
    try:
        response = requests.get(f"{BASE_URL}/v1/messages/test", headers={'X-API-Key': API_KEY}, timeout=5)
        if response.status_code != 200:
            print("❌ API no disponible")
            return
        print("✅ API disponible")
    except:
        print("❌ No se puede conectar a la API")
        return
    
    results = {}
    
    # 1. VIDEO
    video_content = b"FAKE_MP4_CONTENT_" + b"0" * 500
    results['video'] = test_media_type('video', 'test.mp4', video_content, 'video/mp4', '🎬 Video de prueba')
    
    # 2. AUDIO  
    audio_content = b"FAKE_MP3_CONTENT_" + b"0" * 300
    results['audio'] = test_media_type('audio', 'test.mp3', audio_content, 'audio/mpeg')
    
    # 3. DOCUMENT
    pdf_content = b"%PDF-1.4\nFake PDF content"
    results['document'] = test_media_type('document', 'test.pdf', pdf_content, 'application/pdf', '📄 Documento de prueba')
    
    # 4. STICKER
    img = Image.new('RGB', (200, 200), color='blue')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    sticker_content = img_buffer.getvalue()
    results['sticker'] = test_media_type('sticker', 'test_sticker.jpg', sticker_content, 'image/jpeg')
    
    # Resumen
    print(f"\n{'='*50}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*50}")
    
    successful = sum(results.values())
    total = len(results)
    
    for media_type, success in results.items():
        status = "✅" if success else "❌"
        print(f"{media_type.upper():10} - {status}")
    
    print(f"\n📈 RESULTADO: {successful}/{total} exitosos")
    
    if successful == total:
        print("🎉 TODOS LOS ENDPOINTS MULTIMEDIA FUNCIONAN CORRECTAMENTE")
    else:
        print(f"⚠️ {total - successful} endpoints fallaron")

if __name__ == "__main__":
    main()
