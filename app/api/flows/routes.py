# app/api/flows/routes.py - Nuevo archivo
# filepath: e:\DSW\proyectos\proy04\app\api\flows\routes.py

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.api.flows import flows_api
from app.api.flows.models import (
    FLOW_FIELDS, FLOW_RESPONSE, FLOW_TEST_REQUEST, 
    FLOW_TEST_RESPONSE, FLOWS_LIST_RESPONSE
)
from app.repositories.flow_repository import FlowRepository
from app.services.rivescript_service import RiveScriptService
from app.private.auth import require_api_key
from app.utils.logger import WhatsAppLogger

# Crear namespace
flows_ns = Namespace('flows', description='Gestión de flujos de conversación')
flows_api.add_namespace(flows_ns)

logger = WhatsAppLogger.get_logger('flows_api')

@flows_ns.route('')
class FlowListResource(Resource):
    """Gestión de lista de flujos de conversación"""
    
    @flows_ns.doc('list_flows')
    @flows_ns.marshal_with(FLOWS_LIST_RESPONSE)
    @require_api_key
    def get(self):
        """Obtiene lista de todos los flujos"""
        try:
            flow_repo = FlowRepository()
            flows = flow_repo.get_all_flows()
            active_count = len([f for f in flows if f.is_active])
            
            logger.info(f"Obtenidos {len(flows)} flujos ({active_count} activos)")
            
            return {
                'flows': [flow.to_dict() for flow in flows],
                'total': len(flows),
                'active_count': active_count
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de flujos: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")
    
    @flows_ns.doc('create_flow')
    @flows_ns.expect(FLOW_FIELDS, validate=True)
    @flows_ns.marshal_with(FLOW_RESPONSE)
    @require_api_key
    def post(self):
        """Crea un nuevo flujo de conversación"""
        try:
            data = request.get_json()
            flow_repo = FlowRepository()
            
            # Validar que no exista un flujo con el mismo nombre
            existing_flow = flow_repo.get_by_name(data['name'])
            if existing_flow:
                flows_ns.abort(400, f"Ya existe un flujo con el nombre '{data['name']}'")
            
            # Si se marca como default, desactivar otros defaults
            if data.get('is_default', False):
                current_default = flow_repo.get_default_flow()
                if current_default:
                    current_default.is_default = False
                    flow_repo.update(current_default)
            
            # Crear el flujo
            new_flow = flow_repo.create(**data)
            
            # Recargar flujos en RiveScript si el nuevo flujo está activo
            if data.get('is_active', False):
                rivescript_service = RiveScriptService()
                rivescript_service.reload_flows()
                logger.info(f"Flujos recargados después de crear '{data['name']}'")
            
            logger.info(f"Flujo creado exitosamente: {new_flow.name}")
            
            return new_flow.to_dict()
            
        except Exception as e:
            logger.error(f"Error creando flujo: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")

@flows_ns.route('/<string:flow_id>')
class FlowResource(Resource):
    """Gestión de flujo individual"""
    
    @flows_ns.doc('get_flow')
    @flows_ns.marshal_with(FLOW_RESPONSE)
    @require_api_key
    def get(self, flow_id):
        """Obtiene un flujo específico"""
        try:
            flow_repo = FlowRepository()
            flow = flow_repo.get_by_id(flow_id)
            
            if not flow:
                flows_ns.abort(404, f"Flujo con ID {flow_id} no encontrado")
            
            logger.info(f"Flujo {flow_id} obtenido: {flow.name}")
            return flow.to_dict()
            
        except Exception as e:
            logger.error(f"Error obteniendo flujo {flow_id}: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")
    
    @flows_ns.doc('update_flow')
    @flows_ns.expect(FLOW_FIELDS, validate=True)
    @flows_ns.marshal_with(FLOW_RESPONSE)
    @require_api_key
    def put(self, flow_id):
        """Actualiza un flujo completo"""
        try:
            data = request.get_json()
            flow_repo = FlowRepository()
            
            flow = flow_repo.get_by_id(flow_id)
            if not flow:
                flows_ns.abort(404, f"Flujo con ID {flow_id} no encontrado")
            
            # Validar nombre único (excepto el flujo actual)
            if data.get('name') and data['name'] != flow.name:
                existing_flow = flow_repo.get_by_name(data['name'])
                if existing_flow and existing_flow.id != flow_id:
                    flows_ns.abort(400, f"Ya existe un flujo con el nombre '{data['name']}'")
            
            # Si se marca como default, desactivar otros defaults
            if data.get('is_default', False) and not flow.is_default:
                current_default = flow_repo.get_default_flow()
                if current_default:
                    flow_repo.update_flow(current_default.id, {'is_default': False})
            
            # Actualizar flujo
            success = flow_repo.update_flow(flow_id, data)
            if not success:
                flows_ns.abort(500, "Error actualizando el flujo")
                
            updated_flow = flow_repo.get_by_id(flow_id)
            
            # Recargar flujos si hay cambios en flujos activos
            rivescript_service = RiveScriptService()
            rivescript_service.reload_flows()
            
            logger.info(f"Flujo {flow_id} actualizado: {updated_flow.name}")
            
            return updated_flow.to_dict()
            
        except Exception as e:
            logger.error(f"Error actualizando flujo {flow_id}: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")
    
    @flows_ns.doc('delete_flow')
    @require_api_key
    def delete(self, flow_id):
        """Elimina un flujo"""
        try:
            flow_repo = FlowRepository()
            flow = flow_repo.get_by_id(flow_id)
            
            if not flow:
                flows_ns.abort(404, f"Flujo con ID {flow_id} no encontrado")
            
            # No permitir eliminar el flujo por defecto si está activo
            if flow.is_default and flow.is_active:
                flows_ns.abort(400, "No se puede eliminar un flujo que es por defecto y está activo")
            
            flow_name = flow.name
            flow_repo.delete_flow(flow_id)
            
            # Recargar flujos
            rivescript_service = RiveScriptService()
            rivescript_service.reload_flows()
            
            logger.info(f"Flujo eliminado: {flow_name}")
            
            return {'message': f"Flujo '{flow_name}' eliminado exitosamente"}
            
        except Exception as e:
            logger.error(f"Error eliminando flujo {flow_id}: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")

@flows_ns.route('/<string:flow_id>/activate')
class FlowActivateResource(Resource):
    """Activar/desactivar flujos"""
    
    @flows_ns.doc('activate_flow')
    @flows_ns.marshal_with(FLOW_RESPONSE)
    @require_api_key
    def post(self, flow_id):
        """Activa un flujo"""
        try:
            flow_repo = FlowRepository()
            flow = flow_repo.get_by_id(flow_id)
            
            if not flow:
                flows_ns.abort(404, f"Flujo con ID {flow_id} no encontrado")
            
            flow.is_active = True
            success = flow_repo.update_flow(flow_id, {'is_active': True})
            
            if not success:
                flows_ns.abort(500, "Error activando el flujo")
                
            updated_flow = flow_repo.get_by_id(flow_id)
            
            # Recargar flujos
            rivescript_service = RiveScriptService()
            rivescript_service.reload_flows()
            
            logger.info(f"Flujo activado: {updated_flow.name}")
            
            return updated_flow.to_dict()
            
        except Exception as e:
            logger.error(f"Error activando flujo {flow_id}: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")
    
    @flows_ns.doc('deactivate_flow')
    @flows_ns.marshal_with(FLOW_RESPONSE)
    @require_api_key
    def delete(self, flow_id):
        """Desactiva un flujo"""
        try:
            flow_repo = FlowRepository()
            flow = flow_repo.get_by_id(flow_id)
            
            if not flow:
                flows_ns.abort(404, f"Flujo con ID {flow_id} no encontrado")
            
            flow.is_active = False
            success = flow_repo.update_flow(flow_id, {'is_active': False})
            
            if not success:
                flows_ns.abort(500, "Error desactivando el flujo")
                
            updated_flow = flow_repo.get_by_id(flow_id)
            
            # Recargar flujos
            rivescript_service = RiveScriptService()
            rivescript_service.reload_flows()
            
            logger.info(f"Flujo desactivado: {updated_flow.name}")
            
            return updated_flow.to_dict()
            
        except Exception as e:
            logger.error(f"Error desactivando flujo {flow_id}: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")

@flows_ns.route('/test')
class FlowTestResource(Resource):
    """Testing de flujos de conversación"""
    
    @flows_ns.doc('test_flow')
    @flows_ns.expect(FLOW_TEST_REQUEST, validate=True)
    @flows_ns.marshal_with(FLOW_TEST_RESPONSE)
    @require_api_key
    def post(self):
        """Prueba un flujo de conversación"""
        try:
            data = request.get_json()
            
            rivescript_service = RiveScriptService()
            result = rivescript_service.test_flow_response(
                rivescript_content=data['rivescript_content'],
                test_message=data['test_message'],
                user_vars=data.get('user_vars', {})
            )
            
            logger.info(f"Flujo probado - Mensaje: '{data['test_message']}', Éxito: {result.get('success', False)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error probando flujo: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")

@flows_ns.route('/reload')
class FlowReloadResource(Resource):
    """Recarga de flujos"""
    
    @flows_ns.doc('reload_flows')
    @require_api_key
    def post(self):
        """Recarga todos los flujos activos en RiveScript"""
        try:
            rivescript_service = RiveScriptService()
            success = rivescript_service.reload_flows()
            
            if success:
                logger.info("Flujos recargados exitosamente")
                return {'message': 'Flujos recargados exitosamente', 'success': True}
            else:
                flows_ns.abort(500, "Error recargando flujos")
                
        except Exception as e:
            logger.error(f"Error recargando flujos: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")

@flows_ns.route('/info')
class FlowInfoResource(Resource):
    """Información del sistema de flujos"""
    
    @flows_ns.doc('flow_info')
    @require_api_key
    def get(self):
        """Obtiene información sobre el sistema de flujos"""
        try:
            rivescript_service = RiveScriptService()
            flow_repo = FlowRepository()
            
            info = rivescript_service.get_flow_info()
            stats = flow_repo.get_flow_statistics()
            
            result = {
                **info,
                'statistics': stats
            }
            
            logger.info("Información de flujos obtenida")
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo información de flujos: {e}")
            flows_ns.abort(500, f"Error interno: {str(e)}")