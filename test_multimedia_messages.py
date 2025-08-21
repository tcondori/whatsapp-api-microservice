#!/usr/bin/env python3
"""
Test completo para mensajes multimedia de WhatsApp Business API
Casos: VIDEO, AUDIO, DOCUMENTO y STICKER

Documentación oficial: https://developers.facebook.com/docs/whatsapp/cloud-api/messages/

Uso: python test_multimedia_messages.py
"""
import requests
import json
import io
import sys
from PIL import Image

# Configuración
BASE_URL = "http://127.0.0.1:5000"
API_KEY = "dev-api-key"
PHONE_NUMBER = "5491123456789"  # Número de prueba

def create_test_files():
    """
    Crea archivos de prueba para cada tipo de multimedia
    Returns:
        dict: Diccionario con archivos de prueba
    """
    files = {}
    
    try:
        # 1. VIDEO - Crear un "video" simulado (realmente una imagen con extensión mp4)
        # En producción sería un archivo MP4 real
        video_content = b"FAKE_MP4_CONTENT_FOR_TESTING_" + b"0" * 1000
        files['video'] = {
            'content': video_content,
            'filename': 'test_video.mp4',
            'content_type': 'video/mp4',
            'caption': '🎬 Video de prueba enviado con upload + media_id'
        }
        
        # 2. AUDIO - Crear un "audio" simulado (realmente datos con extensión mp3)
        audio_content = b"FAKE_MP3_CONTENT_FOR_TESTING_" + b"0" * 500
        files['audio'] = {
            'content': audio_content,
            'filename': 'test_audio.mp3',
            'content_type': 'audio/mpeg',
            'caption': None  # Los audios no soportan caption
        }
        
        # 3. DOCUMENTO - Crear un PDF simulado
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        files['document'] = {
            'content': pdf_content,
            'filename': 'test_document.pdf',
            'content_type': 'application/pdf',
            'caption': '📄 Documento de prueba enviado con upload + media_id'
        }
        
        # 4. IMAGEN para STICKER - Los stickers son imágenes WebP
        # Crear imagen simple y convertir a bytes
        img = Image.new('RGB', (300, 300), color='yellow')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        sticker_content = img_buffer.getvalue()
        
        files['sticker'] = {
            'content': sticker_content,
            'filename': 'test_sticker.jpg',  # En producción sería .webp
            'content_type': 'image/jpeg',  # En producción sería image/webp
            'caption': None  # Los stickers no soportan caption
        }
        
        print("✅ Archivos de prueba creados exitosamente")
        return files
        
    except Exception as e:
        print(f"❌ Error creando archivos de prueba: {e}")
        return None

def test_multimedia_upload_and_send(media_type: str, file_data: dict):
    """
    Prueba el upload y envío de un tipo específico de multimedia
    
    Args:
        media_type: Tipo de multimedia ('video', 'audio', 'document', 'sticker')
        file_data: Datos del archivo de prueba
    
    Returns:
        bool: True si el test fue exitoso
    """
    print(f"\n🧪 TESTING {media_type.upper()}")
    print("=" * 50)
    
    # Preparar datos del formulario
    form_data = {
        'to': PHONE_NUMBER,
        'type': media_type,
        'messaging_line_id': 1
    }
    
    # Agregar caption si es soportado
    if file_data.get('caption'):
        form_data['caption'] = file_data['caption']
    
    # Preparar archivo
    files = {
        'file': (file_data['filename'], file_data['content'], file_data['content_type'])
    }
    
    # Headers
    headers = {
        'X-API-Key': API_KEY
    }
    
    print(f"📤 Subiendo {media_type}: {file_data['filename']}")
    print(f"📊 Tamaño: {len(file_data['content'])} bytes")
    print(f"🎯 Content-Type: {file_data['content_type']}")
    if file_data.get('caption'):
        print(f"🏷️  Caption: {file_data['caption'][:50]}...")
    
    try:
        # Determinar endpoint según el tipo
        if media_type == 'sticker':
            # Los stickers usan un endpoint diferente
            url = f"{BASE_URL}/v1/messages/sticker/upload"
        else:
            # Video, audio, document usan el endpoint genérico de media
            url = f"{BASE_URL}/v1/messages/{media_type}/upload"
        
        print(f"🔗 Endpoint: {url}")
        
        # Realizar petición POST
        response = requests.post(
            url,
            data=form_data,
            files=files,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        # Intentar parsear respuesta JSON
        try:
            response_data = response.json()
            print(f"📋 Respuesta JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"📋 Respuesta (texto): {response.text}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: {media_type.upper()} enviado exitosamente")
            
            # Extraer información relevante
            if 'data' in response_data:
                data = response_data['data']
                print(f"📨 WhatsApp Message ID: {data.get('whatsapp_message_id', 'N/A')}")
                print(f"🆔 Message ID (DB): {data.get('id', 'N/A')}")
                print(f"📋 Tipo: {data.get('message_type', 'N/A')}")
                
                # Información del upload
                if 'upload_info' in data:
                    upload_info = data['upload_info']
                    print(f"📤 Media ID: {upload_info.get('media_id', 'N/A')}")
                    print(f"📄 Filename: {upload_info.get('filename', 'N/A')}")
            
            return True
        else:
            print(f"❌ ERROR: Fallo en envío de {media_type}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición HTTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verify_api_availability():
    """
    Verifica que la API esté disponible
    """
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{BASE_URL}/v1/messages/test", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ API disponible")
            return True
        else:
            print(f"⚠️  API respondió con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API no disponible: {e}")
        return False

def main():
    """Función principal del test"""
    print("🧪 TEST: Mensajes Multimedia WhatsApp Business API")
    print("Tipos: VIDEO, AUDIO, DOCUMENTO, STICKER")
    print("=" * 60)
    
    # Verificar dependencias
    try:
        from PIL import Image
        print("✅ PIL/Pillow disponible")
    except ImportError:
        print("❌ PIL/Pillow no disponible. Instalar con: pip install Pillow")
        sys.exit(1)
    
    # Verificar API
    if not verify_api_availability():
        print("❌ No se puede conectar a la API. Verificar que el servidor esté corriendo.")
        sys.exit(1)
    
    # Crear archivos de prueba
    test_files = create_test_files()
    if not test_files:
        print("❌ No se pudieron crear archivos de prueba")
        sys.exit(1)
    
    # Ejecutar tests para cada tipo
    results = {}
    media_types = ['video', 'audio', 'document', 'sticker']
    
    for media_type in media_types:
        if media_type in test_files:
            results[media_type] = test_multimedia_upload_and_send(media_type, test_files[media_type])
        else:
            print(f"⚠️  No hay archivo de prueba para {media_type}")
            results[media_type] = False
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for media_type, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{media_type.upper():12} - {status}")
        if success:
            successful += 1
        else:
            failed += 1
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"✅ Exitosos: {successful}")
    print(f"❌ Fallidos: {failed}")
    print(f"📊 Total: {successful + failed}")
    
    if successful == len(media_types):
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("✅ Implementación de mensajes multimedia completa")
    else:
        print(f"\n⚠️  {failed} tests fallaron. Revisar implementación y logs del servidor.")
    
    print("\n📋 Información técnica:")
    print("- Flujo: Upload de archivo → Media ID → Envío de mensaje")
    print("- Formatos soportados:")
    print("  • VIDEO: MP4, 3GPP")
    print("  • AUDIO: MP3, OGG, AMR, AAC")
    print("  • DOCUMENTO: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT")
    print("  • STICKER: WEBP (imagen estática)")

if __name__ == "__main__":
    main()
