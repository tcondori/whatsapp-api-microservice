'''
Script para actualizar credenciales de PRODUCCIÓN
EJECUTAR SOLO DESPUÉS de configurar variables de entorno reales
'''
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def update_to_production():
    print("🔄 ACTUALIZANDO A CREDENCIALES DE PRODUCCIÓN")
    print("=" * 50)
    
    # Verificar variables reales
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.getenv('LINE_1_PHONE_NUMBER_ID') 
    phone_number = os.getenv('LINE_1_PHONE_NUMBER')
    
    if not all([token, phone_id, phone_number]):
        print("❌ Error: Variables de entorno faltantes:")
        print("   - WHATSAPP_ACCESS_TOKEN")
        print("   - LINE_1_PHONE_NUMBER_ID") 
        print("   - LINE_1_PHONE_NUMBER")
        return False
    
    if any('test' in str(v).lower() for v in [token, phone_id]):
        print("❌ Error: Aún tienes valores de TEST en las variables")
        print("   Configura valores REALES de producción")
        return False
    
    app = create_app()
    with app.app_context():
        try:
            from database.connection import db
            from database.models import MessagingLine
            
            # Actualizar línea principal
            line = MessagingLine.query.filter_by(line_id='1').first()
            if not line:
                line = MessagingLine(line_id='1')
                db.session.add(line)
            
            # Configurar valores de producción
            line.phone_number_id = phone_id
            line.phone_number = phone_number
            line.display_name = os.getenv('LINE_1_DISPLAY_NAME', 'Línea Principal')
            line.is_active = True
            line.current_daily_count = 0
            line.max_daily_messages = int(os.getenv('LINE_1_MAX_DAILY_MESSAGES', '1000'))
            
            db.session.commit()
            
            print("✅ ¡ACTUALIZACIÓN EXITOSA!")
            print(f"   • Phone Number ID: {line.phone_number_id}")
            print(f"   • Número: {line.phone_number}")
            print(f"   • Display Name: {line.display_name}")
            print("")
            print("🎉 ¡Ya puedes enviar mensajes REALES!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    update_to_production()
