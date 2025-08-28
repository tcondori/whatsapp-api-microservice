# app/api/rivescript_simple.py
# filepath: e:\DSW\proyectos\proy04\app\api\rivescript_simple.py

"""
API simple para el editor RiveScript usando Flask Blueprint
Version simplificada sin Flask-RESTX para evitar conflictos
"""

from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import os
import json

from app.services.rivescript_service import RiveScriptService
from app.services.chatbot_service import ChatbotService
from app.repositories.flow_repository import FlowRepository
from app.utils.logger import WhatsAppLogger

# Crear blueprint simple con carpeta de templates especificada
import os
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
rivescript_simple_bp = Blueprint('rivescript', __name__, url_prefix='/rivescript', template_folder=template_dir)

logger = WhatsAppLogger.get_logger('rivescript_api')

# ========================================
# ENDPOINT PARA EL EDITOR HTML
# ========================================

@rivescript_simple_bp.route('/')
def dashboard():
    """Servir el dashboard principal"""
    return render_template('dashboard.html')

@rivescript_simple_bp.route('/editor')
def editor():
    """Servir el editor RiveScript HTML"""
    return render_template('flow_manager.html')

@rivescript_simple_bp.route('/simulator')
def simulator():
    """Servir el simulador de chat HTML"""
    return render_template('chat_simulator.html')

# ========================================
# ENDPOINTS SIMPLES DEL API
# ========================================

@rivescript_simple_bp.route('/flows', methods=['GET'])
def get_flows():
    """Obtener todos los flujos RiveScript"""
    try:
        flow_repo = FlowRepository()
        flows = flow_repo.get_all_flows()
        
        flows_data = []
        for flow in flows:
            flows_data.append({
                'id': flow.id,
                'name': flow.name,
                'description': flow.description,
                'is_active': flow.is_active,
                'is_default': flow.is_default,
                'priority': flow.priority,
                'created_at': flow.created_at.isoformat() if flow.created_at else None,
                'updated_at': flow.updated_at.isoformat() if flow.updated_at else None,
                'rivescript_content': flow.rivescript_content[:200] + '...' if len(flow.rivescript_content or '') > 200 else flow.rivescript_content
            })
        
        logger.info(f"Obtenidos {len(flows_data)} flujos")
        
        return jsonify({
            'status': 'success',
            'total': len(flows_data),
            'flows': flows_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo flujos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo flujos: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/flows', methods=['POST'])
def create_flow():
    """Crear un nuevo flujo RiveScript"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos JSON'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['name', 'rivescript_content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Campo requerido faltante: {field}'
                }), 400
        
        # Crear flujo
        flow_repo = FlowRepository()
        flow_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'rivescript_content': data['rivescript_content'],
            'is_active': data.get('is_active', True),
            'priority': data.get('priority', 1)
        }
        
        flow = flow_repo.create_flow(flow_data)
        
        logger.info(f"Flujo creado: {flow.name} (ID: {flow.id})")
        
        return jsonify({
            'status': 'success',
            'message': 'Flujo creado exitosamente',
            'flow': {
                'id': flow.id,
                'name': flow.name,
                'description': flow.description,
                'is_active': flow.is_active,
                'created_at': flow.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error creando flujo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error creando flujo: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/flows/<string:flow_id>', methods=['GET'])
def get_flow_by_id(flow_id):
    """Obtener un flujo específico por ID"""
    try:
        logger.info(f"🔍 GET /flows/{flow_id} - Iniciando búsqueda")
        
        flow_repo = FlowRepository()
        logger.info(f"📁 Repositorio creado para búsqueda de flujo")
        
        # Debug: Verificar total de flujos
        total_flows = flow_repo.get_all_flows()
        logger.info(f"📊 Total flujos disponibles: {len(total_flows)}")
        
        flow = flow_repo.get_by_id(flow_id)
        logger.info(f"🎯 Resultado de búsqueda: {flow is not None}")
        
        if not flow:
            logger.warning(f"❌ Flujo {flow_id} no encontrado")
            return jsonify({
                'status': 'error',
                'message': 'Flujo no encontrado'
            }), 404
        
        flow_data = {
            'id': flow.id,
            'name': flow.name,
            'description': flow.description,
            'is_active': flow.is_active,
            'is_default': flow.is_default,
            'priority': flow.priority,
            'created_at': flow.created_at.isoformat() if flow.created_at else None,
            'updated_at': flow.updated_at.isoformat() if flow.updated_at else None,
            'rivescript_content': flow.rivescript_content
        }
        
        logger.info(f"✅ Flujo obtenido exitosamente: {flow.name}")
        return jsonify(flow_data), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo flujo {flow_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo flujo: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/flows/<string:flow_id>', methods=['PUT'])
def update_flow(flow_id):
    """Actualizar un flujo existente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos JSON'
            }), 400
        
        flow_repo = FlowRepository()
        success = flow_repo.update_flow(flow_id, data)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Flujo no encontrado o error al actualizar'
            }), 404
        
        # Obtener el flujo actualizado para devolver la información
        updated_flow = flow_repo.get_by_id(flow_id)
        
        logger.info(f"Flujo actualizado: {updated_flow.name} (ID: {updated_flow.id})")
        
        return jsonify({
            'status': 'success',
            'message': 'Flujo actualizado exitosamente',
            'flow': {
                'id': updated_flow.id,
                'name': updated_flow.name,
                'description': updated_flow.description,
                'is_active': updated_flow.is_active,
                'priority': updated_flow.priority,
                'updated_at': updated_flow.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando flujo {flow_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error actualizando flujo: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/flows/<string:flow_id>', methods=['DELETE'])
def delete_flow(flow_id):
    """Eliminar un flujo"""
    try:
        flow_repo = FlowRepository()
        success = flow_repo.delete_flow(flow_id)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Flujo no encontrado'
            }), 404
        
        logger.info(f"Flujo eliminado: ID {flow_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Flujo eliminado exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando flujo {flow_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error eliminando flujo: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/test', methods=['POST'])
def test_rivescript():
    """Probar contenido RiveScript directamente"""
    try:
        data = request.get_json()
        
        if not data or 'rivescript_content' not in data or 'test_message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requiere rivescript_content y test_message'
            }), 400
        
        rivescript_service = RiveScriptService()
        result = rivescript_service.test_rivescript_content(
            data['rivescript_content'], 
            data['test_message']
        )
        
        return jsonify({
            'status': 'success',
            'test_message': data['test_message'],
            'bot_response': result['response'],
            'processing_time_ms': result.get('processing_time_ms', 0),
            'has_errors': result.get('has_errors', False),
            'errors': result.get('errors', [])
        }), 200
        
    except Exception as e:
        logger.error(f"Error probando RiveScript: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error probando RiveScript: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/test-flow', methods=['POST'])
def test_flow():
    """Probar un flujo específico por ID"""
    try:
        data = request.get_json()
        
        if not data or 'flow_id' not in data or 'test_message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requiere flow_id y test_message'
            }), 400
        
        flow_repo = FlowRepository()
        flow = flow_repo.get_flow_by_id(data['flow_id'])
        
        if not flow:
            return jsonify({
                'status': 'error',
                'message': 'Flujo no encontrado'
            }), 404
        
        rivescript_service = RiveScriptService()
        result = rivescript_service.test_rivescript_content(
            flow.rivescript_content, 
            data['test_message']
        )
        
        return jsonify({
            'status': 'success',
            'flow_name': flow.name,
            'test_message': data['test_message'],
            'bot_response': result['response'],
            'processing_time_ms': result.get('processing_time_ms', 0),
            'has_errors': result.get('has_errors', False),
            'errors': result.get('errors', [])
        }), 200
        
    except Exception as e:
        logger.error(f"Error probando flujo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error probando flujo: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/chat', methods=['POST'])
def chat_with_rivescript():
    """Endpoint específico para el simulador de chat"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Mensaje requerido'
            }), 400
        
        # Validar que message sea string y no dict
        message_raw = data['message']
        if isinstance(message_raw, dict):
            return jsonify({
                'success': False,
                'error': 'El campo "message" debe ser una cadena de texto'
            }), 400
        
        user_message = str(message_raw).strip()
        user_id = data.get('user_id', 'simulator_user')
        conversation_id = data.get('conversation_id', f'sim_{user_id}')
        flow_id = data.get('flow_id')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Mensaje no puede estar vacío'
            }), 400
        
        logger.info(f"Chat request - Usuario: {user_id}, Mensaje: {user_message}, Flow: {flow_id}")
        
        # Si se especifica un flujo, usar solo ese flujo
        if flow_id:
            try:
                flow_repo = FlowRepository()
                flow = flow_repo.get_by_id(flow_id)
                
                if not flow:
                    return jsonify({
                        'success': False,
                        'error': f'Flujo {flow_id} no encontrado'
                    }), 404
                
                if not flow.is_active:
                    return jsonify({
                        'success': False,
                        'error': f'Flujo {flow.name} está inactivo'
                    }), 400
                
                # Usar el servicio RiveScript principal cargado desde BD
                rivescript_service = RiveScriptService()
                
                # Obtener respuesta usando la instancia principal
                response = rivescript_service.get_response(user_id, user_message)
                
                if response and isinstance(response, dict) and response.get('response'):
                    return jsonify({
                        'success': True,
                        'response': response.get('response'),
                        'flow_name': 'Sistema RiveScript',
                        'flow_id': response.get('flow_id', flow_id),
                        'type': response.get('type', 'flow'),
                        'confidence': response.get('confidence_score', 0.9),
                        'processing_time_ms': 0
                    }), 200
                elif response and isinstance(response, str) and response.strip():
                    return jsonify({
                        'success': True,
                        'response': response,
                        'flow_name': 'Sistema RiveScript',
                        'flow_id': flow_id,
                        'type': 'flow',
                        'confidence': 0.9,
                        'processing_time_ms': 0
                    }), 200
                else:
                    return jsonify({
                        'success': True,
                        'response': f'Sin respuesta específica para "{user_message}"',
                        'flow_name': 'Sistema RiveScript',
                        'flow_id': flow_id,
                        'type': 'no_match',
                        'confidence': 0.0
                    }), 200
                    
            except Exception as flow_error:
                logger.error(f"Error procesando flujo específico: {flow_error}")
                return jsonify({
                    'success': False,
                    'error': f'Error procesando flujo: {str(flow_error)}'
                }), 500
        
        # Si no se especifica flujo, usar el servicio completo
        try:
            from app.services.chatbot_service import ChatbotService
            
            chatbot_service = ChatbotService()
            
            # Forzar uso de flujo específico si se proporciona
            if flow_id:
                # Crear un contexto temporal para el usuario de simulación
                phone_number = f"sim_{user_id}"
                response = chatbot_service.process_message(phone_number, user_message)
            else:
                # Usar servicio completo sin restricción de flujo
                phone_number = f"sim_{user_id}"
                response = chatbot_service.process_message(phone_number, user_message)
            
            if isinstance(response, dict):
                return jsonify({
                    'success': True,
                    'response': response.get('response', 'Sin respuesta'),
                    'type': response.get('type', 'chatbot'),
                    'confidence': response.get('confidence_score', 0.5),
                    'processing_time_ms': response.get('processing_time_ms', 0),
                    'flow_id': response.get('flow_id', flow_id),
                    'flow_name': response.get('flow_name', 'Sistema completo')
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'response': str(response) if response else 'Sin respuesta',
                    'type': 'simple',
                    'confidence': 0.5,
                    'flow_name': 'Sistema completo'
                }), 200
                
        except Exception as chatbot_error:
            logger.error(f"Error en ChatbotService: {chatbot_error}")
            
            # Fallback: usar solo RiveScript directamente
            try:
                rivescript_service = RiveScriptService()
                
                # Forzar inicialización si es necesario
                if not rivescript_service._ensure_initialized():
                    rivescript_service.load_flows_from_database()
                
                result = rivescript_service.get_response(f"sim_{user_id}", user_message)
                
                if result and result.strip():
                    return jsonify({
                        'success': True,
                        'response': result,
                        'type': 'rivescript_fallback',
                        'confidence': 0.7,
                        'flow_name': 'RiveScript Engine'
                    }), 200
                else:
                    return jsonify({
                        'success': True,
                        'response': 'No entiendo tu mensaje. ¿Podrías reformularlo?',
                        'type': 'default_fallback',
                        'confidence': 0.1,
                        'flow_name': 'Respuesta por defecto'
                    }), 200
                    
            except Exception as rs_error:
                logger.error(f"Error en RiveScript fallback: {rs_error}")
                return jsonify({
                    'success': False,
                    'error': f'Error procesando mensaje: {str(rs_error)}'
                }), 500
        
    except Exception as e:
        logger.error(f"Error en chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/reload', methods=['POST'])
def reload_rivescript():
    """Recargar todos los flujos en el chatbot"""
    try:
        rivescript_service = RiveScriptService()
        success = rivescript_service.reload_flows_from_database()
        
        if success:
            logger.info("Flujos RiveScript recargados desde base de datos")
            
            # Obtener número de flujos activos directamente
            try:
                flow_repo = FlowRepository()
                active_flows = flow_repo.get_active_flows()
                flows_count = len(active_flows)
            except:
                flows_count = 0
            
            return jsonify({
                'status': 'success',
                'message': 'Flujos recargados exitosamente',
                'flows_loaded': flows_count,
                'active_flows': flows_count
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error recargando flujos - revisar logs del servidor'
            }), 500
        
    except Exception as e:
        logger.error(f"Error recargando flujos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error recargando flujos: {str(e)}'
        }), 500

@rivescript_simple_bp.route('/import-files', methods=['POST'])
def import_files():
    """Importar archivos RiveScript desde el directorio static/rivescript"""
    try:
        rivescript_dir = os.path.join('static', 'rivescript')
        
        if not os.path.exists(rivescript_dir):
            return jsonify({
                'status': 'error',
                'message': f'Directorio {rivescript_dir} no encontrado'
            }), 404
        
        imported_count = 0
        flow_repo = FlowRepository()
        
        for filename in os.listdir(rivescript_dir):
            if filename.endswith('.rive'):
                file_path = os.path.join(rivescript_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Crear flujo basado en nombre de archivo
                flow_name = filename.replace('.rive', '').replace('_', ' ').title()
                flow_data = {
                    'name': f"Importado: {flow_name}",
                    'description': f'Importado desde {filename}',
                    'rivescript_content': content,
                    'is_active': False,  # Importar como inactivo por seguridad
                    'priority': 10
                }
                
                flow_repo.create_flow(flow_data)
                imported_count += 1
                logger.info(f"Importado flujo desde {filename}")
        
        return jsonify({
            'status': 'success',
            'message': f'{imported_count} archivos importados exitosamente',
            'imported_count': imported_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error importando archivos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error importando archivos: {str(e)}'
        }), 500

# ========================================
# ENDPOINT DE SALUD DEL API
# ========================================

@rivescript_simple_bp.route('/health', methods=['GET'])
def health_check():
    """Health check del API RiveScript"""
    try:
        flow_repo = FlowRepository()
        total_flows = len(flow_repo.get_all_flows())
        
        return jsonify({
            'status': 'healthy',
            'service': 'RiveScript API',
            'total_flows': total_flows,
            'endpoints': [
                'GET /flows - Obtener flujos',
                'POST /flows - Crear flujo',
                'GET /flows/<id> - Obtener flujo específico',
                'PUT /flows/<id> - Actualizar flujo',
                'DELETE /flows/<id> - Eliminar flujo',
                'POST /test - Probar contenido RiveScript',
                'POST /test-flow - Probar flujo específico',
                'POST /reload - Recargar flujos en chatbot',
                'POST /import-files - Importar archivos .rive',
                'GET /health - Health check'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
