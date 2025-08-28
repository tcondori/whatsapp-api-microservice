# app/chatbot/models.py - Modelos para el simulador de chat
# filepath: e:\DSW\proyectos\proy04\app\chatbot\models.py

"""
Modelos específicos para el simulador de chat web
Gestiona sesiones de chat simulado y historial de conversaciones
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid
import json

@dataclass
class ChatMessage:
    """Modelo para un mensaje individual del chat"""
    id: str
    message: str
    sender: str  # 'user' or 'bot'
    timestamp: datetime
    message_type: str = 'text'
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a diccionario para JSON"""
        return {
            'id': self.id,
            'message': self.message,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def create_user_message(cls, message: str) -> 'ChatMessage':
        """Crea un mensaje de usuario"""
        return cls(
            id=str(uuid.uuid4()),
            message=message,
            sender='user',
            timestamp=datetime.now(),
            message_type='text'
        )
    
    @classmethod
    def create_bot_message(cls, message: str, message_type: str = 'text', metadata: Dict = None) -> 'ChatMessage':
        """Crea un mensaje del bot"""
        return cls(
            id=str(uuid.uuid4()),
            message=message,
            sender='bot',
            timestamp=datetime.now(),
            message_type=message_type,
            metadata=metadata or {}
        )

class ChatSession:
    """Maneja una sesión de chat individual"""
    
    def __init__(self, session_id: str = None, phone_number: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.phone_number = phone_number or f"+595987{str(uuid.uuid4())[:6]}"
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
        self.user_name = "Usuario Simulado"
        
    def add_message(self, message: ChatMessage) -> None:
        """Agrega un mensaje a la sesión"""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def add_user_message(self, message: str) -> ChatMessage:
        """Agrega un mensaje de usuario y lo retorna"""
        chat_message = ChatMessage.create_user_message(message)
        self.add_message(chat_message)
        return chat_message
    
    def add_bot_message(self, message: str, message_type: str = 'text', metadata: Dict = None) -> ChatMessage:
        """Agrega un mensaje del bot y lo retorna"""
        chat_message = ChatMessage.create_bot_message(message, message_type, metadata)
        self.add_message(chat_message)
        return chat_message
    
    def get_messages(self, limit: int = None) -> List[ChatMessage]:
        """Obtiene los mensajes de la sesión"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_last_messages(self, count: int = 10) -> List[ChatMessage]:
        """Obtiene los últimos N mensajes"""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def clear_messages(self) -> None:
        """Limpia todos los mensajes de la sesión"""
        self.messages = []
        self.last_activity = datetime.now()
    
    def close_session(self) -> None:
        """Cierra la sesión de chat"""
        self.is_active = False
        self.add_bot_message(
            "Conversación finalizada. ¡Gracias por contactarnos!",
            message_type="system"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la sesión a diccionario"""
        return {
            'session_id': self.session_id,
            'phone_number': self.phone_number,
            'user_name': self.user_name,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active,
            'message_count': len(self.messages),
            'messages': [msg.to_dict() for msg in self.messages]
        }

class ChatSessionManager:
    """Gestor de sesiones de chat para el simulador"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.active_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    def create_session(self, user_id: str = None) -> ChatSession:
        """Crea una nueva sesión de chat"""
        session = ChatSession()
        
        if user_id:
            # Si hay una sesión activa previa, cerrarla
            if user_id in self.active_sessions:
                old_session_id = self.active_sessions[user_id]
                if old_session_id in self.sessions:
                    self.sessions[old_session_id].close_session()
            
            self.active_sessions[user_id] = session.session_id
        
        self.sessions[session.session_id] = session
        
        # Mensaje de bienvenida
        session.add_bot_message(
            "¡Hola! Bienvenido al simulador de chat de WhatsApp. ¿En qué puedo ayudarte?",
            message_type="greeting"
        )
        
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Obtiene una sesión por su ID"""
        return self.sessions.get(session_id)
    
    def get_user_session(self, user_id: str) -> Optional[ChatSession]:
        """Obtiene la sesión activa de un usuario"""
        session_id = self.active_sessions.get(user_id)
        if session_id:
            return self.sessions.get(session_id)
        return None
    
    def get_or_create_user_session(self, user_id: str) -> ChatSession:
        """Obtiene o crea una sesión para un usuario"""
        session = self.get_user_session(user_id)
        if not session or not session.is_active:
            session = self.create_session(user_id)
        return session
    
    def close_session(self, session_id: str) -> bool:
        """Cierra una sesión específica"""
        session = self.get_session(session_id)
        if session:
            session.close_session()
            return True
        return False
    
    def cleanup_inactive_sessions(self, hours: int = 24) -> int:
        """Limpia sesiones inactivas más antiguas que X horas"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        
        inactive_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.last_activity < cutoff
        ]
        
        for session_id in inactive_sessions:
            del self.sessions[session_id]
            
            # Limpiar referencias en active_sessions
            for user_id, active_session_id in list(self.active_sessions.items()):
                if active_session_id == session_id:
                    del self.active_sessions[user_id]
        
        return len(inactive_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de las sesiones"""
        active_count = sum(1 for session in self.sessions.values() if session.is_active)
        total_messages = sum(len(session.messages) for session in self.sessions.values())
        
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': active_count,
            'inactive_sessions': len(self.sessions) - active_count,
            'total_messages': total_messages,
            'average_messages_per_session': total_messages / len(self.sessions) if self.sessions else 0
        }

# Instancia global del gestor de sesiones
chat_manager = ChatSessionManager()
