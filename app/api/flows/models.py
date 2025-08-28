# app/api/flows/models.py - Nuevo archivo
# filepath: e:\DSW\proyectos\proy04\app\api\flows\models.py

from flask_restx import fields
from app.api.flows import flows_api

# Modelo para crear/actualizar flujos
FLOW_FIELDS = flows_api.model('ConversationFlow', {
    'name': fields.String(required=True, description='Nombre del flujo', example='Flujo de Atención al Cliente'),
    'description': fields.String(description='Descripción del flujo', example='Flujo básico para atender consultas de clientes'),
    'rivescript_content': fields.String(required=True, description='Contenido RiveScript del flujo'),
    'is_active': fields.Boolean(description='Si el flujo está activo', default=False),
    'is_default': fields.Boolean(description='Si es el flujo por defecto', default=False),
    'priority': fields.Integer(description='Prioridad del flujo (menor = mayor prioridad)', default=1),
    'fallback_to_llm': fields.Boolean(description='Si usar LLM como fallback', default=True),
    'max_context_messages': fields.Integer(description='Máximo de mensajes en contexto', default=5)
})

# Modelo de respuesta de flujo
FLOW_RESPONSE = flows_api.model('FlowResponse', {
    'id': fields.Integer(description='ID del flujo'),
    'name': fields.String(description='Nombre del flujo'),
    'description': fields.String(description='Descripción del flujo'),
    'rivescript_content': fields.String(description='Contenido RiveScript'),
    'is_active': fields.Boolean(description='Si está activo'),
    'is_default': fields.Boolean(description='Si es por defecto'),
    'priority': fields.Integer(description='Prioridad'),
    'usage_count': fields.Integer(description='Número de veces usado'),
    'created_at': fields.String(description='Fecha de creación'),
    'updated_at': fields.String(description='Fecha de actualización')
})

# Modelo para testing de flujos
FLOW_TEST_REQUEST = flows_api.model('FlowTestRequest', {
    'rivescript_content': fields.String(required=True, description='Contenido RiveScript para probar'),
    'test_message': fields.String(required=True, description='Mensaje de prueba', example='hola'),
    'user_vars': fields.Raw(description='Variables de usuario para la prueba', example={'name': 'Juan', 'age': '25'})
})

# Modelo de respuesta del test
FLOW_TEST_RESPONSE = flows_api.model('FlowTestResponse', {
    'success': fields.Boolean(description='Si la prueba fue exitosa'),
    'response': fields.String(description='Respuesta del flujo'),
    'user_vars': fields.Raw(description='Variables de usuario después del test'),
    'valid_response': fields.Boolean(description='Si la respuesta es válida'),
    'test_message': fields.String(description='Mensaje que se probó'),
    'error': fields.String(description='Error si ocurrió alguno')
})

# Modelo para lista de flujos
FLOWS_LIST_RESPONSE = flows_api.model('FlowsListResponse', {
    'flows': fields.List(fields.Nested(FLOW_RESPONSE), description='Lista de flujos'),
    'total': fields.Integer(description='Total de flujos'),
    'active_count': fields.Integer(description='Número de flujos activos')
})