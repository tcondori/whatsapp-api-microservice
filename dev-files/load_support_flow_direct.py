#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cargar el flujo de soporte técnico directamente en SQLite
"""
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

def load_technical_support_flow():
    """
    Carga el flujo completo de soporte técnico
    """
    print("📝 Cargando flujo de soporte técnico...")
    
    # Ruta de la base de datos
    db_path = Path("instance/whatsapp_test.db")
    
    if not db_path.exists():
        print("❌ Base de datos no encontrada. Ejecuta create_tables_direct.py primero.")
        return False
    
    # Conectar a SQLite
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Leer el flujo de soporte técnico
        flow_file = Path("static/rivescript/technical_support_flow.rive")
        
        if flow_file.exists():
            with open(flow_file, 'r', encoding='utf-8') as f:
                technical_flow_content = f.read()
            print("✅ Archivo de flujo técnico leído correctamente")
        else:
            # Crear el flujo completo si no existe
            technical_flow_content = """! version = 2.0

// Flujo completo de soporte técnico
> topic random

// Triggers principales para activar soporte técnico
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

+ [*] (soporte|support|help|ayuda) [*]
- Te ayudo con soporte técnico.
- Escribe "soporte tecnico" para ver todas las opciones disponibles.

// Opción 1: Problemas de conexión
+ [*] (1|uno|conexion|conexión|internet|red|wifi) [*]
- **Problemas de Conexión** 🌐
- Vamos a revisar tu conectividad paso a paso:
- 
- 1. Verifica que tu WiFi esté conectado
- 2. Reinicia tu router (desconéctalo 30 segundos)
- 3. Prueba con datos móviles
- 
- ¿Funcionó la solución? Responde "si" o "no"

// Opción 2: Errores de aplicación  
+ [*] (2|dos|error|errores|aplicacion|aplicación|app|falla) [*]
- **Errores de Aplicación** ⚠️
- Te ayudo a diagnosticar el problema:
-
- 1. Cierra completamente la aplicación
- 2. Reinicia tu dispositivo
- 3. Abre la aplicación nuevamente
-
- Si persiste el error, describe qué mensaje aparece.

// Opción 3: Problemas de rendimiento
+ [*] (3|tres|lento|rendimiento|performance|velocidad) [*]
- **Problemas de Rendimiento** ⚡
- Optimicemos tu experiencia:
-
- 1. Libera espacio en tu dispositivo
- 2. Cierra aplicaciones en segundo plano  
- 3. Actualiza la aplicación
-
- ¿Notas mejora en la velocidad?

// Opción 4: Configuración de cuenta
+ [*] (4|cuatro|cuenta|perfil|configuracion|configuración|ajustes) [*]
- **Configuración de Cuenta** ⚙️
- Te ayudo con la configuración:
-
- • Cambio de contraseña
- • Actualización de datos
- • Configuración de privacidad  
- • Sincronización
-
- ¿Qué específicamente necesitas configurar?

// Opción 5: Hablar con técnico
+ [*] (5|cinco|tecnico|técnico|humano|persona|agente) [*]
- **Conexión con Técnico** 👨‍💻
- Te voy a conectar con nuestro equipo técnico.
-
- **Horario de atención:**
- • Lunes a Viernes: 8:00 AM - 6:00 PM
- • Sábados: 9:00 AM - 2:00 PM
-
- Un técnico te contactará en breve.
- **Ticket:** #{random}100-500{/random}

// Respuestas de seguimiento
+ (si|sí|yes|funciona|funcionó|resuelto)
- ¡Excelente! 😊 Me alegra que haya funcionado.
- 
- Si necesitas más ayuda, escribe "soporte tecnico" para volver al menú principal.
- 
- ¡Que tengas un gran día!

+ (no|nada|sigue|persiste|continua|continúa)
- Entiendo que el problema persiste. 😔
-
- Vamos a intentar otras opciones:
- • Reinstala la aplicación
- • Contacta soporte técnico (opción 5)
- • Verifica actualizaciones del sistema
-
- ¿Te gustaría que te conecte con un técnico especializado?

+ (gracias|thanks|ok|vale|perfecto)
- ¡De nada! 😊 Me alegra haberte ayudado.
-
- Recuerda que estoy aquí siempre que me necesites.
- Escribe "soporte tecnico" para volver al menú principal.

+ (menu|menú|volver|regresar|menu principal)
- Te llevo de vuelta al menú principal:
-
- 1️⃣ Problemas de conexión
- 2️⃣ Errores de la aplicación
- 3️⃣ Problemas de rendimiento  
- 4️⃣ Configuración de cuenta
- 5️⃣ Hablar con un técnico
-
- ¿En qué más puedo ayudarte?

< topic"""
            print("✅ Flujo técnico creado desde template")
        
        # Generar ID único para el flujo
        flow_id = str(uuid.uuid4())
        
        # Insertar el flujo en la base de datos
        cursor.execute("""
        INSERT OR REPLACE INTO conversation_flows 
        (id, name, description, rivescript_content, is_active, is_default, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flow_id,
            "Soporte Técnico Completo",
            "Flujo completo de soporte técnico con 5 opciones principales",
            technical_flow_content,
            1,  # is_active
            0,  # is_default (no es el por defecto)
            2,  # priority
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print(f"✅ Flujo de soporte técnico cargado con ID: {flow_id}")
        
        # Verificar que se insertó correctamente
        cursor.execute("SELECT COUNT(*) FROM conversation_flows WHERE name LIKE '%Soporte%'")
        count = cursor.fetchone()[0]
        
        print(f"📊 Total de flujos de soporte: {count}")
        
        # Mostrar todos los flujos
        cursor.execute("SELECT name, is_active, priority FROM conversation_flows ORDER BY priority")
        flows = cursor.fetchall()
        
        print("\n📋 Flujos disponibles:")
        for i, (name, active, priority) in enumerate(flows, 1):
            status = "✅" if active else "❌"
            print(f"  {i}. {status} {name} (prioridad: {priority})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    if load_technical_support_flow():
        print("\n🎉 ¡Flujo de soporte técnico cargado exitosamente!")
        print("\n💬 Ahora puedes probar en el simulador:")
        print("   • http://localhost:5001/chat")
        print("   • Escribe: 'soporte tecnico'")
        print("   • Prueba las opciones 1-5")
    else:
        print("\n⚠️ Error cargando el flujo de soporte técnico.")
