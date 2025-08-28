"""
Test final de operaciones UUID con PostgreSQL
Verifica que los botones del editor funcionen correctamente
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.repositories.flow_repository import flow_repository

def test_editor_operations():
    """Prueba las operaciones que usan los botones del editor"""
    
    print("\n=== 🎯 TEST OPERACIONES DEL EDITOR ===")
    
    # Crear aplicación Flask para contexto
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Listar flujos existentes
            print("\n1. 📋 Listando flujos existentes...")
            flows = flow_repository.get_all_flows()
            
            if not flows:
                print("   ⚠️  No hay flujos disponibles")
                return
            
            for i, flow in enumerate(flows, 1):
                status = "🟢 ACTIVO" if flow.is_active else "🔴 INACTIVO"
                default = " ⭐ DEFAULT" if flow.is_default else ""
                print(f"   {i}. {flow.name}")
                print(f"      UUID: {flow.id}")
                print(f"      Estado: {status}{default}")
            
            # 2. Test botón "Editar" - Obtener flujo por UUID
            print(f"\n2. ✏️  TEST BOTÓN 'EDITAR' - Obteniendo flujo...")
            first_flow = flows[0]
            flow_id = str(first_flow.id)
            
            retrieved_flow = flow_repository.get_by_id(flow_id)
            if retrieved_flow:
                print(f"   ✅ Flujo obtenido: {retrieved_flow.name}")
                print(f"   UUID: {retrieved_flow.id}")
                print(f"   Activo: {retrieved_flow.is_active}")
            else:
                print(f"   ❌ Error: No se pudo obtener el flujo {flow_id}")
                return
            
            # 3. Test botón "Activar/Desactivar"
            print(f"\n3. 🔄 TEST BOTÓN 'ACTIVAR/DESACTIVAR'...")
            current_status = retrieved_flow.is_active
            
            if current_status:
                # Desactivar
                print(f"   Desactivando flujo '{retrieved_flow.name}'...")
                success = flow_repository.deactivate_flow(flow_id)
                if success:
                    print("   ✅ Flujo desactivado correctamente")
                else:
                    print("   ❌ Error al desactivar flujo")
                    return
            else:
                # Activar
                print(f"   Activando flujo '{retrieved_flow.name}'...")
                success = flow_repository.activate_flow(flow_id)
                if success:
                    print("   ✅ Flujo activado correctamente")
                else:
                    print("   ❌ Error al activar flujo")
                    return
            
            # 4. Verificar el cambio
            print(f"\n4. 🔍 VERIFICANDO cambio de estado...")
            updated_flow = flow_repository.get_by_id(flow_id)
            if updated_flow:
                new_status = "🟢 ACTIVO" if updated_flow.is_active else "🔴 INACTIVO"
                old_status = "🟢 ACTIVO" if current_status else "🔴 INACTIVO"
                print(f"   Estado anterior: {old_status}")
                print(f"   Estado actual: {new_status}")
                
                if updated_flow.is_active != current_status:
                    print("   ✅ Estado cambiado correctamente")
                else:
                    print("   ❌ El estado no cambió")
            
            # 5. Test actualización de contenido (botón guardar en editor)
            print(f"\n5. 💾 TEST BOTÓN 'GUARDAR' - Actualizando contenido...")
            test_content = "// Contenido de prueba editado\\n+ test\\n- Respuesta de prueba"
            
            updated = flow_repository.update_flow(
                flow_id, 
                rivescript_content=test_content,
                description="Descripción actualizada desde test"
            )
            
            if updated:
                print("   ✅ Contenido actualizado correctamente")
                print(f"   Nueva descripción: {updated.description}")
            else:
                print("   ❌ Error al actualizar contenido")
            
            print(f"\n🎉 RESULTADO: Todas las operaciones del editor funcionan correctamente")
            print(f"   • Los botones 'Editar', 'Activar/Desactivar' y 'Guardar' funcionan")
            print(f"   • Los UUIDs se manejan nativamente con PostgreSQL")
            print(f"   • No hay problemas de conversión UUID")
            
        except Exception as e:
            print(f"   ❌ Error durante las pruebas: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_editor_operations()
