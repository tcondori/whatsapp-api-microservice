#!/usr/bin/env python3
"""
Script para actualizar flujos RiveScript en la base de datos
Reemplaza el contenido corrupto con archivos válidos
"""

import os
import sys
import sqlite3
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def update_rivescript_flows():
    """Actualizar flujos RiveScript en la base de datos"""
    
    # Archivos RiveScript corregidos
    files_to_update = {
        'Flujo Básico WhatsApp': 'static/rivescript/fixed_basic_flow.rive',
        'Flujo de Ventas WhatsApp': 'static/rivescript/fixed_sales_flow.rive'
    }
    
    # Conectar a la base de datos
    db_path = 'instance/whatsapp_test.db'
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Actualizando flujos RiveScript...")
        
        for flow_name, file_path in files_to_update.items():
            if not os.path.exists(file_path):
                print(f"⚠️  Archivo no encontrado: {file_path}")
                continue
            
            # Leer contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                rivescript_content = f.read()
            
            # Actualizar en la base de datos
            cursor.execute('''
                UPDATE conversation_flows 
                SET rivescript_content = ?, updated_at = datetime('now') 
                WHERE name = ?
            ''', (rivescript_content, flow_name))
            
            if cursor.rowcount > 0:
                print(f"✅ Flujo '{flow_name}' actualizado correctamente")
            else:
                print(f"⚠️  Flujo '{flow_name}' no encontrado en DB")
        
        # Confirmar cambios
        conn.commit()
        print("\n📊 Verificando flujos actualizados:")
        
        cursor.execute('SELECT name, LENGTH(rivescript_content), is_active FROM conversation_flows')
        for name, content_length, is_active in cursor.fetchall():
            status = "✅ Activo" if is_active else "❌ Inactivo"
            print(f"  • {name}: {content_length} chars, {status}")
        
        conn.close()
        print("\n✅ Flujos RiveScript actualizados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando flujos: {e}")
        return False

if __name__ == '__main__':
    print("🚀 ACTUALIZADOR DE FLUJOS RIVESCRIPT")
    print("=" * 50)
    
    success = update_rivescript_flows()
    
    if success:
        print("\n🎉 ¡Actualización completada!")
        print("💡 Ejecuta test_rivescript_debug.py para verificar")
    else:
        print("\n❌ Actualización falló")
        sys.exit(1)
