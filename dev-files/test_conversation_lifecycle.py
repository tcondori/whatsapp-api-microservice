#!/usr/bin/env python
"""
Prueba para verificar el manejo de ciclo de vida de conversaciones
Analiza qué pasa cuando un usuario deja una conversación y los controles de cierre
"""

from app import create_app
from database.models import ConversationContext, ChatbotInteraction
from database.connection import db
from datetime import datetime, timedelta

# Importar con manejo de errores
try:
    from app.repositories.conversation_repository import ConversationRepository
    CONV_REPO_AVAILABLE = True
except ImportError:
    CONV_REPO_AVAILABLE = False
    print("⚠️  ConversationRepository no disponible - usando consultas directas")

try:
    from app.services.chatbot_service_test import ChatbotService
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    print("⚠️  ChatbotService no disponible")

def test_conversation_lifecycle():
    """Prueba el ciclo de vida completo de una conversación"""
    
    print("="*70)
    print("🔄 PRUEBA DE CICLO DE VIDA DE CONVERSACIONES")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        test_phone = "595987000123"
        
        # Test 1: Estado inicial - sin conversación
        print("\n📱 TEST 1: ESTADO INICIAL")
        print("-" * 50)
        test_initial_state(test_phone)
        
        # Test 2: Inicio de conversación
        print("\n🗨️  TEST 2: INICIO DE CONVERSACIÓN")
        print("-" * 50)
        test_conversation_start(test_phone)
        
        # Test 3: Conversación activa
        print("\n💬 TEST 3: CONVERSACIÓN ACTIVA")
        print("-" * 50)
        test_active_conversation(test_phone)
        
        # Test 4: Conversación abandonada (timeout)
        print("\n⏰ TEST 4: CONVERSACIÓN ABANDONADA (TIMEOUT)")
        print("-" * 50)
        test_conversation_timeout(test_phone)
        
        # Test 5: Limpieza de conversaciones antiguas
        print("\n🧹 TEST 5: LIMPIEZA DE CONVERSACIONES ANTIGUAS")
        print("-" * 50)
        test_conversation_cleanup()
        
        # Test 6: Reinicio de conversación
        print("\n🔄 TEST 6: REINICIO DE CONVERSACIÓN")
        print("-" * 50)
        test_conversation_restart(test_phone)
        
        print("\n" + "="*70)
        print("📊 RESUMEN DE ANÁLISIS")
        print("="*70)
        print_lifecycle_analysis()

def test_initial_state(test_phone):
    """Verifica el estado inicial sin conversación activa"""
    try:
        # Verificar que no hay contexto existente
        context = ConversationContext.query.filter_by(phone_number=test_phone).first()
        
        if context:
            print(f"⚠️  Contexto existente encontrado para {test_phone}")
            print(f"   • Última interacción: {context.last_interaction}")
            print(f"   • Tema actual: {context.current_topic}")
            print(f"   • Sesiones: {context.session_count}")
        else:
            print(f"✅ No hay contexto previo para {test_phone}")
        
        # Verificar interacciones históricas
        interactions = ChatbotInteraction.query.filter_by(phone_number=test_phone).count()
        print(f"📊 Interacciones históricas: {interactions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estado inicial: {e}")
        return False

def test_conversation_start(test_phone):
    """Prueba el inicio de una nueva conversación"""
    try:
        if not CHATBOT_AVAILABLE:
            print("⚠️  ChatbotService no disponible - simulando creación de contexto")
            
            # Crear contexto manualmente
            context = ConversationContext(
                phone_number=test_phone,
                current_topic="greeting",
                last_interaction=datetime.utcnow(),
                session_count=1
            )
            db.session.add(context)
            db.session.commit()
            
            print(f"✅ Contexto simulado creado:")
            print(f"   • Teléfono: {context.phone_number}")
            print(f"   • Última interacción: {context.last_interaction}")
            print(f"   • Sesiones: {context.session_count}")
            return True
        
        chatbot = ChatbotService()
        
        # Enviar primer mensaje
        response = chatbot.process_message(test_phone, "hola")
        
        print(f"📱 Mensaje enviado: 'hola'")
        print(f"🤖 Respuesta: {response.get('response', 'Sin respuesta')[:80]}...")
        print(f"⏱️  Tiempo: {response.get('processing_time_ms', 0)}ms")
        print(f"🎯 Tipo: {response.get('type', 'unknown')}")
        
        # Verificar que se creó contexto
        context = ConversationContext.query.filter_by(phone_number=test_phone).first()
        
        if context:
            print(f"✅ Contexto creado:")
            print(f"   • Teléfono: {context.phone_number}")
            print(f"   • Última interacción: {context.last_interaction}")
            print(f"   • Sesiones: {context.session_count}")
            print(f"   • Flujo ID: {context.flow_id}")
        else:
            print(f"❌ No se creó contexto de conversación")
        
        return True
        
    except Exception as e:
        print(f"❌ Error iniciando conversación: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_active_conversation(test_phone):
    """Prueba una conversación activa con múltiples mensajes"""
    try:
        if not CHATBOT_AVAILABLE:
            print("⚠️  ChatbotService no disponible - simulando conversación activa")
            
            # Simular múltiples interacciones actualizando el contexto
            context = ConversationContext.query.filter_by(phone_number=test_phone).first()
            if context:
                # Simular 4 interacciones
                for i in range(4):
                    context.last_interaction = datetime.utcnow()
                    context.session_count = context.session_count + 1 if i > 1 else context.session_count
                    db.session.commit()
                    
                    # Simular registro de interacción
                    interaction = ChatbotInteraction(
                        phone_number=test_phone,
                        message_in=f"mensaje_test_{i+1}",
                        message_out=f"respuesta_test_{i+1}",
                        response_type="simulated",
                        processing_time_ms=100,
                        flow_id=context.flow_id
                    )
                    db.session.add(interaction)
                    db.session.commit()
                
                print(f"✅ Conversación simulada con 4 mensajes")
                print(f"   • Sesiones totales: {context.session_count}")
                print(f"   • Última interacción: {context.last_interaction}")
                
                # Verificar interacciones registradas
                interactions_count = ChatbotInteraction.query.filter_by(phone_number=test_phone).count()
                print(f"   • Total interacciones registradas: {interactions_count}")
                
                return True
            else:
                print("❌ No hay contexto para simular conversación")
                return False
        
        chatbot = ChatbotService()
        
        test_messages = [
            "ayuda",
            "precio",
            "1", 
            "gracias"
        ]
        
        print(f"💬 Simulando conversación activa con {len(test_messages)} mensajes:")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   {i}. Usuario: '{message}'")
            
            response = chatbot.process_message(test_phone, message)
            
            print(f"      Bot: {response.get('response', 'Sin respuesta')[:60]}...")
            print(f"      Tipo: {response.get('type', 'unknown')} | Tiempo: {response.get('processing_time_ms', 0)}ms")
            
            # Verificar actualización de contexto
            context = ConversationContext.query.filter_by(phone_number=test_phone).first()
            if context:
                print(f"      Última interacción: {context.last_interaction}")
        
        # Verificar estado final del contexto
        context = ConversationContext.query.filter_by(phone_number=test_phone).first()
        if context:
            print(f"\n✅ Estado del contexto después de conversación:")
            print(f"   • Sesiones totales: {context.session_count}")
            print(f"   • Tema actual: {context.current_topic}")
            print(f"   • Variables de contexto: {context.context_data}")
        
        # Verificar interacciones registradas
        interactions_count = ChatbotInteraction.query.filter_by(phone_number=test_phone).count()
        print(f"   • Total interacciones registradas: {interactions_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en conversación activa: {e}")
        return False

def test_conversation_timeout(test_phone):
    """Simula una conversación abandonada y verifica controles de timeout"""
    try:
        from config.default import DefaultConfig
        
        timeout_hours = DefaultConfig.CHATBOT_SESSION_TIMEOUT_HOURS
        print(f"⚙️  Timeout configurado: {timeout_hours} horas")
        
        # Obtener contexto actual
        context = ConversationContext.query.filter_by(phone_number=test_phone).first()
        
        if context:
            # Simular abandono modificando last_interaction para que sea antigua
            old_time = datetime.utcnow() - timedelta(hours=timeout_hours + 1)
            original_session_count = context.session_count
            context.last_interaction = old_time
            db.session.commit()
            
            print(f"🕐 Simulando abandono - última interacción: {old_time}")
            
            if not CHATBOT_AVAILABLE:
                print("⚠️  ChatbotService no disponible - simulando verificación de timeout")
                
                # Simular lógica de verificación de timeout
                time_diff = datetime.utcnow() - context.last_interaction
                is_expired = time_diff.total_seconds() > (timeout_hours * 3600)
                
                print(f"📊 Análisis de timeout:")
                print(f"   • Tiempo transcurrido: {time_diff}")
                print(f"   • Está expirado: {is_expired}")
                
                if is_expired:
                    # Simular reinicio de sesión
                    context.last_interaction = datetime.utcnow()
                    context.session_count = original_session_count + 1
                    context.current_topic = "session_restart"
                    db.session.commit()
                    
                    print(f"🔄 Sesión simulada reiniciada:")
                    print(f"   • Nueva sesión: {context.session_count}")
                    print(f"   • Nueva última interacción: {context.last_interaction}")
                
                return True
            
            # Intentar nueva interacción después del timeout con chatbot real
            chatbot = ChatbotService()
            response = chatbot.process_message(test_phone, "¿sigues ahí?")
            
            print(f"📱 Mensaje después de timeout: '¿sigues ahí?'")
            print(f"🤖 Respuesta: {response.get('response', 'Sin respuesta')[:80]}...")
            
            # Verificar si se reinició la sesión
            context_after = ConversationContext.query.filter_by(phone_number=test_phone).first()
            
            if context_after:
                session_restarted = context_after.session_count > original_session_count
                print(f"🔄 Sesión reiniciada: {session_restarted}")
                
                if session_restarted:
                    print(f"   • Nueva sesión: {context_after.session_count}")
                    print(f"   • Nueva última interacción: {context_after.last_interaction}")
                else:
                    print(f"   • Mismo número de sesión: {context_after.session_count}")
            
            return True
        else:
            print(f"❌ No hay contexto para simular timeout")
            return False
            
    except Exception as e:
        print(f"❌ Error simulando timeout: {e}")
        return False

def test_conversation_cleanup():
    """Prueba el sistema de limpieza de conversaciones antiguas"""
    try:
        # Crear contextos de diferentes fechas para prueba
        test_phones = ["595987000124", "595987000125", "595987000126"]
        
        print(f"🧹 Creando contextos de prueba para limpieza...")
        
        # Crear contextos antiguos
        for i, phone in enumerate(test_phones):
            days_old = [35, 20, 5][i]  # Diferentes antiguedades
            old_date = datetime.utcnow() - timedelta(days=days_old)
            
            context = ConversationContext(
                phone_number=phone,
                current_topic="test_cleanup",
                last_interaction=old_date,
                session_count=1
            )
            
            db.session.add(context)
            print(f"   • {phone}: {days_old} días atrás")
        
        db.session.commit()
        
        # Verificar total antes de limpieza
        total_before = ConversationContext.query.count()
        print(f"📊 Total contextos antes de limpieza: {total_before}")
        
        # Ejecutar limpieza (30 días por defecto)
        if CONV_REPO_AVAILABLE:
            conv_repo = ConversationRepository()
            cleaned_count = conv_repo.clear_old_contexts(days_old=30)
        else:
            # Simular limpieza manual
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_contexts = ConversationContext.query.filter(
                ConversationContext.last_interaction < cutoff_date
            ).all()
            
            cleaned_count = len(old_contexts)
            
            for context in old_contexts:
                db.session.delete(context)
            
            db.session.commit()
        
        print(f"🧽 Contextos limpiados: {cleaned_count}")
        
        # Verificar total después de limpieza
        total_after = ConversationContext.query.count()
        print(f"📊 Total contextos después de limpieza: {total_after}")
        
        # Verificar que solo se limpiaron los antiguos
        remaining_test_contexts = ConversationContext.query.filter(
            ConversationContext.phone_number.in_(test_phones)
        ).all()
        
        print(f"📱 Contextos de prueba restantes:")
        for context in remaining_test_contexts:
            days_diff = (datetime.utcnow() - context.last_interaction).days
            print(f"   • {context.phone_number}: {days_diff} días")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
        return False

def test_conversation_restart(test_phone):
    """Prueba el reinicio de conversación después de limpieza o timeout"""
    try:
        print(f"🔄 Probando reinicio de conversación para {test_phone}")
        
        # Limpiar contexto existente si existe
        existing_context = ConversationContext.query.filter_by(phone_number=test_phone).first()
        if existing_context:
            db.session.delete(existing_context)
            db.session.commit()
            print(f"🗑️  Contexto existente eliminado")
        
        if not CHATBOT_AVAILABLE:
            print("⚠️  ChatbotService no disponible - simulando reinicio")
            
            # Crear nuevo contexto simulado
            new_context = ConversationContext(
                phone_number=test_phone,
                current_topic="restart",
                last_interaction=datetime.utcnow(),
                session_count=1
            )
            db.session.add(new_context)
            db.session.commit()
            
            print(f"✅ Nuevo contexto simulado:")
            print(f"   • Sesión: {new_context.session_count}")
            print(f"   • Creado: {new_context.last_interaction}")
            print(f"   • Tema: {new_context.current_topic}")
            
            return True
        
        # Iniciar nueva conversación con chatbot real
        chatbot = ChatbotService()
        response = chatbot.process_message(test_phone, "Hola de nuevo")
        
        print(f"📱 Nuevo mensaje: 'Hola de nuevo'")
        print(f"🤖 Respuesta: {response.get('response', 'Sin respuesta')[:80]}...")
        
        # Verificar nuevo contexto
        new_context = ConversationContext.query.filter_by(phone_number=test_phone).first()
        
        if new_context:
            print(f"✅ Nuevo contexto creado:")
            print(f"   • Sesión: {new_context.session_count}")
            print(f"   • Creado: {new_context.last_interaction}")
            print(f"   • Flujo ID: {new_context.flow_id}")
        else:
            print(f"❌ No se pudo crear nuevo contexto")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reiniciando conversación: {e}")
        return False

def print_lifecycle_analysis():
    """Imprime análisis completo del ciclo de vida de conversaciones"""
    print("🔍 ANÁLISIS DE CONTROLES DE CICLO DE VIDA:")
    
    # Controles existentes
    print("\n✅ CONTROLES IMPLEMENTADOS:")
    print("   • ConversationContext.last_interaction - Timestamp de última actividad")
    print("   • CHATBOT_SESSION_TIMEOUT_HOURS - Configuración de timeout (24h por defecto)")
    print("   • ConversationRepository.clear_old_contexts() - Limpieza automática")
    print("   • session_count - Contador de sesiones por usuario")
    
    # Controles faltantes
    print("\n⚠️  CONTROLES FALTANTES IDENTIFICADOS:")
    print("   • ❌ Sin verificación automática de timeout en process_message()")
    print("   • ❌ Sin cierre explícito de conversación cuando usuario dice 'adiós'")
    print("   • ❌ Sin tarea programada (cron/celery) para limpieza automática")
    print("   • ❌ Sin notificación o logging cuando conversación expira")
    
    # Estado actual
    print("\n📊 ESTADO ACTUAL:")
    try:
        total_contexts = ConversationContext.query.count()
        active_contexts = ConversationContext.query.filter(
            ConversationContext.last_interaction > datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        print(f"   • Total contextos en BD: {total_contexts}")
        print(f"   • Contextos activos (últimas 24h): {active_contexts}")
        print(f"   • Contextos inactivos: {total_contexts - active_contexts}")
        
    except Exception as e:
        print(f"   • Error consultando estado: {e}")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    print("   • Implementar verificación de timeout en ChatbotService")
    print("   • Agregar comando explícito de cierre ('cerrar conversación')")
    print("   • Configurar tarea programada para limpieza diaria")
    print("   • Implementar logging de eventos de ciclo de vida")
    print("   • Considerar diferentes timeouts por tipo de conversación")

if __name__ == "__main__":
    test_conversation_lifecycle()
