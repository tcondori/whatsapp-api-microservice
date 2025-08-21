"""
Script de corrección ESPECÍFICA para eliminar línea de TEST
y usar solo la línea REAL que ya funciona
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app

def final_fix():
    """
    Elimina la línea de TEST y asegura que se use la línea REAL
    """
    print("🎯 CORRECCIÓN FINAL - ELIMINANDO LÍNEA DE TEST")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            from database.connection import db
            from database.models import MessagingLine
            
            print("📊 Estado ANTES del fix:")
            lines = MessagingLine.query.all()
            for line in lines:
                status = "🚨 TEST" if "test" in line.phone_number_id.lower() else "✅ REAL"
                print(f"   • Línea {line.line_id}: {line.phone_number_id} {status}")
            
            print(f"\n🗑️ ELIMINANDO LÍNEAS DE TEST...")
            
            # Eliminar todas las líneas que contienen 'test'
            test_lines = MessagingLine.query.filter(
                MessagingLine.phone_number_id.like('%test%')
            ).all()
            
            for line in test_lines:
                print(f"   ❌ Eliminando línea TEST: {line.line_id} ({line.phone_number_id})")
                db.session.delete(line)
            
            # Asegurar que tenemos al menos una línea con ID '1' (que es la que usa por defecto)
            line_1 = MessagingLine.query.filter_by(line_id='1').first()
            line_line1 = MessagingLine.query.filter_by(line_id='line_1').first()
            
            if not line_1 and line_line1:
                # Crear línea '1' basada en 'line_1' que es la real
                print(f"📝 Creando línea principal (ID=1) con datos REALES...")
                new_line = MessagingLine(
                    line_id='1',
                    phone_number_id=line_line1.phone_number_id,  # Usar el ID real
                    phone_number=line_line1.phone_number,
                    display_name=line_line1.display_name,
                    webhook_url=line_line1.webhook_url,
                    is_active=True,
                    max_daily_messages=line_line1.max_daily_messages,
                    current_daily_count=0,
                    api_version=line_line1.api_version,
                    business_id=line_line1.business_id
                )
                db.session.add(new_line)
                print(f"   ✅ Línea '1' creada con phone_number_id: {line_line1.phone_number_id}")
            
            # Guardar cambios
            db.session.commit()
            print("\n✅ Cambios guardados exitosamente!")
            
            print("\n📊 Estado DESPUÉS del fix:")
            lines = MessagingLine.query.all()
            for line in lines:
                status = "🚨 TEST" if "test" in line.phone_number_id.lower() else "✅ REAL"
                active = "🟢" if line.is_active else "🔴"
                print(f"   {active} Línea {line.line_id}: {line.phone_number_id} {status}")
                print(f"      • Nombre: {line.display_name}")
                print(f"      • Número: {line.phone_number}")
            
            # Verificar que no hay líneas de test
            test_count = MessagingLine.query.filter(
                MessagingLine.phone_number_id.like('%test%')
            ).count()
            
            if test_count == 0:
                print(f"\n🎉 ¡ÉXITO! No hay líneas de TEST en la base de datos")
                return True
            else:
                print(f"\n⚠️ Aún hay {test_count} líneas de TEST")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

def test_message_service():
    """
    Prueba que el servicio use la línea correcta
    """
    print(f"\n🧪 PROBANDO MessageService...")
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.api.messages.services import MessageService
            
            service = MessageService()
            
            # Probar con línea ID 1 (la más común)
            line = service._get_available_line(1)
            
            print(f"✅ Línea obtenida para ID 1:")
            print(f"   • Phone Number ID: {line.phone_number_id}")
            print(f"   • Display Name: {line.display_name}")
            
            if 'test' in line.phone_number_id.lower():
                print(f"❌ ¡ERROR! Aún devuelve línea de TEST")
                return False
            else:
                print(f"✅ ¡PERFECTO! Devuelve línea REAL")
                return True
                
        except Exception as e:
            print(f"❌ Error probando servicio: {e}")
            return False

if __name__ == "__main__":
    try:
        print("🚀 CORRECCIÓN FINAL DE LÍNEAS DE MENSAJERÍA")
        
        # Realizar corrección
        success = final_fix()
        
        if success:
            # Probar el servicio
            service_ok = test_message_service()
            
            if service_ok:
                print(f"\n🎉 ¡PROBLEMA COMPLETAMENTE SOLUCIONADO!")
                print(f"✅ Líneas de TEST eliminadas")
                print(f"✅ Solo líneas REALES disponibles")
                print(f"✅ MessageService funcionando correctamente")
                print(f"\n🎯 AHORA PUEDES:")
                print(f"   • Reiniciar el servidor")
                print(f"   • Intentar el envío real")
                print(f"   • Ya NO aparecerá test_phone_id_123")
            else:
                print(f"\n⚠️ Base de datos corregida pero el servicio tiene problemas")
        else:
            print(f"\n❌ No se pudo completar la corrección")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print(f"\n🏁 Corrección completada")
