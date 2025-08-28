# app/api/rivescript_api.py
# filepath: e:\DSW\proyectos\proy04\app\api\rivescript_api.py

from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime
import os
import json

from app.services.rivescript_service import RiveScriptService
from app.services.chatbot_service import ChatbotService
from app.repositories.flow_repository import FlowRepository
from app.utils.logger import WhatsAppLogger

# Crear blueprint
rivescript_bp = Blueprint('rivescript', __name__, url_prefix='/rivescript')
api = Api(rivescript_bp, doc='/doc/', title='RiveScript API', version='1.0')

# Namespace para RiveScript
ns = Namespace('rivescript', description='Operaciones del editor RiveScript')
api.add_namespace(ns)

logger = WhatsAppLogger.get_logger('rivescript_api')

# ========================================
# MODELOS DE DATOS PARA SWAGGER
# ========================================

# Modelo para flujo RiveScript
flow_model = api.model('RiveScriptFlow', {
    'id': fields.Integer(description='ID del flujo'),
    'name': fields.String(required=True, description='Nombre del flujo'),
    'category': fields.String(required=True, description='Categoría del flujo'),
    'rivescript_content': fields.String(required=True, description='Contenido RiveScript'),
    'is_active': fields.Boolean(default=True, description='Si el flujo está activo'),
    'created_at': fields.DateTime(description='Fecha de creación'),
    'updated_at': fields.DateTime(description='Fecha de actualización')
})

# Modelo para crear/actualizar flujo
flow_input_model = api.model('RiveScriptFlowInput', {
    'name': fields.String(required=True, description='Nombre del flujo'),
    'category': fields.String(required=True, description='Categoría del flujo'),
    'rivescript_content': fields.String(required=True, description='Contenido RiveScript'),
    'is_active': fields.Boolean(default=True, description='Si el flujo está activo')
})

# Modelo para prueba de RiveScript
test_input_model = api.model('RiveScriptTestInput', {
    'rivescript_content': fields.String(required=True, description='Contenido RiveScript a probar'),
    'message': fields.String(required=True, description='Mensaje de prueba'),
    'phone_number': fields.String(default='test_user', description='Número de prueba')
})

# Modelo para prueba de flujo
test_flow_input_model = api.model('RiveScriptTestFlowInput', {
    'flow_id': fields.Integer(description='ID del flujo a probar'),
    'message': fields.String(required=True, description='Mensaje de prueba'),
    'phone_number': fields.String(default='test_user', description='Número de prueba')
})

# ========================================
# ENDPOINTS DEL API
# ========================================

@ns.route('/flows')
class FlowListResource(Resource):
    """Gestión de flujos RiveScript"""
    
    @api.marshal_list_with(flow_model)
    def get(self):
        """Obtener todos los flujos RiveScript"""
        try:
            flow_repo = FlowRepository()
            flows = flow_repo.get_all_flows()
            
            flows_data = []
            for flow in flows:
                flows_data.append({
                    'id': flow.id,
                    'name': flow.name,
                    'category': flow.category,
                    'rivescript_content': flow.rivescript_content,
                    'is_active': flow.is_active,
                    'created_at': flow.created_at,
                    'updated_at': flow.updated_at
                })
            
            return {
                'status': 'success',
                'flows': flows_data,
                'total': len(flows_data)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo flujos: {e}")
            return {
                'status': 'error',
                'message': f'Error obteniendo flujos: {str(e)}'
            }, 500
    
    @api.expect(flow_input_model)
    @api.marshal_with(flow_model)
    def post(self):
        """Crear nuevo flujo RiveScript"""
        try:
            data = request.get_json()
            flow_repo = FlowRepository()
            
            # Validar datos requeridos
            if not data.get('name') or not data.get('rivescript_content'):
                return {
                    'status': 'error',
                    'message': 'Nombre y contenido RiveScript son requeridos'
                }, 400
            
            # Crear flujo
            flow_data = {
                'name': data['name'],
                'category': data.get('category', 'general'),
                'rivescript_content': data['rivescript_content'],
                'is_active': data.get('is_active', True),
                'created_by': 'editor_web'  # Identificar origen
            }
            
            flow = flow_repo.create_flow(flow_data)
            
            if flow:
                # Recargar flujos en el servicio RiveScript
                try:
                    rivescript_service = RiveScriptService()
                    rivescript_service.reload_flows_from_database()
                except Exception as reload_error:
                    logger.warning(f"Error recargando flujos después de crear: {reload_error}")
                
                return {
                    'status': 'success',
                    'message': 'Flujo creado correctamente',
                    'flow': {
                        'id': flow.id,
                        'name': flow.name,
                        'category': flow.category,
                        'rivescript_content': flow.rivescript_content,
                        'is_active': flow.is_active,
                        'created_at': flow.created_at,
                        'updated_at': flow.updated_at
                    }
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Error creando flujo'
                }, 500
                
        except Exception as e:
            logger.error(f"Error creando flujo: {e}")
            return {
                'status': 'error',
                'message': f'Error creando flujo: {str(e)}'
            }, 500

@ns.route('/flows/<int:flow_id>')
class FlowResource(Resource):
    """Gestión de flujo específico"""
    
    @api.marshal_with(flow_model)
    def get(self, flow_id):
        """Obtener flujo específico por ID"""
        try:
            flow_repo = FlowRepository()
            flow = flow_repo.get_by_id(flow_id)
            
            if not flow:
                return {
                    'status': 'error',
                    'message': f'Flujo con ID {flow_id} no encontrado'
                }, 404
            
            return {
                'status': 'success',
                'flow': {
                    'id': flow.id,
                    'name': flow.name,
                    'category': flow.category,
                    'rivescript_content': flow.rivescript_content,
                    'is_active': flow.is_active,
                    'created_at': flow.created_at,
                    'updated_at': flow.updated_at
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo flujo {flow_id}: {e}")
            return {
                'status': 'error',
                'message': f'Error obteniendo flujo: {str(e)}'
            }, 500
    
    @api.expect(flow_input_model)
    @api.marshal_with(flow_model)
    def put(self, flow_id):
        """Actualizar flujo existente"""
        try:
            data = request.get_json()
            flow_repo = FlowRepository()
            
            # Verificar que el flujo existe
            existing_flow = flow_repo.get_by_id(flow_id)
            if not existing_flow:
                return {
                    'status': 'error',
                    'message': f'Flujo con ID {flow_id} no encontrado'
                }, 404
            
            # Actualizar flujo
            update_data = {
                'name': data.get('name', existing_flow.name),
                'category': data.get('category', existing_flow.category),
                'rivescript_content': data.get('rivescript_content', existing_flow.rivescript_content),
                'is_active': data.get('is_active', existing_flow.is_active),
                'updated_at': datetime.utcnow()
            }
            
            success = flow_repo.update_flow(flow_id, update_data)
            
            if success:
                # Obtener flujo actualizado
                updated_flow = flow_repo.get_by_id(flow_id)
                
                # Recargar flujos en el servicio RiveScript
                try:
                    rivescript_service = RiveScriptService()
                    rivescript_service.reload_flows_from_database()
                except Exception as reload_error:
                    logger.warning(f"Error recargando flujos después de actualizar: {reload_error}")
                
                return {
                    'status': 'success',
                    'message': 'Flujo actualizado correctamente',
                    'flow': {
                        'id': updated_flow.id,
                        'name': updated_flow.name,
                        'category': updated_flow.category,
                        'rivescript_content': updated_flow.rivescript_content,
                        'is_active': updated_flow.is_active,
                        'created_at': updated_flow.created_at,
                        'updated_at': updated_flow.updated_at
                    }
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Error actualizando flujo'
                }, 500
                
        except Exception as e:
            logger.error(f"Error actualizando flujo {flow_id}: {e}")
            return {
                'status': 'error',
                'message': f'Error actualizando flujo: {str(e)}'
            }, 500
    
    def delete(self, flow_id):
        """Eliminar flujo"""
        try:
            flow_repo = FlowRepository()
            
            # Verificar que el flujo existe
            existing_flow = flow_repo.get_by_id(flow_id)
            if not existing_flow:
                return {
                    'status': 'error',
                    'message': f'Flujo con ID {flow_id} no encontrado'
                }, 404
            
            # Eliminar flujo
            success = flow_repo.delete_flow(flow_id)
            
            if success:
                # Recargar flujos en el servicio RiveScript
                try:
                    rivescript_service = RiveScriptService()
                    rivescript_service.reload_flows_from_database()
                except Exception as reload_error:
                    logger.warning(f"Error recargando flujos después de eliminar: {reload_error}")
                
                return {
                    'status': 'success',
                    'message': 'Flujo eliminado correctamente'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Error eliminando flujo'
                }, 500
                
        except Exception as e:
            logger.error(f"Error eliminando flujo {flow_id}: {e}")
            return {
                'status': 'error',
                'message': f'Error eliminando flujo: {str(e)}'
            }, 500

@ns.route('/test')
class RiveScriptTestResource(Resource):
    """Prueba de contenido RiveScript"""
    
    @api.expect(test_input_model)
    def post(self):
        """Probar contenido RiveScript directamente"""
        try:
            data = request.get_json()
            
            if not data.get('rivescript_content') or not data.get('message'):
                return {
                    'status': 'error',
                    'message': 'Contenido RiveScript y mensaje son requeridos'
                }, 400
            
            # Crear servicio temporal para prueba
            rivescript_service = RiveScriptService()
            
            # Probar contenido RiveScript
            response = rivescript_service.test_rivescript_content(
                rivescript_content=data['rivescript_content'],
                message=data['message'],
                phone_number=data.get('phone_number', 'test_user')
            )
            
            return {
                'status': 'success',
                'response': response,
                'test_data': {
                    'input_message': data['message'],
                    'phone_number': data.get('phone_number', 'test_user'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error probando RiveScript: {e}")
            return {
                'status': 'error',
                'message': f'Error probando RiveScript: {str(e)}'
            }, 500

@ns.route('/test-flow')
class RiveScriptTestFlowResource(Resource):
    """Prueba de flujo específico"""
    
    @api.expect(test_flow_input_model)
    def post(self):
        """Probar flujo específico por ID"""
        try:
            data = request.get_json()
            
            if not data.get('message'):
                return {
                    'status': 'error',
                    'message': 'Mensaje es requerido'
                }, 400
            
            # Usar servicio de chatbot para probar
            chatbot_service = ChatbotService()
            
            response = chatbot_service.test_chatbot_response(
                message=data['message'],
                phone_number=data.get('phone_number', 'test_user'),
                flow_id=data.get('flow_id')
            )
            
            return {
                'status': 'success',
                'response': response,
                'test_data': {
                    'input_message': data['message'],
                    'phone_number': data.get('phone_number', 'test_user'),
                    'flow_id': data.get('flow_id'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error probando flujo: {e}")
            return {
                'status': 'error',
                'message': f'Error probando flujo: {str(e)}'
            }, 500

@ns.route('/reload')
class RiveScriptReloadResource(Resource):
    """Recarga de flujos en el chatbot"""
    
    def post(self):
        """Recargar todos los flujos en el servicio RiveScript"""
        try:
            rivescript_service = RiveScriptService()
            success = rivescript_service.reload_flows_from_database()
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Flujos recargados correctamente en el chatbot',
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Error recargando flujos en el chatbot'
                }, 500
                
        except Exception as e:
            logger.error(f"Error recargando flujos: {e}")
            return {
                'status': 'error',
                'message': f'Error recargando flujos: {str(e)}'
            }, 500

@ns.route('/import-files')
class RiveScriptImportResource(Resource):
    """Importar archivos RiveScript del sistema de archivos"""
    
    def post(self):
        """Importar archivos .rive del directorio static/rivescript a la BD"""
        try:
            flow_repo = FlowRepository()
            rivescript_dir = os.path.join('static', 'rivescript')
            
            if not os.path.exists(rivescript_dir):
                return {
                    'status': 'error',
                    'message': f'Directorio {rivescript_dir} no encontrado'
                }, 404
            
            imported_flows = []
            errors = []
            
            # Buscar archivos .rive
            for filename in os.listdir(rivescript_dir):
                if not filename.endswith('.rive'):
                    continue
                
                try:
                    filepath = os.path.join(rivescript_dir, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    # Crear flujo en BD
                    flow_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    
                    flow_data = {
                        'name': flow_name,
                        'category': 'imported',
                        'rivescript_content': content,
                        'is_active': True,
                        'created_by': 'file_import'
                    }
                    
                    # Verificar si ya existe
                    existing = flow_repo.get_by_name(flow_name)
                    if existing:
                        # Actualizar contenido
                        flow_repo.update_flow(existing.id, {
                            'rivescript_content': content,
                            'updated_at': datetime.utcnow()
                        })
                        imported_flows.append(f"Actualizado: {flow_name}")
                    else:
                        # Crear nuevo
                        new_flow = flow_repo.create_flow(flow_data)
                        if new_flow:
                            imported_flows.append(f"Creado: {flow_name}")
                        else:
                            errors.append(f"Error creando: {flow_name}")
                
                except Exception as file_error:
                    errors.append(f"Error procesando {filename}: {str(file_error)}")
            
            # Recargar flujos
            try:
                rivescript_service = RiveScriptService()
                rivescript_service.reload_flows_from_database()
            except Exception as reload_error:
                errors.append(f"Error recargando flujos: {str(reload_error)}")
            
            return {
                'status': 'success',
                'message': f'Importación completada: {len(imported_flows)} flujos procesados',
                'imported_flows': imported_flows,
                'errors': errors,
                'total_imported': len(imported_flows),
                'total_errors': len(errors)
            }
            
        except Exception as e:
            logger.error(f"Error importando archivos RiveScript: {e}")
            return {
                'status': 'error',
                'message': f'Error importando archivos: {str(e)}'
            }, 500

# ========================================
# FUNCIÓN AUXILIAR PARA FETCHAPI
# ========================================

def register_rivescript_blueprint(app):
    """Registrar blueprint de RiveScript en la aplicación"""
    app.register_blueprint(rivescript_bp)
    logger.info("Blueprint RiveScript registrado correctamente")
