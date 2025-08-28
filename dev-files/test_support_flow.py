#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba directo para verificar el flujo de soporte técnico
"""
import sqlite3
from pathlib import Path

def test_support_flow():
    """
    Prueba el flujo de soporte técnico directamente desde la base de datos
    """
    print("🧪 Probando flujo de soporte técnico...")
    
    # Conectar a la base de datos
    db_path = Path("instance/whatsapp_test.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Obtener el flujo de soporte técnico
        cursor.execute("""
        SELECT name, rivescript_content FROM conversation_flows 
        WHERE name LIKE '%Soporte%' 
        ORDER BY priority
        """)
        
        flows = cursor.fetchall()
        
        if not flows:
            print("❌ No se encontró el flujo de soporte técnico")
            return False
        
        for name, content in flows:
            print(f"\n📄 Flujo: {name}")
            print(f"📏 Longitud: {len(content)} caracteres")
            
            # Buscar el trigger principal
            lines = content.split('\n')
            main_trigger = None
            response_lines = []
            in_response = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('+ [*] (soporte tecnico'):
                    main_trigger = line
                    in_response = True
                    print(f"✅ Trigger encontrado: {line[:50]}...")
                elif in_response and line.startswith('-'):
                    response_lines.append(line[2:])  # Quitar "- "
                elif in_response and (line.startswith('+') or line.startswith('<')):
                    break  # Fin de la respuesta
            
            if main_trigger and response_lines:
                print(f"📋 Respuesta completa ({len(response_lines)} líneas):")
                for i, line in enumerate(response_lines, 1):
                    if line.strip():  # Solo líneas no vacías
                        print(f"  {i:2d}. {line}")
                
                # Contar opciones del menú (1️⃣-5️⃣)
                menu_options = [line for line in response_lines if '️⃣' in line]
                print(f"\n🎯 Opciones del menú encontradas: {len(menu_options)}")
                for option in menu_options:
                    print(f"  • {option}")
                
                if len(menu_options) < 5:
                    print("⚠️ PROBLEMA: Faltan opciones del menú")
                    return False
                else:
                    print("✅ Todas las opciones del menú están presentes")
            else:
                print("❌ No se encontró el contenido completo del trigger")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        conn.close()

def fix_support_flow():
    """
    Arregla el flujo de soporte técnico con formato correcto
    """
    print("\n🔧 Arreglando flujo de soporte técnico...")
    
    # Flujo corregido con formato simple
    fixed_flow = """! version = 2.0

> topic random

+ [*] (soporte tecnico|soporte técnico|ayuda tecnica|ayuda técnica|problema tecnico|problema técnico|no funciona|error|falla) [*]
- Hola, soy el asistente de **Soporte Técnico** 🛠️
- 
- ¿Con qué puedo ayudarte hoy?
- 
- 1️⃣ Problemas de conexión
- 2️⃣ Errores de la aplicación  
- 3️⃣ Problemas de rendimiento
- 4️⃣ Configuración de cuenta
- 5️⃣ Hablar con un técnico
- 
- Escribe el número o describe tu problema.

+ [*] (1|uno|conexion|conexión|internet|red|wifi) [*]
- **Problemas de Conexión** 🌐
- Vamos a revisar tu conectividad:
- 1. Verifica que tu WiFi esté conectado
- 2. Reinicia tu router (30 segundos)
- 3. Prueba con datos móviles
- ¿Funcionó? Responde "si" o "no"

+ [*] (2|dos|error|errores|aplicacion|aplicación|app|falla) [*]
- **Errores de Aplicación** ⚠️
- Te ayudo a diagnosticar:
- 1. Cierra la aplicación completamente
- 2. Reinicia tu dispositivo
- 3. Abre la aplicación nuevamente
- Si persiste, describe el error.

+ [*] (3|tres|lento|rendimiento|performance|velocidad) [*]
- **Problemas de Rendimiento** ⚡
- Optimicemos tu experiencia:
- 1. Libera espacio en tu dispositivo
- 2. Cierra aplicaciones en segundo plano  
- 3. Actualiza la aplicación
- ¿Notas mejora?

+ [*] (4|cuatro|cuenta|perfil|configuracion|configuración|ajustes) [*]
- **Configuración de Cuenta** ⚙️
- Te ayudo con:
- • Cambio de contraseña
- • Actualización de datos
- • Configuración de privacidad  
- • Sincronización
- ¿Qué necesitas configurar?

+ [*] (5|cinco|tecnico|técnico|humano|persona|agente) [*]
- **Conexión con Técnico** 👨‍💻
- Te conectaré con nuestro equipo técnico.
- **Horario:** Lunes a Viernes 8AM-6PM
- **Sábados:** 9AM-2PM
- Un técnico te contactará pronto.
- **Ticket:** #12345

+ (si|sí|yes|funciona|funcionó)
- ¡Excelente! 😊 Me alegra que haya funcionado.
- Si necesitas más ayuda, escribe "soporte tecnico".
- ¡Que tengas un gran día!

+ (no|nada|sigue|persiste)
- Entiendo que el problema persiste. 😔
- Vamos a intentar otras opciones:
- • Reinstala la aplicación
- • Contacta soporte técnico (opción 5)
- • Verifica actualizaciones
- ¿Te conecto con un técnico?

+ (gracias|thanks|ok|vale)
- ¡De nada! 😊 Me alegra haberte ayudado.
- Estoy aquí cuando me necesites.
- Escribe "soporte tecnico" para el menú.

< topic"""
    
    # Conectar a la base de datos
    db_path = Path("instance/whatsapp_test.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        from datetime import datetime
        import uuid
        
        # Actualizar el flujo existente
        cursor.execute("""
        UPDATE conversation_flows 
        SET rivescript_content = ?, updated_at = ?
        WHERE name LIKE '%Soporte%'
        """, (fixed_flow, datetime.now().isoformat()))
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Flujo de soporte técnico actualizado correctamente")
            return True
        else:
            print("❌ No se encontró flujo para actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando flujo: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Verificando flujo de soporte técnico...\n")
    
    # Probar el flujo actual
    if not test_support_flow():
        print("\n🔧 El flujo tiene problemas. Aplicando corrección...")
        if fix_support_flow():
            print("\n✅ Flujo corregido. Probando de nuevo...")
            test_support_flow()
        else:
            print("\n❌ Error corrigiendo el flujo")
    
    print("\n🎉 Verificación completada. Reinicia el servidor para aplicar cambios.")
