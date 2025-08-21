#!/usr/bin/env python3
"""
Diagnóstico específico para problemas de stickers
Verifica formatos, dimensiones y configuración
"""
import requests
import io
from PIL import Image
import json

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "dev-api-key"
PHONE_NUMBER = "5491123456789"

def create_proper_sticker():
    """
    Crea un sticker con las especificaciones exactas de WhatsApp
    Returns:
        tuple: (contenido_bytes, content_type, filename)
    """
    print("🎨 Creando sticker con especificaciones oficiales de WhatsApp...")
    
    # Crear imagen 512x512 con fondo transparente
    img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))  # Fondo transparente
    
    # Dibujar contenido del sticker
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Dibujar un círculo de color
    draw.ellipse([100, 100, 412, 412], fill=(255, 200, 0, 255), outline=(255, 100, 0, 255), width=5)
    
    # Texto en el centro
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    text = "TEST\nSTICKER"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (512 - text_width) // 2
    text_y = (512 - text_height) // 2
    
    draw.multiline_text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font, align='center')
    
    # Convertir a WebP
    webp_buffer = io.BytesIO()
    img.save(webp_buffer, format='WEBP', quality=95)
    webp_bytes = webp_buffer.getvalue()
    
    print(f"✅ Sticker creado:")
    print(f"   📏 Dimensiones: 512x512px")
    print(f"   📊 Tamaño: {len(webp_bytes)} bytes")
    print(f"   🎨 Formato: WebP")
    print(f"   🫥 Fondo: Transparente")
    
    return webp_bytes, 'image/webp', 'perfect_sticker.webp'

def create_jpg_sticker():
    """Crea un sticker en formato JPG para comparar"""
    print("\n🎨 Creando sticker JPG para comparación...")
    
    from PIL import ImageDraw, ImageFont
    
    img = Image.new('RGB', (512, 512), (255, 255, 255))  # Fondo blanco
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 462, 462], fill=(0, 150, 255), outline=(0, 100, 200), width=10)
    
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()
    
    text = "JPG\nSTICKER"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (512 - text_width) // 2
    text_y = (512 - text_height) // 2
    
    draw.multiline_text((text_x, text_y), text, fill=(255, 255, 255), font=font, align='center')
    
    jpg_buffer = io.BytesIO()
    img.save(jpg_buffer, format='JPEG', quality=85)
    jpg_bytes = jpg_buffer.getvalue()
    
    print(f"✅ Sticker JPG creado:")
    print(f"   📏 Dimensiones: 512x512px")
    print(f"   📊 Tamaño: {len(jpg_bytes)} bytes")
    print(f"   🎨 Formato: JPEG")
    
    return jpg_bytes, 'image/jpeg', 'comparison_sticker.jpg'

def test_sticker(sticker_content, content_type, filename, description):
    """Test específico para stickers"""
    
    print(f"\n🧪 TESTING STICKER: {description}")
    print("=" * 50)
    
    files = {'file': (filename, sticker_content, content_type)}
    data = {
        'to': PHONE_NUMBER,
        'type': 'sticker',
        'messaging_line_id': '1'
    }
    
    headers = {'X-API-Key': API_KEY}
    url = f"{BASE_URL}/v1/messages/sticker/upload"
    
    print(f"📤 Enviando: {filename}")
    print(f"📊 Tamaño: {len(sticker_content)} bytes")
    print(f"🎨 Content-Type: {content_type}")
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(f"   📨 WhatsApp Message ID: {result['data']['whatsapp_message_id']}")
            print(f"   📤 Media ID: {result['data']['upload_info']['media_id']}")
            print(f"   🆔 Message ID (DB): {result['data']['id']}")
            print(f"   📋 Content: {result['data']['content']}")
            
            # Información adicional del upload
            upload_info = result['data']['upload_info']
            print(f"\n📦 INFO DEL UPLOAD:")
            print(f"   📄 Filename: {upload_info['filename']}")
            print(f"   🎨 Content Type: {upload_info['content_type']}")
            print(f"   🏷️  Media Type: {upload_info['media_type']}")
            
            return True, result['data']['whatsapp_message_id']
        else:
            print(f"❌ ERROR: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False, None

def check_message_in_db(message_id):
    """Verifica el mensaje en la base de datos"""
    if not message_id:
        return
        
    print(f"\n🔍 VERIFICANDO MENSAJE EN BD: {message_id}")
    
    try:
        headers = {'X-API-Key': API_KEY}
        url = f"{BASE_URL}/v1/messages/whatsapp/{message_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()['data']
            print(f"✅ Mensaje encontrado en BD:")
            print(f"   📱 Status: {data['status']}")
            print(f"   🕐 Created: {data['created_at']}")
            print(f"   📋 Type: {data['message_type']}")
        else:
            print(f"❌ No se pudo verificar mensaje en BD: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")

def main():
    print("🎭 DIAGNÓSTICO COMPLETO DE STICKERS")
    print("Verificando formatos, especificaciones y envío")
    print("="*60)
    
    # Verificar API
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{BASE_URL}/v1/messages/test", headers=headers, timeout=5)
        if response.status_code != 200:
            print("❌ API no disponible")
            return
        print("✅ API disponible")
    except:
        print("❌ No se puede conectar a la API")
        return
    
    results = []
    
    # Test 1: Sticker WebP perfecto
    webp_content, webp_type, webp_name = create_proper_sticker()
    success1, msg_id1 = test_sticker(webp_content, webp_type, webp_name, "WebP 512x512 Transparente")
    results.append(("WebP Perfecto", success1))
    check_message_in_db(msg_id1)
    
    # Test 2: Sticker JPG para comparar
    jpg_content, jpg_type, jpg_name = create_jpg_sticker()
    success2, msg_id2 = test_sticker(jpg_content, jpg_type, jpg_name, "JPEG 512x512 Comparación")
    results.append(("JPEG Comparación", success2))
    check_message_in_db(msg_id2)
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 DIAGNÓSTICO FINAL")
    print(f"{'='*60}")
    
    for description, success in results:
        status = "✅ ENVIADO" if success else "❌ FALLÓ"
        print(f"{description:20} - {status}")
    
    print(f"\n💡 RECOMENDACIONES:")
    print(f"1. 🎨 Usar formato WebP con fondo transparente")
    print(f"2. 📏 Dimensiones exactas: 512x512 pixels")
    print(f"3. 📊 Tamaño menor a 100KB")
    print(f"4. 🚫 NO usar WebP animado")
    print(f"5. 📱 Verificar en cliente WhatsApp real")
    
    print(f"\n🔍 SIGUIENTE PASO:")
    print(f"Revisar los mensajes enviados en WhatsApp para confirmar si aparecen como stickers")

if __name__ == "__main__":
    main()
