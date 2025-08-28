"""
Script simple para ejecutar el servidor de forma manual
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("🚀 Iniciando servidor manual...")

try:
    from entrypoint import create_app
    
    app = create_app()
    print("✅ Aplicación creada")
    
    print(f"📊 Rutas disponibles: {len(list(app.url_map.iter_rules()))}")
    
    # Mostrar algunas rutas importantes
    important_routes = [rule for rule in app.url_map.iter_rules() 
                       if any(keyword in rule.rule for keyword in ['/health', '/webhook', '/messages'])]
    
    print("\n📋 Rutas importantes:")
    for rule in important_routes:
        methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"  • {methods:12} {rule.rule}")
    
    print("\n🌐 Iniciando servidor en puerto 5000...")
    print("   Presiona Ctrl+C para detener")
    print("=" * 50)
    
    # Verificar que el puerto esté disponible
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        if result == 0:
            print("⚠️  Puerto 5000 ya está en uso")
            sock.close()
            exit(1)
        sock.close()
    except:
        pass
    
    print("🚀 Iniciando Flask...")
    # Usar el servidor de desarrollo de Flask con configuración explícita
    app.run(
        host='127.0.0.1',  # Solo localhost
        port=5000,
        debug=True,        # Activar debug para ver errores
        use_reloader=False # Sin reloader
    )
    
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
