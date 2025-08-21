"""
DEBUG PAYLOAD - Interceptar y mostrar exactamente qué se envía a WhatsApp API
============================================================================
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock de requests para interceptar las llamadas
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = {'content-type': 'application/json'}
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"{self.status_code} Client Error")

def mock_requests_post(url, json=None, headers=None, timeout=None, **kwargs):
    """Mock para interceptar requests.post"""
    print(f"🔍 INTERCEPTADA LLAMADA A WHATSAPP API")
    print(f"   • URL: {url}")
    print(f"   • Headers: {headers}")
    print(f"   • Payload JSON:")
    import json as json_module
    print(json_module.dumps(json, indent=4, ensure_ascii=False))
    print(f"   • Timeout: {timeout}")
    print()
    
    # Simular error 400 para debug
    return MockResponse(400, {
        "error": {
            "message": "DEBUG: Payload interceptado correctamente",
            "type": "OAuthException", 
            "code": 400
        }
    })

def test_image_payload_debug():
    """
    Probar envío de imagen con debug del payload
    """
    print("🚀 DEBUG PAYLOAD DE IMAGEN")
    print("=" * 50)
    
    # Patchear requests antes de importar
    import requests
    original_post = requests.post
    requests.post = mock_requests_post
    
    try:
        from entrypoint import create_app
        app = create_app()
        
        with app.app_context():
            from app.api.messages.services import MessageService
            
            service = MessageService()
            
            # Datos de prueba con formato oficial Meta
            message_data = {
                "to": "59167028778",
                "type": "image",
                "image": {
                    "link": "https://picsum.photos/400/300?random=1",
                    "caption": "Debug payload test"
                },
                "messaging_line_id": 1
            }
            
            print("📤 INPUT DATA:")
            import json
            print(json.dumps(message_data, indent=2, ensure_ascii=False))
            
            print(f"\n🔄 EJECUTANDO send_image_message()...")
            
            try:
                result = service.send_image_message(message_data)
                print(f"✅ RESULTADO: {result}")
            except Exception as e:
                print(f"❌ ERROR ESPERADO: {e}")
                print(f"   (Esto es normal, estamos debuggeando)")
    
    finally:
        # Restaurar requests original
        requests.post = original_post

def test_text_payload_for_comparison():
    """
    Probar envío de texto para comparar payload
    """
    print(f"\n🔄 COMPARACIÓN CON PAYLOAD DE TEXTO")
    print("=" * 50)
    
    # Patchear requests antes de importar
    import requests
    original_post = requests.post
    requests.post = mock_requests_post
    
    try:
        from entrypoint import create_app
        app = create_app()
        
        with app.app_context():
            from app.api.messages.services import MessageService
            
            service = MessageService()
            
            # Datos de prueba para texto
            message_data = {
                "to": "59167028778",
                "text": "Debug payload test texto",
                "line_id": "1"
            }
            
            print("📤 INPUT DATA (TEXTO):")
            import json
            print(json.dumps(message_data, indent=2, ensure_ascii=False))
            
            print(f"\n🔄 EJECUTANDO send_text_message()...")
            
            try:
                result = service.send_text_message(message_data)
                print(f"✅ RESULTADO: {result}")
            except Exception as e:
                print(f"❌ ERROR ESPERADO: {e}")
                print(f"   (Esto es normal, estamos debuggeando)")
    
    finally:
        # Restaurar requests original
        requests.post = original_post

if __name__ == "__main__":
    print("🕐 DEBUG COMPLETO DE PAYLOADS")
    print("=" * 60)
    
    # Debug payload de imagen (que falla)
    test_image_payload_debug()
    
    # Debug payload de texto (que funciona) para comparar
    test_text_payload_for_comparison()
    
    print("=" * 60)
    print("🎯 OBJETIVO: Comparar ambos payloads para identificar la diferencia")
    print("   que causa el error 400 en imagen pero no en texto")
    print("=" * 60)
