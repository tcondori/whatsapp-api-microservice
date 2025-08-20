"""
Endpoints de webhooks de WhatsApp
Maneja la recepción y procesamiento de webhooks de WhatsApp Business API
"""
from flask import request, jsonify
from flask_restx import Resource, Namespace
import logging

from app.services.webhook_processor import WebhookProcessor
from app.services.whatsapp_api import WhatsAppAPIService
from app.private.auth import require_webhook_verification
from app.utils.exceptions import WhatsAppAPIError, ValidationError
from app.utils.helpers import create_success_response, create_error_response

# Crear namespace para webhooks
webhook_ns = Namespace('webhooks', description='Endpoints de webhook de WhatsApp')

# Inicializar servicios
webhook_processor = WebhookProcessor()
whatsapp_api = WhatsAppAPIService()
logger = logging.getLogger(__name__)


@webhook_ns.route('')
class WebhookEndpoint(Resource):
    """Endpoint principal para webhooks de WhatsApp"""
    
    @webhook_ns.doc('webhook_verification')
    def get(self):
        """
        Verificación inicial del webhook de WhatsApp
        Endpoint GET utilizado por WhatsApp para verificar la URL del webhook
        """
        try:
            # Obtener parámetros de verificación
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            logger.info(f"Recibida solicitud de verificación de webhook: mode={mode}, token={token}")
            
            # Verificar modo y token
            if mode == 'subscribe' and token == whatsapp_api.config.WEBHOOK_VERIFY_TOKEN:
                logger.info("Verificación de webhook exitosa")
                return challenge, 200
            else:
                logger.warning(f"Verificación de webhook fallida: mode={mode}, token válido={token == whatsapp_api.config.WEBHOOK_VERIFY_TOKEN}")
                return {'error': 'Forbidden'}, 403
                
        except Exception as e:
            logger.error(f"Error en verificación de webhook: {e}")
            return create_error_response("Error interno del servidor", 500), 500
    
    @webhook_ns.doc('webhook_handler')
    def post(self):
        """
        Procesa webhooks de WhatsApp
        Endpoint POST que recibe eventos de WhatsApp Business API
        """
        try:
            # Obtener firma del webhook
            signature = request.headers.get('X-Hub-Signature-256')
            payload = request.get_data()
            
            # Verificar firma del webhook
            if not whatsapp_api.verify_webhook_signature(payload, signature):
                logger.warning("Firma de webhook inválida")
                return create_error_response("Firma inválida", 401), 401
            
            # Obtener datos del webhook
            webhook_data = request.get_json()
            
            if not webhook_data:
                logger.warning("Webhook recibido sin datos")
                return create_error_response("Datos de webhook faltantes", 400), 400
            
            logger.info(f"Webhook recibido: {webhook_data.get('object', 'unknown')}")
            
            # Procesar webhook
            success = webhook_processor.process_webhook(webhook_data)
            
            if success:
                logger.info("Webhook procesado exitosamente")
                return create_success_response(message="Webhook procesado exitosamente"), 200
            else:
                logger.error("Error procesando webhook")
                return create_error_response("Error procesando webhook", 500), 500
                
        except ValidationError as e:
            logger.warning(f"Error de validación en webhook: {e}")
            return create_error_response(str(e), 400), 400
        except WhatsAppAPIError as e:
            logger.error(f"Error de WhatsApp API en webhook: {e}")
            return create_error_response(str(e), 500), 500
        except Exception as e:
            logger.error(f"Error inesperado en webhook: {e}")
            return create_error_response("Error interno del servidor", 500), 500


@webhook_ns.route('/health')
class WebhookHealthCheck(Resource):
    """Health check para webhooks"""
    
    @webhook_ns.doc('webhook_health')
    def get(self):
        """
        Verifica el estado del sistema de webhooks
        """
        try:
            health_data = {
                'webhook_processor': 'active',
                'whatsapp_api_service': 'active',
                'webhook_verify_token_configured': bool(whatsapp_api.config.WEBHOOK_VERIFY_TOKEN),
                'webhook_secret_configured': bool(whatsapp_api.config.WEBHOOK_SECRET),
                'access_token_configured': bool(whatsapp_api.config.WHATSAPP_ACCESS_TOKEN),
                'timestamp': webhook_processor.logger.handlers[0].format(
                    webhook_processor.logger.makeRecord(
                        'health', 20, __file__, 0, 'Health check', (), None
                    )
                ) if webhook_processor.logger.handlers else None
            }
            
            return create_success_response(
                data=health_data,
                message="Sistema de webhooks operativo"
            ), 200
            
        except Exception as e:
            logger.error(f"Error en health check de webhooks: {e}")
            return create_error_response("Error en health check", 500), 500


@webhook_ns.route('/test')
class WebhookTestEndpoint(Resource):
    """Endpoint de prueba para webhooks"""
    
    @webhook_ns.doc('webhook_test')
    def post(self):
        """
        Endpoint de prueba para simular webhooks
        Útil para desarrollo y testing
        """
        try:
            # Solo disponible en desarrollo
            from flask import current_app
            if current_app.config.get('DEBUG') or current_app.config.get('TESTING'):
                webhook_data = request.get_json()
                
                if not webhook_data:
                    return create_error_response("Datos de prueba requeridos", 400), 400
                
                logger.info("Procesando webhook de prueba")
                
                # Procesar webhook de prueba
                success = webhook_processor.process_webhook(webhook_data)
                
                if success:
                    return create_success_response(message="Webhook de prueba procesado exitosamente"), 200
                else:
                    return create_error_response("Error procesando webhook de prueba", 500), 500
            else:
                return create_error_response("Endpoint de prueba no disponible en producción", 403), 403
                
        except Exception as e:
            logger.error(f"Error en webhook de prueba: {e}")
            return create_error_response("Error interno del servidor", 500), 500


# Endpoints específicos por línea (opcional)
@webhook_ns.route('/<string:line_id>')
class LineSpecificWebhook(Resource):
    """Webhook específico para una línea de mensajería"""
    
    @webhook_ns.doc('line_webhook_handler')
    def post(self, line_id):
        """
        Procesa webhook para una línea específica
        Args:
            line_id: ID de la línea de mensajería
        """
        try:
            # Obtener firma del webhook
            signature = request.headers.get('X-Hub-Signature-256')
            payload = request.get_data()
            
            # Verificar firma del webhook
            if not whatsapp_api.verify_webhook_signature(payload, signature):
                logger.warning(f"Firma de webhook inválida para línea {line_id}")
                return create_error_response("Firma inválida", 401), 401
            
            # Obtener datos del webhook
            webhook_data = request.get_json()
            
            if not webhook_data:
                logger.warning(f"Webhook para línea {line_id} recibido sin datos")
                return create_error_response("Datos de webhook faltantes", 400), 400
            
            logger.info(f"Webhook recibido para línea {line_id}")
            
            # Procesar webhook
            success = webhook_processor.process_webhook(webhook_data)
            
            if success:
                logger.info(f"Webhook para línea {line_id} procesado exitosamente")
                return create_success_response(
                    message=f"Webhook para línea {line_id} procesado exitosamente"
                ), 200
            else:
                logger.error(f"Error procesando webhook para línea {line_id}")
                return create_error_response(f"Error procesando webhook para línea {line_id}", 500), 500
                
        except ValidationError as e:
            logger.warning(f"Error de validación en webhook de línea {line_id}: {e}")
            return create_error_response(str(e), 400), 400
        except WhatsAppAPIError as e:
            logger.error(f"Error de WhatsApp API en webhook de línea {line_id}: {e}")
            return create_error_response(str(e), 500), 500
        except Exception as e:
            logger.error(f"Error inesperado en webhook de línea {line_id}: {e}")
            return create_error_response("Error interno del servidor", 500), 500
