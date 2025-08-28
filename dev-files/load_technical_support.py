"""
Script para cargar flujo de Soporte Técnico corregido a PostgreSQL
Modo agente: Ejecuta automáticamente la carga y verificación
"""
from app import create_app
from app.repositories.flow_repository import FlowRepository
import uuid
from datetime import datetime

def cargar_flujo_soporte_tecnico():
    """
    Carga flujo de soporte técnico con formato RiveScript correcto
    """
    contenido_soporte = """// Flujo de Soporte Técnico
// Manejo de consultas técnicas y troubleshooting

! version = 2.0

// Activadores principales
+ [*] soporte [*]
- Hola, soy el asistente de Soporte Técnico 🛠️
^ ¿Con qué puedo ayudarte hoy?
^ 1️⃣ Problemas de conexión
^ 2️⃣ Errores de la aplicación
^ 3️⃣ Problemas de rendimiento
^ 4️⃣ Configuración de cuenta
^ 5️⃣ Hablar con un técnico
^ Escribe el número o describe tu problema.

+ [*] (ayuda|help|problema|error|falla) [*]
@ soporte

// Opciones del menú
+ (1|uno|conexion|internet|red|wifi)
- 🌐 Problemas de Conexión
^ Vamos a solucionar paso a paso:
^ Paso 1: Verifica tu conexión a internet
^ ¿Puedes abrir otras páginas web?
^ ¿Otros dispositivos se conectan bien?
^ Paso 2: Reinicia tu router
^ Desconecta 30 segundos y reconecta
^ ¿Ya probaste estos pasos? Responde sí o no.

+ (2|dos|aplicacion|app|programa|software)
- 🐛 Errores de Aplicación
^ Te ayudo a identificar el problema:
^ ¿Qué error específico ves? Describe el mensaje
^ ¿Cuándo ocurre? Al abrir o usar una función
^ ¿En qué dispositivo? Móvil, tablet, computadora
^ También puedes probar:
^ • Cerrar y abrir la app
^ • Reiniciar el dispositivo
^ • Verificar actualizaciones
^ Cuéntame más detalles del error.

+ (3|tres|lento|rendimiento|demora|performance)
- ⚡ Problemas de Rendimiento
^ Vamos a acelerar tu experiencia:
^ Diagnóstico rápido:
^ ¿La lentitud es general o en funciones específicas?
^ ¿Cuánto tiempo lleva cargando?
^ ¿Tienes muchas aplicaciones abiertas?
^ Soluciones inmediatas:
^ • Reiniciar la aplicación
^ • Limpiar caché del navegador
^ • Liberar espacio de almacenamiento
^ • Verificar velocidad de internet
^ ¿Quieres que te guíe con alguna solución?

+ (4|cuatro|cuenta|configuracion|perfil|usuario)
- ⚙️ Configuración de Cuenta
^ ¿Qué necesitas configurar?
^ 🔐 Seguridad: cambiar contraseña, 2FA, sesiones
^ 👤 Perfil: datos personales, foto, notificaciones
^ 💳 Facturación: métodos de pago, historial, plan
^ Selecciona una categoría o describe qué quieres hacer.

+ (5|cinco|tecnico|humano|agente|especialista)
- 🙋‍♂️ Conexión con Técnico Especializado
^ Te voy a conectar con nuestro equipo técnico.
^ Antes de transferirte, necesito:
^ • Descripción breve del problema
^ • Tu número de cliente si lo tienes
^ • Urgencia: Alta, Media o Baja
^ Horarios de atención:
^ Lunes a Viernes: 8:00 - 18:00
^ Sábados: 9:00 - 14:00
^ Por favor proporciona la información solicitada.

// Respuestas de seguimiento
+ (si|sí|funciona|solucionado|probé)
- ¡Excelente! 🎉 Me alegra que haya funcionado.
^ ¿Necesitas ayuda con algo más?
^ • Otro problema técnico
^ • Consejos de prevención
^ • Volver al menú principal
^ O simplemente escribe gracias si terminamos.

+ (no|persiste|sigue igual|aun no)
- Entiendo, vamos a intentar otras soluciones más específicas.
^ Escalación del problema:
^ 🔧 Te voy a dar pasos más detallados
^ 📞 O puedo conectarte con un técnico especializado
^ Para darte mejor ayuda, necesito saber:
^ • ¿Qué dispositivo o sistema usas exactamente?
^ • ¿El problema comenzó recientemente?
^ • ¿Hay algún mensaje de error específico?
^ Comparte estos detalles conmigo.

// Casos comunes FAQ
+ [*] (olvide|contraseña|no puedo entrar|password) [*]
- 🔐 Recuperación de Contraseña
^ No te preocupes, es muy común.
^ Método 1: Email
^ • Ve a la página de login
^ • Haz clic en ¿Olvidaste tu contraseña?
^ • Ingresa tu email registrado
^ • Revisa tu bandeja de entrada y spam
^ Método 2: SMS
^ • Si tienes teléfono registrado
^ • Selecciona Recibir código por SMS
^ ¿No recibes el email? Puede tomar hasta 10 minutos.
^ ¿Qué método prefieres intentar?

+ [*] (lento|demora|loading|cargando) [*]
- ⏱️ Problema de Velocidad Detectado
^ Vamos a acelerar las cosas:
^ Diagnóstico rápido:
^ ¿Qué tan lento? más de 30 seg, 1-2 min, más de 5 min
^ ¿En qué momento? login, carga página, subir archivo
^ Soluciones por orden de efectividad:
^ 1️⃣ Limpiar caché del navegador
^ 2️⃣ Cerrar otras pestañas o apps
^ 3️⃣ Verificar velocidad de internet
^ 4️⃣ Cambiar de navegador temporalmente
^ ¿Empezamos con el paso 1?

+ [*] (quiero hablar|transferir|urgente|escalار) [*]
- 🚀 Transferencia Inmediata
^ Entiendo que necesitas atención personalizada.
^ Tu caso ha sido escalado con prioridad.
^ Información que se enviará:
^ • Problema reportado
^ • Soluciones intentadas
^ • Hora de solicitud
^ Tiempo estimado de contacto: 5-15 minutos
^ Un técnico te contactará pronto.

// Cierre y agradecimiento
+ [*] (gracias|resuelto|perfecto|excelente) [*]
- ¡De nada! 😊 Me alegra haber podido ayudarte.
^ Resumen de tu sesión de soporte:
^ ✅ Problema atendido
^ ✅ Solución proporcionada
^ ✅ Seguimiento completado
^ ¿Te gustaría?
^ 📧 Recibir un email con el resumen
^ ⭐ Calificar la atención recibida
^ 🔄 Volver al menú principal
^ ¡Que tengas un excelente día!

// Navegación
+ (menu|inicio|volver|principal)
- Te llevo de vuelta al menú principal...
^ ¿En qué puedo ayudarte?
^ 💬 Conversación general
^ 💰 Ventas y precios
^ 🛠️ Soporte técnico
^ 👥 Recursos humanos
^ 💳 Facturación
^ Selecciona un área o escribe tu consulta.
"""

    print("🤖 Iniciando carga del flujo de Soporte Técnico...")
    
    app = create_app()
    with app.app_context():
        repo = FlowRepository()
        
        # Buscar flujo existente
        existing_flows = repo.get_all_flows()
        soporte_flow = None
        
        for flow in existing_flows:
            if 'soporte' in flow.name.lower() or 'técnico' in flow.name.lower():
                soporte_flow = flow
                break
        
        if soporte_flow:
            # Actualizar flujo existente
            print(f"📝 Actualizando flujo existente: {soporte_flow.name}")
            updates = {
                'rivescript_content': contenido_soporte,
                'name': 'Soporte Técnico',
                'description': 'Flujo para consultas de soporte técnico y troubleshooting',
                'is_active': True,
                'priority': 5,
                'updated_at': datetime.utcnow()
            }
            updated_success = repo.update_flow(soporte_flow.id, updates)
            
            if updated_success:
                # Obtener el flujo actualizado
                updated_flow = repo.get_by_id(soporte_flow.id)
                print(f"✅ Flujo actualizado exitosamente")
                print(f"   ID: {updated_flow.id}")
                print(f"   Nombre: {updated_flow.name}")
                print(f"   Estado: {'Activo' if updated_flow.is_active else 'Inactivo'}")
                print(f"   Líneas de código: {len(updated_flow.rivescript_content.splitlines())}")
                return updated_flow
            else:
                print("❌ Error actualizando el flujo")
                return None
        else:
            # Crear nuevo flujo
            print("🆕 Creando nuevo flujo de Soporte Técnico...")
            flow_data = {
                'id': str(uuid.uuid4()),
                'name': 'Soporte Técnico',
                'description': 'Flujo para consultas de soporte técnico y troubleshooting',
                'rivescript_content': contenido_soporte,
                'is_active': True,
                'priority': 5,
                'fallback_to_llm': False,
                'max_context_messages': 10,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            new_flow = repo.create_flow(flow_data)
            
            if new_flow:
                print(f"✅ Nuevo flujo creado exitosamente")
                print(f"   ID: {new_flow.id}")
                print(f"   Nombre: {new_flow.name}")
                print(f"   Estado: {'Activo' if new_flow.is_active else 'Inactivo'}")
                print(f"   Líneas de código: {len(new_flow.rivescript_content.splitlines())}")
                return new_flow
        
        print("❌ Error: No se pudo crear o actualizar el flujo")
        return None

def verificar_flujos_disponibles():
    """
    Verifica todos los flujos disponibles en la base de datos
    """
    print("\n📊 Verificando flujos disponibles en PostgreSQL...")
    print("-" * 50)
    
    app = create_app()
    with app.app_context():
        repo = FlowRepository()
        flows = repo.get_all_flows()
        
        if not flows:
            print("⚠️  No hay flujos en la base de datos")
            return []
        
        for i, flow in enumerate(flows, 1):
            status = '🟢 Activo' if flow.is_active else '🔴 Inactivo'
            print(f"{i}. {flow.name}")
            print(f"   ID: {flow.id}")
            print(f"   Estado: {status}")
            print(f"   Prioridad: {flow.priority}")
            print(f"   Descripción: {flow.description or 'Sin descripción'}")
            print(f"   Líneas: {len(flow.rivescript_content.splitlines())}")
            print()
        
        print(f"✅ Total: {len(flows)} flujos disponibles")
        return flows

def probar_respuestas_bot():
    """
    Prueba las respuestas del bot con mensajes de ejemplo
    """
    print("\n🧪 Probando respuestas del bot...")
    print("-" * 40)
    
    app = create_app()
    with app.app_context():
        try:
            from app.services.rivescript_service import RiveScriptService
            rivescript_service = RiveScriptService()
            
            # Mensajes de prueba
            test_messages = [
                'soporte',
                'ayuda', 
                '1',
                'contraseña',
                'sí',
                'gracias'
            ]
            
            print("🤖 Simulación de conversación:")
            print("=" * 30)
            
            for msg in test_messages:
                try:
                    response_data = rivescript_service.get_response('test_user_123', msg)
                    
                    if response_data and 'response' in response_data:
                        response = response_data['response']
                        print(f"👤 Usuario: {msg}")
                        
                        # Limitar longitud de respuesta para visualización
                        if len(response) > 150:
                            response_preview = response[:150] + "..."
                        else:
                            response_preview = response
                        
                        print(f"🤖 Bot: {response_preview}")
                        print("-" * 30)
                    else:
                        print(f"👤 Usuario: {msg}")
                        print(f"🤖 Bot: [Sin respuesta - revisar configuración]")
                        print("-" * 30)
                    
                except Exception as e:
                    print(f"❌ Error con mensaje '{msg}': {e}")
                    print("-" * 30)
            
            print("✅ Pruebas de conversación completadas")
            
        except Exception as e:
            print(f"❌ Error general en pruebas: {e}")

def main():
    """
    Función principal del agente - Ejecuta todo el proceso
    """
    print("🚀 AGENTE DE IMPLEMENTACIÓN DE FLUJOS RIVESCRIPT")
    print("=" * 55)
    
    # Paso 1: Cargar flujo de soporte
    flujo = cargar_flujo_soporte_tecnico()
    
    if not flujo:
        print("💥 Error crítico: No se pudo cargar el flujo de soporte")
        return False
    
    # Paso 2: Verificar todos los flujos
    flujos = verificar_flujos_disponibles()
    
    # Paso 3: Probar respuestas del bot
    probar_respuestas_bot()
    
    print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 40)
    print("📋 Resumen:")
    print(f"✅ Flujo de Soporte Técnico: Cargado")
    print(f"✅ Total de flujos en BD: {len(flujos)}")
    print(f"✅ Pruebas del bot: Realizadas")
    print("\n🌐 Accede a las interfaces:")
    print("• Dashboard: http://localhost:5001/rivescript/")
    print("• Simulador: http://localhost:5001/rivescript/simulator")
    print("• Editor: http://localhost:5001/rivescript/editor")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💥 El proceso falló. Revisa los errores arriba.")
        exit(1)
    else:
        print("\n🚀 ¡Listo para usar!")
