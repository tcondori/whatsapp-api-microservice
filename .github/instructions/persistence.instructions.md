# Persistence Instructions
# Persistence Instructions
<!-- Instrucciones para manejo de persistencia y base de datos -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar el sistema completo de persistencia de datos, incluyendo:
- Configuración de SQLAlchemy con PostgreSQL y patrones de repositorio
- Modelos de datos completos para mensajes, contactos, webhooks y líneas
- Sistema de migración con Alembic y versionado de esquemas
- Implementación de cache con Redis para alto rendimiento
- Conexión a múltiples bases de datos y gestión de transacciones
- Patrones de consulta optimizadas y indexación de tablas
-->

## Database Schema
<!-- Esquema de base de datos -->

### Core Tables
```sql
-- Tabla de mensajes
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    whatsapp_msg_id VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20),
    message_type VARCHAR(50),
    content TEXT,
    status VARCHAR(20),
    direction VARCHAR(10), -- 'inbound' o 'outbound'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabla de contactos
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE,
    display_name VARCHAR(255),
    profile_pic_url TEXT,
    last_seen TIMESTAMP,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabla de archivos multimedia
CREATE TABLE media_files (
    id UUID PRIMARY KEY,
    whatsapp_media_id VARCHAR(255) UNIQUE,
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size BIGINT,
    storage_url TEXT,
    created_at TIMESTAMP
);
```

### Webhook Events Log
```sql
-- Tabla de eventos de webhook
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100),
    payload JSONB,
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    processed_at TIMESTAMP
);
```

## Data Models
<!-- Modelos de datos con Pydantic -->

### Message Models
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MsgCreate(BaseModel):
    """Modelo para crear un mensaje"""
    phone_number: str
    message_type: str
    content: str
    media_id: Optional[str] = None

class MsgResponse(BaseModel):
    """Respuesta de mensaje creado"""
    id: str
    whatsapp_msg_id: str
    status: str
    created_at: datetime
```

### Contact Models
```python
class ContactCreate(BaseModel):
    """Modelo para crear contacto"""
    phone_number: str
    display_name: Optional[str] = None
    
class ContactUpdate(BaseModel):
    """Modelo para actualizar contacto"""
    display_name: Optional[str] = None
    is_blocked: Optional[bool] = None
```

## Repository Pattern
<!-- Patrón Repository para acceso a datos -->

### Message Repository
```python
class MsgRepository:
    """Repositorio para operaciones de mensajes"""
    
    def save_msg(self, msg_data: MsgCreate) -> MsgResponse:
        """Guarda un nuevo mensaje en la base de datos"""
        pass
    
    def update_msg_status(self, msg_id: str, status: str) -> bool:
        """Actualiza el estado de un mensaje"""
        pass
    
    def get_msg_history(self, phone_number: str, limit: int = 50) -> List[MsgResponse]:
        """Obtiene historial de mensajes de un contacto"""
        pass
```

### Contact Repository
```python
class ContactRepository:
    """Repositorio para operaciones de contactos"""
    
    def save_contact(self, contact_data: ContactCreate) -> ContactResponse:
        """Guarda un nuevo contacto"""
        pass
    
    def get_contact_by_phone(self, phone_number: str) -> Optional[ContactResponse]:
        """Busca contacto por número de teléfono"""
        pass
```

## Database Configuration
<!-- Configuración de base de datos -->

### Connection Settings
```python
# Configuración de base de datos
DATABASE_CONFIG = {
    'postgresql': {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_NAME'),
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }
}
```

### Migration Management
- Use Alembic for database migrations
- Version control for schema changes
- Automated migration deployment
- Rollback capabilities

## Caching Strategy
<!-- Estrategia de caché -->

### Redis Integration
- Contact information caching
- Message template caching
- Rate limiting counters
- Session data storage

### Cache Patterns
```python
def get_cached_contact(phone_number: str):
    """Obtiene contacto desde caché o base de datos"""
    # Buscar en caché primero
    # Si no existe, consultar DB y guardar en caché
    pass
```
