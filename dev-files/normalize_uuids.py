#!/usr/bin/env python
"""
Script para normalizar todos los UUIDs en la base de datos
Convierte todos los UUIDs al formato estándar CON guiones
"""
import uuid
from app import create_app
from database.models import ConversationFlow
from database.connection import db

def normalize_database_uuids():
    """Normalizar todos los UUIDs en la base de datos al formato con guiones"""
    
    app = create_app()
    
    with app.app_context():
        print("=== NORMALIZANDO UUIDs EN BASE DE DATOS ===")
        
        # Obtener todos los flujos
        flows = ConversationFlow.query.all()
        print(f"Total de flujos encontrados: {len(flows)}")
        
        updated_count = 0
        errors = []
        
        for flow in flows:
            try:
                current_id = str(flow.id)
                print(f"\nProcesando: {flow.name}")
                print(f"  ID actual: '{current_id}'")
                
                # Verificar si ya está en formato correcto
                if '-' in current_id and len(current_id) == 36:
                    print(f"  ✅ Ya está en formato correcto")
                    continue
                
                # Si no tiene guiones, convertir al formato estándar
                if '-' not in current_id and len(current_id) == 32:
                    # Crear UUID desde string sin guiones
                    uuid_obj = uuid.UUID(current_id)
                    new_id_str = str(uuid_obj)  # Esto añadirá los guiones
                    
                    print(f"  🔄 Convirtiendo a: '{new_id_str}'")
                    
                    # Actualizar directamente en la base de datos
                    db.session.execute(
                        "UPDATE conversation_flows SET id = ? WHERE id = ?",
                        (new_id_str, current_id)
                    )
                    
                    updated_count += 1
                    print(f"  ✅ Actualizado exitosamente")
                else:
                    print(f"  ⚠️  Formato no reconocido")
                    
            except Exception as e:
                error_msg = f"Error procesando flujo {flow.name}: {e}"
                errors.append(error_msg)
                print(f"  ❌ {error_msg}")
        
        # Confirmar cambios
        if updated_count > 0:
            try:
                db.session.commit()
                print(f"\n✅ NORMALIZACIÓN COMPLETADA")
                print(f"   - Flujos actualizados: {updated_count}")
                print(f"   - Errores: {len(errors)}")
                
                if errors:
                    print("\n❌ Errores encontrados:")
                    for error in errors:
                        print(f"   - {error}")
                        
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error confirmando cambios: {e}")
        else:
            print("\n✅ No se necesitaron cambios - todos los UUIDs ya están normalizados")
            
        # Verificar resultado final
        print(f"\n=== VERIFICACIÓN FINAL ===")
        flows_after = ConversationFlow.query.all()
        for flow in flows_after[:5]:  # Mostrar solo los primeros 5
            print(f"  {flow.name}: {flow.id}")

if __name__ == "__main__":
    normalize_database_uuids()
