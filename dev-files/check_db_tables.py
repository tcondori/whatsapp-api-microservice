#!/usr/bin/env python
"""
Script para verificar las tablas de la base de datos
"""

from app import create_app
from database.models import *
from database.connection import db
import json

def check_database():
    """Verifica el estado de las tablas en la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🔍 VERIFICACIÓN DE BASE DE DATOS")
        print("="*60)
        
        # Obtener nombres de tablas
        try:
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
            print(f"\n📋 TABLAS ENCONTRADAS ({len(table_names)}):")
            for i, table in enumerate(table_names, 1):
                print(f"   {i}. {table}")
        except Exception as e:
            print(f"❌ Error obteniendo lista de tablas: {e}")
            return
        
        print("\n" + "="*60)
        print("📊 VERIFICACIÓN DE MODELOS")
        print("="*60)
        
        # Diccionario de modelos para verificar
        models_to_check = {
            'MessagingLine': MessagingLine,
            'Message': Message,
            'Contact': Contact,
            'WebhookEvent': WebhookEvent,
            'MediaFile': MediaFile,
            'ConversationContext': ConversationContext,
            'ChatbotInteraction': ChatbotInteraction,
        }
        
        results = {}
        for model_name, model_class in models_to_check.items():
            try:
                count = db.session.query(model_class).count()
                results[model_name] = {
                    'status': '✅ OK',
                    'count': count,
                    'table': model_class.__tablename__
                }
                print(f"✅ {model_name:20} -> {count:3} registros (tabla: {model_class.__tablename__})")
            except Exception as e:
                results[model_name] = {
                    'status': '❌ ERROR',
                    'error': str(e),
                    'table': getattr(model_class, '__tablename__', 'N/A')
                }
                print(f"❌ {model_name:20} -> Error: {str(e)[:50]}...")
        
        print("\n" + "="*60)
        print("🆕 MODELOS DEL CHATBOT")
        print("="*60)
        
        chatbot_models = ['ConversationContext', 'ChatbotInteraction']
        chatbot_ok = True
        
        for model_name in chatbot_models:
            if model_name in results:
                status = results[model_name]['status']
                if '✅' in status:
                    count = results[model_name]['count']
                    table = results[model_name]['table']
                    print(f"✅ {model_name} listo - {count} registros en tabla '{table}'")
                else:
                    print(f"❌ {model_name} - {results[model_name].get('error', 'Error desconocido')}")
                    chatbot_ok = False
            else:
                print(f"⚠️  {model_name} - No verificado")
                chatbot_ok = False
        
        print("\n" + "="*60)
        print("📈 RESUMEN")
        print("="*60)
        
        working_models = sum(1 for r in results.values() if '✅' in r['status'])
        total_models = len(results)
        
        print(f"🔹 Modelos funcionando: {working_models}/{total_models}")
        print(f"🔹 Tablas totales: {len(table_names)}")
        print(f"🔹 Chatbot ready: {'✅ SÍ' if chatbot_ok else '❌ NO'}")
        
        if working_models == total_models and chatbot_ok:
            print("\n🎉 ¡BASE DE DATOS LISTA PARA CHATBOT!")
            print("🚀 Puedes continuar con la Fase 2 del desarrollo")
        else:
            print(f"\n⚠️  Base de datos parcialmente configurada")
            print("🔧 Revisa los errores antes de continuar")
            
        print("="*60)

if __name__ == "__main__":
    check_database()
