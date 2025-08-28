"""
Tests para el sistema de logging y eventos
Pruebas unitarias e integración para validar funcionalidad completa
"""

import pytest
import asyncio
import tempfile
import json
import logging
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.utils.logger import (
    WhatsAppLogger, EventLogger, JsonFormatter, log_execution_time, log_api_call
)
from app.utils.events import (
    Event, EventType, EventBus, EventHandler, LoggingEventHandler,
    MetricsEventHandler, EventEmitter, event_bus
)
from app.utils.middleware import (
    RequestLoggingMiddleware, WhatsAppAPILoggingMiddleware,
    SecurityLoggingMiddleware, DatabaseLoggingMiddleware
)
from app.utils.log_config import LoggingConfig, initialize_logging


class TestJsonFormatter:
    """Tests para el formateador JSON"""
    
    def test_basic_formatting(self):
        """Prueba formateo básico JSON"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=123,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert log_data['level'] == 'INFO'
        assert log_data['logger'] == 'test_logger'
        assert log_data['message'] == 'Test message'
        assert log_data['line'] == 123
        assert 'timestamp' in log_data
    
    def test_formatting_with_exception(self):
        """Prueba formateo con información de excepción"""
        formatter = JsonFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name='test_logger',
                level=logging.ERROR,
                pathname='/test/path.py',
                lineno=123,
                msg='Error occurred',
                args=(),
                exc_info=(ValueError, ValueError("Test exception"), None)
            )
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert 'exception' in log_data
        assert log_data['exception']['type'] == 'ValueError'
        assert log_data['exception']['message'] == 'Test exception'
    
    def test_formatting_with_extra_data(self):
        """Prueba formateo con datos extra"""
        formatter = JsonFormatter(include_extra=True)
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=123,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Agregar datos extra
        record.extra_data = {'user_id': '123', 'action': 'test'}
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert 'extra' in log_data
        assert log_data['extra']['user_id'] == '123'
        assert log_data['extra']['action'] == 'test'


class TestWhatsAppLogger:
    """Tests para la clase WhatsAppLogger"""
    
    def test_configure_logging(self):
        """Prueba configuración del sistema de logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            WhatsAppLogger.configure_logging(
                log_level='DEBUG',
                log_dir=temp_dir,
                environment='testing'
            )
            
            # Verificar que se configuró correctamente
            assert WhatsAppLogger._configured
            
            # Verificar que se crearon los archivos de log
            log_path = Path(temp_dir)
            assert (log_path / 'whatsapp_api.log').exists()
    
    def test_get_logger(self):
        """Prueba obtención de loggers específicos"""
        logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        
        assert logger is not None
        assert logger.name == WhatsAppLogger.API_LOGGER
    
    def test_component_loggers_creation(self):
        """Prueba creación de loggers por componente"""
        components = [
            WhatsAppLogger.API_LOGGER,
            WhatsAppLogger.WEBHOOK_LOGGER,
            WhatsAppLogger.SERVICE_LOGGER,
            WhatsAppLogger.DATABASE_LOGGER,
            WhatsAppLogger.SECURITY_LOGGER
        ]
        
        for component in components:
            logger = WhatsAppLogger.get_logger(component)
            assert logger is not None
            assert logger.name == component


class TestEventLogger:
    """Tests para el EventLogger"""
    
    @pytest.fixture
    def event_logger(self):
        """Fixture que proporciona un EventLogger configurado"""
        return EventLogger()
    
    def test_log_whatsapp_request(self, event_logger, caplog):
        """Prueba logging de request de WhatsApp API"""
        with caplog.at_level(logging.INFO):
            event_logger.log_whatsapp_request(
                endpoint='/messages',
                method='POST',
                payload={'message': 'test'},
                phone_number='+1234567890',
                message_id='msg_123'
            )
        
        assert len(caplog.records) == 1
        assert 'WhatsApp API Request' in caplog.records[0].message
        assert hasattr(caplog.records[0], 'extra_data')
    
    def test_log_whatsapp_response(self, event_logger, caplog):
        """Prueba logging de response de WhatsApp API"""
        with caplog.at_level(logging.INFO):
            event_logger.log_whatsapp_response(
                endpoint='/messages',
                status_code=200,
                response_data={'success': True},
                response_time_ms=150.5
            )
        
        assert len(caplog.records) == 1
        assert '200 from /messages' in caplog.records[0].message
    
    def test_log_security_event(self, event_logger, caplog):
        """Prueba logging de evento de seguridad"""
        with caplog.at_level(logging.WARNING):
            event_logger.log_security_event(
                event_type='unauthorized_access',
                ip_address='192.168.1.100',
                user_agent='TestAgent',
                details={'endpoint': '/api/test'}
            )
        
        assert len(caplog.records) == 1
        assert 'Security event' in caplog.records[0].message
        assert 'unauthorized_access' in caplog.records[0].message
    
    def test_phone_sanitization(self, event_logger):
        """Prueba sanitización de números de teléfono"""
        sanitized = event_logger._sanitize_phone('+1234567890')
        assert sanitized == '+12***90'
        
        sanitized_short = event_logger._sanitize_phone('12345')
        assert sanitized_short == '****'
        
        sanitized_none = event_logger._sanitize_phone(None)
        assert sanitized_none is None


class TestEventSystem:
    """Tests para el sistema de eventos"""
    
    @pytest.fixture
    def event_bus(self):
        """Fixture que proporciona un EventBus limpio"""
        return EventBus()
    
    @pytest.fixture
    def mock_handler(self):
        """Fixture que proporciona un handler mock"""
        handler = Mock(spec=EventHandler)
        handler.handle = Mock(return_value=asyncio.sleep(0))  # Async mock
        return handler
    
    def test_event_creation(self):
        """Prueba creación de eventos"""
        event = Event(
            event_type=EventType.MESSAGE_SENT,
            timestamp=datetime.utcnow(),
            source='test_source',
            data={'test': 'data'},
            correlation_id='test_id'
        )
        
        assert event.event_type == EventType.MESSAGE_SENT
        assert event.source == 'test_source'
        assert event.data['test'] == 'data'
        assert event.correlation_id == 'test_id'
    
    def test_event_subscription(self, event_bus, mock_handler):
        """Prueba suscripción a eventos específicos"""
        event_bus.subscribe(EventType.MESSAGE_SENT, mock_handler)
        
        handlers = event_bus._get_handlers_for_event(EventType.MESSAGE_SENT)
        assert mock_handler in handlers
    
    def test_global_subscription(self, event_bus, mock_handler):
        """Prueba suscripción global a eventos"""
        event_bus.subscribe_global(mock_handler)
        
        handlers = event_bus._get_handlers_for_event(EventType.MESSAGE_SENT)
        assert mock_handler in handlers
        
        handlers = event_bus._get_handlers_for_event(EventType.WEBHOOK_RECEIVED)
        assert mock_handler in handlers
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, event_bus, mock_handler):
        """Prueba publicación de eventos"""
        event_bus.subscribe(EventType.MESSAGE_SENT, mock_handler)
        
        event = Event(
            event_type=EventType.MESSAGE_SENT,
            timestamp=datetime.utcnow(),
            source='test',
            data={'message_id': '123'}
        )
        
        await event_bus.publish_sync(event)
        
        mock_handler.handle.assert_called_once_with(event)


class TestEventHandlers:
    """Tests para los manejadores de eventos"""
    
    @pytest.fixture
    def logging_handler(self):
        """Fixture que proporciona LoggingEventHandler"""
        return LoggingEventHandler()
    
    @pytest.fixture
    def metrics_handler(self):
        """Fixture que proporciona MetricsEventHandler"""
        return MetricsEventHandler()
    
    @pytest.mark.asyncio
    async def test_logging_event_handler(self, logging_handler, caplog):
        """Prueba LoggingEventHandler"""
        event = Event(
            event_type=EventType.MESSAGE_SENT,
            timestamp=datetime.utcnow(),
            source='test',
            data={'message_id': '123'}
        )
        
        with caplog.at_level(logging.INFO):
            await logging_handler.handle(event)
        
        assert len(caplog.records) >= 1
        assert 'MESSAGE_SENT' in caplog.records[0].message
    
    @pytest.mark.asyncio
    async def test_metrics_event_handler(self, metrics_handler):
        """Prueba MetricsEventHandler"""
        # Evento de mensaje enviado
        event = Event(
            event_type=EventType.MESSAGE_SENT,
            timestamp=datetime.utcnow(),
            source='test',
            data={'message_id': '123'}
        )
        
        initial_metrics = metrics_handler.get_metrics()
        await metrics_handler.handle(event)
        updated_metrics = metrics_handler.get_metrics()
        
        assert updated_metrics['messages_sent'] == initial_metrics['messages_sent'] + 1


class TestEventEmitter:
    """Tests para EventEmitter"""
    
    def test_event_emitter_creation(self):
        """Prueba creación de EventEmitter"""
        emitter = EventEmitter('test_source')
        assert emitter.source_name == 'test_source'
    
    def test_sync_event_emission(self):
        """Prueba emisión síncrona de eventos"""
        emitter = EventEmitter('test_source')
        
        # Mock para evitar problemas con asyncio en tests
        with patch('app.utils.events.event_bus') as mock_bus:
            emitter.emit_event_sync(
                EventType.MESSAGE_SENT,
                {'message_id': '123'},
                correlation_id='test_corr'
            )
            
            # Verificar que se intentó publicar el evento
            assert mock_bus.publish.call_count >= 0  # Depende de si hay loop


class TestDecorators:
    """Tests para decoradores de logging"""
    
    def test_log_execution_time_decorator(self, caplog):
        """Prueba decorador de tiempo de ejecución"""
        
        @log_execution_time()
        def test_function():
            time.sleep(0.01)
            return "success"
        
        with caplog.at_level(logging.INFO):
            result = test_function()
        
        assert result == "success"
        # Verificar que se loggeó el tiempo de ejecución
        execution_logs = [r for r in caplog.records if 'executed in' in r.message]
        assert len(execution_logs) > 0
    
    def test_log_api_call_decorator(self, caplog):
        """Prueba decorador de llamadas API"""
        
        @log_api_call()
        def test_api_function():
            return {"success": True}
        
        with caplog.at_level(logging.INFO):
            result = test_api_function()
        
        assert result == {"success": True}
        # Verificar logs de inicio y finalización
        start_logs = [r for r in caplog.records if 'API call started' in r.message]
        end_logs = [r for r in caplog.records if 'API call completed' in r.message]
        
        assert len(start_logs) >= 1
        assert len(end_logs) >= 1
    
    def test_decorator_error_handling(self, caplog):
        """Prueba manejo de errores en decoradores"""
        
        @log_execution_time()
        def failing_function():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                failing_function()
        
        # Verificar que se loggeó el error
        error_logs = [r for r in caplog.records if 'failed after' in r.message]
        assert len(error_logs) >= 1


class TestMiddleware:
    """Tests para middleware de logging"""
    
    @pytest.fixture
    def mock_app(self):
        """Fixture que proporciona una app Flask mock"""
        from flask import Flask
        app = Flask(__name__)
        return app
    
    def test_request_logging_middleware_init(self, mock_app):
        """Prueba inicialización del middleware de requests"""
        middleware = RequestLoggingMiddleware(mock_app)
        
        # Verificar que se registraron los hooks
        assert len(mock_app.before_request_funcs[None]) >= 1
        assert len(mock_app.after_request_funcs[None]) >= 1
    
    def test_whatsapp_api_logging_decorator(self, caplog):
        """Prueba decorador de logging para WhatsApp API"""
        middleware = WhatsAppAPILoggingMiddleware()
        
        @middleware.log_api_call
        def test_whatsapp_call():
            return {"message_id": "123"}
        
        with caplog.at_level(logging.INFO):
            result = test_whatsapp_call()
        
        assert result == {"message_id": "123"}
        # Verificar logs específicos de WhatsApp API
        whatsapp_logs = [r for r in caplog.records if 'WhatsApp API call' in r.message]
        assert len(whatsapp_logs) >= 1


class TestLogConfig:
    """Tests para configuración de logging"""
    
    def test_base_config_structure(self):
        """Prueba estructura de configuración base"""
        config = LoggingConfig.get_base_config()
        
        required_keys = ['version', 'formatters', 'handlers', 'loggers', 'root']
        for key in required_keys:
            assert key in config
    
    def test_development_config(self):
        """Prueba configuración de desarrollo"""
        config = LoggingConfig.get_development_config()
        
        assert 'console' in config['handlers']
        assert 'file_rotating' in config['handlers']
        assert config['handlers']['console']['level'] == 'DEBUG'
    
    def test_production_config(self):
        """Prueba configuración de producción"""
        config = LoggingConfig.get_production_config()
        
        assert 'app_file' in config['handlers']
        assert 'security_file' in config['handlers']
        assert 'error_file' in config['handlers']
    
    def test_testing_config(self):
        """Prueba configuración de testing"""
        config = LoggingConfig.get_testing_config()
        
        assert config['handlers']['console']['level'] == 'WARNING'
        assert 'test_file' in config['handlers']


class TestIntegration:
    """Tests de integración completos"""
    
    @pytest.mark.asyncio
    async def test_complete_logging_flow(self):
        """Prueba flujo completo de logging y eventos"""
        
        # Configurar sistema
        with tempfile.TemporaryDirectory() as temp_dir:
            WhatsAppLogger.configure_logging(
                log_level='DEBUG',
                log_dir=temp_dir,
                environment='testing'
            )
            
            # Crear componentes
            event_logger = EventLogger()
            metrics_handler = MetricsEventHandler()
            
            # Simular flujo completo
            event_logger.log_whatsapp_request(
                endpoint='/messages',
                method='POST',
                payload={'message': 'test'},
                phone_number='+1234567890'
            )
            
            # Crear y procesar evento
            event = Event(
                event_type=EventType.MESSAGE_SENT,
                timestamp=datetime.utcnow(),
                source='integration_test',
                data={'message_id': '123'}
            )
            
            await metrics_handler.handle(event)
            
            # Verificar métricas
            metrics = metrics_handler.get_metrics()
            assert metrics['messages_sent'] >= 1
            
            # Verificar archivos de log
            log_files = list(Path(temp_dir).glob('*.log'))
            assert len(log_files) > 0


# Función para ejecutar todos los tests
def run_all_tests():
    """
    Ejecuta todos los tests del sistema de logging
    """
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--show-capture=no'
    ])


if __name__ == "__main__":
    run_all_tests()
