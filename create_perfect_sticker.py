#!/usr/bin/env python3
"""
Creador de sticker con especificaciones EXACTAS de WhatsApp Business API
"""
import io
from PIL import Image, ImageDraw, ImageFont
import requests

def create_whatsapp_compliant_sticker():
    """
    Crea un sticker que cumple TODAS las especificaciones de WhatsApp Business API
    """
    print("🎨 Creando sticker con especificaciones EXACTAS de WhatsApp...")
    
    # ESPECIFICACIONES OFICIALES WHATSAPP BUSINESS API:
    # - Formato: WebP estático
    # - Dimensiones: EXACTAMENTE 512x512 pixels
    # - Tamaño máximo: 100KB
    # - Fondo: Preferiblemente transparente
    # - Calidad: No excesivamente comprimido
    
    # Crear imagen base con especificaciones exactas
    img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))  # Fondo completamente transparente
    
    # Dibujar contenido centrado y llamativo
    draw = ImageDraw.Draw(img)
    
    # Círculo de fondo con borde
    center = 256
    radius = 180
    
    # Fondo del sticker
    draw.ellipse(
        [center-radius, center-radius, center+radius, center+radius], 
        fill=(52, 152, 219, 255),  # Azul sólido
        outline=(41, 128, 185, 255),  # Azul más oscuro para el borde
        width=8
    )
    
    # Texto principal
    try:
        # Intentar cargar fuente del sistema
        font_large = ImageFont.truetype("arial.ttf", 45)
        font_small = ImageFont.truetype("arial.ttf", 25)
    except:
        # Fallback a fuente por defecto
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Texto principal centrado
    main_text = "TEST"
    bbox = draw.textbbox((0, 0), main_text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = center - text_width // 2
    text_y = center - 30
    
    # Sombra del texto
    draw.text((text_x + 2, text_y + 2), main_text, fill=(0, 0, 0, 128), font=font_large)
    # Texto principal
    draw.text((text_x, text_y), main_text, fill=(255, 255, 255, 255), font=font_large)
    
    # Texto secundario
    sub_text = "STICKER"
    bbox2 = draw.textbbox((0, 0), sub_text, font=font_small)
    text_width2 = bbox2[2] - bbox2[0]
    
    text_x2 = center - text_width2 // 2
    text_y2 = center + 20
    
    # Sombra del subtexto
    draw.text((text_x2 + 1, text_y2 + 1), sub_text, fill=(0, 0, 0, 128), font=font_small)
    # Subtexto
    draw.text((text_x2, text_y2), sub_text, fill=(255, 255, 255, 255), font=font_small)
    
    # Añadir algunos elementos decorativos
    # Estrellitas alrededor
    star_positions = [
        (150, 150), (350, 150), (150, 350), (350, 350),
        (100, 256), (412, 256), (256, 100), (256, 412)
    ]
    
    for x, y in star_positions:
        # Estrella simple (rombo)
        points = [(x, y-8), (x+8, y), (x, y+8), (x-8, y)]
        draw.polygon(points, fill=(255, 215, 0, 255), outline=(255, 193, 7, 255))
    
    print(f"✅ Sticker diseñado con especificaciones WhatsApp:")
    print(f"   📏 Dimensiones: {img.size[0]}x{img.size[1]}px")
    print(f"   🎨 Modo: {img.mode} (con transparencia)")
    
    # Guardar con configuración óptima para WhatsApp
    webp_buffer = io.BytesIO()
    
    # Configuración específica para WebP compatible con WhatsApp
    img.save(
        webp_buffer, 
        format='WEBP', 
        quality=95,  # Alta calidad pero no máxima
        method=6,    # Mejor compresión
        lossless=False  # Compresión con pérdida para menor tamaño
    )
    
    webp_bytes = webp_buffer.getvalue()
    
    print(f"   📊 Tamaño final: {len(webp_bytes)} bytes ({len(webp_bytes)/1024:.1f}KB)")
    
    # Verificar que cumple límite de tamaño
    if len(webp_bytes) > 100 * 1024:  # 100KB
        print(f"   ⚠️  ADVERTENCIA: Tamaño excede 100KB recomendado")
    else:
        print(f"   ✅ Tamaño dentro del límite (< 100KB)")
    
    return webp_bytes, 'image/webp', 'whatsapp_compliant_sticker.webp'

def test_perfect_sticker():
    """Test con sticker perfectamente compatible"""
    
    BASE_URL = "http://127.0.0.1:5000"
    API_KEY = "dev-api-key"
    PHONE_NUMBER = "5491123456789"
    
    print("\n🧪 ENVIANDO STICKER PERFECTAMENTE COMPATIBLE")
    print("="*55)
    
    # Crear sticker perfecto
    sticker_content, content_type, filename = create_whatsapp_compliant_sticker()
    
    # Enviar
    files = {'file': (filename, sticker_content, content_type)}
    data = {
        'to': PHONE_NUMBER,
        'type': 'sticker',
        'messaging_line_id': '1'
    }
    
    headers = {'X-API-Key': API_KEY}
    url = f"{BASE_URL}/v1/messages/sticker/upload"
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 STICKER ENVIADO EXITOSAMENTE")
            print(f"📨 WhatsApp Message ID: {result['data']['whatsapp_message_id']}")
            print(f"📤 Media ID: {result['data']['upload_info']['media_id']}")
            
            # Guardar archivo localmente para inspección
            with open(f"generated_{filename}", 'wb') as f:
                f.write(sticker_content)
            print(f"💾 Sticker guardado como: generated_{filename}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

if __name__ == "__main__":
    print("🎭 CREADOR DE STICKERS COMPATIBLES CON WHATSAPP BUSINESS API")
    print("="*65)
    
    success = test_perfect_sticker()
    
    print(f"\n{'='*65}")
    print("📋 RESULTADO Y RECOMENDACIONES")
    print(f"{'='*65}")
    
    if success:
        print("✅ Sticker enviado correctamente")
        print("\n🔍 PASOS PARA VERIFICAR:")
        print("1. 📱 Abrir WhatsApp en el teléfono destino")
        print("2. 👀 Buscar mensaje reciente")
        print("3. 🎭 Verificar si aparece como sticker (no como imagen)")
        print("4. ✋ Debería poder ser añadido a favoritos de stickers")
        
        print(f"\n💡 SI AÚN NO APARECE COMO STICKER:")
        print("• 🎨 El formato puede verse como imagen normal")
        print("• 📱 Algunos clientes WhatsApp son estrictos con stickers")
        print("• ⏰ Puede tardar unos segundos en procesar")
        print("• 🔄 Intentar con archivo WebP real (no generado)")
    else:
        print("❌ Error enviando sticker")
    
    print(f"\n📚 ESPECIFICACIONES OFICIALES WHATSAPP:")
    print("• Formato: WebP estático únicamente")
    print("• Dimensiones: Exactamente 512x512 pixels")
    print("• Tamaño: Máximo 100KB")
    print("• Fondo: Transparente recomendado")
    print("• Calidad: No excesivamente comprimido")
