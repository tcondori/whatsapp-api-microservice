"""
Script para inspeccionar y corregir los datos en la tabla messaging_lines
"""
import sys
sys.path.append('.')

from entrypoint import create_app
from database.connection import db
from database.models import MessagingLine

def inspect_messaging_lines():
    """Inspecciona el contenido actual de messaging_lines"""
    app = create_app()
    
    with app.app_context():
        print("🔍 INSPECCIONANDO TABLA messaging_lines:")
        print("=" * 50)
        
        lines = MessagingLine.query.all()
        print(f"📊 Líneas encontradas: {len(lines)}")
        
        for i, line in enumerate(lines, 1):
            print(f"\n📋 LÍNEA {i}:")
            print(f"  • ID interno: {line.id}")
            print(f"  • line_id: {line.line_id}")
            print(f"  • phone_number_id: {line.phone_number_id}")
            print(f"  • display_name: {line.display_name}")
            print(f"  • phone_number: {line.phone_number}")
            print(f"  • is_active: {line.is_active}")
            print(f"  • max_daily_messages: {line.max_daily_messages}")
            print(f"  • current_daily_count: {line.current_daily_count}")
            print(f"  • webhook_url: {line.webhook_url}")
            print(f"  • api_version: {line.api_version}")
            print(f"  • business_id: {line.business_id}")
            print(f"  • created_at: {line.created_at}")
            print(f"  • updated_at: {line.updated_at}")

def update_line_1_config():
    """Actualiza la configuración de line_1 con los datos reales"""
    app = create_app()
    
    with app.app_context():
        print("\n🔧 ACTUALIZANDO CONFIGURACIÓN DE line_1:")
        print("=" * 50)
        
        # Buscar line_1
        line_1 = MessagingLine.query.filter_by(line_id='line_1').first()
        
        if not line_1:
            print("❌ No se encontró line_1, creando nueva línea...")
            
            # Leer configuración real del .env
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            line_1 = MessagingLine(
                line_id='line_1',
                phone_number_id=os.getenv('LINE_1_PHONE_NUMBER_ID'),
                display_name=os.getenv('LINE_1_DISPLAY_NAME', 'Línea Comercial'),
                phone_number=os.getenv('LINE_1_PHONE_NUMBER'),
                is_active=True,
                max_daily_messages=int(os.getenv('LINE_1_MAX_DAILY_MESSAGES', '1000')),
                api_version='v18.0',
                business_id=os.getenv('WHATSAPP_BUSINESS_ID')
            )
            
            db.session.add(line_1)
            print("✅ Nueva línea line_1 creada")
        else:
            print("✅ line_1 encontrada, actualizando datos...")
            
            # Leer configuración real del .env
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            # Actualizar con datos reales
            line_1.phone_number_id = os.getenv('LINE_1_PHONE_NUMBER_ID')
            line_1.display_name = os.getenv('LINE_1_DISPLAY_NAME', 'Línea Comercial')
            line_1.phone_number = os.getenv('LINE_1_PHONE_NUMBER')
            line_1.is_active = True
            line_1.max_daily_messages = int(os.getenv('LINE_1_MAX_DAILY_MESSAGES', '1000'))
            line_1.api_version = 'v18.0'
            line_1.business_id = os.getenv('WHATSAPP_BUSINESS_ID')
            
            print("✅ line_1 actualizada con datos reales")
        
        # Guardar cambios
        try:
            db.session.commit()
            print("✅ Cambios guardados en base de datos")
            
            # Mostrar resultado final
            print(f"\n📊 CONFIGURACIÓN FINAL DE line_1:")
            print(f"  • phone_number_id: {line_1.phone_number_id}")
            print(f"  • display_name: {line_1.display_name}")
            print(f"  • phone_number: {line_1.phone_number}")
            print(f"  • business_id: {line_1.business_id}")
            print(f"  • is_active: {line_1.is_active}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error guardando cambios: {e}")

def validate_configuration():
    """Valida que la configuración esté correcta"""
    app = create_app()
    
    with app.app_context():
        print("\n✅ VALIDANDO CONFIGURACIÓN:")
        print("=" * 50)
        
        line_1 = MessagingLine.query.filter_by(line_id='line_1').first()
        
        if line_1:
            print(f"✅ line_1 existe en base de datos")
            
            # Validaciones
            if line_1.phone_number_id and line_1.phone_number_id != 'demo-phone-id':
                print(f"✅ phone_number_id válido: {line_1.phone_number_id}")
            else:
                print(f"❌ phone_number_id inválido: {line_1.phone_number_id}")
            
            if line_1.business_id:
                print(f"✅ business_id válido: {line_1.business_id}")
            else:
                print(f"❌ business_id faltante")
            
            if line_1.is_active:
                print(f"✅ Línea activa")
            else:
                print(f"❌ Línea inactiva")
                
        else:
            print(f"❌ line_1 NO existe en base de datos")

if __name__ == "__main__":
    inspect_messaging_lines()
    update_line_1_config()
    validate_configuration()
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"  1. La línea line_1 ahora debería tener datos reales")
    print(f"  2. Reinicia el servidor para usar la configuración actualizada")
    print(f"  3. Los mensajes deberían enviarse a través de WhatsApp API real")
    print(f"  4. Ya no necesitarás las variables LINE_1_* en .env para el funcionamiento básico")
