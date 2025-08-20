#!/usr/bin/env python3
"""
Script para corregir todos los endpoints que devuelven tuplas con códigos de estado
Cambia return create_error_response(...), status_code por api.abort(status_code, ...)
"""
import re

def fix_error_responses():
    """Corrige todos los endpoints que devuelven tuplas de error"""
    file_path = "e:/DSW/proyectos/proy04/app/api/messages/routes.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar return create_error_response(...), status_code
    pattern = r'return create_error_response\(\s*message="([^"]*)",\s*error_code="([^"]*)"(?:,\s*details=([^)]*))?\s*\),\s*(\d+)'
    
    def replace_func(match):
        message = match.group(1)
        error_code = match.group(2)
        details = match.group(3)
        status_code = match.group(4)
        
        if details:
            return f'api.abort({status_code},\n                message="{message}",\n                error_code="{error_code}",\n                details={details}\n            )'
        else:
            return f'api.abort({status_code},\n                message="{message}",\n                error_code="{error_code}"\n            )'
    
    # Aplicar reemplazos
    new_content = re.sub(pattern, replace_func, content)
    
    # Patrón para casos con str(e)
    pattern2 = r'return create_error_response\(\s*message=str\(e\),\s*error_code="([^"]*)"(?:,\s*details=([^)]*))?\s*\),\s*(\d+)'
    
    def replace_func2(match):
        error_code = match.group(1)
        details = match.group(2)
        status_code = match.group(3)
        
        if details:
            return f'api.abort({status_code},\n                message=str(e),\n                error_code="{error_code}",\n                details={details}\n            )'
        else:
            return f'api.abort({status_code},\n                message=str(e),\n                error_code="{error_code}"\n            )'
    
    new_content = re.sub(pattern2, replace_func2, new_content)
    
    # Patrón para casos más complejos
    pattern3 = r'return create_error_response\(\s*([^)]+)\),\s*(\d+)'
    
    def replace_func3(match):
        params = match.group(1)
        status_code = match.group(2)
        return f'api.abort({status_code}, {params})'
    
    new_content = re.sub(pattern3, replace_func3, new_content)
    
    # También arreglar returns de éxito que devuelven tuplas
    success_pattern = r'return ([^,\n]+),\s*(\d+)'
    
    def replace_success(match):
        result = match.group(1)
        status_code = match.group(2)
        if status_code == '200':
            return f'return {result}'
        else:
            return match.group(0)  # No cambiar si no es 200
    
    new_content = re.sub(success_pattern, replace_success, new_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Correcciones aplicadas exitosamente")

if __name__ == "__main__":
    fix_error_responses()
