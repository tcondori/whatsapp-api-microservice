#!/usr/bin/env python3
"""
Test directo de la API para verificar el endpoint
"""
import requests
import json

def test_api():
    """Probar el API directamente"""
    base_url = "http://localhost:5001"
    flow_id = "32561960-1902-495f-af1f-c6157c2d12b0"
    
    print(f"🌐 Probando API: {base_url}")
    print(f"🔍 Flow ID: {flow_id}")
    
    # Probar GET
    print("\n1️⃣ GET /rivescript/flows/{flow_id}")
    try:
        url = f"{base_url}/rivescript/flows/{flow_id}"
        print(f"   URL: {url}")
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar PUT  
    print("\n2️⃣ PUT /rivescript/flows/{flow_id}")
    try:
        url = f"{base_url}/rivescript/flows/{flow_id}"
        data = {"is_active": False}
        print(f"   URL: {url}")
        print(f"   Data: {data}")
        response = requests.put(url, json=data, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api()
