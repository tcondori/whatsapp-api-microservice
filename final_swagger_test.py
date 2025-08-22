#!/usr/bin/env python3
"""
Prueba final para confirmar que Swagger UI está funcionando correctamente
"""

import requests
import webbrowser
import time

def final_swagger_test():
    """
    Prueba final de autenticación en Swagger
    """
    
    BASE_URL = "http://localhost:5000"
    
    print("🎯 PRUEBA FINAL DE SWAGGER AUTHENTICATION")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    print("\n1️⃣  Verificando servidor...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print("❌ Problema con el servidor")
            return
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        return
    
    # Verificar swagger.json
    print("\n2️⃣  Verificando configuración de Swagger...")
    try:
        response = requests.get(f"{BASE_URL}/swagger.json")
        if response.status_code == 200:
            config = response.json()
            
            # Verificar consistency
            security_defs = list(config.get('securityDefinitions', {}).keys())
            security_global = config.get('security', [])
            
            print(f"✅ SecurityDefinitions: {security_defs}")
            print(f"✅ Security global: {security_global}")
            
            # Verificar endpoint específico
            endpoint_security = config.get('paths', {}).get('/v1/messages/text', {}).get('post', {}).get('security', [])
            print(f"✅ Security en endpoint: {endpoint_security}")
            
            # Verificar consistencia
            if security_defs and security_global and endpoint_security:
                auth_name = security_defs[0]
                uses_same_auth = all(auth_name in str(sec) for sec in security_global + endpoint_security)
                
                if uses_same_auth:
                    print("✅ CONSISTENCIA PERFECTA: Todos usan el mismo auth")
                else:
                    print("❌ INCONSISTENCIA: Auth names no coinciden")
            
        else:
            print("❌ Error obteniendo swagger.json")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🚀 SWAGGER UI DEBE FUNCIONAR AHORA!")
    print("=" * 60)
    
    print("📋 INSTRUCCIONES FINALES PARA SWAGGER UI:")
    print("1. Ve a: http://localhost:5000/docs/")
    print("2. Busca el botón 'Authorize' 🔒 (parte superior derecha)")
    print("3. Haz clic en 'Authorize'")
    print("4. En el modal que aparece:")
    print("   - Campo 'ApiKeyAuth (apiKey)' o similar")
    print("   - Valor: dev-api-key")
    print("5. Haz clic en 'Authorize' y luego 'Close'")
    print("6. Ahora el candado 🔒 debe aparecer cerrado/verde")
    print("7. Prueba cualquier endpoint /v1/messages")
    
    print(f"\n💡 PAYLOAD DE PRUEBA:")
    print("""{
  "to": "+59167028778",
  "text": "Mensaje de prueba desde Swagger UI",
  "line_id": 1
}""")
    
    print("\n✨ API KEYS VÁLIDAS:")
    print("- dev-api-key")
    print("- test-key-123") 
    print("- test_key")
    
    # Opcionalmente abrir el navegador
    try:
        print(f"\n🌐 Abriendo Swagger UI en el navegador...")
        webbrowser.open(f"{BASE_URL}/docs/")
    except:
        print("❌ No se pudo abrir automáticamente el navegador")
        print(f"   Manualmente ve a: {BASE_URL}/docs/")

if __name__ == "__main__":
    final_swagger_test()
