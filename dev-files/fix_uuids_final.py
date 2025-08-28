#!/usr/bin/env python3
"""
Verificar y corregir UUIDs inconsistentes en la base de datos
"""
import sqlite3
import uuid

def check_and_fix_uuids():
    """Verificar y corregir UUIDs"""
    print("🔍 Verificando UUIDs en la base de datos...")
    
    db_path = 'instance/whatsapp_test.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Contar UUIDs por formato
    cursor.execute('SELECT COUNT(*) FROM conversation_flows WHERE LENGTH(id) = 36')
    with_hyphens = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM conversation_flows WHERE LENGTH(id) = 32')  
    without_hyphens = cursor.fetchone()[0]
    
    print(f"📊 UUIDs con guiones (36 chars): {with_hyphens}")
    print(f"📊 UUIDs sin guiones (32 chars): {without_hyphens}")
    print(f"📊 Total: {with_hyphens + without_hyphens}")
    
    if without_hyphens > 0:
        print("\n❌ HAY UUIDs SIN GUIONES - corrigiendo...")
        
        # Obtener todos los UUIDs sin guiones
        cursor.execute('SELECT id, name FROM conversation_flows WHERE LENGTH(id) = 32')
        rows = cursor.fetchall()
        
        print(f"🔧 Corrigiendo {len(rows)} UUIDs...")
        
        for old_id, name in rows:
            # Convertir UUID sin guiones a formato con guiones
            try:
                uuid_obj = uuid.UUID(old_id)
                new_id = str(uuid_obj)  # Esto incluirá los guiones automáticamente
                
                print(f"  📝 {old_id} → {new_id} ({name})")
                
                # Actualizar en la base de datos
                cursor.execute('UPDATE conversation_flows SET id = ? WHERE id = ?', (new_id, old_id))
                
            except ValueError as e:
                print(f"  ❌ Error con UUID {old_id}: {e}")
        
        # Confirmar cambios
        conn.commit()
        print("✅ Corrección completada")
        
        # Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM conversation_flows WHERE LENGTH(id) = 32')
        remaining = cursor.fetchone()[0]
        print(f"📊 UUIDs sin guiones restantes: {remaining}")
        
    else:
        print("✅ Todos los UUIDs ya tienen formato correcto")
    
    conn.close()

if __name__ == "__main__":
    check_and_fix_uuids()
