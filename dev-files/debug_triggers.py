#!/usr/bin/env python3
"""
Debug: Verificar triggers activos en RiveScript
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app import create_app
from app.services.rivescript_service import RiveScriptService
from app.repositories.flow_repository import FlowRepository

def debug_triggers():
    print("🔍 DEBUG: Verificando triggers de RiveScript")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # 1. Verificar flujos en BD
        print("\n1️⃣ Flujos activos en BD:")
        flow_repo = FlowRepository()
        flows = flow_repo.get_all_flows()
        
        for flow in flows:
            print(f"   - {flow.name} (Active: {flow.is_active})")
            if flow.is_active:
                print(f"     Content preview: {flow.rivescript_content[:100]}...")
        
        print(f"\n   📊 Total: {len(flows)} flujos, {len([f for f in flows if f.is_active])} activos")
        
        # 2. Verificar RiveScript cargado
        print("\n2️⃣ Verificando RiveScript Service:")
        rs_service = RiveScriptService()
        
        # Verificar que esté inicializado
        if hasattr(rs_service, 'rs') and rs_service.rs:
            print("   ✅ RiveScript inicializado")
            
            # Intentar obtener información de triggers (si está disponible)
            try:
                # Probar diferentes mensajes
                test_messages = ["hola", "soporte", "ayuda", "test"]
                
                print("\n3️⃣ Probando triggers:")
                for msg in test_messages:
                    try:
                        response = rs_service.get_response("debug_user", msg)
                        if response and isinstance(response, dict):
                            resp_text = response.get('response', 'No response')
                            print(f"   📝 '{msg}' → {resp_text[:50]}{'...' if len(resp_text) > 50 else ''}")
                        elif response:
                            print(f"   📝 '{msg}' → {str(response)[:50]}{'...' if len(str(response)) > 50 else ''}")
                        else:
                            print(f"   ❌ '{msg}' → Sin respuesta")
                    except Exception as e:
                        print(f"   ❌ '{msg}' → Error: {e}")
                        
            except Exception as e:
                print(f"   ❌ Error probando triggers: {e}")
        else:
            print("   ❌ RiveScript no inicializado")

if __name__ == "__main__":
    debug_triggers()
