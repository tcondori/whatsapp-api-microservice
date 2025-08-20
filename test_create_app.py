"""
Script de prueba completo para create_app
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("🚀 Probando create_app completa...")

try:
    from entrypoint import create_app
    
    print("✅ create_app importada correctamente")
    
    app = create_app()
    
    print("✅ Aplicación creada exitosamente")
    print(f"📊 Total de rutas: {len(list(app.url_map.iter_rules()))}")
    
    # Mostrar rutas de webhook
    webhook_routes = [rule for rule in app.url_map.iter_rules() if 'webhook' in rule.rule]
    print(f"\n📋 Rutas de webhooks ({len(webhook_routes)}):")
    for rule in webhook_routes:
        methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"  • {methods:12} {rule.rule}")
    
    # Probar inicialización del servidor
    print("\n🌐 Probando inicio del servidor...")
    
    # Simular inicialización sin usar run()
    with app.app_context():
        print("✅ Contexto de aplicación inicializado")
    
    print("✅ Aplicación lista para ejecutar!")
    
except Exception as e:
    print(f"❌ Error en create_app: {e}")
    import traceback
    traceback.print_exc()
