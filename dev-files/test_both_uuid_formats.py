#!/usr/bin/env python
"""
Probar el método get_by_id corregido
"""
from app import create_app
from app.repositories.flow_repository import FlowRepository  

def test_both_formats():
    app = create_app()
    
    with app.app_context():
        flow_repo = FlowRepository()
        
        # Test 1: UUID con guiones
        uuid_with_hyphens = "32561960-1902-495f-af1f-c6157c2d12b0"
        print(f"Probando UUID con guiones: {uuid_with_hyphens}")
        result1 = flow_repo.get_by_id(uuid_with_hyphens)
        print(f"Resultado 1: {'✅ Encontrado' if result1 else '❌ No encontrado'}")
        if result1:
            print(f"  Nombre: {result1.name}")
        
        # Test 2: UUID sin guiones  
        uuid_without_hyphens = "1ab9d2c9fe1b4ef6a448a9bdf7775b35"
        print(f"\nProbando UUID sin guiones: {uuid_without_hyphens}")
        result2 = flow_repo.get_by_id(uuid_without_hyphens)
        print(f"Resultado 2: {'✅ Encontrado' if result2 else '❌ No encontrado'}")
        if result2:
            print(f"  Nombre: {result2.name}")

if __name__ == "__main__":
    test_both_formats()
