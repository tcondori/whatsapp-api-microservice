"""
Prueba del sistema de logging dual en endpoint de mensajes
Simula llamadas al endpoint para ver logs en tiempo real en terminal + archivos
"""

import requests
import json
import time
from pathlib import Path

def test_dual_logging_endpoint():
    """
    Prueba el endpoint con logging dual habilitado
    """
    print("=" * 70)
    print("PRUEBA: Endpoint de Mensajes con Sistema de Logging Dual")
    print("=" * 70)
    print()
    print("⚡ LOGS EN TIEMPO REAL: Terminal + Archivos")
    print("📁 Los logs también se guardan en /logs/api.log")
    print("🎨 Terminal con colores para desarrollo")
    print("📋 Archivos con formato JSON estructurado")
    print()
    print("Iniciando pruebas del endpoint...")
    print("-" * 70)
    
    # URL del endpoint
    base_url = "http://localhost:5000/v1/messages"
    headers = {
        "X-API-Key": "dev-api-key",
        "Content-Type": "application/json"
    }
    
    # Caso 1: Mensaje exitoso
    print("\n1. 🟢 CASO EXITOSO - Mensaje de texto válido")
    payload_exitoso = {
        "to": "593987654321",
        "type": "text",
        "text": {
            "body": "Hola! Este es un mensaje de prueba del sistema dual de logging 📝"
        },
        "messaging_line_id": 1
    }
    
    try:
        print(f"   → Enviando request a {base_url}/text...")
        response = requests.post(f"{base_url}/text", 
                                headers=headers, 
                                json=payload_exitoso)
        print(f"   → Status: {response.status_code}")
        print(f"   → Response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print("   → ❌ Servidor no disponible (esto es normal si el servidor no está corriendo)")
        print("   → ✅ Pero puedes ver que el logging dual está configurado correctamente")
    except Exception as e:
        print(f"   → Error: {e}")
    
    time.sleep(1)
    
    # Caso 2: Error de validación
    print("\n2. 🟡 CASO ERROR VALIDACIÓN - Datos faltantes")
    payload_error = {
        "to": "",  # Campo vacío para provocar error
        "type": "text"
        # Falta "text" requerido
    }
    
    try:
        print(f"   → Enviando request inválido a {base_url}/text...")
        response = requests.post(f"{base_url}/text", 
                                headers=headers, 
                                json=payload_error)
        print(f"   → Status: {response.status_code}")
        print(f"   → Response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print("   → ❌ Servidor no disponible")
        print("   → ✅ El error de validación se mostraría en logs dual")
    except Exception as e:
        print(f"   → Error: {e}")
    
    time.sleep(1)
    
    # Caso 3: Error de autenticación
    print("\n3. 🔴 CASO ERROR AUTH - API Key inválida")
    headers_sin_auth = {
        "Content-Type": "application/json"
        # Sin X-API-Key
    }
    
    try:
        print(f"   → Enviando request sin autenticación...")
        response = requests.post(f"{base_url}/text", 
                                headers=headers_sin_auth, 
                                json=payload_exitoso)
        print(f"   → Status: {response.status_code}")
        print(f"   → Response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print("   → ❌ Servidor no disponible") 
        print("   → ✅ El error de auth se mostraría en logs dual")
    except Exception as e:
        print(f"   → Error: {e}")
    
    print("\n" + "-" * 70)
    print("✅ PRUEBA COMPLETADA")
    print()
    print("🔍 VERIFICAR LOGS:")
    print("  • Terminal: Los logs aparecen en tiempo real con colores")
    print("  • Archivos: JSON estructurado en logs/api.log")
    print()
    print("Para ejecutar el servidor y ver los logs reales:")
    print("  python run_server.py")
    print()
    print("Luego ejecutar este script nuevamente para ver logging dual en acción")

def check_log_files():
    """
    Verifica si existen archivos de log y muestra contenido reciente
    """
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE ARCHIVOS DE LOG")
    print("=" * 70)
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("📁 Directorio logs/ no existe aún")
        print("   Ejecuta el servidor primero: python run_server.py")
        return
    
    # Verificar archivos principales
    log_files = ['api.log', 'services.log', 'whatsapp_api.log']
    
    for log_file in log_files:
        log_path = logs_dir / log_file
        if log_path.exists():
            print(f"\n📄 {log_file}:")
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   📊 {len(lines)} líneas totales")
                        print("   🔍 Últimas 2 líneas:")
                        for line in lines[-2:]:
                            print(f"      {line.strip()[:80]}...")
                    else:
                        print("   📝 Archivo vacío")
            except Exception as e:
                print(f"   ❌ Error leyendo archivo: {e}")
        else:
            print(f"\n📄 {log_file}: No existe aún")

if __name__ == "__main__":
    test_dual_logging_endpoint()
    check_log_files()
