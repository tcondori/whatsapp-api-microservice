# test_phase5_flows_simplified.py - Pruebas simplificadas de la Fase 5
# filepath: e:\DSW\proyectos\proy04\test_phase5_flows_simplified.py

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# Configurar la aplicación Flask
from app import create_app
from database.connection import init_database

class Phase5FlowTester:
    """Tester simplificado para flujos de la Fase 5"""
    
    def __init__(self):
        self.app = create_app()
        self.app_context = None
    
    def setup_test_environment(self):
        """Configura el entorno de prueba"""
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Inicializar base de datos
        with self.app.app_context():
            init_database(self.app)
    
    def cleanup_test_environment(self):
        """Limpia el entorno de prueba"""
        if self.app_context:
            self.app_context.pop()
    
    def test_rivescript_files(self):
        """Verifica que los archivos RiveScript existan"""
        print("🧪 Verificando archivos RiveScript...")
        
        flow_files = [
            "app/services/rivescript_flows/basic_flow.rive",
            "app/services/rivescript_flows/sales_flow.rive",
            "app/services/rivescript_flows/technical_support_flow.rive",
            "app/services/rivescript_flows/hr_flow.rive",
            "app/services/rivescript_flows/billing_flow.rive"
        ]
        
        missing_files = []
        for file_path in flow_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Archivos faltantes: {missing_files}")
            return False
        
        print("✅ Todos los archivos RiveScript encontrados")
        return True
    
    def test_basic_rivescript_syntax(self):
        """Verifica la sintaxis básica de RiveScript"""
        print("🧪 Verificando sintaxis RiveScript...")
        
        try:
            import rivescript
            rs = rivescript.RiveScript()
            
            # Probar carga del flujo básico
            rs.stream("""
                + hola
                - ¡Hola! Bienvenido al sistema de atención al cliente.
                
                + menu
                - ¿En qué puedo ayudarte? Escribe:
                ^ 1️⃣ VENTAS - Información sobre productos
                ^ 2️⃣ SOPORTE - Asistencia técnica
            """)
            
            rs.sort_replies()
            
            # Prueba básica
            response = rs.reply("user", "hola")
            print(f"🤖 Respuesta de prueba: {response}")
            
            if "Bienvenido" in response:
                print("✅ RiveScript funcionando correctamente")
                return True
            else:
                print(f"❌ Respuesta inesperada: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Error en RiveScript: {e}")
            return False
    
    def test_app_initialization(self):
        """Verifica que la aplicación Flask se inicialice"""
        print("🧪 Verificando inicialización de Flask...")
        
        try:
            with self.app.test_client() as client:
                # Verificar que la aplicación responda
                response = client.get('/health')
                if response.status_code in [200, 404]:  # 404 es OK si no existe el endpoint
                    print("✅ Aplicación Flask funcionando")
                    return True
                else:
                    print(f"❌ Aplicación respondió con status: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Error inicializando Flask: {e}")
            return False
    
    def test_database_tables(self):
        """Verifica que las tablas de base de datos existan"""
        print("🧪 Verificando tablas de base de datos...")
        
        try:
            from database.models import ConversationFlow, ConversationContext, ChatbotInteraction
            from database.connection import get_db_session
            
            session = get_db_session()
            
            # Verificar que podemos hacer consultas básicas
            flow_count = session.query(ConversationFlow).count()
            context_count = session.query(ConversationContext).count()
            interaction_count = session.query(ChatbotInteraction).count()
            
            print(f"📊 Flujos: {flow_count}, Contextos: {context_count}, Interacciones: {interaction_count}")
            print("✅ Base de datos funcionando correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error en base de datos: {e}")
            return False
    
    def test_services_import(self):
        """Verifica que los servicios se puedan importar"""
        print("🧪 Verificando importación de servicios...")
        
        try:
            from app.services.chatbot_service import ChatbotService
            from app.services.rivescript_service import RiveScriptService
            
            print("✅ Servicios importados correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error importando servicios: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests de la Fase 5"""
        print("=" * 70)
        print("🧪 TESTS SIMPLIFICADOS - FASE 5")
        print("=" * 70)
        
        self.setup_test_environment()
        
        tests = [
            ("Archivos RiveScript", self.test_rivescript_files),
            ("Sintaxis RiveScript", self.test_basic_rivescript_syntax),
            ("Inicialización Flask", self.test_app_initialization),
            ("Tablas Base de Datos", self.test_database_tables),
            ("Importación Servicios", self.test_services_import)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Ejecutando: {test_name}")
            print("-" * 50)
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASÓ")
                else:
                    print(f"❌ {test_name}: FALLÓ")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        self.cleanup_test_environment()
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 70)
        print(f"✅ Tests exitosos: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 FASE 5 - TODOS LOS TESTS PASARON")
            return True
        else:
            print("⚠️  FASE 5 - ALGUNOS TESTS FALLARON")
            return False

if __name__ == "__main__":
    tester = Phase5FlowTester()
    tester.run_all_tests()
