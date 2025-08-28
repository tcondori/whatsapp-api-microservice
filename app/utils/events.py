"""
Sistema de eventos para el microservicio WhatsApp API
Implementa patrón Observer para desacoplar componentes y facilitar el logging
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import weakref
import threading


class EventType(Enum):
    """
    Tipos de eventos del sistema WhatsApp API
    """
    # Eventos de mensajes
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received" 
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"
    MESSAGE_FAILED = "message_failed"
    
    # Eventos de webhook
    WEBHOOK_RECEIVED = "webhook_received"
    WEBHOOK_PROCESSED = "webhook_processed"
    WEBHOOK_FAILED = "webhook_failed"
    
    # Eventos de API
    API_REQUEST_STARTED = "api_request_started"
    API_REQUEST_COMPLETED = "api_request_completed"
    API_REQUEST_FAILED = "api_request_failed"
    API_RATE_LIMIT_HIT = "api_rate_limit_hit"
    
    # Eventos de sistema
    SYSTEM_STARTED = "system_started"
    SYSTEM_SHUTDOWN = "system_shutdown"
    HEALTH_CHECK = "health_check"
    
    # Eventos de seguridad
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILED = "auth_failed"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Eventos de base de datos
    DB_CONNECTION_ESTABLISHED = "db_connection_established"
    DB_CONNECTION_FAILED = "db_connection_failed"
    DB_QUERY_EXECUTED = "db_query_executed"
    DB_QUERY_FAILED = "db_query_failed"


@dataclass
class Event:
    """
    Estructura de datos para eventos del sistema
    """
    event_type: EventType
    timestamp: datetime
    source: str  # Componente que genera el evento
    data: Dict[str, Any]
    correlation_id: Optional[str] = None  # Para rastrear eventos relacionados
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el evento a diccionario para logging
        """
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'data': self.data,
            'correlation_id': self.correlation_id,
            'user_id': self.user_id,
            'session_id': self.session_id
        }


class EventHandler:
    """
    Interfaz base para manejadores de eventos
    """
    
    async def handle(self, event: Event) -> None:
        """
        Procesa un evento del sistema
        
        Args:
            event: Evento a procesar
        """
        raise NotImplementedError


class LoggingEventHandler(EventHandler):
    """
    Manejador de eventos que registra todos los eventos en el sistema de logging
    """
    
    def __init__(self):
        from app.utils.logger import WhatsAppLogger, EventLogger
        self.event_logger = EventLogger()
    
    async def handle(self, event: Event) -> None:
        """
        Registra el evento en el sistema de logging
        """
        log_message = f"Event: {event.event_type.value} from {event.source}"
        
        # Determinar nivel de log según tipo de evento
        if event.event_type in [EventType.MESSAGE_FAILED, EventType.WEBHOOK_FAILED, 
                               EventType.API_REQUEST_FAILED, EventType.AUTHENTICATION_FAILED]:
            self.event_logger.logger.error(log_message, extra={'extra_data': event.to_dict()})
        elif event.event_type in [EventType.UNAUTHORIZED_ACCESS, EventType.RATE_LIMIT_EXCEEDED]:
            self.event_logger.logger.warning(log_message, extra={'extra_data': event.to_dict()})
        else:
            self.event_logger.logger.info(log_message, extra={'extra_data': event.to_dict()})


class MetricsEventHandler(EventHandler):
    """
    Manejador de eventos que recolecta métricas del sistema
    """
    
    def __init__(self):
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'webhooks_processed': 0,
            'api_calls': 0,
            'errors': 0
        }
        self._lock = threading.Lock()
    
    async def handle(self, event: Event) -> None:
        """
        Actualiza métricas basadas en el evento
        """
        with self._lock:
            if event.event_type == EventType.MESSAGE_SENT:
                self.metrics['messages_sent'] += 1
            elif event.event_type == EventType.MESSAGE_RECEIVED:
                self.metrics['messages_received'] += 1
            elif event.event_type == EventType.WEBHOOK_PROCESSED:
                self.metrics['webhooks_processed'] += 1
            elif event.event_type in [EventType.API_REQUEST_COMPLETED, EventType.API_REQUEST_FAILED]:
                self.metrics['api_calls'] += 1
            
            # Contar errores
            if event.event_type.value.endswith('_failed'):
                self.metrics['errors'] += 1
    
    def get_metrics(self) -> Dict[str, int]:
        """
        Obtiene las métricas actuales del sistema
        """
        with self._lock:
            return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """
        Reinicia las métricas del sistema
        """
        with self._lock:
            for key in self.metrics:
                self.metrics[key] = 0


class EventBus:
    """
    Bus de eventos centralizado para el sistema WhatsApp API
    Implementa patrón Observer con soporte asíncrono
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_queue = asyncio.Queue()
        self._processing = False
        self._weak_refs = weakref.WeakSet()
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Suscribe un manejador a un tipo específico de evento
        
        Args:
            event_type: Tipo de evento a escuchar
            handler: Manejador que procesará el evento
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        self._weak_refs.add(handler)
    
    def subscribe_global(self, handler: EventHandler) -> None:
        """
        Suscribe un manejador a todos los tipos de eventos
        
        Args:
            handler: Manejador que procesará todos los eventos
        """
        self._global_handlers.append(handler)
        self._weak_refs.add(handler)
    
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Desuscribe un manejador de un tipo de evento
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    def unsubscribe_global(self, handler: EventHandler) -> None:
        """
        Desuscribe un manejador global
        """
        if handler in self._global_handlers:
            self._global_handlers.remove(handler)
    
    async def publish(self, event: Event) -> None:
        """
        Publica un evento en el bus
        
        Args:
            event: Evento a publicar
        """
        await self._event_queue.put(event)
        
        # Iniciar procesamiento si no está en curso
        if not self._processing:
            asyncio.create_task(self._process_events())
    
    async def publish_sync(self, event: Event) -> None:
        """
        Publica un evento y espera a que sea procesado por todos los manejadores
        """
        handlers = self._get_handlers_for_event(event.event_type)
        
        # Ejecutar todos los manejadores
        tasks = []
        for handler in handlers:
            tasks.append(handler.handle(event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_events(self) -> None:
        """
        Procesa eventos de forma asíncrona desde la cola
        """
        self._processing = True
        
        try:
            while True:
                try:
                    # Esperar por un evento con timeout
                    event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                    
                    # Obtener manejadores para este evento
                    handlers = self._get_handlers_for_event(event.event_type)
                    
                    # Ejecutar manejadores de forma concurrente
                    if handlers:
                        tasks = [handler.handle(event) for handler in handlers]
                        await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Marcar tarea como completada
                    self._event_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # No hay más eventos, salir del bucle
                    break
                except Exception as e:
                    # Log error pero continuar procesando
                    from app.utils.logger import WhatsAppLogger
                    logger = WhatsAppLogger.get_logger('event_bus')
                    logger.error(f"Error processing event: {str(e)}", exc_info=True)
        finally:
            self._processing = False
    
    def _get_handlers_for_event(self, event_type: EventType) -> List[EventHandler]:
        """
        Obtiene todos los manejadores para un tipo de evento específico
        """
        handlers = []
        
        # Agregar manejadores específicos del tipo de evento
        if event_type in self._handlers:
            handlers.extend(self._handlers[event_type])
        
        # Agregar manejadores globales
        handlers.extend(self._global_handlers)
        
        return handlers


# Instancia global del bus de eventos
event_bus = EventBus()


class EventEmitter:
    """
    Clase base para componentes que emiten eventos
    """
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    async def emit_event(self, event_type: EventType, data: Dict[str, Any],
                        correlation_id: str = None, user_id: str = None,
                        session_id: str = None) -> None:
        """
        Emite un evento al bus de eventos
        """
        event = Event(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source=self.source_name,
            data=data,
            correlation_id=correlation_id,
            user_id=user_id,
            session_id=session_id
        )
        
        await event_bus.publish(event)
    
    def emit_event_sync(self, event_type: EventType, data: Dict[str, Any],
                       correlation_id: str = None, user_id: str = None,
                       session_id: str = None) -> None:
        """
        Emite un evento de forma síncrona (sin await)
        """
        event = Event(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source=self.source_name,
            data=data,
            correlation_id=correlation_id,
            user_id=user_id,
            session_id=session_id
        )
        
        # Programar para ejecución asíncrona
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(event_bus.publish(event))
        except RuntimeError:
            # No hay loop activo, crear uno nuevo para esta tarea
            asyncio.create_task(event_bus.publish(event))


def setup_default_event_handlers():
    """
    Configura los manejadores de eventos por defecto del sistema
    """
    # Configurar manejador de logging global
    logging_handler = LoggingEventHandler()
    event_bus.subscribe_global(logging_handler)
    
    # Configurar manejador de métricas
    metrics_handler = MetricsEventHandler()
    event_bus.subscribe_global(metrics_handler)
    
    return {
        'logging_handler': logging_handler,
        'metrics_handler': metrics_handler
    }


# Helper functions para eventos comunes
async def log_whatsapp_message_sent(phone_number: str, message_id: str, 
                                   message_type: str, template_name: str = None):
    """
    Helper para registrar mensaje enviado
    """
    await event_bus.publish(Event(
        event_type=EventType.MESSAGE_SENT,
        timestamp=datetime.utcnow(),
        source='whatsapp_api',
        data={
            'phone_number': phone_number,
            'message_id': message_id,
            'message_type': message_type,
            'template_name': template_name
        }
    ))


async def log_webhook_received(webhook_type: str, payload: Dict[str, Any]):
    """
    Helper para registrar webhook recibido
    """
    await event_bus.publish(Event(
        event_type=EventType.WEBHOOK_RECEIVED,
        timestamp=datetime.utcnow(),
        source='webhook_handler',
        data={
            'webhook_type': webhook_type,
            'payload_size': len(str(payload))
        }
    ))


async def log_api_performance(endpoint: str, method: str, response_time_ms: float,
                            status_code: int):
    """
    Helper para registrar performance de API
    """
    await event_bus.publish(Event(
        event_type=EventType.API_REQUEST_COMPLETED,
        timestamp=datetime.utcnow(),
        source='api_layer',
        data={
            'endpoint': endpoint,
            'method': method,
            'response_time_ms': response_time_ms,
            'status_code': status_code
        }
    ))
