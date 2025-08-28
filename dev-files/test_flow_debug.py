#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debug específico del método test_flow_response
"""

import sys
import os
sys.path.append('.')

from app.services.rivescript_service import RiveScriptService

def test_flow_directly():
    print("🔍 DEBUG: Probando test_flow_response directamente")
    
    # Contenido básico de RiveScript
    content = """! version = 2.0

+ [*] soporte [*]
- Hola, soy el asistente de Soporte Técnico 🛠️

+ hola
- ¡Hola! ¿En qué puedo ayudarte?
"""
    
    print(f"📝 Contenido RiveScript:")
    print(content)
    print("-" * 50)
    
    service = RiveScriptService()
    
    # Probar diferentes mensajes
    test_messages = ["soporte", "hola", "ayuda soporte", "necesito soporte"]
    
    for msg in test_messages:
        print(f"\n👤 Probando: '{msg}'")
        result = service.test_flow_response(content, msg)
        print(f"🤖 Resultado: {result}")
        
        if result.get('success'):
            print(f"✅ Respuesta: {result.get('response')}")
            print(f"📊 Válida: {result.get('valid_response')}")
        else:
            print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    test_flow_directly()
