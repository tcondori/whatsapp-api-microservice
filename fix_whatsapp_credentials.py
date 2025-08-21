"""
Diagnóstico específico para error de envío real WhatsApp
Identifica si las credenciales son de test o producción
"""
import sys
import os
import json

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def diagnose_whatsapp_error():
    """
    Diagnostica el error específico de WhatsApp
    """
    print("=" * 60)
    print("🚨 DIAGNÓSTICO: ERROR 400 WHATSAPP API")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print("\n📋 TU ERROR ACTUAL:")
        print('❌ "400 Client Error: Bad Request for url: https://graph.facebook.com/v18.0/test_phone_id_123/messages"')
        
        print("\n🔍 ANÁLISIS DEL ERROR:")
        print("• La URL contiene 'test_phone_id_123'")
        print("• Esto indica que estás usando CREDENCIALES DE TEST")
        print("• Las credenciales de test NO pueden enviar mensajes reales")
        
        print("\n📊 VERIFICANDO CONFIGURACIÓN ACTUAL:")
        
        try:
            from database.connection import db
            from database.models import MessagingLine
            
            lines = MessagingLine.query.all()
            
            if not lines:
                print("   ❌ No hay líneas configuradas")
            else:
                for line in lines:
                    print(f"\n   📱 Línea {line.line_id}:")
                    print(f"      • Phone Number ID: {line.phone_number_id}")
                    
                    if 'test' in line.phone_number_id.lower():
                        print("      🚨 ¡ESTA ES UNA CREDENCIAL DE TEST!")
                        print("      ❌ No puede enviar mensajes reales")
                    else:
                        print("      ✅ Parece ser una credencial real")
                    
                    print(f"      • Número: {line.phone_number}")
                    print(f"      • Activa: {line.is_active}")
                    
        except Exception as e:
            print(f"   ❌ Error consultando base de datos: {e}")
        
        print("\n📋 VARIABLES DE ENTORNO:")
        
        # Verificar variables críticas
        token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'NO_CONFIGURADA')
        phone_id = os.getenv('LINE_1_PHONE_NUMBER_ID', 'NO_CONFIGURADA')
        
        print(f"   • WHATSAPP_ACCESS_TOKEN: {'✅ Configurada' if token != 'NO_CONFIGURADA' else '❌ No configurada'}")
        if 'test' in token.lower():
            print("     🚨 ¡TOKEN DE TEST! No sirve para envío real")
        
        print(f"   • LINE_1_PHONE_NUMBER_ID: {'✅ Configurada' if phone_id != 'NO_CONFIGURADA' else '❌ No configurada'}")
        if 'test' in phone_id.lower():
            print("     🚨 ¡PHONE ID DE TEST! No sirve para envío real")

def show_solution():
    """
    Muestra la solución paso a paso
    """
    print("\n" + "=" * 60)
    print("🔧 SOLUCIÓN PASO A PASO")
    print("=" * 60)
    
    print("""
🎯 PROBLEMA IDENTIFICADO:
   Estás usando credenciales de TEST que no pueden enviar mensajes reales.

🚀 SOLUCIÓN:

1️⃣ OBTENER CREDENCIALES REALES:
   • Ve a: https://developers.facebook.com/apps
   • Selecciona tu app de WhatsApp Business
   • En "WhatsApp" > "API Setup":
     - Copia el Access Token REAL
     - Copia el Phone Number ID REAL 
     - Copia tu Business Account ID

2️⃣ CONFIGURAR VARIABLES DE ENTORNO:
   Crear archivo .env o configurar en el sistema:
   
   WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxx (tu token real)
   LINE_1_PHONE_NUMBER_ID=1234567890 (tu phone ID real)
   LINE_1_PHONE_NUMBER=+5491234567890 (tu número real)
   WHATSAPP_BUSINESS_ID=1234567890 (tu business ID)

3️⃣ ACTUALIZAR BASE DE DATOS:
   Ejecutar script de actualización que voy a crear...

4️⃣ VERIFICAR:
   Probar nuevamente el envío

⚠️ IMPORTANTE:
• Tu cuenta de WhatsApp Business debe estar VERIFICADA
• El número debe estar registrado en Meta Business
• Debes tener permisos de envío de mensajes
""")

def create_update_script():
    """
    Crea script para actualizar a credenciales reales
    """
    script = """'''
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
"""
    
    with open('fix_production_credentials.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n📝 Script creado: fix_production_credentials.py")
    print("   Ejecuta este script DESPUÉS de configurar variables reales")

if __name__ == "__main__":
    try:
        # Diagnosticar el problema
        diagnose_whatsapp_error()
        
        # Mostrar solución
        show_solution()
        
        # Crear script de solución  
        create_update_script()
        
        print("\n" + "=" * 60)
        print("📋 SIGUIENTE PASO:")
        print("1. Configura variables de entorno REALES")
        print("2. Ejecuta: python fix_production_credentials.py")
        print("3. Prueba el envío nuevamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🏁 Diagnóstico completado")
