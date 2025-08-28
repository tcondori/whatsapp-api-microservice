# test_phase5_basic.py - Test básico de la Fase 5
# filepath: e:\DSW\proyectos\proy04\test_phase5_basic.py

import os
import sys

def test_rivescript_files():
    """Verifica que los archivos RiveScript existan"""
    print("🧪 Verificando archivos RiveScript de la Fase 5...")
    
    flow_files = [
        "static/rivescript/basic_flow.rive",
        "static/rivescript/sales_flow.rive", 
        "static/rivescript/technical_support_flow.rive",
        "static/rivescript/hr_flow.rive",
        "static/rivescript/billing_flow.rive"
    ]
    
    results = {}
    for file_path in flow_files:
        if os.path.exists(file_path):
            # Leer contenido y verificar tamaño
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
                results[file_path] = f"✅ {lines} líneas"
        else:
            results[file_path] = "❌ No encontrado"
    
    print("\n📋 RESULTADO DE ARCHIVOS RIVESCRIPT:")
    for file_path, status in results.items():
        print(f"   {os.path.basename(file_path):30s} - {status}")
    
    return all("✅" in status for status in results.values())

def test_rivescript_syntax():
    """Verifica la sintaxis básica de RiveScript"""
    print("\n🧪 Verificando sintaxis RiveScript...")
    
    try:
        import rivescript
        
        # Test básico de RiveScript
        rs = rivescript.RiveScript(utf8=True)
        
        test_script = """
            + hola
            - ¡Hola! ¿En qué puedo ayudarte?
            
            + menu
            - Opciones disponibles:
            ^ 1️⃣ VENTAS - Información sobre productos
            ^ 2️⃣ SOPORTE - Asistencia técnica
            ^ 3️⃣ RH - Recursos humanos
            ^ 4️⃣ FACTURACIÓN - Consultas de facturación
            ^ 5️⃣ AYUDA - Más opciones
            
            + (ventas|1)
            - 💰 ¡Perfecto! Te ayudo con información de ventas.
            
            + (soporte|soporte tecnico|2)
            - 🛠️ Te conectaré con soporte técnico.
        """
        
        rs.stream(test_script)
        rs.sort_replies()
        
        # Probar respuestas
        tests = [
            ("hola", ["Hola", "ayudarte"]),
            ("menu", ["Opciones", "VENTAS", "SOPORTE"]),
            ("ventas", ["ventas", "💰"]),
            ("1", ["ventas", "💰"]),
            ("soporte", ["soporte", "🛠️"]),
            ("soporte tecnico", ["soporte", "🛠️"])
        ]
        
        all_passed = True
        print("📋 PRUEBAS DE RESPUESTAS:")
        
        for input_text, expected_words in tests:
            response = rs.reply("user", input_text)
            contains_expected = any(word.lower() in response.lower() for word in expected_words)
            
            if contains_expected:
                print(f"   ✅ '{input_text}' -> Respuesta válida")
            else:
                print(f"   ❌ '{input_text}' -> '{response}' (esperaba: {expected_words})")
                all_passed = False
        
        return all_passed
        
    except ImportError:
        print("❌ RiveScript no está instalado")
        return False
    except Exception as e:
        print(f"❌ Error en RiveScript: {e}")
        return False

def test_flow_content():
    """Verifica el contenido de los flujos específicos"""
    print("\n🧪 Verificando contenido de flujos especializados...")
    
    flow_tests = {
        "static/rivescript/technical_support_flow.rive": [
            "soporte técnico", "problema", "error", "solucion"
        ],
        "static/rivescript/hr_flow.rive": [
            "recursos humanos", "vacaciones", "nomina", "beneficios" 
        ],
        "static/rivescript/billing_flow.rive": [
            "facturacion", "pago", "factura", "cuenta"
        ],
        "static/rivescript/sales_flow.rive": [
            "ventas", "producto", "precio", "comprar"
        ]
    }
    
    all_valid = True
    print("📋 CONTENIDO DE FLUJOS:")
    
    for file_path, keywords in flow_tests.items():
        if not os.path.exists(file_path):
            print(f"   ❌ {os.path.basename(file_path)} - Archivo no encontrado")
            all_valid = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            found_keywords = sum(1 for keyword in keywords if keyword in content)
            if found_keywords >= len(keywords) // 2:  # Al menos la mitad de las palabras clave
                print(f"   ✅ {os.path.basename(file_path)} - {found_keywords}/{len(keywords)} palabras clave")
            else:
                print(f"   ❌ {os.path.basename(file_path)} - Solo {found_keywords}/{len(keywords)} palabras clave")
                all_valid = False
                
        except Exception as e:
            print(f"   ❌ {os.path.basename(file_path)} - Error leyendo: {e}")
            all_valid = False
    
    return all_valid

def test_navigation_menu():
    """Verifica que el menú de navegación esté actualizado"""
    print("\n🧪 Verificando menú de navegación actualizado...")
    
    basic_flow_path = "static/rivescript/basic_flow.rive"
    
    if not os.path.exists(basic_flow_path):
        print("❌ Archivo basic_flow.rive no encontrado")
        return False
    
    try:
        with open(basic_flow_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        # Verificar que tenga las 5 opciones principales
        expected_areas = [
            "ventas", "soporte", "recursos humanos", "facturación", "ayuda"
        ]
        
        found_areas = [area for area in expected_areas if area in content]
        
        print(f"📋 ÁREAS EN MENÚ: {len(found_areas)}/5")
        for area in expected_areas:
            status = "✅" if area in content else "❌"
            print(f"   {status} {area.title()}")
        
        return len(found_areas) >= 4  # Al menos 4 de 5 áreas
        
    except Exception as e:
        print(f"❌ Error leyendo menú: {e}")
        return False

def main():
    """Ejecuta todos los tests básicos de la Fase 5"""
    print("=" * 70)
    print("🧪 TESTS BÁSICOS DE LA FASE 5 - FLUJOS RIVESCRIPT COMPLETOS")
    print("=" * 70)
    
    tests = [
        ("Archivos RiveScript", test_rivescript_files),
        ("Sintaxis RiveScript", test_rivescript_syntax), 
        ("Contenido de Flujos", test_flow_content),
        ("Menú de Navegación", test_navigation_menu)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        print("-" * 50)
        
        try:
            if test_func():
                passed += 1
                print(f"   ✅ {test_name}: PASÓ")
            else:
                print(f"   ❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"   ❌ {test_name}: ERROR - {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE LA FASE 5")
    print("=" * 70)
    print(f"✅ Tests exitosos: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ¡FASE 5 COMPLETADA EXITOSAMENTE!")
        print("✨ Todos los flujos RiveScript están implementados correctamente")
        print("🚀 El sistema está listo para testing completo")
    elif passed >= total * 0.75:
        print("\n✅ FASE 5 MAYORMENTE COMPLETADA")
        print("🔧 Algunos aspectos menores requieren ajustes")
    else:
        print("\n⚠️  FASE 5 NECESITA MÁS TRABAJO") 
        print("🛠️  Varios componentes requieren implementación o corrección")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
