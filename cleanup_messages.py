#!/usr/bin/env python3
"""
Script para verificar y limpiar mensajes duplicados en la base de datos
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

from entrypoint import create_app
from database.models import Message
from database.connection import db


def check_duplicate_messages():
    """Verifica si hay mensajes duplicados en la base de datos"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando mensajes duplicados...")
        print()
        
        # Consulta para encontrar whatsapp_message_ids duplicados
        duplicate_query = db.session.query(
            Message.whatsapp_message_id,
            db.func.count(Message.whatsapp_message_id).label('count')
        ).group_by(
            Message.whatsapp_message_id
        ).having(
            db.func.count(Message.whatsapp_message_id) > 1
        ).all()
        
        if duplicate_query:
            print(f"❌ Se encontraron {len(duplicate_query)} mensajes con duplicados:")
            for msg_id, count in duplicate_query:
                print(f"  • {msg_id[:50]}... (duplicado {count} veces)")
                
                # Mostrar detalles de cada duplicado
                duplicates = Message.query.filter_by(whatsapp_message_id=msg_id).all()
                for i, dup in enumerate(duplicates, 1):
                    print(f"    {i}. ID: {dup.id} | Created: {dup.created_at} | Status: {dup.status}")
            
            return duplicate_query
        else:
            print("✅ No se encontraron mensajes duplicados")
            return []


def clean_duplicate_messages(dry_run=True):
    """Limpia mensajes duplicados, manteniendo el más antiguo"""
    
    app = create_app()
    
    with app.app_context():
        duplicates = check_duplicate_messages()
        
        if not duplicates:
            print("✅ No hay nada que limpiar")
            return
        
        print()
        if dry_run:
            print("🧪 MODO DRY RUN - No se realizarán cambios reales")
        else:
            print("🧹 LIMPIANDO mensajes duplicados...")
        
        cleaned_count = 0
        
        for msg_id, count in duplicates:
            # Obtener todos los duplicados ordenados por fecha (el más antiguo primero)
            duplicates_list = Message.query.filter_by(
                whatsapp_message_id=msg_id
            ).order_by(Message.created_at.asc()).all()
            
            # Mantener el primer mensaje (más antiguo) y eliminar el resto
            keep_message = duplicates_list[0]
            delete_messages = duplicates_list[1:]
            
            print(f"\n📝 Procesando: {msg_id[:50]}...")
            print(f"  ✅ Mantener: ID {keep_message.id} (creado: {keep_message.created_at})")
            
            for delete_msg in delete_messages:
                print(f"  ❌ Eliminar: ID {delete_msg.id} (creado: {delete_msg.created_at})")
                
                if not dry_run:
                    try:
                        db.session.delete(delete_msg)
                        cleaned_count += 1
                    except Exception as e:
                        print(f"    🚨 Error eliminando mensaje {delete_msg.id}: {e}")
        
        if not dry_run:
            try:
                db.session.commit()
                print(f"\n✅ Limpieza completada: {cleaned_count} mensajes duplicados eliminados")
            except Exception as e:
                db.session.rollback()
                print(f"\n🚨 Error en la limpieza: {e}")
        else:
            print(f"\n📊 Se eliminarían {sum(count-1 for _, count in duplicates)} mensajes duplicados")


def show_message_stats():
    """Muestra estadísticas de mensajes"""
    
    app = create_app()
    
    with app.app_context():
        print("📊 Estadísticas de mensajes:")
        print()
        
        total_messages = Message.query.count()
        print(f"  📨 Total de mensajes: {total_messages}")
        
        if total_messages > 0:
            # Mensajes por tipo
            types = db.session.query(
                Message.message_type,
                db.func.count(Message.id).label('count')
            ).group_by(Message.message_type).all()
            
            print("  📋 Por tipo:")
            for msg_type, count in types:
                print(f"    • {msg_type}: {count}")
            
            # Mensajes por dirección
            directions = db.session.query(
                Message.direction,
                db.func.count(Message.id).label('count')
            ).group_by(Message.direction).all()
            
            print("  🔄 Por dirección:")
            for direction, count in directions:
                print(f"    • {direction}: {count}")
            
            # Mensajes recientes
            recent = Message.query.order_by(
                Message.created_at.desc()
            ).limit(5).all()
            
            print("  🕐 Mensajes recientes:")
            for msg in recent:
                print(f"    • {msg.whatsapp_message_id[:30]}... | {msg.message_type} | {msg.created_at}")


if __name__ == "__main__":
    print("🧹 Script de verificación y limpieza de mensajes")
    print("=" * 50)
    print()
    
    # Mostrar estadísticas
    show_message_stats()
    print()
    
    # Verificar duplicados
    duplicates = check_duplicate_messages()
    
    if duplicates:
        print()
        print("⚠️  Se encontraron mensajes duplicados.")
        
        choice = input("¿Deseas limpiarlos? (y/N): ").strip().lower()
        if choice in ['y', 'yes', 's', 'si']:
            # Primero hacer dry run
            print()
            clean_duplicate_messages(dry_run=True)
            
            print()
            confirm = input("¿Confirmas la eliminación? (y/N): ").strip().lower()
            if confirm in ['y', 'yes', 's', 'si']:
                clean_duplicate_messages(dry_run=False)
            else:
                print("❌ Limpieza cancelada")
        else:
            print("❌ Limpieza cancelada")
    
    print()
    print("✅ Script completado")
