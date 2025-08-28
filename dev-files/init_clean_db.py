#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar base de datos limpia con configuración optimizada
"""

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def init_clean_database():
    """
    Inicializa una base de datos limpia con configuración optimizada
    """
    try:
        print("🔧 Inicializando base de datos limpia...")
        
        # Configurar variables de entorno necesarias
        os.environ['FLASK_ENV'] = 'development'
        os.environ['DATABASE_URL'] = 'sqlite:///instance/whatsapp_test.db'
        
        # Importar después de configurar el entorno
        from app import create_app
        from sqlalchemy import create_engine, text
        from app.models.base import Base
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            print("📋 Creando tablas...")
            
            # Obtener la URL de la base de datos desde la configuración
            database_url = app.config.get('DATABASE_URL', 'sqlite:///instance/whatsapp_test.db')
            
            # Crear engine y tablas
            engine = create_engine(database_url)
            Base.metadata.create_all(engine)
            
            # Configurar SQLite para mejor rendimiento
            with engine.connect() as conn:
                conn.execute(text("PRAGMA synchronous=NORMAL"))
                conn.execute(text("PRAGMA cache_size=10000")) 
                conn.execute(text("PRAGMA temp_store=MEMORY"))
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.commit()
            
            print("✅ Base de datos inicializada correctamente")
            
            # Cargar flujos básicos
            print("📝 Cargando flujos de conversación...")
            
            from app.repositories.flow_repository import FlowRepository
            from app.models.conversation import ConversationFlow
            import uuid
            from datetime import datetime
            from sqlalchemy.orm import sessionmaker
            
            # Crear sesión de base de datos
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
            
            try:
                
                # Flujo básico
                basic_flow_content = """! version = 2.0

// Flujo básico de saludo
> topic random

+ hola
- ¡Hola! 👋 Bienvenido a nuestro asistente virtual.
- ¿En qué puedo ayudarte?
- 1️⃣ Ventas - Información de productos
- 2️⃣ Soporte - Ayuda técnica  
- 3️⃣ Recursos Humanos - Consultas de empleados
- Escribe el número de la opción o describe tu consulta.

+ (hello|hi|hey)
- Hello! 👋 Welcome to our virtual assistant.
- How can I help you today?
- 1️⃣ Sales - Product information
- 2️⃣ Support - Technical help
- 3️⃣ Human Resources - Employee queries

+ (1|uno|ventas|productos)
- ¡Perfecto! Te conectaré con nuestro equipo de ventas.
- ¿Tienes alguna pregunta específica sobre nuestros servicios?

+ (2|dos|soporte|ayuda|problema)
- Te ayudo con soporte técnico.
- Por favor describe tu problema o consulta.

+ (3|tres|recursos humanos|rrhh|empleado)
- ¡Hola! Soy tu asistente de Recursos Humanos.
- ¿En qué puedo ayudarte hoy?
- 1️⃣ Solicitudes y permisos
- 2️⃣ Información sobre nómina
- 3️⃣ Beneficios y prestaciones
- Escribe el número o describe tu consulta.

+ *
- Gracias por contactarnos.
- Para ayudarte mejor, puedes escribir "hola" para ver el menú.
- ¿En qué te puedo ayudar?

< topic"""

                basic_flow = ConversationFlow(
                    id=str(uuid.uuid4()),
                    name="Flujo Básico Inicial",
                    description="Flujo de conversación básico con saludo y opciones principales",
                    rivescript_content=basic_flow_content,
                    is_active=True,
                    is_default=True,
                    priority=1,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                session.add(basic_flow)
                session.commit()
                print("✅ Flujo básico cargado")
                
            except Exception as e:
                session.rollback()
                print(f"⚠️ Error cargando flujos: {e}")
            finally:
                session.close()
            
        print("\n🎉 ¡Base de datos inicializada exitosamente!")
        print("\n💡 Configuración aplicada:")
        print("   • Tablas creadas correctamente")
        print("   • SQLite optimizado para rendimiento")
        print("   • Flujo básico de conversación cargado")
        print("   • Listo para usar")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_clean_database()
    
    if success:
        print("\n🚀 ¡Listo para usar! Puedes iniciar el servidor ahora.")
    else:
        print("\n⚠️ Hubo errores en la inicialización.")
