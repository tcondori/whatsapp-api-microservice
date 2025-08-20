"""
Servicio principal para integración con WhatsApp Business API
Maneja autenticación, envío de mensajes y llamadas a la API externa
"""
import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import hmac
import hashlib
from flask import current_app

from app.utils.exceptions import WhatsAppAPIError, ValidationError


class WhatsAppAPIService:
    """Servicio para integración con WhatsApp Business API"""
    
    def __init__(self):
        """Inicializa el servicio de WhatsApp API"""
        self.logger = logging.getLogger(__name__)
        
        # Usar la configuración de la aplicación Flask actual
        try:
            if current_app:
                self.config = current_app.config
                self.base_url = self.config.get('WHATSAPP_API_BASE_URL', 'https://graph.facebook.com')
                self.api_version = self.config.get('WHATSAPP_API_VERSION', 'v18.0')
                self.access_token = self.config.get('WHATSAPP_ACCESS_TOKEN')
            else:
                raise RuntimeError("No current app")
        except RuntimeError:
            # Fallback para testing o inicialización
            from config.default import DefaultConfig
            self.config = DefaultConfig()
            self.base_url = getattr(self.config, 'WHATSAPP_API_BASE_URL', 'https://graph.facebook.com')
            self.api_version = getattr(self.config, 'WHATSAPP_API_VERSION', 'v18.0')
            self.access_token = getattr(self.config, 'WHATSAPP_ACCESS_TOKEN', None)
        
        if not self.access_token:
            self.logger.warning("WhatsApp Access Token no configurado. Solo modo simulación disponible.")
    
    def _make_api_request(self, endpoint: str, method: str = 'POST', data: Dict[str, Any] = None, 
                         phone_number_id: str = None) -> Dict[str, Any]:
        """
        Realiza una petición a la API de WhatsApp
        Args:
            endpoint: Endpoint de la API (ej: 'messages', 'media')
            method: Método HTTP (GET, POST, etc.)
            data: Datos a enviar en el cuerpo de la petición
            phone_number_id: ID del número de teléfono para la petición
        Returns:
            dict: Respuesta de la API
        """
        if not self.access_token:
            raise WhatsAppAPIError("Access Token de WhatsApp no configurado")
        
        # Construir URL
        if phone_number_id:
            url = f"{self.base_url}/{self.api_version}/{phone_number_id}/{endpoint}"
        else:
            url = f"{self.base_url}/{self.api_version}/{endpoint}"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            self.logger.info(f"Realizando petición {method} a WhatsApp API: {url}")
            
            # Realizar petición
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise WhatsAppAPIError(f"Método HTTP no soportado: {method}")
            
            # Verificar respuesta
            response.raise_for_status()
            response_data = response.json()
            
            self.logger.info(f"Respuesta exitosa de WhatsApp API: {response.status_code}")
            return response_data
            
        except requests.exceptions.Timeout:
            error_msg = "Timeout en petición a WhatsApp API"
            self.logger.error(error_msg)
            raise WhatsAppAPIError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en petición a WhatsApp API: {str(e)}"
            self.logger.error(error_msg)
            
            # Intentar extraer detalles del error de la respuesta
            try:
                if hasattr(e, 'response') and e.response:
                    error_details = e.response.json()
                    error_msg = f"WhatsApp API Error: {error_details.get('error', {}).get('message', str(e))}"
            except:
                pass
                
            raise WhatsAppAPIError(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado en WhatsApp API: {str(e)}"
            self.logger.error(error_msg)
            raise WhatsAppAPIError(error_msg)
    
    def send_text_message(self, phone_number: str, text: str, phone_number_id: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto vía WhatsApp API
        Args:
            phone_number: Número de destino
            text: Texto del mensaje
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Respuesta de WhatsApp API con message_id
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": text
            }
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)
    
    def send_media_message(self, phone_number: str, media_type: str, media_id: str, 
                          phone_number_id: str, caption: str = None) -> Dict[str, Any]:
        """
        Envía un mensaje multimedia vía WhatsApp API
        Args:
            phone_number: Número de destino
            media_type: Tipo de media ('image', 'video', 'audio', 'document')
            media_id: ID del archivo multimedia
            phone_number_id: ID del número de WhatsApp Business
            caption: Texto adicional (opcional)
        Returns:
            dict: Respuesta de WhatsApp API
        """
        media_data = {"id": media_id}
        if caption and media_type in ['image', 'video', 'document']:
            media_data["caption"] = caption
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": media_type,
            media_type: media_data
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)
    
    def send_template_message(self, phone_number: str, template_name: str, 
                             language_code: str, phone_number_id: str,
                             parameters: List[Dict] = None) -> Dict[str, Any]:
        """
        Envía un mensaje de plantilla vía WhatsApp API
        Args:
            phone_number: Número de destino
            template_name: Nombre de la plantilla
            language_code: Código del idioma (ej: 'es', 'en')
            phone_number_id: ID del número de WhatsApp Business
            parameters: Parámetros de la plantilla (opcional)
        Returns:
            dict: Respuesta de WhatsApp API
        """
        template_data = {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
        
        if parameters:
            template_data["components"] = [
                {
                    "type": "body",
                    "parameters": parameters
                }
            ]
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "template",
            "template": template_data
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)
    
    def send_interactive_message(self, phone_number: str, interactive_type: str,
                                phone_number_id: str, header_text: str = None,
                                body_text: str = None, footer_text: str = None,
                                buttons: List[Dict] = None, sections: List[Dict] = None) -> Dict[str, Any]:
        """
        Envía un mensaje interactivo vía WhatsApp API
        Args:
            phone_number: Número de destino
            interactive_type: Tipo de interactivo ('button', 'list')
            phone_number_id: ID del número de WhatsApp Business
            header_text: Texto del header (opcional)
            body_text: Texto del cuerpo
            footer_text: Texto del footer (opcional)
            buttons: Lista de botones (para tipo 'button')
            sections: Lista de secciones (para tipo 'list')
        Returns:
            dict: Respuesta de WhatsApp API
        """
        interactive_data = {"type": interactive_type}
        
        if header_text:
            interactive_data["header"] = {"type": "text", "text": header_text}
        
        if body_text:
            interactive_data["body"] = {"text": body_text}
        
        if footer_text:
            interactive_data["footer"] = {"text": footer_text}
        
        if interactive_type == "button" and buttons:
            interactive_data["action"] = {"buttons": buttons}
        elif interactive_type == "list" and sections:
            interactive_data["action"] = {"sections": sections}
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": interactive_data
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)
    
    def upload_media(self, file_path: str, phone_number_id: str) -> Dict[str, Any]:
        """
        Sube un archivo multimedia a WhatsApp
        Args:
            file_path: Ruta del archivo
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Respuesta con media_id
        """
        url = f"{self.base_url}/{self.api_version}/{phone_number_id}/media"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'messaging_product': 'whatsapp'}
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            return response.json()
    
    def get_media(self, media_id: str) -> Dict[str, Any]:
        """
        Obtiene información de un archivo multimedia
        Args:
            media_id: ID del archivo multimedia
        Returns:
            dict: Información del archivo
        """
        return self._make_api_request(media_id, 'GET')
    
    def download_media(self, media_url: str) -> bytes:
        """
        Descarga un archivo multimedia
        Args:
            media_url: URL del archivo multimedia
        Returns:
            bytes: Contenido del archivo
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(media_url, headers=headers, timeout=60)
        response.raise_for_status()
        
        return response.content
    
    def mark_message_as_read(self, message_id: str, phone_number_id: str) -> Dict[str, Any]:
        """
        Marca un mensaje como leído
        Args:
            message_id: ID del mensaje
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Respuesta de la API
        """
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verifica la firma de un webhook de WhatsApp
        Args:
            payload: Cuerpo de la petición webhook
            signature: Firma recibida en el header
        Returns:
            bool: True si la firma es válida
        """
        webhook_secret = self.config.get('WEBHOOK_SECRET') if hasattr(self.config, 'get') else getattr(self.config, 'WEBHOOK_SECRET', None)
        
        if not webhook_secret:
            self.logger.warning("Webhook secret no configurado. Saltando verificación de firma.")
            return True
        
        try:
            # WhatsApp envía la firma con prefijo "sha256="
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Calcular firma esperada
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Comparación segura
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Error verificando firma de webhook: {e}")
            return False
    
    def get_business_profile(self, phone_number_id: str) -> Dict[str, Any]:
        """
        Obtiene el perfil del negocio
        Args:
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Información del perfil
        """
        return self._make_api_request('whatsapp_business_profile', 'GET', phone_number_id=phone_number_id)
    
    def update_business_profile(self, phone_number_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza el perfil del negocio
        Args:
            phone_number_id: ID del número de WhatsApp Business
            profile_data: Datos del perfil a actualizar
        Returns:
            dict: Respuesta de la API
        """
        return self._make_api_request('whatsapp_business_profile', 'POST', profile_data, phone_number_id)
