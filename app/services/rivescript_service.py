# app/services/rivescript_service.py - Nuevo archivo
# filepath: e:\DSW\proyectos\proy04\app\services\rivescript_service.py

import os
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.repositories.flow_repository import FlowRepository
from app.repositories.conversation_repository import ConversationRepository
from app.utils.logger import WhatsAppLogger

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
        self.flow_repo = None
        self.context_repo = None
        self.logger = WhatsAppLogger.get_logger('rivescript_service')
        self._initialized = False
        
        if not RIVESCRIPT_AVAILABLE:
            self.logger.warning("RiveScript no disponible, usando modo simulación")
        
        # No inicializar automáticamente, se hace cuando se necesite con contexto
    
    def _ensure_initialized(self) -> bool:
        """
        Asegura que el servicio esté inicializado con contexto de aplicación
        """
        from flask import has_app_context, current_app
        
        if not has_app_context():
            self.logger.warning("No hay contexto de aplicación disponible para RiveScript")
            return False
            
        if self._initialized:
            return True
            
        try:
            # Inicializar repositorios dentro del contexto de aplicación
            self.flow_repo = FlowRepository()
            self.context_repo = ConversationRepository()
            
            # Cargar flujos activos si RiveScript está disponible
            if RIVESCRIPT_AVAILABLE:
                self._load_active_flows()
                
            self._initialized = True
            self.logger.info("RiveScript service inicializado correctamente con contexto de aplicación")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando RiveScript service: {e}")
            return False
    
    def _load_active_flows(self) -> None:
        """Carga todos los flujos activos en RiveScript"""
        if not RIVESCRIPT_AVAILABLE:
            return
            
        try:
            self.rs = rivescript.RiveScript(utf8=True, debug=False)
            
            # Obtener flujos activos (debe estar dentro del contexto de aplicación)
            if not self.flow_repo:
                self.logger.error("FlowRepository no inicializado")
                return
                
            active_flows = self.flow_repo.get_active_flows()
            
            if not active_flows:
                self.logger.warning("No hay flujos activos para cargar")
                return
            
            # Cargar cada flujo
            for flow in active_flows:
                try:
                    # Cargar contenido directamente en RiveScript (no archivo temporal)
                    self.rs.stream(flow.rivescript_content)
                    self.logger.info(f"Flujo '{flow.name}' cargado exitosamente")
                    
                except Exception as flow_error:
                    self.logger.error(f"Error cargando flujo '{flow.name}': {flow_error}")
            
            # Compilar el cerebro
            self.rs.sort_replies()
            self.logger.info(f"RiveScript inicializado con {len(active_flows)} flujos")
            
        except Exception as e:
            self.logger.error(f"Error inicializando RiveScript: {e}")
            self.rs = None
    
    def get_response(self, phone_number: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene respuesta del flujo RiveScript para un mensaje
        
        Args:
            phone_number: Número del usuario
            message: Mensaje entrante
            
        Returns:
            dict: Respuesta del flujo o None si no hay match
        """
        # Asegurar inicialización antes de procesar
        if not self._ensure_initialized():
            return self._get_simulation_response(message)
            
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
            self.logger.error(f"Error obteniendo respuesta RiveScript para {phone_number}: {e}")
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
        if not self._ensure_initialized():
            return False
            
        try:
            self._load_active_flows()
            self.logger.info("Flujos recargados exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error recargando flujos: {e}")
            return False
    
    def test_flow_response(self, rivescript_content: str, test_message: str, 
                          user_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prueba un flujo sin afectar la instancia principal
        """
        if not RIVESCRIPT_AVAILABLE:
            return {
                'success': False,
                'error': 'RiveScript no disponible',
                'response': 'RiveScript no está instalado. Instala con: pip install rivescript'
            }
        
        try:
            # Crear instancia temporal de RiveScript
            temp_rs = rivescript.RiveScript(utf8=True, debug=False)
            
            # Crear archivo temporal con el contenido (método que funciona)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rive', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(rivescript_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Cargar archivo temporal
                temp_rs.stream(tmp_file_path)
                temp_rs.sort_replies()
                
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
                
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"Error probando flujo: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Obtiene información sobre los flujos cargados"""
        try:
            # Intentar inicializar si es necesario y hay contexto
            if not self._ensure_initialized():
                return {
                    'rivescript_available': RIVESCRIPT_AVAILABLE,
                    'rs_initialized': False,
                    'error': 'No application context available'
                }
                
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
            self.logger.error(f"Error obteniendo información de flujos: {e}")
            return {
                'rivescript_available': RIVESCRIPT_AVAILABLE,
                'rs_initialized': False,
                'error': str(e)
            }
    
    # ========================================
    # MÉTODOS PARA EL EDITOR RIVESCRIPT
    # ========================================
    
    def reload_flows_from_database(self) -> bool:
        """
        Recarga todos los flujos desde la base de datos
        Útil cuando se actualizan los archivos RiveScript desde el editor
        """
        try:
            if not self._ensure_initialized():
                self.logger.error("No se puede recargar flujos sin contexto de aplicación")
                return False
            
            if not RIVESCRIPT_AVAILABLE:
                self.logger.warning("RiveScript no disponible para recarga")
                return False
            
            # Recrear el objeto RiveScript para "limpiar" contenido anterior
            from rivescript import RiveScript
            self.rs = RiveScript(utf8=True, debug=False)
            
            # Cargar flujos activos desde BD
            flows = self.flow_repo.get_active_flows()
            flows_loaded = 0
            
            for flow in flows:
                if flow.rivescript_content:
                    try:
                        # Parsear contenido RiveScript línea por línea
                        content_lines = flow.rivescript_content.split('\n')
                        for line in content_lines:
                            if line.strip():  # Solo líneas no vacías
                                self.rs.stream(line)
                        flows_loaded += 1
                        self.logger.debug(f"Flujo '{flow.name}' cargado desde BD")
                    except Exception as e:
                        self.logger.error(f"Error cargando flujo '{flow.name}' desde BD: {e}")
            
            # Cargar archivos del sistema también (si existen)
            try:
                self._load_system_files()
            except:
                pass  # No es crítico si fallan los archivos del sistema
            
            # Reordenar respuestas
            self.rs.sort_replies()
            
            self.logger.info(f"Recargados {flows_loaded} flujos desde base de datos")
            return flows_loaded > 0  # True si se cargó al menos un flujo
            
        except Exception as e:
            self.logger.error(f"Error recargando flujos desde BD: {e}")
            return False
    
    def test_rivescript_content(self, rivescript_content: str, message: str, 
                              phone_number: str = "test_user") -> Dict[str, Any]:
        """
        Prueba contenido RiveScript directamente sin guardarlo en BD
        
        Args:
            rivescript_content: Contenido RiveScript a probar
            message: Mensaje de prueba
            phone_number: Número de teléfono de prueba
            
        Returns:
            dict: Resultado de la prueba
        """
        try:
            if not RIVESCRIPT_AVAILABLE:
                return {
                    'response': 'RiveScript no disponible - modo simulación',
                    'type': 'simulation',
                    'confidence_score': 0.5,
                    'error': 'RiveScript library not available'
                }
            
            # Crear instancia temporal de RiveScript
            temp_rs = rivescript.RiveScript(utf8=True, debug=False)
            
            # Cargar contenido
            temp_rs.stream(rivescript_content)
            temp_rs.sort_replies()
            
            # Obtener respuesta
            response = temp_rs.reply(phone_number, message)
            
            # Determinar tipo de respuesta
            response_type = 'rivescript_test'
            if response.startswith("ERR:"):
                response_type = 'error'
            elif response == message:
                response_type = 'no_match'
                response = "Sin respuesta encontrada para este mensaje"
            
            return {
                'response': response,
                'type': response_type,
                'confidence_score': 0.8 if response_type == 'rivescript_test' else 0.1,
                'test_info': {
                    'input_message': message,
                    'phone_number': phone_number,
                    'content_lines': len(rivescript_content.split('\n')),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error probando contenido RiveScript: {e}")
            return {
                'response': f"Error en prueba: {str(e)}",
                'type': 'test_error',
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def validate_rivescript_content(self, rivescript_content: str) -> Dict[str, Any]:
        """
        Valida sintaxis de contenido RiveScript
        
        Args:
            rivescript_content: Contenido a validar
            
        Returns:
            dict: Resultado de validación con errores encontrados
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_lines': 0,
                'triggers': 0,
                'responses': 0,
                'comments': 0,
                'empty_lines': 0
            }
        }
        
        try:
            lines = rivescript_content.split('\n')
            validation_result['stats']['total_lines'] = len(lines)
            
            triggers = []
            responses = []
            current_trigger = None
            
            for i, line in enumerate(lines):
                line_num = i + 1
                stripped = line.strip()
                
                # Contar tipos de líneas
                if not stripped:
                    validation_result['stats']['empty_lines'] += 1
                    continue
                elif stripped.startswith('//'):
                    validation_result['stats']['comments'] += 1
                    continue
                
                # Validar triggers
                if stripped.startswith('+'):
                    validation_result['stats']['triggers'] += 1
                    current_trigger = stripped[1:].strip()
                    triggers.append(current_trigger)
                    
                    if not current_trigger:
                        validation_result['errors'].append(f"Línea {line_num}: Trigger vacío")
                        validation_result['is_valid'] = False
                
                # Validar responses
                elif stripped.startswith('-'):
                    validation_result['stats']['responses'] += 1
                    response_content = stripped[1:].strip()
                    responses.append(response_content)
                    
                    if not response_content:
                        validation_result['errors'].append(f"Línea {line_num}: Respuesta vacía")
                        validation_result['is_valid'] = False
                    
                    if current_trigger is None:
                        validation_result['errors'].append(f"Línea {line_num}: Respuesta sin trigger previo")
                        validation_result['is_valid'] = False
                
                # Validar continuaciones
                elif stripped.startswith('^'):
                    if not responses:
                        validation_result['errors'].append(f"Línea {line_num}: Continuación sin respuesta previa")
                        validation_result['is_valid'] = False
                
                # Validar topics
                elif stripped.startswith('>'):
                    topic_name = stripped[1:].strip()
                    if not topic_name:
                        validation_result['errors'].append(f"Línea {line_num}: Nombre de topic vacío")
                        validation_result['is_valid'] = False
                
                # Líneas no reconocidas
                elif stripped and not stripped.startswith(('<', '*', '{')):
                    validation_result['warnings'].append(f"Línea {line_num}: Formato no reconocido - '{stripped[:50]}'")
            
            # Validar balance triggers/responses
            if validation_result['stats']['triggers'] != validation_result['stats']['responses']:
                validation_result['warnings'].append(
                    f"Desbalance: {validation_result['stats']['triggers']} triggers vs "
                    f"{validation_result['stats']['responses']} responses"
                )
            
            # Probar sintaxis con RiveScript si está disponible
            if RIVESCRIPT_AVAILABLE and validation_result['is_valid']:
                try:
                    temp_rs = rivescript.RiveScript(utf8=True, debug=False)
                    temp_rs.stream(rivescript_content)
                    temp_rs.sort_replies()
                except Exception as rs_error:
                    validation_result['errors'].append(f"Error de sintaxis RiveScript: {str(rs_error)}")
                    validation_result['is_valid'] = False
            
        except Exception as e:
            validation_result['errors'].append(f"Error durante validación: {str(e)}")
            validation_result['is_valid'] = False
        
        return validation_result
    
    def get_rivescript_examples(self) -> Dict[str, str]:
        """
        Obtiene ejemplos de sintaxis RiveScript para el editor
        
        Returns:
            dict: Ejemplos categorizados de RiveScript
        """
        return {
            'basic_greeting': """// Saludo básico
+ hola
- ¡Hola! ¿En qué puedo ayudarte?

+ [*] buenos dias [*]
- ¡Buenos días! Espero que tengas un excelente día.

+ (hi|hello)
- Hello! How can I help you today?""",
            
            'with_wildcards': """// Usando comodines
+ [*] ayuda [*]
- Estoy aquí para ayudarte. ¿Qué necesitas?

+ mi nombre es *
- Mucho gusto, <star>. ¿En qué puedo asistirte?

+ tengo * años
- <star> años es una buena edad. ¿Cómo puedo ayudarte hoy?""",
            
            'with_topics': """// Usando topics para contexto
+ quiero comprar
- ¿Qué te interesa comprar? {topic=ventas}
^ 1. Productos
^ 2. Servicios  
^ 3. Consultoría

> topic ventas
  + productos
  - Excelente, tenemos varios productos disponibles...
  
  + servicios
  - Nuestros servicios incluyen...
  
  + (1|productos)
  - {topic=random}Te muestro nuestros productos...
< topic""",
            
            'with_arrays': """// Usando arrays para variedad
! array colors = rojo azul verde amarillo negro blanco
! array saludos = hola buenos días buenas tardes hey

+ dame un color
- Qué tal el color <get colors>

+ *
% * saludos *
- <get saludos> también para ti!""",
            
            'with_conditions': """// Usando condiciones
+ cual es mi nombre
* <get name> != undefined => Tu nombre es <get name>
- No sé tu nombre aún. ¿Cómo te llamas?

+ mi nombre es *
- <set name=<star>>Perfecto, <get name>. Un gusto conocerte.

+ cuantos años tengo
* <get age> != undefined => Tienes <get age> años
- No me has dicho tu edad. ¿Cuántos años tienes?"""
        }
    
    def format_rivescript_content(self, content: str) -> str:
        """
        Formatea contenido RiveScript para mejor legibilidad
        
        Args:
            content: Contenido RiveScript a formatear
            
        Returns:
            str: Contenido formateado
        """
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Mantener líneas vacías y comentarios
            if not stripped or stripped.startswith('//'):
                formatted_lines.append(line)
                continue
            
            # Formatear diferentes tipos de líneas
            if stripped.startswith('+'):
                formatted_lines.append('+ ' + stripped[1:].strip())
            elif stripped.startswith('-'):
                formatted_lines.append('- ' + stripped[1:].strip())
            elif stripped.startswith('^'):
                formatted_lines.append('^ ' + stripped[1:].strip())
            elif stripped.startswith('>'):
                formatted_lines.append('> ' + stripped[1:].strip())
            elif stripped.startswith('<'):
                formatted_lines.append('< ' + stripped[1:].strip())
            elif stripped.startswith('*'):
                formatted_lines.append('  * ' + stripped[1:].strip())
            elif stripped.startswith('!'):
                formatted_lines.append('! ' + stripped[1:].strip())
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)