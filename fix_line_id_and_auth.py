#!/usr/bin/env python3
"""
Script para verificar y corregir los problemas de line_id y API key
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_lines():
    """
    Verifica qué líneas existen en la base de datos
    """
    try:
        from database.models import MessagingLine
        from database.connection import init_database
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/DSW/proyectos/proy04/instance/whatsapp_test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        init_database(app)
        
        with app.app_context():
            print("🔍 VERIFICANDO LÍNEAS EN BASE DE DATOS:")
            print("=" * 50)
            
            lines = MessagingLine.query.all()
            
            if not lines:
                print("❌ No hay líneas en la base de datos")
                return False
            
            for line in lines:
                print(f"📱 Line ID: {line.line_id} (tipo: {type(line.line_id)})")
                print(f"   Phone Number ID: {line.phone_number_id}")
                print(f"   Display Name: {line.display_name}")
                print(f"   Active: {line.is_active}")
                print(f"   Phone: {line.phone_number}")
                print("-" * 30)
            
            return True
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def create_test_line():
    """
    Crea una línea de prueba con line_id numérico
    """
    try:
        from database.models import MessagingLine
        from database.connection import init_database, db
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/DSW/proyectos/proy04/instance/whatsapp_test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        init_database(app)
        
        with app.app_context():
            # Verificar si ya existe una línea con ID 1
            existing_line = MessagingLine.query.filter_by(line_id=1).first()
            
            if existing_line:
                print("✅ Línea con ID 1 ya existe")
                print(f"   Phone Number ID: {existing_line.phone_number_id}")
                return True
            
            # Crear línea de prueba
            test_line = MessagingLine(
                line_id=1,  # ID numérico
                phone_number_id="137474306106595",  # Del .env
                display_name="Línea Principal",
                phone_number="+59167028778",
                is_active=True,
                max_daily_messages=1000
            )
            
            db.session.add(test_line)
            db.session.commit()
            
            print("✅ Línea de prueba creada:")
            print(f"   Line ID: {test_line.line_id}")
            print(f"   Phone Number ID: {test_line.phone_number_id}")
            print(f"   Display Name: {test_line.display_name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creando línea de prueba: {e}")
        return False

def fix_swagger_security_again():
    """
    Arregla la configuración de seguridad en Swagger una vez más
    """
    print("🔧 VERIFICANDO CONFIGURACIÓN DE SWAGGER SECURITY:")
    print("=" * 50)
    
    # Verificar entrypoint.py
    entrypoint_path = "entrypoint.py"
    
    if not os.path.exists(entrypoint_path):
        print(f"❌ Archivo {entrypoint_path} no encontrado")
        return False
    
    with open(entrypoint_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si tiene la configuración correcta
    if "'security': [{'apiKey': []}]" in content:
        print("✅ Configuración de seguridad correcta en entrypoint.py")
    else:
        print("❌ Configuración de seguridad incorrecta en entrypoint.py")
        return False
    
    # Verificar routes.py
    routes_path = "app/api/messages/routes.py"
    
    if not os.path.exists(routes_path):
        print(f"❌ Archivo {routes_path} no encontrado")
        return False
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        routes_content = f.read()
    
    # Contar cuántos endpoints tienen @doc(security='apiKey')
    security_count = routes_content.count("@messages_ns.doc(security='apiKey')")
    require_api_key_count = routes_content.count("@require_api_key")
    
    print(f"📊 Endpoints con @doc(security='apiKey'): {security_count}")
    print(f"📊 Endpoints con @require_api_key: {require_api_key_count}")
    
    if security_count == require_api_key_count and security_count > 0:
        print("✅ Todos los endpoints protegidos tienen documentación de seguridad")
    else:
        print("❌ Algunos endpoints faltan documentación de seguridad")
        return False
    
    return True

if __name__ == "__main__":
    print("🛠️  DIAGNÓSTICO Y CORRECCIÓN DE PROBLEMAS")
    print("=" * 60)
    
    # 1. Verificar líneas en BD
    print("\n1️⃣  Verificando base de datos...")
    if not check_database_lines():
        print("🔧 Creando línea de prueba...")
        create_test_line()
        print("✅ Reintentando verificación...")
        check_database_lines()
    
    # 2. Verificar configuración de Swagger
    print("\n2️⃣  Verificando configuración de Swagger...")
    fix_swagger_security_again()
    
    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Usa line_id numérico: 1 (en lugar de 'line_1')")
    print("2. En Swagger, prueba con este payload:")
    print("   {")
    print('     "to": "+59167028778",')
    print('     "text": "Mensaje de prueba",')
    print('     "line_id": 1')
    print("   }")
    print("3. Asegúrate de usar el botón 'Authorize' en Swagger")
    print("4. API Key válida: dev-api-key")
