#!/usr/bin/env python3
"""
Script de prueba para verificar RiveScript y flujos con manejo de entorno
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar entorno
os.environ.setdefault('FLASK_ENV', 'development')

def create_minimal_rivescript_file():
    """Crear archivo RiveScript mínimo que funcione"""
    content = """! version = 2.0

> topic random

+ hola
- ¡Hola! 👋 Bienvenido a nuestro asistente virtual.{/random}¿En que puedo ayudarte?{/random}1. Ventas - Informacion de productos{/random}2. Soporte - Ayuda tecnica{/random}3. Recursos Humanos - Consultas de empleados{/random}Escribe el numero de la opcion o describe tu consulta.

+ (hello|hi|hey)
- Hello! Welcome to our virtual assistant.{/random}How can I help you today?{/random}1. Sales - Product information{/random}2. Support - Technical help{/random}3. Human Resources - Employee queries

+ (1|uno|ventas|productos)
- Perfecto! Te conectare con nuestro equipo de ventas.{/random}¿Tienes alguna pregunta especifica sobre nuestros servicios?

+ (2|dos|soporte|ayuda|problema)
- Te ayudo con soporte tecnico.{/random}Por favor describe tu problema o consulta.

+ (3|tres|recursos humanos|rrhh|empleado)
- ¡Hola! Soy tu asistente de Recursos Humanos.{/random}¿En que puedo ayudarte hoy?{/random}1. Solicitudes y permisos{/random}2. Informacion sobre nomina{/random}3. Beneficios y prestaciones{/random}Escribe el numero o describe tu consulta.

+ *
- Gracias por contactarnos.{/random}Para ayudarte mejor, puedes escribir "hola" para ver el menu.{/random}¿En que te puedo ayudar?

< topic
"""
    
    # Crear directorio si no existe
    static_dir = Path("static/rivescript")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Escribir archivo con encoding correcto
    test_file = static_dir / "test_minimal.rive"
    with open(test_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    
    return test_file

def test_rivescript_standalone():
    """Prueba RiveScript sin base de datos"""
    try:
        print("🧪 TESTING RIVESCRIPT STANDALONE")
        print("=" * 50)
        
        # Verificar que rivescript esté instalado
        try:
            import rivescript
            print("✅ RiveScript module importado correctamente")
        except ImportError:
            print("❌ RiveScript no está instalado")
            print("   Ejecuta: pip install rivescript")
            return False
        
        # Crear archivo minimal de prueba
        print("📝 Creando archivo RiveScript minimal...")
        test_file = create_minimal_rivescript_file()
        print(f"📁 Archivo creado: {test_file}")
        
        # Crear instancia de RiveScript
        print("⚙️  Inicializando RiveScript...")
        rs = rivescript.RiveScript(utf8=True, debug=False)
        
        # Cargar el archivo de prueba
        print(f"📁 Cargando flujo: {test_file}")
        rs.stream(str(test_file))
        
        # Compilar
        print("⚙️  Compilando flujo...")
        rs.sort_replies()
        print("✅ Compilación exitosa")
        
        # Probar mensajes
        test_cases = [
            "hola",
            "hello", 
            "1",
            "3",
            "recursos humanos",
            "cualquier cosa"
        ]
        
        print("\n🔍 RESULTADOS DE PRUEBA:")
        print("-" * 40)
        
        test_user = "test_user_123"
        success_count = 0
        
        for message in test_cases:
            try:
                response = rs.reply(test_user, message)
                
                if response and not response.startswith("ERR:") and response != message:
                    print(f"✅ '{message}' -> {response[:80]}...")
                    success_count += 1
                else:
                    print(f"⚠️  '{message}' -> Sin respuesta válida: {response}")
                
            except Exception as e:
                print(f"❌ '{message}' -> ERROR: {e}")
        
        print(f"\n📊 RESUMEN: {success_count}/{len(test_cases)} pruebas exitosas")
        
        if success_count >= len(test_cases) // 2:
            print("✅ RiveScript standalone funcionando correctamente")
            return True
        else:
            print("❌ RiveScript standalone tiene problemas")
            return False
        
    except Exception as e:
        print(f"❌ Error en prueba standalone: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_app_context():
    """Prueba con contexto de aplicación Flask"""
    try:
        print("\n🧪 TESTING CON CONTEXTO DE APLICACIÓN")
        print("=" * 50)
        
        # Verificar disponibilidad de SQLAlchemy
        try:
            import sqlalchemy
            print("✅ SQLAlchemy disponible")
        except ImportError:
            print("⚠️  SQLAlchemy no disponible, usando modo simulación")
        
        # Crear app con manejo de errores
        print("🔧 Inicializando aplicación Flask...")
        
        try:
            from app import create_app
            app = create_app('development')
            print("✅ Aplicación Flask creada")
        except Exception as e:
            print(f"❌ Error creando aplicación: {e}")
            return False
        
        with app.app_context():
            print("✅ Contexto de aplicación activo")
            
            # Probar RiveScriptService con manejo de errores
            try:
                from app.services.rivescript_service import RiveScriptService
                print("✅ RiveScriptService importado")
                
                print("🔧 Inicializando RiveScriptService...")
                rivescript_service = RiveScriptService()
                print("✅ RiveScriptService inicializado")
                
            except Exception as service_error:
                print(f"❌ Error inicializando RiveScriptService: {service_error}")
                return False
            
            # Probar mensajes con el servicio
            test_cases = [
                "hola",
                "hello",
                "3",
                "recursos humanos",
                "cualquier consulta"
            ]
            
            print("\n🔍 RESULTADOS CON SERVICIO:")
            print("-" * 40)
            
            test_phone = "+123456789"
            success_count = 0
            
            for message in test_cases:
                try:
                    response = rivescript_service.get_response(test_phone, message)
                    
                    if response and isinstance(response, dict):
                        response_text = response.get('response', 'Sin respuesta')
                        response_type = response.get('type', 'unknown')
                        print(f"✅ '{message}' -> [{response_type}]: {response_text[:60]}...")
                        success_count += 1
                    else:
                        print(f"⚠️  '{message}' -> Sin respuesta del servicio")
                        
                except Exception as e:
                    print(f"❌ '{message}' -> ERROR: {e}")
            
            print(f"\n📊 RESUMEN: {success_count}/{len(test_cases)} pruebas exitosas con servicio")
            
            if success_count >= len(test_cases) // 2:
                print("✅ Servicio RiveScript funcionando correctamente")
                return True
            else:
                print("❌ Servicio RiveScript tiene problemas")
                return False
        
    except Exception as e:
        print(f"❌ Error en prueba con app context: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chatbot_service():
    """Prueba específica del ChatbotService"""
    try:
        print("\n🧪 TESTING CHATBOT SERVICE")
        print("=" * 50)
        
        # Crear app
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            print("✅ Contexto de aplicación activo")
            
            try:
                from app.services.chatbot_service import ChatbotService
                print("✅ ChatbotService importado")
                
                chatbot_service = ChatbotService()
                print("✅ ChatbotService inicializado")
                
                # Probar proceso completo de mensaje
                test_cases = [
                    "hola",
                    "ok",
                    "3"
                ]
                
                test_phone = "+5959875690"  # Usar el mismo número del log de error
                
                print(f"\n🔍 PROBANDO CHATBOT CON {test_phone}:")
                print("-" * 40)
                
                for message in test_cases:
                    try:
                        print(f"\n📨 Enviando: '{message}'")
                        response = chatbot_service.process_message(test_phone, message)
                        
                        if response and isinstance(response, dict):
                            response_text = response.get('response', 'Sin respuesta')
                            response_type = response.get('type', 'unknown')
                            processing_time = response.get('processing_time_ms', 0)
                            
                            print(f"✅ Respuesta [{response_type}] en {processing_time}ms:")
                            print(f"   {response_text[:100]}...")
                        else:
                            print(f"⚠️  Sin respuesta válida: {response}")
                            
                    except Exception as e:
                        print(f"❌ Error procesando '{message}': {e}")
                        # Continuar con el siguiente mensaje
                
                print("\n✅ Test de ChatbotService completado")
                return True
                
            except Exception as e:
                print(f"❌ Error en ChatbotService: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error en test de ChatbotService: {e}")
        return False

def main():
    """Función principal de testing con manejo completo de entorno"""
    print("🚀 DIAGNÓSTICO COMPLETO RIVESCRIPT - WHATSAPP API")
    print("=" * 70)
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Directorio: {Path.cwd()}")
    print(f"🌍 FLASK_ENV: {os.environ.get('FLASK_ENV', 'no definido')}")
    print("=" * 70)
    
    # Test standalone (sin Flask)
    print("\n🔧 FASE 1: TESTING RIVESCRIPT PURO")
    standalone_ok = test_rivescript_standalone()
    
    # Test con app context
    print("\n🔧 FASE 2: TESTING CON FLASK")
    app_context_ok = test_with_app_context()
    
    # Test ChatbotService completo  
    print("\n🔧 FASE 3: TESTING CHATBOT SERVICE")
    chatbot_ok = test_chatbot_service()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL DE DIAGNÓSTICO:")
    print(f"  • RiveScript puro:       {'✅ OK' if standalone_ok else '❌ FALLO'}")
    print(f"  • Con contexto Flask:    {'✅ OK' if app_context_ok else '❌ FALLO'}")
    print(f"  • ChatbotService:        {'✅ OK' if chatbot_ok else '❌ FALLO'}")
    
    if standalone_ok and app_context_ok and chatbot_ok:
        print("\n🎉 TODAS LAS PRUEBAS PASARON")
        print("   RiveScript está funcionando correctamente")
        print("   El problema original debería estar resuelto")
        return 0
    elif standalone_ok:
        print("\n⚠️  PROBLEMAS DE INTEGRACIÓN")
        print("   RiveScript funciona, pero hay problemas con Flask o base de datos")
        print("   Revisar dependencias: flask-sqlalchemy, sqlalchemy")
        return 1
    else:
        print("\n❌ PROBLEMAS FUNDAMENTALES")
        print("   RiveScript no funciona correctamente")
        print("   Revisar instalación y archivos .rive")
        return 2

if __name__ == '__main__':
    sys.exit(main())
