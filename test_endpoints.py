"""
Script de prueba unitaria para verificar la aplicación
"""
from entrypoint import app
import json

def test_app():
    """Prueba la aplicación Flask localmente"""
    
    with app.test_client() as client:
        print("🧪 Probando health check...")
        
        # Probar health check
        response = client.get('/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        print("\n🧪 Probando documentación Swagger...")
        
        # Probar documentación
        response = client.get('/docs/')
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        
        print("\n🧪 Probando health checks de módulos...")
        
        # Probar health checks de módulos
        modules = ['messages', 'contacts', 'media', 'webhooks']
        
        for module in modules:
            response = client.get(f'/api/v1/{module}/health')
            print(f"{module}: Status {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {response.get_json()}")

if __name__ == '__main__':
    test_app()
