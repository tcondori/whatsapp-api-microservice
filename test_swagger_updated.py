#!/usr/bin/env python3
"""
Test de validación de actualización de Swagger
Verifica que todos los nuevos modelos y endpoints estén correctamente documentados
"""

import requests
import json
from pprint import pprint

def test_swagger_documentation():
    """
    Prueba que la documentación Swagger incluya todos los nuevos endpoints multimedia
    """
    try:
        # Obtener el schema de Swagger
        response = requests.get('http://localhost:5000/swagger.json')
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo swagger.json: {response.status_code}")
            return False
            
        swagger_data = response.json()
        
        # Endpoints esperados
        expected_endpoints = [
            '/v1/messages/video/upload',
            '/v1/messages/audio/upload', 
            '/v1/messages/document/upload',
            '/v1/messages/sticker/upload'
        ]
        
        # Verificar que existen los endpoints
        paths = swagger_data.get('paths', {})
        missing_endpoints = []
        
        for endpoint in expected_endpoints:
            if endpoint not in paths:
                missing_endpoints.append(endpoint)
            else:
                print(f"✅ Endpoint documentado: {endpoint}")
        
        if missing_endpoints:
            print(f"❌ Endpoints faltantes: {missing_endpoints}")
            return False
        
        # Verificar que existen los nuevos modelos
        definitions = swagger_data.get('definitions', {})
        expected_models = [
            'VideoUploadMessageFields',
            'AudioUploadMessageFields',
            'DocumentUploadMessageFields', 
            'StickerUploadMessageFields',
            'MultimediaResponse'
        ]
        
        missing_models = []
        for model in expected_models:
            if model not in definitions:
                missing_models.append(model)
            else:
                print(f"✅ Modelo documentado: {model}")
        
        if missing_models:
            print(f"❌ Modelos faltantes: {missing_models}")
            return False
        
        # Verificar que los endpoints tienen documentación detallada
        for endpoint in expected_endpoints:
            path_data = paths[endpoint]
            post_data = path_data.get('post', {})
            
            # Verificar que tiene descripción
            if not post_data.get('description'):
                print(f"❌ {endpoint} no tiene descripción")
                return False
                
            # Verificar que tiene parámetros
            parameters = post_data.get('parameters', [])
            has_file_param = any(p.get('name') == 'file' for p in parameters)
            
            if not has_file_param:
                print(f"❌ {endpoint} no tiene parámetro 'file'")
                return False
                
            print(f"✅ {endpoint} tiene documentación completa")
        
        print("\n🎉 TODAS LAS VALIDACIONES PASARON")
        print("📋 Resumen de la documentación Swagger:")
        print(f"   • Total endpoints documentados: {len(paths)}")
        print(f"   • Endpoints multimedia: {len(expected_endpoints)}")
        print(f"   • Total modelos definidos: {len(definitions)}")
        print(f"   • Modelos multimedia nuevos: {len(expected_models)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

def test_endpoint_details():
    """
    Muestra detalles específicos de cada endpoint multimedia
    """
    try:
        response = requests.get('http://localhost:5000/swagger.json')
        swagger_data = response.json()
        paths = swagger_data.get('paths', {})
        
        multimedia_endpoints = [
            '/v1/messages/video/upload',
            '/v1/messages/audio/upload', 
            '/v1/messages/document/upload',
            '/v1/messages/sticker/upload'
        ]
        
        print("\n📋 DETALLES DE ENDPOINTS MULTIMEDIA:")
        print("=" * 60)
        
        for endpoint in multimedia_endpoints:
            if endpoint in paths:
                post_data = paths[endpoint]['post']
                print(f"\n🔹 {endpoint}")
                print(f"   Descripción: {post_data.get('summary', 'N/A')}")
                
                parameters = post_data.get('parameters', [])
                file_params = [p for p in parameters if p.get('name') == 'file']
                if file_params:
                    file_param = file_params[0]
                    print(f"   Archivo: {file_param.get('description', 'N/A')}")
                
                responses = post_data.get('responses', {})
                print(f"   Respuestas: {', '.join(responses.keys())}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error mostrando detalles: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VALIDACIÓN DE DOCUMENTACIÓN SWAGGER ACTUALIZADA")
    print("=" * 60)
    
    # Ejecutar tests
    test_swagger_documentation()
    test_endpoint_details()
    
    print("\n✨ Validación completada")
