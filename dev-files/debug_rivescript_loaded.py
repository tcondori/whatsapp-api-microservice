#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar si RiveScript está cargado correctamente desde BD
"""

import sys
sys.path.append('.')

from app import create_app
from app.services.rivescript_service import RiveScriptService
from app.services.chatbot_service import ChatbotService

def debug_rivescript_loaded():
    print("🔍 DEBUG: Verificando RiveScript cargado desde BD")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print("\n1️⃣ Probando RiveScriptService directamente:")
        rs_service = RiveScriptService()
        
        # Verificar estado
        print(f"   - Inicializado: {rs_service._initialized}")
        
        # Forzar inicialización
        try:
            init_result = rs_service._ensure_initialized()
            print(f"   - Resultado inicialización: {init_result}")
            print(f"   - RiveScript disponible: {rs_service.rs is not None}")
        except Exception as e:
            print(f"   - Error en _ensure_initialized: {e}")
        
        # Probar directamente
        print("\n   🧪 Probando mensaje 'soporte':")
        try:
            response = rs_service.get_response("debug_user", "soporte")
            print(f"   ✅ Respuesta: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n   🧪 Probando mensaje 'hola':")
        try:
            response = rs_service.get_response("debug_user", "hola")
            print(f"   ✅ Respuesta: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n2️⃣ Probando ChatbotService:")
        try:
            chatbot_service = ChatbotService()
            print(f"   - ChatbotService creado: OK")
            
            response = chatbot_service.process_message("debug_phone", "soporte")
            print(f"   ✅ Respuesta ChatBot: {response}")
            
        except Exception as e:
            print(f"   ❌ Error en ChatbotService: {e}")
        
        print("\n3️⃣ Verificando flujos en BD:")
        from app.repositories.flow_repository import FlowRepository
        flow_repo = FlowRepository()
        flows = flow_repo.get_all_flows()
        
        print(f"   📊 Total flujos: {len(flows)}")
        for flow in flows:
            print(f"   - {flow.name} (ID: {str(flow.id)[:8]}...) - Activo: {flow.is_active}")
            if flow.is_active:
                # Mostrar una muestra del contenido
                content_sample = flow.rivescript_content[:100].replace('\n', ' ')
                print(f"     Contenido: {content_sample}...")

if __name__ == "__main__":
    debug_rivescript_loaded()
