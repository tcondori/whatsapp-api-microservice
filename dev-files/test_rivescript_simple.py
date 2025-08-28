#!/usr/bin/env python3
"""Test de RiveScript simple para identificar el problema específico"""

from rivescript import RiveScript
import os

# Crear un archivo RiveScript ultra simple
simple_content = """! version = 2.0

> topic random

    + hello
    - Hello there!

    + hola
    - ¡Hola! ¿Cómo estás?

    + *
    - I don't understand that.

< topic
"""

# Escribir archivo de test
test_file = 'static/rivescript/ultra_simple_test.rive'
os.makedirs(os.path.dirname(test_file), exist_ok=True)

with open(test_file, 'w', encoding='utf-8') as f:
    f.write(simple_content)

print(f"✅ Archivo creado: {test_file}")
print(f"📝 Contenido del archivo:")
print(simple_content)
print("=" * 50)

# Probar RiveScript
try:
    rs = RiveScript(debug=True, utf8=True)
    print(f"🔧 RiveScript inicializado (debug=True, utf8=True)")
    
    # Cargar el archivo
    print(f"📁 Cargando archivo: {test_file}")
    rs.stream(simple_content)
    
    print(f"⚙️  Compilando...")
    rs.sort_replies()
    
    print(f"✅ Compilación exitosa!")
    
    # Probar respuestas
    test_messages = ['hello', 'hola', 'test', 'anything']
    
    for msg in test_messages:
        try:
            response = rs.reply('user', msg)
            print(f"✅ '{msg}' -> '{response}'")
        except Exception as e:
            print(f"❌ '{msg}' -> ERROR: {e}")
            
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
