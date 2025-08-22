#!/usr/bin/env python3
"""
Script para actualizar todos los decoradores de security de 'apiKey' a 'ApiKeyAuth'
"""

import os
import re

def update_security_decorators():
    """
    Actualiza todos los decoradores @doc(security='apiKey') a @doc(security='ApiKeyAuth')
    """
    
    files_to_update = [
        "app/api/messages/routes.py",
        "app/api/contacts/routes.py"  # Si existe
    ]
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"⚠️  Archivo no encontrado: {file_path}")
            continue
        
        print(f"🔧 Actualizando: {file_path}")
        
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar todos los casos
        original_count = content.count("@messages_ns.doc(security='apiKey')")
        new_content = content.replace(
            "@messages_ns.doc(security='apiKey')",
            "@messages_ns.doc(security='ApiKeyAuth')"
        )
        
        # También buscar variantes
        new_content = new_content.replace(
            "@contacts_ns.doc(security='apiKey')",
            "@contacts_ns.doc(security='ApiKeyAuth')"
        )
        
        final_count = new_content.count("@messages_ns.doc(security='ApiKeyAuth')")
        
        # Escribir archivo si hubo cambios
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Actualizado: {original_count} decoradores cambiados a 'ApiKeyAuth'")
        else:
            print(f"ℹ️  Sin cambios necesarios en: {file_path}")

if __name__ == "__main__":
    print("🔄 ACTUALIZANDO DECORADORES DE SECURITY")
    print("=" * 50)
    
    update_security_decorators()
    
    print("\n✅ ACTUALIZACIÓN COMPLETADA!")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Reinicia el servidor: Ctrl+C y luego python entrypoint.py")
    print("2. Ve a http://localhost:5000/docs/")
    print("3. Verifica que aparezca el botón 'Authorize' 🔒")
    print("4. Haz clic en 'Authorize' e ingresa: dev-api-key")
    print("5. Prueba cualquier endpoint de /v1/messages")
    
    print("\n🎯 CAMBIOS REALIZADOS:")
    print("- entrypoint.py: authorization 'apiKey' → 'ApiKeyAuth'") 
    print("- routes.py: @doc(security='apiKey') → @doc(security='ApiKeyAuth')")
    print("- Ahora ambos usan el mismo nombre: 'ApiKeyAuth'")
