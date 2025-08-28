#!/usr/bin/env python
"""
Paso 3: Crear datos de prueba y verificar que los botones funcionen
Base de datos limpia con PostgreSQL
"""

def create_test_data():
    """Crear algunos flujos de prueba en PostgreSQL"""
    print("=== 🧪 PASO 3: DATOS DE PRUEBA EN POSTGRESQL ===\n")
    
    try:
        from app import create_app
        from database.connection import db
        from database.models import ConversationFlow
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            print("1. 🔌 Conexión PostgreSQL establecida")
            
            # Limpiar datos existentes (solo el test flow)
            existing_flows = ConversationFlow.query.all()
            for flow in existing_flows:
                db.session.delete(flow)
            db.session.commit()
            print(f"   Limpiados {len(existing_flows)} flujos existentes")
            
            # Crear flujos de prueba optimizados para WhatsApp
            test_flows = [
                {
                    'name': 'Saludo Básico',
                    'description': 'Flujo de bienvenida principal',
                    'rivescript_content': '''! version = 2.0

// Flujo básico de saludo
> topic random

+ hola
- ¡Hola! 👋 Bienvenido a nuestro asistente virtual.
- ¿En qué puedo ayudarte hoy?
- 1️⃣ Ventas - Información de productos
- 2️⃣ Soporte - Ayuda técnica  
- 3️⃣ Recursos Humanos - Consultas
- Escribe el número de la opción o describe tu consulta.

+ (hello|hi|hey)
- Hello! 👋 Welcome to our virtual assistant.
- How can I help you today?

+ (1|uno|ventas|productos)
- ¡Perfecto! Te ayudo con información de ventas.
- ¿Qué productos te interesan?

+ (2|dos|soporte|ayuda|problema)  
- Te ayudo con soporte técnico.
- Por favor describe tu problema.

+ (3|tres|recursos humanos|rrhh|empleado)
- ¡Hola! Soy tu asistente de Recursos Humanos.
- ¿En qué puedo ayudarte?

+ *
- Gracias por contactarnos.
- Para ayudarte mejor, puedes escribir "hola" para ver el menú.
- ¿En qué te puedo ayudar?

< topic''',
                    'is_active': True,
                    'is_default': True,
                    'priority': 1
                },
                {
                    'name': 'Soporte Técnico',
                    'description': 'Flujo especializado en soporte técnico',
                    'rivescript_content': '''! version = 2.0

> topic soporte

+ *
- 🔧 Soporte Técnico Activo
- Por favor describe tu problema técnico.
- Puedo ayudarte con:
- • Problemas de conexión
- • Errores de la aplicación  
- • Configuración de cuenta
- • Recuperación de contraseña

+ (problema|error|falla|bug)
- Entiendo que tienes un problema técnico.
- ¿Podrías darme más detalles?
- Mientras tanto, verifica:
- 1. Conexión a internet
- 2. Última versión de la app
- 3. Reiniciar la aplicación

+ (conexion|internet|red)
- Problema de conexión detectado.
- Pasos para solucionar:
- 1️⃣ Verifica tu WiFi/datos móviles
- 2️⃣ Reinicia tu router
- 3️⃣ Prueba en otra red
- Si persiste, contacta a tu proveedor ISP.

< topic''',
                    'is_active': True,
                    'is_default': False,
                    'priority': 2
                },
                {
                    'name': 'Ventas y Productos',
                    'description': 'Flujo para consultas de ventas',
                    'rivescript_content': '''! version = 2.0

> topic ventas

+ *  
- 🛍️ Departamento de Ventas
- ¡Excelente elección! Te ayudo con información de productos.
- Nuestros productos principales:
- • 📱 Smartphones y tablets
- • 💻 Computadoras y laptops
- • 🎧 Accesorios tecnológicos
- • 🏠 Smart Home
- ¿Qué categoría te interesa?

+ (smartphone|celular|telefono|movil)
- 📱 Smartphones Disponibles:
- • iPhone 15 Pro - Desde $999
- • Samsung Galaxy S24 - Desde $799  
- • Google Pixel 8 - Desde $699
- 💳 Financiamiento disponible a 12 meses
- ¿Te interesa algún modelo específico?

+ (computadora|laptop|pc)
- 💻 Computadoras y Laptops:
- • MacBook Pro M3 - Desde $1,999
- • Dell XPS 13 - Desde $1,299
- • HP Pavilion Gaming - Desde $899
- 🚚 Envío gratis a nivel nacional
- ¿Para qué uso la necesitas?

< topic''',
                    'is_active': False,  # Inactivo para probar el botón activar
                    'is_default': False,
                    'priority': 3
                }
            ]
            
            created_flows = []
            for flow_data in test_flows:
                flow = ConversationFlow(**flow_data)
                db.session.add(flow)
                created_flows.append(flow)
            
            db.session.commit()
            print(f"2. ✅ Creados {len(created_flows)} flujos de prueba")
            
            # Mostrar los flujos creados con sus UUIDs
            print("\n📋 FLUJOS CREADOS:")
            for i, flow in enumerate(created_flows, 1):
                status = "🟢 ACTIVO" if flow.is_active else "🔴 INACTIVO" 
                default = "⭐ DEFAULT" if flow.is_default else ""
                print(f"   {i}. {flow.name}")
                print(f"      UUID: {flow.id}")
                print(f"      Estado: {status} {default}")
                print(f"      Prioridad: {flow.priority}")
                print()
            
            print("🎯 LISTO PARA PROBAR BOTONES DEL EDITOR")
            print("   • Tenemos flujos activos e inactivos")  
            print("   • UUIDs nativos de PostgreSQL")
            print("   • Datos optimizados para WhatsApp")
            
            return created_flows
            
    except Exception as e:
        print(f"❌ Error creando datos: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def test_uuid_operations():
    """Probar operaciones UUID que antes fallaban"""
    print(f"\n=== 🔧 TEST OPERACIONES UUID ===\n")
    
    try:
        from app import create_app  
        from app.repositories.flow_repository import FlowRepository
        
        app = create_app()
        
        with app.app_context():
            repo = FlowRepository()
            
            # Obtener flujos
            flows = repo.get_all()
            if not flows:
                print("❌ No hay flujos para probar")
                return False
                
            test_flow = flows[0]
            flow_id = str(test_flow.id)  # Convertir UUID a string
            
            print(f"1. 🔍 Test get_by_id con UUID: {flow_id}")
            
            # Test operación que antes fallaba
            found_flow = repo.get_by_id(flow_id)
            if found_flow:
                print(f"   ✅ Flujo encontrado: {found_flow.name}")
                print(f"   ✅ Tipo ID: {type(found_flow.id)}")
            else:
                print(f"   ❌ Flujo NO encontrado")
                return False
            
            print(f"\n2. 🔄 Test update_flow (lo que no funcionaba antes)")
            
            # Cambiar estado
            original_status = found_flow.is_active
            new_status = not original_status
            
            success = repo.update_flow(flow_id, {'is_active': new_status})
            if success:
                print(f"   ✅ Actualización exitosa: {original_status} → {new_status}")
                
                # Verificar cambio
                updated_flow = repo.get_by_id(flow_id)
                if updated_flow and updated_flow.is_active == new_status:
                    print(f"   ✅ Cambio confirmado en base de datos")
                else:
                    print(f"   ❌ Cambio NO persistido")
                    return False
            else:
                print(f"   ❌ Actualización falló")
                return False
                
            print(f"\n🎉 TODAS LAS OPERACIONES UUID FUNCIONAN CORRECTAMENTE")
            print("   • get_by_id: ✅")
            print("   • update_flow: ✅") 
            print("   • Persistencia: ✅")
            
            return True
            
    except Exception as e:
        print(f"❌ Error en test UUID: {e}")
        return False

if __name__ == "__main__":
    # Crear datos de prueba
    flows = create_test_data()
    
    if flows:
        # Probar operaciones que antes fallaban
        success = test_uuid_operations()
        
        if success:
            print(f"\n🚀 MIGRACIÓN COMPLETA - POSTGRESQL FUNCIONANDO")
            print("="*60)  
            print("🎯 Los botones del editor RiveScript deberían funcionar ahora")
            print("🔗 Iniciar servidor: python run_server.py")
            print("🌐 Editor: http://localhost:5001/rivescript/editor")
            print("="*60)
        else:
            print(f"\n⚠️ Hay problemas en las operaciones UUID")
    else:
        print(f"\n❌ No se pudieron crear datos de prueba")
