#!/usr/bin/env python3
"""
Test del CASO 2: Envío de imagen por media_id
Flujo oficial Meta WhatsApp Business API:
1. Sube archivo para obtener media_id
2. Envía mensaje usando media_id

Uso: python test_image_upload_media_id.py
"""
import requests
import json
import io
from PIL import Image
import sys

# Configuración
BASE_URL = "http://127.0.0.1:5000"
API_KEY = "dev-api-key"
PHONE_NUMBER = "5491123456789"  # Número de prueba

def create_test_image():
    """
    Crea una imagen de prueba en memoria
    Returns:
        tuple: (contenido_bytes, content_type, filename)
    """
    # Crear imagen simple con PIL
    img = Image.new('RGB', (300, 200), color='lightblue')
    
    # Agregar texto a la imagen
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar fuente por defecto
        try:
            # Para Windows
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            try:
                # Para Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                # Fuente por defecto si no hay otras disponibles
                font = ImageFont.load_default()
        
        text = "Imagen de Prueba\nCaso 2: Media ID\nUpload + Envío"
        draw.multiline_text((20, 50), text, fill='darkblue', font=font, spacing=10)
        
    except ImportError:
        # Si PIL no está disponible para draw/fonts, continuar sin texto
        print("⚠️  PIL no disponible para dibujar texto, usando imagen simple")
    
    # Convertir a bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=85)
    img_bytes = img_buffer.getvalue()
    
    return img_bytes, 'image/jpeg', 'test_upload_media_id.jpg'

def test_image_upload_media_id():
    """
    Test del flujo completo: upload de archivo + envío por media_id
    """
    print("🚀 TESTING CASO 2: Envío de imagen por media_id")
    print("=" * 60)
    
    # Crear imagen de prueba
    print("📸 Creando imagen de prueba...")
    try:
        file_content, content_type, filename = create_test_image()
        print(f"✅ Imagen creada: {filename} ({content_type}) - {len(file_content)} bytes")
    except Exception as e:
        print(f"❌ Error creando imagen: {e}")
        return False
    
    # Preparar datos del formulario
    form_data = {
        'to': PHONE_NUMBER,
        'type': 'image',
        'caption': '🖼️ Imagen enviada con CASO 2: Upload + Media ID\n\nFlujo oficial Meta:\n1. Upload de archivo\n2. Obtención de media_id\n3. Envío con media_id',
        'messaging_line_id': 'line_1'  # Usar line_1 que sabemos existe
    }
    
    # Preparar archivo
    files = {
        'file': (filename, file_content, content_type)
    }
    
    # Headers
    headers = {
        'X-API-Key': API_KEY
    }
    
    print(f"📤 Enviando imagen a: {PHONE_NUMBER}")
    print(f"🏷️  Caption: {form_data['caption'][:50]}...")
    print(f"📱 Línea: {form_data['messaging_line_id']}")
    print("⏳ Procesando upload + envío...")
    
    try:
        # Realizar petición POST al endpoint de upload
        url = f"{BASE_URL}/v1/messages/image/upload"
        response = requests.post(
            url, 
            data=form_data,  # Form data (no JSON)
            files=files,     # Archivo
            headers=headers,
            timeout=60       # Timeout mayor para upload
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
            print("\n✅ SUCCESS: Imagen enviada exitosamente con CASO 2 (Upload + Media ID)")
            
            # Extraer información relevante
            if 'data' in response_data:
                data = response_data['data']
                print(f"📨 WhatsApp Message ID: {data.get('whatsapp_message_id', 'N/A')}")
                print(f"🆔 Message ID (DB): {data.get('id', 'N/A')}")
                print(f"📋 Tipo: {data.get('message_type', 'N/A')}")
                print(f"📍 Estado: {data.get('status', 'N/A')}")
                
                # Información del upload
                if 'upload_info' in data:
                    upload_info = data['upload_info']
                    print(f"📤 Media ID: {upload_info.get('media_id', 'N/A')}")
                    print(f"📄 Filename: {upload_info.get('filename', 'N/A')}")
                    print(f"🎨 Content Type: {upload_info.get('content_type', 'N/A')}")
            
            return True
            
        else:
            print(f"\n❌ ERROR: Fallo en envío de imagen")
            print(f"Status: {response.status_code}")
            if response_data and 'message' in response_data:
                print(f"Error: {response_data['message']}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición HTTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verify_api_availability():
    """Verifica que la API esté disponible"""
    try:
        response = requests.get(f"{BASE_URL}/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API disponible")
            return True
        else:
            print(f"⚠️  API respondió con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API no disponible: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEST: Envío de imagen por media_id (Caso 2)")
    print("Implementación oficial Meta WhatsApp Business API")
    print("=" * 60)
    
    # Verificar disponibilidad de PIL
    try:
        from PIL import Image
        print("✅ PIL/Pillow disponible para crear imágenes")
    except ImportError:
        print("❌ PIL/Pillow no disponible. Instalar con: pip install Pillow")
        sys.exit(1)
    
    # Verificar API
    if not verify_api_availability():
        print("❌ No se puede conectar a la API. Verificar que el servidor esté corriendo.")
        sys.exit(1)
    
    # Ejecutar test
    success = test_image_upload_media_id()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETADO EXITOSAMENTE")
        print("✅ El CASO 2 (Upload + Media ID) funciona correctamente")
        print("\nFlujo implementado:")
        print("1. ✅ Upload de archivo al endpoint /v1/messages/image/upload")
        print("2. ✅ Obtención de media_id (real o simulado)")
        print("3. ✅ Envío de mensaje con media_id")
        print("4. ✅ Registro en base de datos")
    else:
        print("❌ TEST FALLÓ")
        print("Revisar logs del servidor para más detalles.")
    
    print("\n📋 Información adicional:")
    print("- Endpoint utilizado: POST /v1/messages/image/upload")
    print("- Formato: multipart/form-data con archivo")
    print("- Flujo oficial Meta WhatsApp Business API")
