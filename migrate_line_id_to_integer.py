#!/usr/bin/env python3
"""
Migración: Cambiar line_id de String a Integer con valores incrementales

PASO 1: Modificar datos existentes
- line_1 -> 1
- line_2 -> 2

PASO 2: Actualizar modelo (requiere actualización manual del modelo)

Uso: python migrate_line_id_to_integer.py
"""
from entrypoint import create_app
from database.connection import db
from database.models import MessagingLine, Message
import logging

def migrate_line_id_to_integer():
    """
    Migra los line_id de string a integer
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 INICIANDO MIGRACIÓN: line_id String -> Integer")
            print("=" * 60)
            
            # PASO 1: Revisar estado actual
            print("📋 Estado actual de messaging_lines:")
            lines = MessagingLine.query.all()
            for line in lines:
                print(f"  - line_id: {repr(line.line_id)} | phone_number_id: {line.phone_number_id}")
            
            # PASO 2: Mapear conversiones
            mapping = {
                'line_1': 1,
                'line_2': 2,
                'line_3': 3,
                'line_4': 4,
                'line_5': 5
                # Agregar más si es necesario
            }
            
            print(f"\n🔄 Aplicando mapeo de conversión:")
            for old_id, new_id in mapping.items():
                print(f"  {old_id} -> {new_id}")
            
            # PASO 3: Actualizar messaging_lines
            print(f"\n📝 Actualizando tabla messaging_lines...")
            updated_lines = 0
            
            for line in lines:
                old_line_id = line.line_id
                if old_line_id in mapping:
                    new_line_id = mapping[old_line_id]
                    print(f"  ✅ Actualizando {old_line_id} -> {new_line_id}")
                    
                    # Actualizar el line_id (aunque sigue siendo string por ahora)
                    line.line_id = str(new_line_id)
                    updated_lines += 1
                else:
                    print(f"  ⚠️  No se encontró mapeo para: {old_line_id}")
            
            # PASO 4: Actualizar tabla messages para mantener consistencia
            print(f"\n📝 Actualizando tabla messages...")
            updated_messages = 0
            
            messages = Message.query.all()
            for message in messages:
                old_line_id = message.line_id
                if old_line_id in mapping:
                    new_line_id = str(mapping[old_line_id])
                    print(f"  ✅ Mensaje {message.id}: {old_line_id} -> {new_line_id}")
                    message.line_id = new_line_id
                    updated_messages += 1
            
            # PASO 5: Confirmar cambios
            db.session.commit()
            print(f"\n💾 Cambios guardados exitosamente")
            print(f"  - Lines actualizadas: {updated_lines}")
            print(f"  - Messages actualizados: {updated_messages}")
            
            # PASO 6: Verificar resultado
            print(f"\n✅ Estado final de messaging_lines:")
            lines = MessagingLine.query.all()
            for line in lines:
                print(f"  - line_id: {repr(line.line_id)} | phone_number_id: {line.phone_number_id} | display_name: {line.display_name}")
            
            print(f"\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print("📋 SIGUIENTE PASO MANUAL:")
            print("1. Actualizar el modelo MessagingLine en database/models.py")
            print("2. Cambiar: line_id = db.Column(db.String(50), ...)")
            print("3. Por:     line_id = db.Column(db.Integer, ...)")
            print("4. Reiniciar la aplicación")
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            db.session.rollback()
            return False

def verify_migration():
    """
    Verifica que la migración sea correcta
    """
    app = create_app()
    
    with app.app_context():
        try:
            lines = MessagingLine.query.all()
            messages = Message.query.all()
            
            print("🔍 VERIFICACIÓN POST-MIGRACIÓN:")
            print("=" * 40)
            
            # Verificar que todos los line_id sean números
            valid_lines = True
            for line in lines:
                try:
                    int(line.line_id)  # Intentar convertir a int
                    print(f"✅ Line ID válido: {line.line_id}")
                except ValueError:
                    print(f"❌ Line ID inválido: {line.line_id}")
                    valid_lines = False
            
            # Verificar consistencia entre tablas
            valid_consistency = True
            line_ids_set = {line.line_id for line in lines}
            
            for message in messages:
                if message.line_id not in line_ids_set:
                    print(f"❌ Mensaje con line_id inconsistente: {message.line_id}")
                    valid_consistency = False
            
            if valid_lines and valid_consistency:
                print("✅ Migración verificada correctamente")
                return True
            else:
                print("❌ Se encontraron problemas en la migración")
                return False
                
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            return False

if __name__ == "__main__":
    print("📦 MIGRACIÓN DE line_id: String -> Integer")
    print("Preparando datos para usar valores enteros incrementales")
    print("=" * 60)
    
    # Ejecutar migración
    success = migrate_line_id_to_integer()
    
    if success:
        # Verificar resultado
        verify_migration()
        
        print("\n" + "=" * 60)
        print("🎯 MIGRACIÓN DE DATOS COMPLETADA")
        print("⚠️  ACCIÓN REQUERIDA:")
        print("1. Modificar database/models.py manualmente")
        print("2. Cambiar line_id de db.String(50) a db.Integer")
        print("3. Reiniciar aplicación")
    else:
        print("\n❌ MIGRACIÓN FALLÓ")
        print("Los datos no fueron modificados")
