#!/usr/bin/env python3
"""
Script para verificar y crear la línea de mensajería por defecto
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def fix_messaging_line():
    """Verifica y crea la línea de mensajería por defecto"""
    try:
        # Importar después de cargar las variables de entorno
        from app import create_app
        from app.repositories.base_repo import MessagingLineRepository
        from database.connection import get_db_session
        
        print("🔧 Verificando línea de mensajería...")
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            # Inicializar repositorio
            line_repo = MessagingLineRepository()
            
            # Verificar si existe la línea por defecto
            default_line_id = os.getenv('DEFAULT_LINE_ID', 'line_1')
            line = line_repo.get_by_line_id(default_line_id)
            
            if line:
                print(f"✅ Línea encontrada: {line.line_id}")
                print(f"   📱 Phone Number ID: {line.phone_number_id}")
                print(f"   📞 Número: {line.phone_number}")
                print(f"   ✅ Activa: {line.is_active}")
                print(f"   📊 Límite diario: {line.max_daily_messages}")
                return True
            
            print(f"⚠️  Línea {default_line_id} no encontrada, creando...")
            
            # Crear línea por defecto
            line_config = {
                'line_id': default_line_id,
                'phone_number_id': os.getenv('LINE_1_PHONE_NUMBER_ID', os.getenv('WHATSAPP_PHONE_NUMBER_ID', '137474306106595')),
                'display_name': os.getenv('LINE_1_DISPLAY_NAME', 'Mi WhatsApp Business'),
                'phone_number': os.getenv('LINE_1_PHONE_NUMBER', '+59167028778'),
                'is_active': os.getenv('LINE_1_IS_ACTIVE', 'true').lower() == 'true',
                'max_daily_messages': int(os.getenv('LINE_1_MAX_DAILY_MESSAGES', '1000'))
            }
            
            # Crear la línea
            new_line = line_repo.create(**line_config)
            
            print(f"✅ Línea creada exitosamente:")
            print(f"   🆔 ID: {new_line.line_id}")
            print(f"   📱 Phone Number ID: {new_line.phone_number_id}")
            print(f"   📞 Número: {new_line.phone_number}")
            print(f"   📝 Nombre: {new_line.display_name}")
            print(f"   ✅ Activa: {new_line.is_active}")
            print(f"   📊 Límite diario: {new_line.max_daily_messages}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verificando/creando línea: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_message_endpoint():
    """Prueba el endpoint de mensajes después de crear la línea"""
    try:
        print("\n🧪 Probando endpoint de mensajes...")
        
        import requests
        
        # Datos de prueba
        test_data = {
            "to": "59167028778",
            "text": "¡Hola! Mensaje de prueba desde el endpoint reparado",
            "line_id": "line_1"
        }
        
        headers = {
            "X-API-Key": "dev-api-key",
            "Content-Type": "application/json"
        }
        
        # Hacer petición
        response = requests.post(
            "http://localhost:5001/v1/messages/text",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mensaje enviado exitosamente:")
            print(f"   📱 Número destino: {test_data['to']}")
            print(f"   📝 Texto: {test_data['text']}")
            print(f"   🆔 Message ID: {data.get('data', {}).get('whatsapp_message_id', 'N/A')}")
        else:
            print(f"❌ Error en endpoint:")
            print(f"   {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Servidor no está ejecutándose en http://localhost:5001")
        print("   Ejecuta primero: python run_server.py")
        return False
    except Exception as e:
        print(f"❌ Error probando endpoint: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🛠️  REPARAR LÍNEA DE MENSAJERÍA WHATSAPP")
    print("=" * 60)
    
    # Paso 1: Verificar/crear línea
    if fix_messaging_line():
        print("\n✅ Línea de mensajería configurada correctamente")
        
        # Paso 2: Probar endpoint si el servidor está corriendo
        test_message_endpoint()
        
    else:
        print("\n❌ No se pudo configurar la línea de mensajería")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("=" * 60)
    print("\n📝 PARA PROBAR MANUALMENTE:")
    print("curl -X POST http://localhost:5001/v1/messages/text \\")
    print('     -H "X-API-Key: dev-api-key" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{')
    print('       "to": "59167028778",')
    print('       "text": "Mensaje de prueba",')
    print('       "line_id": "line_1"')
    print('     }\'')
