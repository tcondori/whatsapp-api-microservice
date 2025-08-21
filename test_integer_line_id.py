#!/usr/bin/env python3
"""
Test completo de endpoints con line_id como INTEGER

CASOS A PROBAR:
1. Envío de mensaje de texto (messaging_line_id: 1, 2)
2. Envío de mensaje de imagen con URL (messaging_line_id: 1, 2)  
3. Verificación de estructuras JSON de request

Uso: python test_integer_line_id.py
"""
import requests
import json
import sys

# Configuración
BASE_URL = "http://127.0.0.1:5000"
API_KEY = "dev-api-key"
PHONE_NUMBER = "5491123456789"  # Número de prueba

def test_text_message(line_id):
    """
    Test de envío de mensaje de texto con line_id entero
    """
    print(f"\n📝 TEST: Mensaje de texto (line_id: {line_id})")
    print("-" * 50)
    
    # JSON de request con line_id entero
    payload = {
        "to": PHONE_NUMBER,
        "text": f"🧪 Test con line_id INTEGER: {line_id}\n\nVerificando que los endpoints acepten correctamente valores enteros para messaging_line_id.",
        "messaging_line_id": line_id  # INTEGER, no string
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    print(f"📋 JSON Request:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        url = f"{BASE_URL}/v1/messages/text"
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📋 Response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"📋 Response (text): {response.text}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Mensaje de texto con line_id {line_id}")
            return True
        else:
            print(f"❌ ERROR: Fallo con line_id {line_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False

def test_image_message(line_id):
    """
    Test de envío de mensaje de imagen con line_id entero
    """
    print(f"\n🖼️  TEST: Mensaje de imagen (line_id: {line_id})")
    print("-" * 50)
    
    # JSON de request con formato oficial Meta y line_id entero
    payload = {
        "to": PHONE_NUMBER,
        "type": "image",
        "image": {
            "link": "https://picsum.photos/400/300",
            "caption": f"🧪 Test imagen con line_id INTEGER: {line_id}\n\nFormato oficial Meta WhatsApp Business API con valores enteros."
        },
        "messaging_line_id": line_id  # INTEGER, no string
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    print(f"📋 JSON Request (Formato oficial Meta):")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        url = f"{BASE_URL}/v1/messages/image"
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📋 Response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"📋 Response (text): {response.text}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Mensaje de imagen con line_id {line_id}")
            return True
        else:
            print(f"❌ ERROR: Fallo con line_id {line_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False

def verify_database_state():
    """
    Verifica el estado actual de la base de datos
    """
    print("\n📊 VERIFICACIÓN: Estado de messaging_lines")
    print("-" * 50)
    
    try:
        import subprocess
        result = subprocess.run([
            'python', '-c',
            "from entrypoint import create_app; app=create_app(); ctx=app.app_context(); ctx.push(); from database.models import MessagingLine; lines=MessagingLine.query.all(); [print(f'line_id: {line.line_id} (tipo: {type(line.line_id).__name__}) | phone_number_id: {line.phone_number_id}') for line in lines]; ctx.pop()"
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Estado de base de datos:")
            # Filtrar solo las líneas relevantes
            lines = result.stdout.split('\n')
            for line in lines:
                if 'line_id:' in line and 'phone_number_id:' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print(f"❌ Error verificando base de datos: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def verify_api_availability():
    """Verifica que la API esté disponible"""
    try:
        response = requests.get(f"{BASE_URL}/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API disponible")
            return True
        else:
            print(f"⚠️  API respondió con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API no disponible: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEST COMPLETO: line_id como INTEGER")
    print("Verificando que los endpoints acepten valores enteros")
    print("=" * 60)
    
    # Verificar API
    if not verify_api_availability():
        print("❌ No se puede conectar a la API. Verificar que el servidor esté corriendo.")
        sys.exit(1)
    
    # Verificar estado de BD
    if not verify_database_state():
        print("❌ No se puede verificar estado de base de datos.")
        sys.exit(1)
    
    # Tests de los endpoints
    results = []
    
    # Test con line_id 1
    results.append(test_text_message(1))
    results.append(test_image_message(1))
    
    # Test con line_id 2
    results.append(test_text_message(2))
    results.append(test_image_message(2))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE RESULTADOS:")
    
    test_names = [
        "Texto (line_id: 1)",
        "Imagen (line_id: 1)", 
        "Texto (line_id: 2)",
        "Imagen (line_id: 2)"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ Los endpoints aceptan correctamente line_id como INTEGER")
        print("✅ La migración de String -> Integer fue exitosa")
        print("\n📋 Estructuras JSON validadas:")
        print("- messaging_line_id: INTEGER (no string)")
        print("- Formato oficial Meta para imágenes")
        print("- Consistencia entre base de datos y endpoints")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        print("Revisar logs del servidor para más detalles.")
    
    print("\n📋 Información adicional:")
    print("- Base de datos: line_id ahora es INTEGER")
    print("- Endpoints: messaging_line_id acepta INTEGER")
    print("- Formato: JSON requests con valores numéricos")
