"""
CONFIGURADOR DE CREDENCIALES REALES WHATSAPP BUSINESS API
==========================================================
Este script te ayuda a configurar las credenciales REALES de tu WhatsApp Business
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def show_current_config():
    """
    Mostrar configuración actual
    """
    print("📋 CONFIGURACIÓN ACTUAL")
    print("=" * 40)
    
    from entrypoint import create_app
    app = create_app()
    
    with app.app_context():
        from database.models import MessagingLine
        
        lines = MessagingLine.query.all()
        if lines:
            for line in lines:
                print(f"   • Línea '{line.line_id}':")
                print(f"     - PHONE_NUMBER_ID: {line.phone_number_id}")
                print(f"     - PHONE_NUMBER: {line.phone_number}")
                print(f"     - DISPLAY_NAME: {line.display_name}")
                print(f"     - BUSINESS_ID: {line.business_id}")
                print()
        else:
            print("   • No hay líneas configuradas")

def show_whatsapp_setup_guide():
    """
    Mostrar guía para obtener credenciales reales
    """
    print("\n🔧 CÓMO OBTENER TUS CREDENCIALES REALES DE WHATSAPP BUSINESS")
    print("=" * 70)
    print()
    print("1️⃣ Ve a Meta Business Manager:")
    print("   https://business.facebook.com/")
    print()
    print("2️⃣ Ve a 'Herramientas' > 'WhatsApp Manager'")
    print()
    print("3️⃣ Selecciona tu App de WhatsApp Business")
    print()
    print("4️⃣ En la sección 'API Setup', encontrarás:")
    print("   📱 PHONE_NUMBER_ID (Ejemplo: 1234567890123456)")
    print("   🔑 ACCESS_TOKEN (Ejemplo: EAAIbJ...)")
    print("   🏢 BUSINESS_ACCOUNT_ID (Ejemplo: 9876543210)")
    print()
    print("5️⃣ IMPORTANTE:")
    print("   • El PHONE_NUMBER_ID debe ser el ID numérico de tu número de WhatsApp")
    print("   • NO uses IDs de ejemplo o test")
    print("   • Verifica que tu número esté verificado y activo")
    print()

def configure_real_credentials():
    """
    Configurar credenciales reales interactivamente
    """
    print("\n⚙️ CONFIGURACIÓN DE CREDENCIALES REALES")
    print("=" * 50)
    print("⚠️  Solo ingresa credenciales REALES de WhatsApp Business API")
    print()
    
    # Solicitar credenciales
    phone_number_id = input("📱 Ingresa tu PHONE_NUMBER_ID real: ").strip()
    if not phone_number_id or len(phone_number_id) < 10:
        print("❌ PHONE_NUMBER_ID inválido")
        return False
    
    phone_number = input("📞 Ingresa tu número de WhatsApp (ej: +1234567890): ").strip()
    if not phone_number:
        phone_number = "+1234567890"  # Default
    
    display_name = input("🏷️ Nombre de la línea (ej: Mi WhatsApp Business): ").strip()
    if not display_name:
        display_name = "WhatsApp Business Line"
    
    business_id = input("🏢 BUSINESS_ACCOUNT_ID (opcional): ").strip()
    if not business_id:
        business_id = "unknown"
    
    print(f"\n📋 CREDENCIALES A CONFIGURAR:")
    print(f"   • PHONE_NUMBER_ID: {phone_number_id}")
    print(f"   • PHONE_NUMBER: {phone_number}")
    print(f"   • DISPLAY_NAME: {display_name}")
    print(f"   • BUSINESS_ID: {business_id}")
    print()
    
    confirm = input("¿Confirmas estas credenciales? (s/n): ").lower()
    if confirm != 's':
        print("❌ Configuración cancelada")
        return False
    
    # Actualizar base de datos
    try:
        from entrypoint import create_app
        app = create_app()
        
        with app.app_context():
            from database.connection import db
            from database.models import MessagingLine
            
            # Eliminar líneas existentes
            MessagingLine.query.delete()
            
            # Crear nueva línea con credenciales reales
            new_line = MessagingLine(
                line_id='1',
                phone_number_id=phone_number_id,
                phone_number=phone_number,
                display_name=display_name,
                is_active=True,
                max_daily_messages=1000,
                current_daily_count=0,
                api_version='v18.0',
                business_id=business_id
            )
            
            db.session.add(new_line)
            db.session.commit()
            
            print("✅ Credenciales configuradas exitosamente!")
            return True
            
    except Exception as e:
        print(f"❌ Error configurando credenciales: {e}")
        return False

def test_credentials():
    """
    Test básico de credenciales
    """
    print(f"\n🧪 TEST DE CREDENCIALES")
    print("=" * 30)
    print("ℹ️  Este test verifica que las credenciales estén configuradas")
    print("   Para un test real, usa el endpoint /v1/messages/text")
    
    from entrypoint import create_app
    app = create_app()
    
    with app.app_context():
        from database.models import MessagingLine
        
        line = MessagingLine.query.filter_by(line_id='1').first()
        if line:
            print(f"✅ Línea configurada:")
            print(f"   • PHONE_NUMBER_ID: {line.phone_number_id}")
            print(f"   • URL que se usará: https://graph.facebook.com/v18.0/{line.phone_number_id}/messages")
            
            # Verificar que no sea un ID de prueba
            if 'test' in line.phone_number_id.lower() or len(line.phone_number_id) < 10:
                print(f"⚠️  ADVERTENCIA: Este parece ser un ID de prueba")
                return False
            else:
                print(f"✅ ID parece válido (longitud: {len(line.phone_number_id)})")
                return True
        else:
            print("❌ No hay línea configurada")
            return False

if __name__ == "__main__":
    print("🚀 CONFIGURADOR DE WHATSAPP BUSINESS API")
    print("=" * 60)
    
    # Mostrar configuración actual
    show_current_config()
    
    # Mostrar guía
    show_whatsapp_setup_guide()
    
    # Preguntar si quiere configurar
    print("\n" + "=" * 60)
    configure = input("¿Quieres configurar credenciales reales ahora? (s/n): ").lower()
    
    if configure == 's':
        if configure_real_credentials():
            test_credentials()
    else:
        print("\n📌 PASOS SIGUIENTES:")
        print("1. Obtén tus credenciales reales de Meta Business Manager")
        print("2. Ejecuta este script nuevamente para configurarlas")
        print("3. Prueba con: POST http://localhost:5000/v1/messages/text")
    
    print("\n" + "=" * 60)
