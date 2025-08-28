#!/usr/bin/env python3
"""
Script para verificar todos los endpoints disponibles en la aplicación
"""
import sys
sys.path.insert(0, '.')

try:
    # Importar la aplicación
    from entrypoint import create_app
    
    app = create_app()
    
    print("🔍 Verificando endpoints registrados:")
    print("=" * 50)
    
    # Obtener todas las rutas registradas
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"{methods:10} {rule.rule}")
    
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error al verificar endpoints: {e}")
    import traceback
    traceback.print_exc()
