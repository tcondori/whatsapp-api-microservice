#!/usr/bin/env python3
"""
Script para diagnosticar errores de Swagger
Identifica problemas en la configuración de Flask-RESTX
"""
import traceback
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_swagger():
    """Función para probar la configuración de Swagger"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE SWAGGER")
    print("=" * 60)
    
    try:
        print("\n1️⃣ Importando entrypoint...")
        from entrypoint import create_app
        print("✅ Importación exitosa")
        
        print("\n2️⃣ Creando aplicación...")
        app = create_app()
        print("✅ Aplicación creada exitosamente")
        
        print("\n3️⃣ Probando acceso a Swagger JSON...")
        with app.test_client() as client:
            response = client.get('/swagger.json')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Swagger JSON generado correctamente")
            else:
                print(f"❌ Error en Swagger JSON: {response.data.decode()}")
        
        print("\n4️⃣ Probando acceso a documentación Swagger UI...")
        with app.test_client() as client:
            response = client.get('/docs/')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Swagger UI funcionando correctamente")
            else:
                print(f"❌ Error en Swagger UI: {response.data.decode()}")
        
        print("\n5️⃣ Verificando rutas registradas...")
        for rule in app.url_map.iter_rules():
            if '/docs' in rule.rule or '/swagger' in rule.rule:
                print(f"  📄 {rule.rule} -> {rule.endpoint}")
        
        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
        print("🌐 Swagger disponible en: http://localhost:5000/docs/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR ENCONTRADO: {str(e)}")
        print("\n📋 TRACEBACK COMPLETO:")
        traceback.print_exc()
        
        print(f"\n💡 SUGERENCIAS DE SOLUCIÓN:")
        error_str = str(e).lower()
        if "dict" in error_str and "callable" in error_str:
            print("  • El error 'dict object is not callable' indica problema en modelos Flask-RESTX")
            print("  • Revisar definiciones de api.model() en routes.py")
            print("  • Verificar que no se estén llamando diccionarios como funciones")
        elif "import" in error_str:
            print("  • Error de importación - verificar dependencias")
            print("  • Ejecutar: pip install flask-restx")
        elif "circular" in error_str:
            print("  • Importación circular detectada")
            print("  • Revisar imports en models.py y routes.py")

if __name__ == '__main__':
    test_swagger()
