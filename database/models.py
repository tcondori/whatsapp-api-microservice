"""
Modelos de base de datos para el microservicio WhatsApp API
Define la estructura de datos para mensajes, contactos, webhooks y líneas de mensajería
"""
from database.connection import db
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
import uuid
import logging

class BaseModel(db.Model):
    """
    Modelo base con campos comunes para todas las tablas
    Proporciona funcionalidad común como timestamps, conversión a dict y operaciones CRUD
    """
    __abstract__ = True
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def to_dict(self, convert_dates_to_local=True):
        """
        Convierte el modelo a diccionario para serialización JSON
        
        Args:
            convert_dates_to_local: Si True, convierte fechas UTC a zona horaria local
            
        Returns:
            dict: Representación del modelo como diccionario
        """
        from app.utils.date_utils import format_datetime
        
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            if isinstance(value, datetime):
                if convert_dates_to_local:
                    result[column.name] = format_datetime(value)
                else:
                    result[column.name] = value.isoformat() if value else None
            elif isinstance(value, (uuid.UUID, date)):
                result[column.name] = str(value)
            else:
                result[column.name] = value
                
        return result
    
    def save(self):
        """
        Guarda el modelo en la base de datos con manejo de errores
        Returns:
            BaseModel: La instancia guardada
        """
        try:
            db.session.add(self)
            db.session.commit()
            logging.info(f"Modelo {self.__class__.__name__} guardado con ID: {self.id}")
            return self
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error al guardar modelo {self.__class__.__name__}: {e}")
            raise e
    
    def delete(self):
        """
        Elimina el modelo de la base de datos con manejo de errores
        """
        try:
            db.session.delete(self)
            db.session.commit()
            logging.info(f"Modelo {self.__class__.__name__} eliminado con ID: {self.id}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error al eliminar modelo {self.__class__.__name__}: {e}")
            raise e
    
    def update(self, **kwargs):
        """
        Actualiza los campos del modelo
        Args:
            **kwargs: Campos a actualizar
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self.save()

class MessagingLine(BaseModel):
    """
    Modelo para líneas de mensajería de WhatsApp
    Representa diferentes números/cuentas de WhatsApp Business
    """
    __tablename__ = 'messaging_lines'
    
    line_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    phone_number_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    webhook_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    max_daily_messages = db.Column(db.Integer, default=1000)
    current_daily_count = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=func.current_date())
    
    # Metadatos adicionales
    api_version = db.Column(db.String(10), default='v18.0')
    business_id = db.Column(db.String(255))
    
    def reset_daily_counter_if_needed(self):
        """
        Resetea el contador diario si ha pasado un día
        """
        today = date.today()
        
        if self.last_reset_date != today:
            self.current_daily_count = 0
            self.last_reset_date = today
            self.save()
            logging.info(f"Contador diario reseteado para línea {self.line_id}")
    
    def can_send_message(self) -> bool:
        """
        Verifica si la línea puede enviar más mensajes hoy
        Returns:
            bool: True si puede enviar mensajes
        """
        self.reset_daily_counter_if_needed()
        can_send = self.is_active and self.current_daily_count < self.max_daily_messages
        
        if not can_send:
            logging.warning(f"Línea {self.line_id} no puede enviar mensajes: active={self.is_active}, count={self.current_daily_count}/{self.max_daily_messages}")
        
        return can_send
    
    def increment_message_count(self):
        """
        Incrementa el contador de mensajes enviados
        """
        self.reset_daily_counter_if_needed()
        self.current_daily_count += 1
        self.save()
        logging.info(f"Contador incrementado para línea {self.line_id}: {self.current_daily_count}/{self.max_daily_messages}")

class Message(BaseModel):
    """
    Modelo para mensajes de WhatsApp
    Almacena tanto mensajes enviados como recibidos
    """
    __tablename__ = 'messages'
    
    # ID único de WhatsApp para el mensaje
    whatsapp_message_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Línea de mensajería utilizada
    line_id = db.Column(db.String(50), db.ForeignKey('messaging_lines.line_id'), nullable=True, index=True)
    
    # Información del destinatario/remitente
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    
    # Tipo y contenido del mensaje
    message_type = db.Column(db.String(50), nullable=False, index=True)  # text, image, video, document, template, etc.
    content = db.Column(db.Text)
    
    # Estado del mensaje
    status = db.Column(db.String(20), default='pending', index=True)  # pending, sent, delivered, read, failed
    direction = db.Column(db.String(10), nullable=False, index=True)  # 'inbound' o 'outbound'
    
    # Media relacionado (si aplica)
    media_id = db.Column(db.String(255), nullable=True)
    
    # Metadata adicional
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    # Relación con la línea de mensajería
    messaging_line = db.relationship('MessagingLine', backref='messages', lazy='select')
    
    def __repr__(self):
        return f'<Message {self.whatsapp_message_id}: {self.message_type} to {self.phone_number}>'

class Contact(BaseModel):
    """
    Modelo para contactos de WhatsApp
    Gestiona información de perfil y estado de contactos
    """
    __tablename__ = 'contacts'
    
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(255))
    profile_pic_url = db.Column(db.Text)
    last_seen = db.Column(db.DateTime)
    is_blocked = db.Column(db.Boolean, default=False, index=True)
    
    # Información adicional del contacto
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    
    # Estadísticas de mensajería
    total_messages_sent = db.Column(db.Integer, default=0)
    total_messages_received = db.Column(db.Integer, default=0)
    last_message_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Contact {self.phone_number}: {self.display_name}>'
    
    def update_last_message(self):
        """Actualiza la timestamp del último mensaje"""
        self.last_message_at = datetime.utcnow()
        self.save()

class WebhookEvent(BaseModel):
    """
    Modelo para eventos de webhook recibidos de WhatsApp
    Registra todos los eventos para procesamiento y auditoría
    """
    __tablename__ = 'webhook_events'
    
    event_type = db.Column(db.String(100), nullable=False, index=True)
    line_id = db.Column(db.String(50), nullable=True, index=True)  # Línea que recibió el webhook
    payload = db.Column(db.JSON, nullable=False)  # Contenido completo del webhook
    
    # Estado de procesamiento
    processed = db.Column(db.Boolean, default=False, index=True)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    processed_at = db.Column(db.DateTime)
    
    # Información adicional
    source_ip = db.Column(db.String(45))  # IP del remitente del webhook
    user_agent = db.Column(db.String(255))
    
    def mark_as_processed(self, success: bool = True, error_msg: str = None):
        """
        Marca el evento como procesado
        Args:
            success: Si el procesamiento fue exitoso
            error_msg: Mensaje de error si falló
        """
        self.processed = success
        self.processed_at = datetime.utcnow()
        if error_msg:
            self.error_message = error_msg
        self.save()
    
    def increment_retry(self):
        """Incrementa el contador de reintentos"""
        self.retry_count += 1
        self.save()
    
    def __repr__(self):
        return f'<WebhookEvent {self.event_type}: processed={self.processed}>'

class MediaFile(BaseModel):
    """
    Modelo para archivos multimedia de WhatsApp
    Gestiona metadatos y referencias de archivos
    """
    __tablename__ = 'media_files'
    
    # ID único de WhatsApp para el archivo
    whatsapp_media_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Información del archivo
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, video, audio, document
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.BigInteger)
    
    # URLs de almacenamiento
    whatsapp_url = db.Column(db.Text)  # URL temporal de WhatsApp
    storage_url = db.Column(db.Text)   # URL de nuestro almacenamiento
    local_path = db.Column(db.Text)    # Ruta local si se almacena localmente
    
    # Estado del archivo
    downloaded = db.Column(db.Boolean, default=False)
    download_error = db.Column(db.Text)
    
    # Metadatos adicionales
    hash_sha256 = db.Column(db.String(64))  # Hash para verificar integridad
    expires_at = db.Column(db.DateTime)     # Cuando expira la URL de WhatsApp
    
    def __repr__(self):
        return f'<MediaFile {self.whatsapp_media_id}: {self.file_type}>'
    
    def is_expired(self) -> bool:
        """
        Verifica si el archivo ha expirado
        Returns:
            bool: True si el archivo ha expirado
        """
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

# Índices para optimización de consultas
db.Index('idx_messages_phone_created', Message.phone_number, Message.created_at)
db.Index('idx_messages_status_direction', Message.status, Message.direction)
db.Index('idx_webhook_events_type_processed', WebhookEvent.event_type, WebhookEvent.processed)
db.Index('idx_contacts_last_seen', Contact.last_seen)
db.Index('idx_media_files_type_downloaded', MediaFile.file_type, MediaFile.downloaded)


class ConversationFlow(BaseModel):
    """Modelo para flujos de conversación con RiveScript"""
    __tablename__ = 'conversation_flows'
    
    name = db.Column(db.String(100), nullable=False, comment='Nombre del flujo')
    description = db.Column(db.Text, comment='Descripción del flujo')
    rivescript_content = db.Column(db.Text, nullable=False, comment='Contenido .rive')
    is_active = db.Column(db.Boolean, default=False, comment='Si está activo')
    is_default = db.Column(db.Boolean, default=False, comment='Si es el flujo por defecto')
    priority = db.Column(db.Integer, default=1, comment='Prioridad (menor número = mayor prioridad)')
    
    # Configuración del chatbot
    fallback_to_llm = db.Column(db.Boolean, default=True, comment='Si usar LLM como fallback')
    max_context_messages = db.Column(db.Integer, default=5, comment='Máximo de mensajes en contexto')
    
    # Estadísticas
    usage_count = db.Column(db.Integer, default=0, comment='Veces que se ha usado')
    last_used = db.Column(db.DateTime, comment='Última vez usado')
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'rivescript_content': self.rivescript_content,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'priority': self.priority,
            'fallback_to_llm': self.fallback_to_llm,
            'max_context_messages': self.max_context_messages,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None
        })
        return data

class ConversationContext(BaseModel):
    """Modelo para contexto de conversaciones de usuarios"""
    __tablename__ = 'conversation_contexts'
    
    phone_number = db.Column(db.String(20), nullable=False, unique=True, comment='Número de teléfono del usuario')
    current_topic = db.Column(db.String(100), comment='Tema actual de conversación')
    context_data = db.Column(db.JSON, comment='Variables de contexto del usuario')
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow, comment='Última interacción')
    flow_id = db.Column(db.Integer, db.ForeignKey('conversation_flows.id'), comment='Flujo actual')
    session_count = db.Column(db.Integer, default=1, comment='Número de sesiones')
    
    # Relación con flujo
    flow = db.relationship('ConversationFlow', backref='contexts')
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        data = super().to_dict()
        data.update({
            'phone_number': self.phone_number,
            'current_topic': self.current_topic,
            'context_data': self.context_data or {},
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'flow_id': self.flow_id,
            'session_count': self.session_count,
            'flow_name': self.flow.name if self.flow else None
        })
        return data

class ChatbotInteraction(BaseModel):
    """Modelo para registrar interacciones del chatbot"""
    __tablename__ = 'chatbot_interactions'
    
    phone_number = db.Column(db.String(20), nullable=False, comment='Número de teléfono')
    user_message = db.Column(db.Text, nullable=False, comment='Mensaje entrante del usuario')
    bot_response = db.Column(db.Text, comment='Mensaje de respuesta del bot')
    intent = db.Column(db.String(100), comment='Intención detectada')
    confidence_score = db.Column(db.Numeric(3,2), comment='Puntuación de confianza')
    flow_id = db.Column(UUID(as_uuid=True), db.ForeignKey('conversation_flows.id'), comment='Flujo usado')
    context_id = db.Column(UUID(as_uuid=True), db.ForeignKey('conversation_contexts.id'), comment='Contexto de conversación')
    processing_time_ms = db.Column(db.Integer, comment='Tiempo de procesamiento en ms')
    
    # Relaciones
    flow = db.relationship('ConversationFlow')
    context = db.relationship('ConversationContext')
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        data = super().to_dict()
        data.update({
            'phone_number': self.phone_number,
            'user_message': self.user_message[:100] + '...' if len(self.user_message) > 100 else self.user_message,
            'bot_response': self.bot_response[:100] + '...' if self.bot_response and len(self.bot_response) > 100 else self.bot_response,
            'intent': self.intent,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'processing_time_ms': self.processing_time_ms,
            'flow_id': str(self.flow_id) if self.flow_id else None,
            'context_id': str(self.context_id) if self.context_id else None,
            'flow_name': self.flow.name if self.flow else None
        })
        return data

# Índices adicionales para los modelos del chatbot
db.Index('idx_conversation_context_phone_number', ConversationContext.phone_number)
db.Index('idx_conversation_context_last_interaction', ConversationContext.last_interaction)
db.Index('idx_chatbot_interactions_phone_created', ChatbotInteraction.phone_number, ChatbotInteraction.created_at)
db.Index('idx_chatbot_interactions_intent', ChatbotInteraction.intent)
