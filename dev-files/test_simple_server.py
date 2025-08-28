#!/usr/bin/env python3
"""
Test simple del servidor para diagnosticar problemas
"""
import requests
import time
import sys

def test_server():
    """Prueba simple de conectividad del servidor"""
    base_url = "http://localhost:5001"
    
    print("🔍 DIAGNÓSTICO DEL SERVIDOR")
    print("=" * 50)
    
    # Intentar múltiples URLs
    test_urls = [
        "/health",
        "/",
        "/docs",
        "/chat",
        "/rivescript/flows"
    ]
    
    for url in test_urls:
        full_url = f"{base_url}{url}"
        try:
            print(f"🧪 Probando: {full_url}")
            response = requests.get(full_url, timeout=5)
            print(f"   ✅ Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📄 Respuesta JSON válida")
                except:
                    print(f"   📄 Respuesta HTML/texto")
            else:
                print(f"   ⚠️  Contenido: {response.text[:100]}...")
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Error de conexión: {e}")
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout")
        except Exception as e:
            print(f"   💥 Error inesperado: {e}")
        
        time.sleep(0.5)
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_server()
