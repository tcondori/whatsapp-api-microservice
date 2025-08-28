#!/usr/bin/env python3
"""Test directo del contenido de RiveScript desde base de datos"""

from rivescript import RiveScript
import sqlite3
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_content():
    """Probar contenido de base de datos directamente"""
    
    # Conectar a la base de datos
    db_path = 'instance/whatsapp_test.db'
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener flujos activos
        cursor.execute('''
            SELECT name, rivescript_content 
            FROM conversation_flows 
            WHERE is_active = 1 
            ORDER BY priority ASC
        ''')
        
        flows = cursor.fetchall()
        print(f"📊 Encontrados {len(flows)} flujos activos")
        
        for flow_name, content in flows:
            print(f"\n{'='*60}")
            print(f"🔄 Probando flujo: {flow_name}")
            print(f"📝 Longitud del contenido: {len(content)} caracteres")
            print(f"🔍 Primeros 200 caracteres:")
            print(repr(content[:200]))
            print(f"🔍 Últimos 100 caracteres:")
            print(repr(content[-100:]))
            
            # Probar con RiveScript
            try:
                rs = RiveScript(debug=True, utf8=True)
                print(f"⚙️  Cargando contenido con stream()...")
                
                rs.stream(content)
                print(f"✅ stream() exitoso")
                
                rs.sort_replies()
                print(f"✅ sort_replies() exitoso")
                
                # Probar respuestas
                test_messages = ['hola', 'hello', 'precio']
                for msg in test_messages:
                    try:
                        response = rs.reply('test_user', msg)
                        print(f"✅ '{msg}' -> '{response}'")
                    except Exception as e:
                        print(f"❌ '{msg}' -> ERROR: {e}")
                
            except Exception as e:
                print(f"❌ Error procesando flujo '{flow_name}': {e}")
                import traceback
                traceback.print_exc()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def test_combined_flows():
    """Probar combinación de múltiples flujos"""
    print(f"\n{'='*60}")
    print(f"🔄 PROBANDO FLUJOS COMBINADOS")
    
    try:
        conn = sqlite3.connect('instance/whatsapp_test.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, rivescript_content 
            FROM conversation_flows 
            WHERE is_active = 1 
            ORDER BY priority ASC
        ''')
        
        flows = cursor.fetchall()
        
        # Combinar todos los flujos en un solo RiveScript
        rs = RiveScript(debug=True, utf8=True)
        
        for flow_name, content in flows:
            print(f"📁 Agregando flujo: {flow_name}")
            rs.stream(content)
        
        print(f"⚙️  Compilando flujos combinados...")
        rs.sort_replies()
        print(f"✅ Compilación exitosa")
        
        # Probar respuestas combinadas
        test_messages = ['hola', 'hello', 'precio', 'venta', 'ayuda', '1', '2', '3']
        print(f"\n🔍 PROBANDO RESPUESTAS:")
        
        for msg in test_messages:
            try:
                response = rs.reply('combined_test_user', msg)
                print(f"✅ '{msg}' -> '{response}'")
            except Exception as e:
                print(f"❌ '{msg}' -> ERROR: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error en test combinado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🧪 TEST DIRECTO DE CONTENIDO RIVESCRIPT DESDE BASE DE DATOS")
    print("=" * 70)
    
    test_database_content()
    test_combined_flows()
    
    print("\n🎯 Test completado")
