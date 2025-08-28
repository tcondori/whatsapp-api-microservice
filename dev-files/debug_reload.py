#!/usr/bin/env python3
"""
Debug: Verificar por qué falla reload_flows_from_database
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app import create_app
from app.services.rivescript_service import RiveScriptService

def debug_reload():
    print("🔍 DEBUG: Verificando por qué falla la recarga")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print("\n1️⃣ Creando RiveScriptService...")
        rs_service = RiveScriptService()
        
        print(f"   - Servicio creado: {rs_service is not None}")
        print(f"   - _initialized: {getattr(rs_service, '_initialized', 'No existe')}")
        print(f"   - RIVESCRIPT_AVAILABLE: {getattr(rs_service, 'RIVESCRIPT_AVAILABLE', 'No existe')}")
        
        print("\n2️⃣ Intentando _ensure_initialized()...")
        try:
            initialized = rs_service._ensure_initialized()
            print(f"   - Resultado: {initialized}")
            print(f"   - rs objeto: {rs_service.rs is not None if hasattr(rs_service, 'rs') else 'No existe'}")
        except Exception as e:
            print(f"   - Error: {e}")
        
        print("\n3️⃣ Verificando flujos activos...")
        try:
            active_flows = rs_service.flow_repo.get_active_flows()
            print(f"   - Flujos activos encontrados: {len(active_flows)}")
            for flow in active_flows:
                print(f"     * {flow.name} (ID: {str(flow.id)[:8]}...)")
        except Exception as e:
            print(f"   - Error obteniendo flujos: {e}")
        
        print("\n4️⃣ Intentando recarga completa...")
        try:
            result = rs_service.reload_flows_from_database()
            print(f"   - Resultado: {result}")
            
            if not result:
                print("   ❌ La recarga falló. Posibles causas:")
                print("      - No hay contexto de aplicación")
                print("      - RiveScript no está disponible")  
                print("      - Erro en _ensure_initialized()")
                print("      - Error al cargar flujos")
        except Exception as e:
            print(f"   - Error en recarga: {e}")

if __name__ == "__main__":
    debug_reload()
