"""
Corrector rápido de api.abort a messages_ns.abort
"""
import re

def fix_routes_file():
    file_path = 'E:/DSW/proyectos/proy04/app/api/messages/routes.py'
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar todas las ocurrencias de api.abort con messages_ns.abort
    content = content.replace('api.abort', 'messages_ns.abort')
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo corregido: api.abort -> messages_ns.abort")

if __name__ == "__main__":
    fix_routes_file()
