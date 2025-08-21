"""
ACTUALIZACIÓN RÁPIDA DE CREDENCIALES
===================================
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def update_credentials():
    from entrypoint import create_app
    app = create_app()
    
    with app.app_context():
        from database.connection import db
        from database.models import MessagingLine
        
        # Actualizar todas las líneas con el ID correcto
        lines = MessagingLine.query.all()
        for line in lines:
            line.phone_number_id = '137474306106595'
            line.phone_number = '+59167028778'
            line.display_name = 'Mi WhatsApp Business'
            line.business_id = '137474306106595'
        
        db.session.commit()
        
        print("✅ CREDENCIALES ACTUALIZADAS:")
        print(f"   • PHONE_NUMBER_ID: 137474306106595")
        print(f"   • PHONE_NUMBER: +59167028778")
        print(f"   • DISPLAY_NAME: Mi WhatsApp Business")

if __name__ == "__main__":
    update_credentials()
