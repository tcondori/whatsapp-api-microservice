# Testing Instructions
# Tests Instructions
<!-- Instrucciones para testing completo del microservicio -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar el sistema completo de testing, incluyendo:
- Tests unitarios con pytest para todos los componentes del sistema
- Tests de integración para APIs, webhooks y base de datos
- Mocking de servicios externos (WhatsApp API, Redis, S3)
- Tests de carga y rendimiento para endpoints críticos
- Coverage completo de código y reportes de calidad
- CI/CD pipeline con testing automatizado y deployment
-->

## Testing Strategy
<!-- Estrategia de testing -->

### Test Pyramid Structure
- **Unit Tests**: Servicios, repositorios, utilidades (70%)
- **Integration Tests**: Endpoints, base de datos (20%)
- **E2E Tests**: Flujos completos con WhatsApp API (10%)

### Test Configuration
```python
# tests/conftest.py
import pytest
from app import create_app
from app.config.database import db

@pytest.fixture
def app():
    """Crea aplicación para testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de testing para requests HTTP"""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Headers de autenticación para testing"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }
```

## Unit Tests
<!-- Tests unitarios -->

### Message Service Tests
```python
# tests/unit/test_msg_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.msg_service import MsgService

class TestMsgService:
    """Tests para el servicio de mensajes"""
    
    def setup_method(self):
        """Configurar mocks para cada test"""
        self.msg_repo_mock = Mock()
        self.contact_repo_mock = Mock()
        self.whatsapp_client_mock = Mock()
        
        self.service = MsgService(
            self.msg_repo_mock,
            self.contact_repo_mock,
            self.whatsapp_client_mock
        )
    
    def test_send_text_message_success(self):
        """Debe enviar mensaje de texto exitosamente"""
        # Arrange
        phone_number = "+1234567890"
        content = "Mensaje de prueba"
        
        self.whatsapp_client_mock.send_text.return_value = {
            'id': 'wamid.test123',
            'status': 'sent'
        }
        
        # Act
        result = self.service.send_text_msg(phone_number, content)
        
        # Assert
        assert result['status'] == 'sent'
        self.whatsapp_client_mock.send_text.assert_called_once_with(
            phone_number, content
        )
        self.msg_repo_mock.save_msg.assert_called_once()
    
    def test_send_message_invalid_phone(self):
        """Debe fallar con número de teléfono inválido"""
        # Arrange
        invalid_phone = "invalid-phone"
        content = "Mensaje de prueba"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Número de teléfono inválido"):
            self.service.send_text_msg(invalid_phone, content)
    
    @patch('app.utils.validators.validate_phone_number')
    def test_send_message_whatsapp_api_error(self, mock_validate):
        """Debe manejar errores de la API de WhatsApp"""
        # Arrange
        mock_validate.return_value = True
        phone_number = "+1234567890"
        content = "Mensaje de prueba"
        
        self.whatsapp_client_mock.send_text.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            self.service.send_text_msg(phone_number, content)
```

### Webhook Service Tests
```python
# tests/unit/test_webhook_service.py
import pytest
from unittest.mock import Mock
from app.services.webhook_service import WebhookService

class TestWebhookService:
    """Tests para el servicio de webhooks"""
    
    def setup_method(self):
        self.msg_service_mock = Mock()
        self.service = WebhookService(self.msg_service_mock)
    
    def test_process_text_message_webhook(self):
        """Debe procesar webhook de mensaje de texto"""
        # Arrange
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.test123",
                            "type": "text",
                            "text": {"body": "Hola mundo"}
                        }]
                    }
                }]
            }]
        }
        
        # Act
        result = self.service.process_webhook(webhook_data)
        
        # Assert
        assert result is True
        # Verificar que se procesó el mensaje
        assert self.msg_service_mock.save_incoming_msg.called
    
    def test_process_status_update_webhook(self):
        """Debe procesar webhook de actualización de estado"""
        # Arrange
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "statuses": [{
                            "id": "wamid.test123",
                            "status": "delivered",
                            "timestamp": "1664827504"
                        }]
                    }
                }]
            }]
        }
        
        # Act
        result = self.service.process_webhook(webhook_data)
        
        # Assert
        assert result is True
        # Verificar que se actualizó el estado
        assert self.msg_service_mock.update_msg_status.called
```

## Integration Tests
<!-- Tests de integración -->

### API Endpoint Tests
```python
# tests/integration/test_msg_endpoints.py
import pytest
import json
from unittest.mock import patch

class TestMessageEndpoints:
    """Tests de integración para endpoints de mensajes"""
    
    def test_send_message_endpoint_success(self, client, auth_headers):
        """Debe enviar mensaje a través del endpoint"""
        # Arrange
        payload = {
            "phone_number": "+1234567890",
            "message_type": "text",
            "content": "Mensaje de prueba"
        }
        
        with patch('app.services.msg_service.MsgService.send_text_msg') as mock_send:
            mock_send.return_value = {
                'id': 'uuid-123',
                'whatsapp_message_id': 'wamid.test123',
                'status': 'sent'
            }
            
            # Act
            response = client.post(
                '/api/v1/messages/send',
                data=json.dumps(payload),
                headers=auth_headers
            )
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'sent'
            assert 'whatsapp_message_id' in data
    
    def test_send_message_invalid_payload(self, client, auth_headers):
        """Debe rechazar payload inválido"""
        # Arrange
        payload = {
            "phone_number": "invalid-phone",
            "message_type": "text"
            # Falta el campo 'content'
        }
        
        # Act
        response = client.post(
            '/api/v1/messages/send',
            data=json.dumps(payload),
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_webhook_endpoint_verification(self, client):
        """Debe verificar webhook de WhatsApp correctamente"""
        # Arrange
        verify_token = "test-verify-token"
        challenge = "test-challenge"
        
        # Act
        response = client.get(
            f'/api/v1/webhooks?hub.mode=subscribe&hub.challenge={challenge}&hub.verify_token={verify_token}'
        )
        
        # Assert
        assert response.status_code == 200
        assert response.data.decode() == challenge
    
    @patch('app.utils.auth.verify_webhook_signature')
    def test_webhook_endpoint_process_message(self, mock_verify, client):
        """Debe procesar webhook de mensaje entrante"""
        # Arrange
        mock_verify.return_value = True
        
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.test123",
                            "type": "text",
                            "text": {"body": "Hola"}
                        }]
                    }
                }]
            }]
        }
        
        # Act
        response = client.post(
            '/api/v1/webhooks',
            data=json.dumps(webhook_payload),
            headers={
                'Content-Type': 'application/json',
                'X-Hub-Signature-256': 'sha256=test-signature'
            }
        )
        
        # Assert
        assert response.status_code == 200
```

## Test Data & Fixtures
<!-- Datos de prueba y fixtures -->

### Webhook Sample Data
```python
# tests/fixtures/webhook_samples.py

INCOMING_TEXT_MESSAGE = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "15551234567",
                    "phone_number_id": "123456789"
                },
                "messages": [{
                    "from": "16315551234",
                    "id": "wamid.ABGGFlA5Fpa",
                    "timestamp": "1664827504",
                    "text": {
                        "body": "Hola mundo"
                    },
                    "type": "text"
                }]
            },
            "field": "messages"
        }]
    }]
}

MESSAGE_STATUS_UPDATE = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "15551234567",
                    "phone_number_id": "123456789"
                },
                "statuses": [{
                    "id": "wamid.ABGGFlA5Fpa",
                    "status": "delivered",
                    "timestamp": "1664827505",
                    "recipient_id": "16315551234"
                }]
            },
            "field": "messages"
        }]
    }]
}
```

## Mock WhatsApp API
<!-- Mock de la API de WhatsApp para testing -->

### Mock Client
```python
# tests/mocks/whatsapp_client_mock.py
from unittest.mock import Mock

class WhatsAppClientMock:
    """Mock del cliente de WhatsApp API para testing"""
    
    def __init__(self):
        self.send_text = Mock()
        self.send_template = Mock()
        self.upload_media = Mock()
        self.download_media = Mock()
    
    def setup_success_responses(self):
        """Configura respuestas exitosas por defecto"""
        self.send_text.return_value = {
            'messages': [{
                'id': 'wamid.mock123',
                'status': 'sent'
            }]
        }
        
        self.upload_media.return_value = {
            'id': 'media_id_mock123'
        }
```

## Performance Tests
<!-- Tests de rendimiento -->

### Load Testing with pytest-benchmark
```python
# tests/performance/test_msg_service_performance.py
import pytest

class TestMessageServicePerformance:
    """Tests de rendimiento para el servicio de mensajes"""
    
    def test_send_message_performance(self, benchmark, msg_service):
        """Debe enviar mensaje en tiempo razonable"""
        
        def send_message():
            return msg_service.send_text_msg("+1234567890", "Mensaje de prueba")
        
        # Benchmark debe completar en menos de 100ms
        result = benchmark(send_message)
        assert result is not None
```

## Test Commands
<!-- Comandos para ejecutar tests -->

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Ejecutar solo tests unitarios
pytest tests/unit/

# Ejecutar tests de integración
pytest tests/integration/

# Ejecutar tests en paralelo
pytest -n 4

# Ejecutar tests con output detallado
pytest -v -s
```
