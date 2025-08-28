# app/api/rivescript.py
from flask_restx import Namespace, Resource, fields
from flask import request

api = Namespace('rivescript', description='Operaciones de RiveScript')

# Modelo para respuestas
flow_model = api.model('Flow', {
    'id': fields.String(required=True, description='ID del flujo'),
    'name': fields.String(required=True, description='Nombre del flujo'),
    'content': fields.String(required=True, description='Contenido del flujo'),
    'created_at': fields.DateTime(description='Fecha de creación')
})

@api.route('/flows')
class FlowList(Resource):
    @api.doc('list_flows')
    @api.marshal_list_with(flow_model)
    def get(self):
        """Obtiene lista de flujos disponibles"""
        # Implementación temporal - reemplaza con tu lógica
        flows = [
            {
                'id': '1',
                'name': 'Saludo básico',
                'content': '+ hola\n- ¡Hola! ¿En qué puedo ayudarte?',
                'created_at': '2024-01-01T00:00:00Z'
            }
        ]
        return flows
    
    @api.doc('create_flow')
    @api.expect(flow_model)
    @api.marshal_with(flow_model, code=201)
    def post(self):
        """Crea un nuevo flujo"""
        data = request.json
        # Implementación temporal - reemplaza con tu lógica
        new_flow = {
            'id': '2',
            'name': data.get('name', 'Nuevo flujo'),
            'content': data.get('content', ''),
            'created_at': '2024-01-01T00:00:00Z'
        }
        return new_flow, 201