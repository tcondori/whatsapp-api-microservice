"""
Servicio simplificado de RiveScript para pruebas
"""
import os
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.repositories.flow_repository_test import FlowRepository
from app.repositories.conversation_repository_test import ConversationRepository

# Importar RiveScript solo si está disponible
try:
    import rivescript
    RIVESCRIPT_AVAILABLE = True
except ImportError:
    RIVESCRIPT_AVAILABLE = False

class RiveScriptService:
    """Servicio para manejo de flujos RiveScript"""
    
    def __init__(self):
        self.rs = None
        self.flow_repo = FlowRepository()
        self.context_repo = ConversationRepository()
        
        if not RIVESCRIPT_AVAILABLE:
            print("RiveScript no disponible, usando modo simulación")
        else:
            self._load_active_flows()
    
    def _load_active_flows(self) -> None:
        """Carga todos los flujos activos en RiveScript"""
        if not RIVESCRIPT_AVAILABLE:
            return
            
        try:
            self.rs = rivescript.RiveScript(utf8=True, debug=False)
            
            # Obtener flujos activos
            active_flows = self.flow_repo.get_active_flows()
            
            if not active_flows:
                print("No hay flujos activos para cargar")
                return
            
            # Cargar cada flujo
            for flow in active_flows:
                try:
                    # Crear archivo temporal para el flujo
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.rive', delete=False, encoding='utf-8') as tmp_file:
                        tmp_file.write(flow.rivescript_content)
                        tmp_file_path = tmp_file.name
                    
                    # Cargar en RiveScript
                    self.rs.stream(tmp_file_path)
                    
                    # Limpiar archivo temporal
                    os.unlink(tmp_file_path)
                    
                    print(f"Flujo '{flow.name}' cargado exitosamente")
                    
                except Exception as flow_error:
                    print(f"Error cargando flujo '{flow.name}': {flow_error}")
            
            # Compilar el cerebro
            self.rs.sort_replies()
            print(f"RiveScript inicializado con {len(active_flows)} flujos")
            
        except Exception as e:
            print(f"Error inicializando RiveScript: {e}")
            self.rs = None
    
    def get_response(self, phone_number: str, message: str) -> Optional[Dict[str, Any]]:
        """Obtiene respuesta del flujo RiveScript para un mensaje"""
        if not RIVESCRIPT_AVAILABLE or not self.rs:
            return self._get_simulation_response(message)
        
        try:
            # Obtener/crear contexto del usuario
            context = self.context_repo.get_or_create_context(phone_number)
            
            # Establecer variables de usuario en RiveScript
            if context.context_data:
                for key, value in context.context_data.items():
                    if isinstance(value, (str, int, float)):
                        self.rs.set_uservar(phone_number, key, str(value))
            
            # Obtener respuesta
            reply = self.rs.reply(phone_number, message)
            
            # Verificar si es una respuesta válida
            if reply and not reply.startswith("ERR:") and reply != message:
                
                # Obtener variables actualizadas del usuario
                updated_vars = self.rs.get_uservars(phone_number)
                
                # Actualizar contexto si hay cambios
                if updated_vars != context.context_data:
                    self.context_repo.update_context_data(phone_number, updated_vars)
                
                # Incrementar uso del flujo si hay uno activo
                if context.flow_id:
                    self.flow_repo.increment_usage(context.flow_id)
                
                return {
                    'response': reply,
                    'type': 'flow',
                    'flow_id': context.flow_id,
                    'context_updated': updated_vars != context.context_data,
                    'confidence_score': 0.9  # Alta confianza para matches de flujo
                }
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo respuesta RiveScript para {phone_number}: {e}")
            return None
    
    def _get_simulation_response(self, message: str) -> Optional[Dict[str, Any]]:
        """Respuesta simulada cuando RiveScript no está disponible"""
        message_lower = message.lower()
        
        # Respuestas simuladas básicas
        if any(greeting in message_lower for greeting in ['hola', 'hello', 'hi', 'buenos días', 'buenas tardes']):
            return {
                'response': '¡Hola! Bienvenido a nuestro servicio. ¿En qué puedo ayudarte?',
                'type': 'flow_simulation',
                'confidence_score': 0.8
            }
        
        if any(help_word in message_lower for help_word in ['ayuda', 'help', 'menu', 'opciones']):
            return {
                'response': 'Estas son las opciones disponibles:\n1. Información de productos\n2. Soporte técnico\n3. Contactar agente humano\n\nEscribe el número de la opción que desees.',
                'type': 'flow_simulation',
                'confidence_score': 0.8
            }
        
        if message_lower in ['1', 'productos', 'info']:
            return {
                'response': 'Tenemos varios productos disponibles:\n• Producto A - $100\n• Producto B - $200\n• Producto C - $300\n\n¿Te interesa alguno en particular?',
                'type': 'flow_simulation',
                'confidence_score': 0.9
            }
        
        if message_lower in ['2', 'soporte', 'técnico']:
            return {
                'response': 'Para soporte técnico, por favor describe tu problema y un técnico te contactará pronto.',
                'type': 'flow_simulation',
                'confidence_score': 0.9
            }
        
        if message_lower in ['3', 'agente', 'humano']:
            return {
                'response': 'Perfecto, te estoy conectando con un agente humano. Por favor espera un momento.',
                'type': 'flow_simulation',
                'confidence_score': 0.9
            }
        
        return None
    
    def reload_flows(self) -> bool:
        """Recarga todos los flujos activos"""
        try:
            self._load_active_flows()
            print("Flujos recargados exitosamente")
            return True
        except Exception as e:
            print(f"Error recargando flujos: {e}")
            return False
    
    def test_flow_response(self, rivescript_content: str, test_message: str, 
                          user_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prueba un flujo sin afectar la instancia principal"""
        if not RIVESCRIPT_AVAILABLE:
            return {
                'success': False,
                'error': 'RiveScript no disponible',
                'response': 'RiveScript no está instalado. Instala con: pip install rivescript'
            }
        
        try:
            # Crear instancia temporal de RiveScript
            temp_rs = rivescript.RiveScript(utf8=True, debug=False)
            
            # Crear archivo temporal con el contenido
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rive', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(rivescript_content)
                tmp_file_path = tmp_file.name
            
            # Cargar y compilar
            temp_rs.stream(tmp_file_path)
            temp_rs.sort_replies()
            
            # Limpiar archivo temporal
            os.unlink(tmp_file_path)
            
            test_user = "test_user_" + str(datetime.now().timestamp())
            
            # Establecer variables de usuario si se proporcionan
            if user_vars:
                for key, value in user_vars.items():
                    temp_rs.set_uservar(test_user, key, str(value))
            
            # Obtener respuesta
            reply = temp_rs.reply(test_user, test_message)
            
            return {
                'success': True,
                'response': reply,
                'user_vars': temp_rs.get_uservars(test_user),
                'valid_response': not reply.startswith("ERR:") and reply != test_message,
                'test_message': test_message
            }
            
        except Exception as e:
            print(f"Error probando flujo: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Obtiene información sobre los flujos cargados"""
        try:
            active_flows = self.flow_repo.get_active_flows()
            
            return {
                'rivescript_available': RIVESCRIPT_AVAILABLE,
                'rs_initialized': self.rs is not None,
                'active_flows_count': len(active_flows),
                'flows': [
                    {
                        'id': flow.id,
                        'name': flow.name,
                        'description': flow.description,
                        'priority': flow.priority,
                        'usage_count': flow.usage_count or 0,
                        'last_used': flow.last_used.isoformat() if flow.last_used else None
                    }
                    for flow in active_flows
                ]
            }
            
        except Exception as e:
            print(f"Error obteniendo información de flujos: {e}")
            return {
                'rivescript_available': RIVESCRIPT_AVAILABLE,
                'rs_initialized': False,
                'error': str(e)
            }
