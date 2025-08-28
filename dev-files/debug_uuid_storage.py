#!/usr/bin/env python
"""
Investigar cómo están almacenados los UUIDs en la base de datos
"""
import sqlite3
from app import create_app
from app.repositories.flow_repository import FlowRepository  
from database.models import ConversationFlow

def investigate_uuid_storage():
    app = create_app()
    
    with app.app_context():
        # Obtener flujos usando SQLAlchemy
        flow_repo = FlowRepository()
        flows = flow_repo.get_all()
        
        print(f"=== FLUJOS DESDE SQLALCHEMY ===")
        print(f"Total: {len(flows)}")
        if flows:
            first_flow = flows[0]
            print(f"Primer flujo:")
            print(f"  ID: {first_flow.id}")
            print(f"  Tipo: {type(first_flow.id)}")
            print(f"  String: '{str(first_flow.id)}'")
            print(f"  Nombre: {first_flow.name}")
        
        print(f"\n=== ACCESO DIRECTO A SQLITE ===")
        # Obtener la ruta de la base de datos
        from flask import current_app
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        
        if db_path:
            print(f"Ruta DB: {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Ver todas las tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"Tablas disponibles: {[t[0] for t in tables]}")
                
                # Si existe conversation_flows, ver algunos registros
                if any('conversation_flows' in table[0] for table in tables):
                    cursor.execute("SELECT id, name FROM conversation_flows LIMIT 5")
                    raw_flows = cursor.fetchall()
                    
                    print(f"Registros directos de SQLite:")
                    for i, (flow_id, name) in enumerate(raw_flows):
                        print(f"  {i+1}. ID: '{flow_id}' (tipo: {type(flow_id)}) -> {name}")
                        
                        # Comparar con el primer flujo de SQLAlchemy
                        if flows and i == 0:
                            sqlalchemy_id = str(flows[0].id)
                            print(f"      SQLAlchemy: '{sqlalchemy_id}'")
                            print(f"      Iguales: {flow_id == sqlalchemy_id}")
                            print(f"      Sin guiones: {flow_id.replace('-', '') if '-' in flow_id else 'N/A'}")
                
                conn.close()
                
            except Exception as e:
                print(f"Error accediendo a SQLite: {e}")
        else:
            print("No se pudo obtener la ruta de la base de datos")

if __name__ == "__main__":
    investigate_uuid_storage()
