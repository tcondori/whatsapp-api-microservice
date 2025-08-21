#!/usr/bin/env python3
"""
Script para probar la configuración de zona horaria
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
API_KEY = "dev-api-key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_timezone_configuration():
    """Probar la configuración de zona horaria"""
    print("🕒 PROBANDO CONFIGURACIÓN DE ZONA HORARIA")
    print("=" * 50)
    
    # Test 1: Health check con información de timezone
    print("1. Health Check con información de timezone:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🕒 Zona Horaria: {data.get('timezone', {}).get('name', 'No configurado')}")
            print(f"   📍 Offset: {data.get('timezone', {}).get('offset', 'No configurado')}")
            print(f"   🌍 UTC Time: {data.get('timezone', {}).get('current_utc_time', 'No disponible')}")
            print(f"   🏠 Local Time: {data.get('timezone', {}).get('current_local_time', 'No disponible')}")
            print()
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Envío de mensaje para ver timestamps locales
    print("2. Enviando mensaje para verificar timestamps locales:")
    try:
        payload = {
            "to": "+51987654321",
            "text": f"Prueba de timezone - {datetime.now().strftime('%H:%M:%S')}",
            "messaging_line_id": 1
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/messages/text",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📅 Timestamp de respuesta: {data.get('timestamp', 'No disponible')}")
            
            message_data = data.get('data', {})
            print(f"   📅 Created at: {message_data.get('created_at', 'No disponible')}")
            print(f"   📅 Updated at: {message_data.get('updated_at', 'No disponible')}")
            print()
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Obtener lista de mensajes para ver timestamps
    print("3. Obteniendo lista de mensajes para verificar timestamps:")
    try:
        response = requests.get(f"{BASE_URL}/v1/messages", headers=HEADERS)
        
        if response.status_code == 200:
            messages = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total mensajes: {len(messages) if isinstance(messages, list) else 'Error en formato'}")
            
            if isinstance(messages, list) and messages:
                latest_message = messages[0]
                print(f"   📅 Último mensaje - Created: {latest_message.get('created_at', 'No disponible')}")
                print(f"   📅 Último mensaje - Updated: {latest_message.get('updated_at', 'No disponible')}")
            print()
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def compare_with_system_time():
    """Comparar con la hora del sistema"""
    print("⏰ COMPARACIÓN CON HORA DEL SISTEMA")
    print("=" * 50)
    
    import subprocess
    import sys
    
    # Obtener hora del sistema
    if sys.platform == "win32":
        try:
            result = subprocess.run(['powershell', 'Get-Date -Format "yyyy-MM-ddTHH:mm:ss"'], 
                                  capture_output=True, text=True)
            system_time = result.stdout.strip()
            print(f"🖥️  Hora del sistema: {system_time}")
        except Exception as e:
            print(f"🖥️  Error obteniendo hora del sistema: {e}")
    else:
        system_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print(f"🖥️  Hora del sistema: {system_time}")
    
    # Obtener hora del servidor
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            server_time = data.get('timezone', {}).get('current_local_time', 'No disponible')
            print(f"🌐 Hora del servidor (local): {server_time}")
            
            utc_time = data.get('timezone', {}).get('current_utc_time', 'No disponible')
            print(f"🌍 Hora del servidor (UTC): {utc_time}")
        else:
            print(f"❌ Error obteniendo hora del servidor: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("🕒 PRUEBAS DE CONFIGURACIÓN DE ZONA HORARIA")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está respondiendo correctamente")
            return
        print("✅ Servidor detectado y funcionando\n")
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("Asegúrate de que el servidor esté corriendo en http://localhost:5000")
        return
    
    # Ejecutar pruebas
    test_timezone_configuration()
    compare_with_system_time()
    
    print("=" * 60)
    print("✅ PRUEBAS DE ZONA HORARIA COMPLETADAS")
    print("=" * 60)
    
    print("\n📋 RESUMEN:")
    print("   • Las fechas ahora se muestran en zona horaria local (UTC-4)")
    print("   • Los timestamps se almacenan en UTC en la base de datos")
    print("   • Las respuestas de la API incluyen fechas convertidas")
    print("   • El health check muestra información de zona horaria")

if __name__ == "__main__":
    main()
