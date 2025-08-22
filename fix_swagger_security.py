#!/usr/bin/env python3
"""
Script para agregar documentación de seguridad a todos los endpoints protegidos
con @require_api_key en la aplicación WhatsApp API
"""

import os
import re

def fix_swagger_security():
    """
    Agrega @messages_ns.doc(security='apiKey') antes de @require_api_key
    en todos los archivos de rutas
    """
    
    # Archivos a procesar
    files_to_process = [
        "app/api/messages/routes.py",
        "app/api/contacts/routes.py",
        # Agregar más archivos según necesidad
    ]
    
    for file_path in files_to_process:
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            continue
            
        print(f"🔧 Procesando: {file_path}")
        
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patron para encontrar @require_api_key sin @doc(security='apiKey') antes
        pattern = r"(\n\s*@[a-z_]+\.response\([^)]+\)[^\n]*\n(?:\s*@[a-z_]+\.response\([^)]+\)[^\n]*\n)*)\s*(@require_api_key)"
        
        # Función de reemplazo
        def replace_func(match):
            responses = match.group(1)
            require_decorator = match.group(2)
            
            # Verificar si ya tiene @doc(security='apiKey')
            if "@doc(security='apiKey')" in responses:
                return match.group(0)  # No cambiar si ya está
            
            # Agregar @doc(security='apiKey') antes de @require_api_key
            return f"{responses}    @messages_ns.doc(security='apiKey')\n    {require_decorator}"
        
        # Aplicar reemplazo
        new_content = re.sub(pattern, replace_func, content)
        
        # Si el contenido cambió, escribir el archivo
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Actualizado: {file_path}")
        else:
            print(f"ℹ️  Sin cambios necesarios: {file_path}")

def fix_contacts_routes():
    """
    Agrega documentación de seguridad a contacts/routes.py específicamente
    """
    file_path = "app/api/contacts/routes.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return
    
    print(f"🔧 Procesando contacts routes: {file_path}")
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos específicos para contacts
    replacements = [
        # Para endpoints de contacts que necesitan autenticación
        (
            r"(\s*@contacts_ns\.response\([^)]+\)[^\n]*\n(?:\s*@contacts_ns\.response\([^)]+\)[^\n]*\n)*)\s*(@require_api_key)",
            r"\1    @contacts_ns.doc(security='apiKey')\n    \2"
        )
    ]
    
    changed = False
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            changed = True
    
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Actualizado contacts: {file_path}")
    else:
        print(f"ℹ️  Sin cambios necesarios en contacts: {file_path}")

if __name__ == "__main__":
    print("🛠️  Iniciando corrección de documentación de seguridad en Swagger...")
    
    # Cambiar al directorio del proyecto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Ejecutar correcciones
    fix_swagger_security()
    fix_contacts_routes()
    
    print("\n✅ Corrección completada!")
    print("\n📋 Pasos siguientes:")
    print("1. Reinicia el servidor: python entrypoint.py")
    print("2. Ve a http://localhost:5000/docs/")
    print("3. Haz clic en 'Authorize' en la parte superior derecha")
    print("4. Ingresa la API key: dev-api-key")
    print("5. Haz clic en 'Authorize'")
    print("6. Ahora podrás usar todos los endpoints /v1/messages")
