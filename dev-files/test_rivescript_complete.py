"""
Script de prueba completo para verificar flujos RiveScript
Incluye inicialización completa del servicio y pruebas detalladas
"""
from app import create_app
from app.services.rivescript_service import RiveScriptService
from app.repositories.flow_repository import FlowRepository

def probar_rivescript_completo():
    """
    Prueba completa del servicio RiveScript con inicialización adecuada
    """
    print("🧪 PRUEBA COMPLETA DE RIVESCRIPT SERVICE")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        try:
            # Inicializar servicio
            print("1️⃣ Inicializando RiveScriptService...")
            rivescript_service = RiveScriptService()
            
            # Verificar flujos disponibles
            print("\n2️⃣ Verificando flujos en base de datos...")
            repo = FlowRepository()
            flows = repo.get_all_flows()
            active_flows = [f for f in flows if f.is_active]
            
            print(f"   📊 Total flujos: {len(flows)}")
            print(f"   🟢 Flujos activos: {len(active_flows)}")
            
            for flow in active_flows:
                print(f"   • {flow.name} (ID: {str(flow.id)[:8]}...)")
            
            # Probar inicialización forzada
            print("\n3️⃣ Forzando inicialización del servicio...")
            init_result = rivescript_service._ensure_initialized()
            print(f"   Inicialización exitosa: {init_result}")
            
            # Verificar disponibilidad de RiveScript
            print(f"   RiveScript disponible: {rivescript_service.rs is not None}")
            
            # Probar mensajes con diferentes usuarios
            print("\n4️⃣ Probando conversaciones...")
            print("-" * 30)
            
            test_conversations = [
                ("usuario_1", "soporte"),
                ("usuario_1", "1"),
                ("usuario_1", "sí"),
                ("usuario_2", "ayuda"),
                ("usuario_2", "contraseña"),
                ("usuario_3", "hola"),
                ("usuario_3", "gracias")
            ]
            
            for user, msg in test_conversations:
                print(f"👤 {user}: {msg}")
                try:
                    response_data = rivescript_service.get_response(user, msg)
                    
                    if response_data:
                        response = response_data.get('response', 'Sin respuesta')
                        response_type = response_data.get('type', 'desconocido')
                        confidence = response_data.get('confidence_score', 0.0)
                        
                        # Limitar respuesta para visualización
                        if len(response) > 200:
                            response_short = response[:200] + "..."
                        else:
                            response_short = response
                        
                        print(f"🤖 Bot: {response_short}")
                        print(f"   📊 Tipo: {response_type}, Confianza: {confidence}")
                    else:
                        print("🤖 Bot: [Sin respuesta]")
                        print("   ⚠️  El servicio retornó None")
                    
                except Exception as e:
                    print(f"🤖 Bot: [ERROR]")
                    print(f"   ❌ Error: {e}")
                
                print("-" * 30)
            
            print("\n5️⃣ Diagnóstico del sistema...")
            
            # Verificar si RiveScript está instalado
            try:
                import rivescript
                print("   ✅ Módulo RiveScript: Instalado")
                print(f"   📦 Versión: {getattr(rivescript, '__version__', 'desconocida')}")
            except ImportError:
                print("   ❌ Módulo RiveScript: NO instalado")
                print("   💡 Instala con: pip install rivescript")
            
            # Verificar estado del servicio
            if hasattr(rivescript_service, 'rs') and rivescript_service.rs:
                print("   ✅ Instancia RiveScript: Creada")
            else:
                print("   ❌ Instancia RiveScript: NO creada")
            
            # Verificar repositorios
            if rivescript_service.flow_repo:
                print("   ✅ FlowRepository: Inicializado")
            else:
                print("   ❌ FlowRepository: NO inicializado")
            
            if rivescript_service.context_repo:
                print("   ✅ ConversationRepository: Inicializado")  
            else:
                print("   ❌ ConversationRepository: NO inicializado")
            
            print("\n🎉 DIAGNÓSTICO COMPLETADO")
            return True
            
        except Exception as e:
            print(f"\n💥 ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            return False

def instalar_rivescript_si_necesario():
    """
    Verifica e instala RiveScript si no está disponible
    """
    try:
        import rivescript
        print("✅ RiveScript ya está instalado")
        return True
    except ImportError:
        print("⚠️  RiveScript no está instalado")
        print("💡 Para instalarlo ejecuta: pip install rivescript")
        
        # Intentar instalación automática
        try:
            import subprocess
            print("🔄 Intentando instalar RiveScript automáticamente...")
            result = subprocess.run(['pip', 'install', 'rivescript'], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ RiveScript instalado exitosamente")
                return True
            else:
                print(f"❌ Error instalando: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error en instalación automática: {e}")
            return False

def main():
    """
    Función principal de diagnóstico y prueba
    """
    print("🚀 DIAGNÓSTICO COMPLETO DE RIVESCRIPT")
    print("=" * 55)
    
    # Paso 1: Verificar/instalar RiveScript
    if not instalar_rivescript_si_necesario():
        print("\n💥 No se puede continuar sin RiveScript")
        return False
    
    # Paso 2: Probar servicio completo
    success = probar_rivescript_completo()
    
    if success:
        print("\n🏆 SISTEMA RIVESCRIPT FUNCIONANDO CORRECTAMENTE")
        print("🌐 Ahora puedes usar las interfaces:")
        print("   • Dashboard: http://localhost:5001/rivescript/")
        print("   • Simulador: http://localhost:5001/rivescript/simulator")
        print("   • Editor: http://localhost:5001/rivescript/editor")
    else:
        print("\n🔧 SISTEMA RIVESCRIPT NECESITA CORRECCIONES")
        print("📋 Revisa los errores mostrados arriba")
    
    return success

if __name__ == "__main__":
    main()
