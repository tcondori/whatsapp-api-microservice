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
    
    def send_image_message_direct(self, phone_number: str, image_url: str, 
                                 phone_number_id: str, caption: str = None) -> Dict[str, Any]:
        """
        Envía un mensaje de imagen directamente con URL (formato oficial Meta)
        Args:
            phone_number: Número de destino
            image_url: URL directa de la imagen
            phone_number_id: ID del número de WhatsApp Business
            caption: Texto adicional (opcional)
        Returns:
            dict: Respuesta de WhatsApp API
        """
        image_data = {"link": image_url}
        if caption:
            image_data["caption"] = caption
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "image",
            "image": image_data
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)
    
    def send_contacts_message(self, phone_number: str, contacts_data: List[Dict[str, Any]], 
                             phone_number_id: str) -> Dict[str, Any]:
        """
        Envía un mensaje de contactos vía WhatsApp API
        Args:
            phone_number: Número de destino
            contacts_data: Array de contactos en formato oficial Meta
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Respuesta de WhatsApp API
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "contacts",
            "contacts": contacts_data
        }
        
        return self._make_api_request('messages', 'POST', data, phone_number_id)

    def send_location_message(self, phone_number: str, latitude: float, longitude: float, 
                             phone_number_id: str, name: str = None, address: str = None) -> Dict[str, Any]:
        """
        Envía un mensaje de ubicación vía WhatsApp API
        Args:
            phone_number: Número de destino
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            phone_number_id: ID del número de WhatsApp Business
            name: Nombre del lugar (opcional)
            address: Dirección del lugar (opcional)
        Returns:
            dict: Respuesta de WhatsApp API
        """
        location_data = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Agregar campos opcionales si se proporcionan
        if name:
            location_data["name"] = name
        if address:
            location_data["address"] = address
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "location",
            "location": location_data
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
    
    def send_message(self, payload: Dict[str, Any], phone_number_id: str) -> Dict[str, Any]:
        """
        Método genérico para enviar cualquier tipo de mensaje usando el payload completo
        Args:
            payload: Payload completo del mensaje según formato oficial de Meta
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Respuesta de WhatsApp API
        """
        self.logger.info(f"Enviando mensaje genérico a WhatsApp API: {payload.get('type', 'unknown')}")
        
        try:
            # El payload ya debe estar en el formato correcto de Meta
            return self._make_api_request('messages', 'POST', payload, phone_number_id)
        except Exception as e:
            self.logger.error(f"Error enviando mensaje genérico: {e}")
            # En caso de error, devolver respuesta simulada
            import uuid
            from datetime import datetime, timezone
            timestamp = int(datetime.now(timezone.utc).timestamp())
            
            return {
                "messages": [{
                    "id": f"wamid.sim_{payload.get('type', 'msg')}_{timestamp}_{uuid.uuid4().hex[:8]}"
                }],
                "meta": {
                    "api_status": "stable",
                    "version": self.api_version
                }
            }

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

    def upload_media_file(self, file_content: bytes, filename: str, content_type: str, 
                         phone_number_id: str) -> Dict[str, Any]:
        """
        Sube un archivo multimedia desde contenido en memoria a WhatsApp
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            content_type: Tipo de contenido (image/jpeg, image/png, etc.)
            phone_number_id: ID del número de WhatsApp Business
        Returns:
            dict: Respuesta con media_id
        """
        if not self.access_token:
            # Modo simulación
            import uuid
            fake_media_id = f"fake_upload_{uuid.uuid4().hex[:12]}"
            self.logger.info(f"SIMULACIÓN: Upload de archivo {filename} - Media ID: {fake_media_id}")
            
            return {
                'id': fake_media_id,
                'filename': filename,
                'content_type': content_type,
                'messaging_product': 'whatsapp'
            }
        
        try:
            url = f"{self.base_url}/{self.api_version}/{phone_number_id}/media"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            # Determinar el tipo de media basado en content_type
            media_type = 'image'
            if content_type.startswith('video/'):
                media_type = 'video'
            elif content_type.startswith('audio/'):
                media_type = 'audio'
            elif content_type.startswith('application/'):
                media_type = 'document'
            
            files = {
                'file': (filename, file_content, content_type)
            }
            data = {
                'messaging_product': 'whatsapp',
                'type': media_type
            }
            
            self.logger.info(f"Subiendo archivo {filename} ({content_type}) a WhatsApp API")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Upload exitoso - Media ID: {result.get('id')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error subiendo archivo a WhatsApp: {str(e)}")
            # Fallback a simulación en caso de error
            import uuid
            fake_media_id = f"error_upload_{uuid.uuid4().hex[:12]}"
            
            return {
                'id': fake_media_id,
                'filename': filename,
                'content_type': content_type,
                'messaging_product': 'whatsapp',
                'error': str(e)
            }
        except Exception as e:
            self.logger.error(f"Error inesperado subiendo archivo: {str(e)}")
            raise WhatsAppAPIError(f"Error subiendo archivo: {str(e)}")

    def upload_media_from_url(self, image_url: str, media_type: str = 'image', phone_number_id: str = None) -> Dict[str, Any]:
        """
        Sube un archivo multimedia desde URL a WhatsApp
        Args:
            image_url: URL de la imagen
            media_type: Tipo de media (image, video, audio, document)
            phone_number_id: ID del número de WhatsApp Business (opcional en simulación)
        Returns:
            dict: Respuesta simulada con media_id
        """
        try:
            # En modo simulación, generar respuesta falsa pero válida
            if not self.access_token or self.access_token in ['fake_token', 'test_token']:
                self.logger.info(f"SIMULACIÓN: Subiendo {media_type} desde URL: {image_url}")
                
                # Generar un media_id falso pero válido
                import uuid
                fake_media_id = f"fake_media_{uuid.uuid4().hex[:8]}"
                
                return {
                    'id': fake_media_id,
                    'url': image_url,
                    'messaging_product': 'whatsapp'
                }
            
            # En modo real, descargar imagen y subirla
            # Primero descargar la imagen
            self.logger.info(f"Descargando imagen desde: {image_url}")
            headers = {
                'User-Agent': 'WhatsApp-Bot/1.0'
            }
            
            img_response = requests.get(image_url, headers=headers, timeout=30)
            img_response.raise_for_status()
            
            # Obtener el phone_number_id de la configuración
            if not phone_number_id:
                phone_number_id = self.config.get('WHATSAPP_PHONE_NUMBER_ID')
                
            if not phone_number_id:
                # En modo simulación total
                import uuid
                fake_media_id = f"fake_media_{uuid.uuid4().hex[:8]}"
                self.logger.info(f"SIMULACIÓN: Media ID generado: {fake_media_id}")
                
                return {
                    'id': fake_media_id,
                    'url': image_url,
                    'messaging_product': 'whatsapp'
                }
            
            # Subir a WhatsApp
            url = f"{self.base_url}/{self.api_version}/{phone_number_id}/media"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            # Determinar el tipo de contenido
            content_type = img_response.headers.get('content-type', 'image/jpeg')
            filename = 'image.jpg'
            if 'png' in content_type:
                filename = 'image.png'
            elif 'gif' in content_type:
                filename = 'image.gif'
                
            files = {
                'file': (filename, img_response.content, content_type)
            }
            data = {
                'messaging_product': 'whatsapp',
                'type': media_type
            }
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error subiendo media desde URL: {str(e)}")
            # En caso de error, devolver respuesta simulada
            import uuid
            fake_media_id = f"error_media_{uuid.uuid4().hex[:8]}"
            
            return {
                'id': fake_media_id,
                'url': image_url,
                'messaging_product': 'whatsapp',
                'error': str(e)
            }
    
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
