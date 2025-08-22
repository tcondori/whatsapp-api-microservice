#!/usr/bin/env python3
"""
Test de importación de modelos para diagnosticar problemas específicos
"""

def test_model_imports():
    """
    Prueba importar cada modelo por separado para identificar problemas
    """
    print("🔍 Probando importaciones de modelos...")
    
    try:
        from app.api.messages.models import TEXT_MESSAGE_FIELDS
        print("✅ TEXT_MESSAGE_FIELDS")
    except Exception as e:
        print(f"❌ TEXT_MESSAGE_FIELDS: {e}")
    
    try:
        from app.api.messages.models import VIDEO_UPLOAD_MESSAGE_FIELDS
        print("✅ VIDEO_UPLOAD_MESSAGE_FIELDS")
    except Exception as e:
        print(f"❌ VIDEO_UPLOAD_MESSAGE_FIELDS: {e}")
    
    try:
        from app.api.messages.models import AUDIO_UPLOAD_MESSAGE_FIELDS
        print("✅ AUDIO_UPLOAD_MESSAGE_FIELDS")
    except Exception as e:
        print(f"❌ AUDIO_UPLOAD_MESSAGE_FIELDS: {e}")
    
    try:
        from app.api.messages.models import DOCUMENT_UPLOAD_MESSAGE_FIELDS
        print("✅ DOCUMENT_UPLOAD_MESSAGE_FIELDS")
    except Exception as e:
        print(f"❌ DOCUMENT_UPLOAD_MESSAGE_FIELDS: {e}")
    
    try:
        from app.api.messages.models import STICKER_UPLOAD_MESSAGE_FIELDS
        print("✅ STICKER_UPLOAD_MESSAGE_FIELDS")
    except Exception as e:
        print(f"❌ STICKER_UPLOAD_MESSAGE_FIELDS: {e}")
    
    try:
        from app.api.messages.models import MULTIMEDIA_RESPONSE_FIELDS
        print("✅ MULTIMEDIA_RESPONSE_FIELDS")
    except Exception as e:
        print(f"❌ MULTIMEDIA_RESPONSE_FIELDS: {e}")

def test_flask_restx_model_creation():
    """
    Prueba crear modelos Flask-RESTX para encontrar el error específico
    """
    print("\n🔍 Probando creación de modelos Flask-RESTX...")
    
    try:
        from flask_restx import Namespace, fields
        from app.api.messages.models import VIDEO_UPLOAD_MESSAGE_FIELDS
        
        test_ns = Namespace('test')
        test_model = test_ns.model('TestVideoUpload', VIDEO_UPLOAD_MESSAGE_FIELDS)
        print("✅ Modelo de video creado exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando modelo de video: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_imports()
    test_flask_restx_model_creation()
