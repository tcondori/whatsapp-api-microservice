"""
Script simple para probar la conectividad del servidor
"""
import requests
import time

def test_simple_connection():
    """Prueba conexión básica al servidor"""
    print("🔗 Probando conexión básica...")
    
    # Esperar un poco para que el servidor termine de inicializar
    time.sleep(2)
    
    try:
        # Probar endpoint básico de health
        response = requests.get("http://localhost:5000/health", headers={"X-API-Key": "dev-api-key"})
        print(f"Health check - Status: {response.status_code}")
        print(f"Health check - Response: {response.text}")
    except Exception as e:
        print(f"Error en health check: {e}")
    
    try:
        # Probar endpoint de mensajes
        response = requests.get("http://localhost:5000/api/v1/messages/test", headers={"X-API-Key": "dev-api-key"})
        print(f"Messages test - Status: {response.status_code}")
        print(f"Messages test - Response: {response.text}")
    except Exception as e:
        print(f"Error en messages test: {e}")

if __name__ == "__main__":
    test_simple_connection()
