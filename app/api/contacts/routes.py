"""
Endpoints básicos de contactos para WhatsApp
"""
from flask_restx import Resource, Namespace

from app.utils.helpers import create_success_response

# Crear namespace para contactos
contacts_ns = Namespace('contacts', description='API de contactos de WhatsApp')


@contacts_ns.route('/health')
class ContactsHealthCheck(Resource):
    """Health check para contactos"""
    
    @contacts_ns.doc('contacts_health')
    def get(self):
        """
        Verifica el estado del módulo de contactos
        """
        return create_success_response(
            data={'status': 'active'},
            message="Módulo de contactos operativo"
        ), 200
