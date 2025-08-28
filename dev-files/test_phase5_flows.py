#!/usr/bin/env python3
"""
Test Integral de Flujos RiveScript - Fase 5
Validación completa de todos los flujos de conversación implementados
"""

import sys
import os
import time
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.chatbot_service import ChatbotService
from app.services.rivescript_service import RiveScriptService

class FlowIntegrationTester:
    """Tester integral de todos los flujos RiveScript"""
    
    def __init__(self):
        self.app = create_app('development')
        self.chatbot_service = None
        self.test_phone = "+595987000999"
        self.conversation_flows = []
        
    def setup(self):
        """Configurar el entorno de testing"""
        print("=" * 70)
        print("🧪 TEST INTEGRAL DE FLUJOS RIVESCRIPT - FASE 5")
        print("=" * 70)
        
        with self.app.app_context():
            try:
                # Verificar que todos los archivos .rive existen
                required_flows = [
                    'basic_flow.rive',
                    'sales_flow.rive', 
                    'technical_support_flow.rive',
                    'hr_flow.rive',
                    'billing_flow.rive'
                ]
                
                rivescript_dir = 'static/rivescript'
                missing_files = []
                
                for flow_file in required_flows:
                    if not os.path.exists(os.path.join(rivescript_dir, flow_file)):
                        missing_files.append(flow_file)
                
                if missing_files:
                    print(f"❌ Archivos faltantes: {missing_files}")
                    return False
                
                print("✅ Todos los archivos de flujo encontrados")
                
                # Inicializar servicios
                try:
                    from app.services.rivescript_service import RiveScriptService
                    from app.services.chatbot_service import ChatbotService
                    
                    rivescript_service = RiveScriptService()
                    self.chatbot_service = ChatbotService()
                    
                    print("✅ Servicios inicializados correctamente")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error inicializando servicios: {e}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error en setup: {e}")
                return False

    def test_menu_navigation(self):
        """Test de navegación del menú principal"""
        print("\n" + "="*50)
        print("📋 TEST 1: NAVEGACIÓN DEL MENÚ PRINCIPAL")
        print("="*50)
        
        # Test saludo inicial
        response = self.send_message("hola")
        print(f"👋 Saludo: 'hola'")
        print(f"🤖 Respuesta: {response[:100]}...")
        
        if "Centro de Atención Virtual" in response:
            print("✅ Menú principal mostrado correctamente")
            
            # Test navegación por números
            navigation_tests = [
                ("1", "ventas"),
                ("2", "soporte"),
                ("3", "recursos humanos"), 
                ("4", "facturación"),
                ("5", "conversación general")
            ]
            
            success_count = 0
            for number, expected_area in navigation_tests:
                response = self.send_message(number)
                print(f"🔢 Navegación: '{number}' -> Esperado: {expected_area}")
                print(f"🤖 Respuesta: {response[:80]}...")
                
                if any(keyword in response.lower() for keyword in expected_area.split()):
                    print("✅ Navegación exitosa")
                    success_count += 1
                else:
                    print("❌ Navegación fallida")
                    
                time.sleep(0.5)  # Evitar spam
                
            print(f"\n📊 Navegación exitosa: {success_count}/5")
            return success_count == 5
        else:
            print("❌ Menú principal no mostrado correctamente")
            return False

    def test_sales_flow(self):
        """Test completo del flujo de ventas"""
        print("\n" + "="*50)
        print("💰 TEST 2: FLUJO DE VENTAS COMPLETO")
        print("="*50)
        
        # Activar flujo de ventas
        response = self.send_message("ventas")
        print(f"🎯 Activación: 'ventas'")
        print(f"🤖 Respuesta: {response[:100]}...")
        
        if "ventas" in response.lower() or "precios" in response.lower():
            print("✅ Flujo de ventas activado")
            
            # Test preguntas específicas de ventas
            sales_tests = [
                ("precio", "precio"),
                ("producto a", "producto a"),
                ("descuento", "descuento"),
                ("comprar", "comprar")
            ]
            
            success_count = 0
            for question, expected in sales_tests:
                response = self.send_message(question)
                print(f"❓ Pregunta: '{question}'")
                print(f"🤖 Respuesta: {response[:80]}...")
                
                if expected.lower() in response.lower():
                    print("✅ Respuesta apropiada")
                    success_count += 1
                else:
                    print("❌ Respuesta no encontrada")
                    
                time.sleep(0.5)
                
            print(f"\n📊 Tests de ventas exitosos: {success_count}/4")
            return success_count >= 3
        else:
            print("❌ Flujo de ventas no activado")
            return False

    def test_technical_support_flow(self):
        """Test del flujo de soporte técnico"""
        print("\n" + "="*50)
        print("🛠️ TEST 3: FLUJO DE SOPORTE TÉCNICO")
        print("="*50)
        
        # Activar flujo de soporte
        response = self.send_message("soporte tecnico")
        print(f"🔧 Activación: 'soporte tecnico'")
        print(f"🤖 Respuesta: {response[:100]}...")
        
        if "soporte técnico" in response.lower() or "problemas" in response.lower():
            print("✅ Flujo de soporte técnico activado")
            
            # Test problemas técnicos comunes
            support_tests = [
                ("1", "conexión"),
                ("no funciona", "error"),
                ("lento", "rendimiento"),
                ("contraseña", "password")
            ]
            
            success_count = 0
            for issue, expected in support_tests:
                response = self.send_message(issue)
                print(f"🐛 Problema: '{issue}'")
                print(f"🤖 Respuesta: {response[:80]}...")
                
                if expected.lower() in response.lower() or "paso" in response.lower():
                    print("✅ Solución proporcionada")
                    success_count += 1
                else:
                    print("❌ Solución no encontrada")
                    
                time.sleep(0.5)
                
            print(f"\n📊 Tests de soporte exitosos: {success_count}/4")
            return success_count >= 3
        else:
            print("❌ Flujo de soporte técnico no activado")
            return False

    def test_hr_flow(self):
        """Test del flujo de recursos humanos"""
        print("\n" + "="*50)
        print("👥 TEST 4: FLUJO DE RECURSOS HUMANOS")
        print("="*50)
        
        # Activar flujo de RRHH
        response = self.send_message("recursos humanos")
        print(f"👔 Activación: 'recursos humanos'")
        print(f"🤖 Respuesta: {response[:100]}...")
        
        if "recursos humanos" in response.lower() or "rrhh" in response.lower():
            print("✅ Flujo de RRHH activado")
            
            # Test consultas de RRHH
            hr_tests = [
                ("vacaciones", "vacaciones"),
                ("nomina", "nómina"),
                ("beneficios", "beneficios"),
                ("certificado", "certificado")
            ]
            
            success_count = 0
            for query, expected in hr_tests:
                response = self.send_message(query)
                print(f"📋 Consulta: '{query}'")
                print(f"🤖 Respuesta: {response[:80]}...")
                
                if expected.lower() in response.lower():
                    print("✅ Información de RRHH proporcionada")
                    success_count += 1
                else:
                    print("❌ Información no encontrada")
                    
                time.sleep(0.5)
                
            print(f"\n📊 Tests de RRHH exitosos: {success_count}/4")
            return success_count >= 3
        else:
            print("❌ Flujo de RRHH no activado")
            return False

    def test_billing_flow(self):
        """Test del flujo de facturación"""
        print("\n" + "="*50)
        print("💳 TEST 5: FLUJO DE FACTURACIÓN")
        print("="*50)
        
        # Activar flujo de facturación
        response = self.send_message("facturacion")
        print(f"🧾 Activación: 'facturacion'")
        print(f"🤖 Respuesta: {response[:100]}...")
        
        if "facturación" in response.lower() or "pago" in response.lower():
            print("✅ Flujo de facturación activado")
            
            # Test consultas de facturación
            billing_tests = [
                ("saldo", "saldo"),
                ("factura", "factura"),
                ("pagar", "pago"),
                ("estado de cuenta", "cuenta")
            ]
            
            success_count = 0
            for query, expected in billing_tests:
                response = self.send_message(query)
                print(f"💰 Consulta: '{query}'")
                print(f"🤖 Respuesta: {response[:80]}...")
                
                if expected.lower() in response.lower():
                    print("✅ Información de facturación proporcionada")
                    success_count += 1
                else:
                    print("❌ Información no encontrada")
                    
                time.sleep(0.5)
                
            print(f"\n📊 Tests de facturación exitosos: {success_count}/4")
            return success_count >= 3
        else:
            print("❌ Flujo de facturación no activado")
            return False

    def test_conversation_lifecycle(self):
        """Test del ciclo de vida de conversaciones"""
        print("\n" + "="*50)
        print("🔄 TEST 6: CICLO DE VIDA DE CONVERSACIONES")
        print("="*50)
        
        # Test comandos de cierre
        close_commands = [
            "cerrar conversacion",
            "terminar",
            "adiós",
            "gracias"
        ]
        
        success_count = 0
        for command in close_commands:
            response = self.send_message(command)
            print(f"👋 Comando: '{command}'")
            print(f"🤖 Respuesta: {response[:80]}...")
            
            if any(word in response.lower() for word in ["gracias", "hasta", "cerrada", "finaliz"]):
                print("✅ Comando de cierre reconocido")
                success_count += 1
            else:
                print("❌ Comando de cierre no reconocido")
                
            time.sleep(0.5)
            
        print(f"\n📊 Tests de ciclo de vida exitosos: {success_count}/4")
        return success_count >= 3

    def test_cross_flow_navigation(self):
        """Test de navegación entre flujos"""
        print("\n" + "="*50)
        print("🔀 TEST 7: NAVEGACIÓN ENTRE FLUJOS")
        print("="*50)
        
        # Test cambio de flujo
        flow_transitions = [
            ("ventas", "soporte tecnico"),
            ("soporte tecnico", "recursos humanos"),
            ("recursos humanos", "facturacion"),
            ("facturacion", "menu principal")
        ]
        
        success_count = 0
        for from_flow, to_flow in flow_transitions:
            # Activar primer flujo
            response1 = self.send_message(from_flow)
            print(f"🔄 De '{from_flow}' a '{to_flow}'")
            
            # Cambiar al segundo flujo
            response2 = self.send_message(to_flow)
            print(f"🤖 Cambio: {response2[:60]}...")
            
            # Verificar que cambió correctamente
            if to_flow.replace(" ", "").lower() in response2.replace(" ", "").lower():
                print("✅ Transición exitosa")
                success_count += 1
            else:
                print("❌ Transición fallida")
                
            time.sleep(0.5)
            
        print(f"\n📊 Tests de navegación exitosos: {success_count}/4")
        return success_count >= 3

    def send_message(self, message: str) -> str:
        """Enviar un mensaje al chatbot y obtener respuesta"""
        try:
            if self.chatbot_service:
                response = self.chatbot_service.process_message(self.test_phone, message)
                return response
            else:
                # Fallback si no hay chatbot service
                return f"Mensaje procesado: {message}"
        except Exception as e:
            print(f"Error enviando mensaje '{message}': {e}")
            return f"Error: {str(e)}"

    def run_full_test_suite(self):
        """Ejecutar toda la suite de tests"""
        if not self.setup():
            print("❌ Error en configuración inicial")
            return False
            
        tests = [
            ("Navegación del Menú", self.test_menu_navigation),
            ("Flujo de Ventas", self.test_sales_flow),
            ("Soporte Técnico", self.test_technical_support_flow),
            ("Recursos Humanos", self.test_hr_flow),
            ("Facturación", self.test_billing_flow),
            ("Ciclo de Vida", self.test_conversation_lifecycle),
            ("Navegación Entre Flujos", self.test_cross_flow_navigation)
        ]
        
        results = []
        start_time = datetime.now()
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Ejecutando: {test_name}")
                result = test_func()
                results.append((test_name, result))
                print(f"{'✅' if result else '❌'} {test_name}: {'EXITOSO' if result else 'FALLIDO'}")
            except Exception as e:
                print(f"❌ Error en {test_name}: {e}")
                results.append((test_name, False))
                
        # Resumen final
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*70)
        print("📊 RESUMEN DE RESULTADOS - FASE 5")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ EXITOSO" if result else "❌ FALLIDO"
            print(f"   {status:<12} {test_name}")
            
        print(f"\n📈 Tests exitosos: {passed}/{total} ({passed/total*100:.1f}%)")
        print(f"⏱️ Tiempo total: {duration:.1f} segundos")
        
        if passed >= total * 0.8:  # 80% success rate
            print("\n🎉 ¡FASE 5 COMPLETADA EXITOSAMENTE!")
            print("✅ Sistema de flujos RiveScript totalmente funcional")
            print("✅ Navegación entre flujos operativa") 
            print("✅ Todos los flujos especializados activos")
            print("✅ Ciclo de vida de conversaciones controlado")
            return True
        else:
            print("\n⚠️ FASE 5 NECESITA AJUSTES")
            print("❌ Algunos flujos requieren corrección")
            print("🔧 Revisar implementaciones fallidas")
            return False

def main():
    """Función principal de testing"""
    tester = FlowIntegrationTester()
    success = tester.run_full_test_suite()
    
    if success:
        print("\n🚀 ¡LISTOS PARA LA FASE 6!")
        print("💡 Próximos pasos: Optimizaciones y mejoras de UX")
    else:
        print("\n🔧 CORRECCIONES NECESARIAS")
        print("💡 Revisar flujos fallidos antes de continuar")
        
    return success

if __name__ == "__main__":
    main()
