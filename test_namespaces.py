"""
Script de prueba para verificar las importaciones de los namespaces
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("🔍 Probando importaciones de namespaces...")

try:
    from app.api.messages.routes import messages_ns
    print(f"✅ messages_ns importado: {messages_ns.name}")
    print(f"   Routes: {len(list(messages_ns.resources))}")
except Exception as e:
    print(f"❌ Error importando messages_ns: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.api.contacts.routes import contacts_ns
    print(f"✅ contacts_ns importado: {contacts_ns.name}")
    print(f"   Routes: {len(list(contacts_ns.resources))}")
except Exception as e:
    print(f"❌ Error importando contacts_ns: {e}")

try:
    from app.api.media.routes import media_ns
    print(f"✅ media_ns importado: {media_ns.name}")
    print(f"   Routes: {len(list(media_ns.resources))}")
except Exception as e:
    print(f"❌ Error importando media_ns: {e}")

try:
    from app.api.webhooks.routes import webhook_ns
    print(f"✅ webhook_ns importado: {webhook_ns.name}")
    print(f"   Routes: {len(list(webhook_ns.resources))}")
except Exception as e:
    print(f"❌ Error importando webhook_ns: {e}")
    import traceback
    traceback.print_exc()

print("\n🔧 Probando creación de API con namespaces...")

try:
    from flask import Flask
    from flask_restx import Api
    
    app = Flask(__name__)
    api = Api(app, title='Test API', version='1.0')
    
    # Registrar namespaces
    from app.api.messages.routes import messages_ns
    from app.api.contacts.routes import contacts_ns
    from app.api.media.routes import media_ns
    from app.api.webhooks.routes import webhook_ns
    
    api.add_namespace(messages_ns, path='/v1/messages')
    api.add_namespace(contacts_ns, path='/v1/contacts')
    api.add_namespace(media_ns, path='/v1/media')
    api.add_namespace(webhook_ns, path='/v1/webhooks')
    
    print(f"✅ API creada con {len(list(app.url_map.iter_rules()))} rutas")
    
    # Mostrar todas las rutas
    print("\n📋 Rutas registradas:")
    for rule in app.url_map.iter_rules():
        methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"  • {methods:12} {rule.rule}")
    
except Exception as e:
    print(f"❌ Error creando API: {e}")
    import traceback
    traceback.print_exc()
