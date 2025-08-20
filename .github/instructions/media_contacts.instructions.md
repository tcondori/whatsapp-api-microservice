# Media and Contacts Instructions
<!-- Instrucciones para manejo de medios y contactos en WhatsApp API -->

## Resumen del Archivo
<!-- Este archivo contiene las instrucciones para implementar el sistema completo de gestión de medios y contactos, incluyendo:
- Upload y download de archivos multimedia (imágenes, videos, documentos, audio)
- Validación de tipos de archivo, tamaños y compresión automática
- Gestión completa de contactos con perfiles, bloqueo y sincronización
- Integración con servicios de almacenamiento (local, AWS S3, Google Cloud)
- APIs para operaciones CRUD de contactos y archivos multimedia
- Manejo de metadata, thumbnails y optimización de archivos
-->

## Media Handling
<!-- Manejo de archivos multimedia -->

### Supported Media Types
- Images: JPEG, PNG, WebP (max 5MB)
- Videos: MP4, 3GPP (max 16MB)
- Audio: AAC, M4A, AMR, MP3, OGG (max 16MB)
- Documents: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX (max 100MB)
- Stickers: WebP format only

### Media Upload Flow
```python
# Subir archivo multimedia
def upload_media(file_path, media_type):
    """
    Sube un archivo multimedia a WhatsApp
    Args:
        file_path: Ruta del archivo
        media_type: Tipo de medio (image, video, audio, document)
    """
    pass
```

### Media Download Flow
```python
# Descargar archivo multimedia
def download_media(media_id, local_path):
    """
    Descarga un archivo multimedia desde WhatsApp
    Args:
        media_id: ID del medio en WhatsApp
        local_path: Ruta local para guardar
    """
    pass
```

## Contact Management
<!-- Gestión de contactos -->

### Contact Operations
- Retrieve contact info
- Update contact status
- Block/unblock contacts
- Contact profile management

### Contact Data Structure
```python
class ContactInfo:
    """Información de contacto de WhatsApp"""
    phone_number: str  # Número de teléfono
    display_name: str  # Nombre mostrado
    profile_pic_url: str  # URL de foto de perfil
    status: str  # Estado del contacto
    last_seen: datetime  # Última conexión
```

### Contact Validation
- Phone number format validation (E.164)
- WhatsApp Business account verification
- Contact existence verification

## File Storage Integration
<!-- Integración con almacenamiento de archivos -->

### Storage Requirements
- Secure media storage (AWS S3, Google Cloud Storage)
- Temporary file cleanup
- Media URL generation with expiration
- Backup and retention policies

### Security Considerations
- File type validation and sanitization
- Virus scanning for uploaded files
- Access control and permissions
- Encryption at rest and in transit
