# app/api/flows/__init__.py - Nuevo archivo
# filepath: e:\DSW\proyectos\proy04\app\api\flows\__init__.py

from flask import Blueprint
from flask_restx import Api

# Crear blueprint
flows_bp = Blueprint('flows', __name__)

# Crear API namespace
flows_api = Api(flows_bp, 
               title='Chatbot Flows API',
               version='1.0',
               description='API para gestión de flujos de conversación',
               doc='/docs/')

# Importar recursos después de crear la API para evitar imports circulares
from app.api.flows import routes