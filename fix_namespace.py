import re

# Leer el archivo
with open('app/api/messages/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar @api. con @messages_ns.
content = content.replace('@api.', '@messages_ns.')

# Escribir el archivo
with open('app/api/messages/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Referencias de @api. actualizadas a @messages_ns.")
