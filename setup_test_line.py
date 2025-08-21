"""
Script para crear línea de mensajería de prueba
Crea la línea por defecto requerida para las pruebas
"""
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entrypoint import create_app
from app.repositories.base_repo import MessagingLineRepository
from database.models import MessagingLine
from datetime import datetime

def setup_test_messaging_line():
    """
    Crea o actualiza la línea de mensajería de prueba
    """
    print("🔧 Configurando línea de mensajería de prueba...")
    
    # Crear aplicación
    app = create_app()
    
    with app.app_context():
        # Inicializar repositorio
        line_repo = MessagingLineRepository()
        
        try:
            # Buscar si ya existe la línea con ID 1
            existing_line = line_repo.get_by_line_id(1)
            
            if existing_line:
                print(f"✅ Línea de mensajería ya existe:")
                print(f"   • Line ID: {existing_line.line_id}")
                print(f"   • Display Name: {existing_line.display_name}")
                print(f"   • Phone: {existing_line.phone_number}")
                print(f"   • Activa: {existing_line.is_active}")
                print(f"   • Mensajes diarios: {existing_line.current_daily_count}/{existing_line.max_daily_messages}")
                return existing_line
            else:
                # Crear nueva línea de mensajería
                line_data = {
                    'line_id': 1,
                    'phone_number_id': 'test_phone_id_123',
                    'display_name': 'Línea de Prueba',
                    'phone_number': '+1234567890',
                    'webhook_url': 'https://webhook.test.com',
                    'is_active': True,
                    'max_daily_messages': 1000,
                    'current_daily_count': 0,
                    'last_reset_date': datetime.utcnow().date(),
                    'api_version': 'v18.0',
                    'business_id': 'test_business_123'
                }
                
                print(f"🔨 Creando nueva línea de mensajería:")
                print(f"   • Line ID: {line_data['line_id']}")
                print(f"   • Display Name: {line_data['display_name']}")
                print(f"   • Phone: {line_data['phone_number']}")
                
                new_line = line_repo.create(**line_data)
                print(f"✅ Línea creada exitosamente con ID: {new_line.id}")
                return new_line
                
        except Exception as e:
            print(f"❌ Error configurando línea: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def verify_messaging_line():
    """
    Verifica que la línea de mensajería esté funcionando
    """
    print("\n🧪 Verificando línea de mensajería...")
    
    app = create_app()
    
    with app.app_context():
        line_repo = MessagingLineRepository()
        
        try:
            # Obtener línea por ID
            line = line_repo.get_by_line_id(1)
            
            if line:
                print("✅ Verificación exitosa:")
                print(f"   • Puede enviar mensajes: {line.can_send_message()}")
                print(f"   • Capacidad restante: {line.max_daily_messages - line.current_daily_count}")
                
                # Probar incremento de contador
                initial_count = line.current_daily_count
                line.increment_message_count()
                print(f"   • Contador antes: {initial_count}")
                print(f"   • Contador después: {line.current_daily_count}")
                
                return True
            else:
                print("❌ Línea no encontrada")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando línea: {str(e)}")
            return False

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🛠️ CONFIGURACIÓN DE LÍNEA DE MENSAJERÍA DE PRUEBA")
        print("=" * 60)
        
        # Configurar línea
        line = setup_test_messaging_line()
        
        if line:
            # Verificar funcionalidad
            verify_messaging_line()
            print("\n✅ Configuración completada exitosamente")
        else:
            print("\n❌ Error en la configuración")
            
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🏁 Fin de la configuración")
