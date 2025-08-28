#!/usr/bin/env python3
"""
Script para cargar el flujo completo de soporte técnico en la base de datos
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.repositories.flow_repository import FlowRepository
from database.models import ConversationFlow

def cargar_flujo_soporte_tecnico():
    """Carga el flujo de soporte técnico completo desde el archivo .rive"""
    print("🛠️ CARGANDO FLUJO DE SOPORTE TÉCNICO COMPLETO")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Leer el archivo completo
            archivo_flujo = "static/rivescript/technical_support_flow.rive"
            
            if not os.path.exists(archivo_flujo):
                print(f"❌ Archivo no encontrado: {archivo_flujo}")
                return False
            
            # Leer con diferentes encodings para evitar problemas
            contenido_flujo = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
                try:
                    with open(archivo_flujo, 'r', encoding=encoding) as f:
                        contenido_flujo = f.read()
                    print(f"✅ Archivo leído correctamente con encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if not contenido_flujo:
                print("❌ No se pudo leer el archivo con ningún encoding")
                return False
            
            print(f"📄 Contenido del archivo:")
            print(f"   📏 Tamaño: {len(contenido_flujo)} caracteres")
            print(f"   📊 Líneas: {len(contenido_flujo.splitlines())}")
            
            # 2. Verificar si ya existe el flujo
            flow_repo = FlowRepository()
            flujo_existente = None
            
            # Buscar por nombre similar
            flujos = flow_repo.get_all()  # Obtener todos, no solo activos
            for flujo in flujos:
                if any(palabra in flujo.name.lower() for palabra in ['soporte', 'tecnico', 'technical', 'support']):
                    flujo_existente = flujo
                    break
            
            # 3. Crear o actualizar el flujo
            if flujo_existente:
                print(f"\n🔄 Actualizando flujo existente: {flujo_existente.name}")
                
                # Actualizar contenido
                result = flow_repo.update(flujo_existente.id,
                    name="Soporte Técnico Completo",
                    description="Flujo completo de soporte técnico con troubleshooting detallado y escalación",
                    rivescript_content=contenido_flujo,
                    is_active=True,
                    priority=2,  # Alta prioridad para soporte técnico
                    fallback_to_llm=False
                )
                
                if result:
                    print("✅ Flujo actualizado exitosamente")
                else:
                    print("❌ Error actualizando flujo")
                    return False
                    
            else:
                print(f"\n➕ Creando nuevo flujo de soporte técnico")
                
                # Crear nuevo flujo
                nuevo_flujo = flow_repo.create(
                    name="Soporte Técnico Completo",
                    description="Flujo completo de soporte técnico con troubleshooting detallado y escalación",
                    rivescript_content=contenido_flujo,
                    is_active=True,
                    is_default=False,
                    priority=2,
                    fallback_to_llm=False,
                    max_context_messages=20,
                    usage_count=0
                )
                
                if nuevo_flujo:
                    print(f"✅ Nuevo flujo creado exitosamente con ID: {nuevo_flujo.id}")
                else:
                    print("❌ Error creando flujo")
                    return False
            
            # 4. Verificar carga en RiveScript
            print(f"\n🧪 Verificando carga del flujo...")
            
            from app.services.rivescript_service import RiveScriptService
            
            # Reinicializar RiveScript para que tome los cambios
            rivescript_service = RiveScriptService()
            
            # Forzar reinicialización
            rivescript_service._initialized = False
            rivescript_service._rs = None
            
            if rivescript_service._ensure_initialized():
                print("✅ RiveScript reinicializado correctamente")
                
                # Probar triggers específicos
                test_phone = "+5959871886"
                test_messages = [
                    "soporte tecnico",
                    "soporte técnico", 
                    "ayuda tecnica",
                    "problema tecnico",
                    "no funciona",
                    "error",
                    "falla"
                ]
                
                print(f"\n🎯 Probando triggers específicos:")
                funcionando = False
                
                for msg in test_messages:
                    try:
                        response = rivescript_service.get_response(test_phone, msg)
                        if response and response.get('response'):
                            resp_text = response['response']
                            if "Soporte Técnico" in resp_text and "🛠️" in resp_text:
                                print(f"✅ '{msg}' → ¡TRIGGER FUNCIONA!")
                                print(f"   Respuesta completa ({len(resp_text)} chars)")
                                # Verificar que tenga las opciones
                                opciones_encontradas = 0
                                for num in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
                                    if num in resp_text:
                                        opciones_encontradas += 1
                                print(f"   Opciones del menú: {opciones_encontradas}/5")
                                funcionando = True
                            else:
                                print(f"❌ '{msg}' → Respuesta incorrecta: {resp_text[:50]}...")
                        else:
                            print(f"❌ '{msg}' → Sin respuesta")
                    except Exception as e:
                        print(f"❌ '{msg}' → Error: {e}")
                
                if funcionando:
                    print(f"\n🎉 ¡FLUJO TÉCNICO FUNCIONANDO CORRECTAMENTE!")
                    return True
                else:
                    print(f"\n⚠️ Flujo cargado pero no responde correctamente")
            else:
                print("❌ Error reinicializando RiveScript")
            
            return False
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
            return False

def verificar_todos_los_flujos():
    """Verifica qué flujos están actualmente en la base de datos"""
    print("\n" + "=" * 60)
    print("📋 VERIFICANDO TODOS LOS FLUJOS EN BASE DE DATOS")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            flow_repo = FlowRepository()
            flujos = flow_repo.get_active_flows()
            
            print(f"📊 Total de flujos activos: {len(flujos)}")
            
            for i, flujo in enumerate(flujos, 1):
                print(f"\n{i}. 📄 {flujo.name}")
                print(f"   🆔 ID: {flujo.id}")
                print(f"   🎯 Prioridad: {flujo.priority}")
                print(f"   📊 Uso: {flujo.usage_count}")
                print(f"   📏 Contenido: {len(flujo.rivescript_content)} caracteres")
                
                # Buscar triggers principales
                lineas = flujo.rivescript_content.splitlines()
                triggers = [l.strip() for l in lineas if l.strip().startswith('+ ')]
                print(f"   🎯 Triggers: {len(triggers)}")
                
                # Mostrar algunos triggers importantes
                for trigger in triggers[:3]:
                    if len(trigger) > 80:
                        trigger = trigger[:80] + "..."
                    print(f"      • {trigger}")
                if len(triggers) > 3:
                    print(f"      ... y {len(triggers) - 3} más")
                    
        except Exception as e:
            print(f"❌ Error verificando flujos: {e}")

def test_flujo_completo():
    """Test completo del flujo técnico con diferentes mensajes"""
    print("\n" + "=" * 60)
    print("🧪 TEST COMPLETO DEL FLUJO DE SOPORTE TÉCNICO")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.services.rivescript_service import RiveScriptService
            
            rivescript_service = RiveScriptService()
            if not rivescript_service._ensure_initialized():
                print("❌ No se pudo inicializar RiveScript para testing")
                return
            
            test_phone = "+5959871886"
            
            # Test del flujo principal
            test_scenarios = [
                {
                    "name": "Activación del flujo",
                    "messages": ["soporte tecnico", "soporte técnico", "ayuda tecnica", "problema tecnico", "no funciona"],
                    "expected": "Soporte Técnico"
                },
                {
                    "name": "Opciones del menú",
                    "messages": ["1", "2", "3", "4", "5"],
                    "expected": ["Conexión", "Aplicación", "Rendimiento", "Configuración", "Técnico"]
                },
                {
                    "name": "Respuestas de seguimiento",
                    "messages": ["si", "no", "gracias", "menu principal"],
                    "expected": ["funcionado", "intentar", "alegra", "menú principal"]
                }
            ]
            
            for scenario in test_scenarios:
                print(f"\n🎬 Escenario: {scenario['name']}")
                print(f"-" * 40)
                
                for msg in scenario['messages']:
                    try:
                        response = rivescript_service.get_response(test_phone, msg)
                        if response and response.get('response'):
                            resp_text = response['response']
                            print(f"✅ '{msg}' → {len(resp_text)} chars")
                            
                            # Verificar contenido esperado
                            expected = scenario['expected']
                            if isinstance(expected, str):
                                if expected in resp_text:
                                    print(f"   ✅ Contiene: '{expected}'")
                                else:
                                    print(f"   ❌ No contiene: '{expected}'")
                            elif isinstance(expected, list):
                                found = [exp for exp in expected if exp in resp_text]
                                print(f"   ✅ Encontrados: {found}")
                                
                        else:
                            print(f"❌ '{msg}' → Sin respuesta")
                    except Exception as e:
                        print(f"❌ '{msg}' → Error: {e}")
                        
        except Exception as e:
            print(f"❌ Error en testing: {e}")

if __name__ == "__main__":
    print("💡 Recuerda activar el entorno virtual: .\\venv\\Scripts\\activate")
    
    # 1. Cargar flujo técnico
    if cargar_flujo_soporte_tecnico():
        print("\n🎉 ¡FLUJO DE SOPORTE TÉCNICO CARGADO EXITOSAMENTE!")
        
        # 2. Verificar todos los flujos
        verificar_todos_los_flujos()
        
        # 3. Test completo
        test_flujo_completo()
        
        print(f"\n" + "=" * 60)
        print(f"💬 AHORA PUEDES PROBAR EN EL SIMULADOR:")
        print(f"=" * 60)
        print(f"🌐 URL: http://localhost:5001/chat")
        print(f"")
        print(f"💬 Mensajes de prueba:")
        print(f"   • 'soporte tecnico'")
        print(f"   • 'ayuda tecnica'") 
        print(f"   • 'problema tecnico'")
        print(f"   • 'no funciona'")
        print(f"   • 'error'")
        print(f"")
        print(f"⚡ Después prueba las opciones:")
        print(f"   • '1' (problemas de conexión)")
        print(f"   • '2' (errores de aplicación)")
        print(f"   • '3' (problemas de rendimiento)")
        print(f"   • '4' (configuración de cuenta)")
        print(f"   • '5' (hablar con técnico)")
        
    else:
        print("\n❌ Hubo problemas cargando el flujo")
        print("🔧 Revisa los errores arriba y vuelve a intentar")
