# Editor RiveScript Integrado - Guía Completa

## 🎯 Descripción

El editor RiveScript integrado permite crear, editar y probar flujos de conversación directamente desde la interfaz web del simulador de chat. Es una herramienta poderosa que facilita el desarrollo y mantenimiento de flujos de chatbot.

## ✨ Características Principales

### 🔧 Editor Completo
- **Editor de código** con syntax highlighting básico
- **Validación en tiempo real** de sintaxis RiveScript
- **Formateo automático** de código
- **Contador de líneas y caracteres**
- **Autocompletado** de patrones comunes

### 🧪 Sistema de Pruebas
- **Pruebas en tiempo real** sin afectar el chatbot principal
- **Pruebas de flujos específicos** por ID
- **Pruebas de contenido directo** sin guardar
- **Historial de pruebas** con resultados detallados

### 💾 Gestión de Flujos
- **CRUD completo** de flujos RiveScript
- **Importación automática** desde archivos .rive
- **Recarga dinámica** del chatbot sin reinicio
- **Categorización** y organización de flujos
- **Estados activo/inactivo** para flujos

### 🔄 Integración con Chat
- **Vista previa en tiempo real** en el simulador
- **Recarga automática** después de cambios
- **Persistencia en base de datos**
- **Sincronización** con el motor RiveScript

## 🚀 Cómo Usar el Editor

### 1. Acceso al Editor
```bash
# Iniciar el servidor
python run_server.py

# Ir a la interfaz web
http://localhost:5001/chat

# Hacer clic en el botón del editor (</>)
```

### 2. Crear un Nuevo Flujo
1. Hacer clic en **"Nuevo"** en el panel del editor
2. Escribir el contenido RiveScript:
```rivescript
// Mi primer flujo
+ hola
- ¡Hola! ¿En qué puedo ayudarte?

+ [*] ayuda [*]
- Estoy aquí para ayudarte con tus consultas.

+ adios
- ¡Hasta luego! Que tengas un buen día.
```
3. Hacer clic en **"Guardar"**
4. Hacer clic en **"Recargar Bot"** para activar los cambios

### 3. Probar Flujos
1. En el panel de **"Pruebas Rápidas"**:
   - Escribir un mensaje de prueba: `"hola"`
   - Hacer clic en **"Probar"**
   - Ver la respuesta generada

2. Probar diferentes mensajes:
   - `"necesito ayuda"`
   - `"como estas"`
   - `"adios"`

### 4. Editar Flujos Existentes
1. Seleccionar flujo del dropdown
2. Modificar el contenido en el editor
3. Usar **"Formatear"** para limpiar el código
4. Usar **"Validar"** para verificar sintaxis
5. **"Guardar"** y **"Recargar Bot"**

## 📝 Sintaxis RiveScript Básica

### Patrones Básicos
```rivescript
// Comentarios
+ trigger exacto
- Respuesta exacta

// Comodines
+ [*] palabra clave [*]
- Respuesta con comodín

// Alternativas
+ (hola|hello|hi)
- Respuesta a saludos

// Variables
+ mi nombre es *
- Mucho gusto, <star>!
```

### Flujos con Topics
```rivescript
+ quiero comprar
- ¿Qué te interesa? {topic=ventas}
^ 1. Productos
^ 2. Servicios

> topic ventas
  + productos
  - Tenemos varios productos...
  
  + servicios  
  - Nuestros servicios incluyen...
< topic
```

### Respuestas Múltiples
```rivescript
+ como estas
- Muy bien, gracias.
- Excelente, ¿y tú?
- Perfecto, ¿cómo puedo ayudarte?
```

## 🔗 API Endpoints

### Flujos
- `GET /rivescript/flows` - Listar todos los flujos
- `POST /rivescript/flows` - Crear nuevo flujo
- `GET /rivescript/flows/{id}` - Obtener flujo específico
- `PUT /rivescript/flows/{id}` - Actualizar flujo
- `DELETE /rivescript/flows/{id}` - Eliminar flujo

### Pruebas
- `POST /rivescript/test` - Probar contenido RiveScript directo
- `POST /rivescript/test-flow` - Probar flujo específico

### Gestión
- `POST /rivescript/reload` - Recargar flujos en el chatbot
- `POST /rivescript/import-files` - Importar archivos .rive

## 🎨 Personalización del Editor

### Colores y Temas
El editor usa CSS personalizado en `static/css/rivescript-editor.css`:

```css
/* Cambiar colores del editor */
.rivescript-editor textarea {
    background-color: #f8f9fa; /* Fondo del editor */
    color: #374151;           /* Color del texto */
}

/* Syntax highlighting */
.rivescript-trigger { color: #059669; } /* Triggers verdes */
.rivescript-response { color: #0ea5e9; } /* Respuestas azules */
.rivescript-comment { color: #6b7280; }  /* Comentarios grises */
```

### Atajos de Teclado
- `Ctrl + S` - Guardar flujo (próximamente)
- `Ctrl + Enter` - Probar mensaje (próximamente)
- `F11` - Pantalla completa del editor (próximamente)

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Habilitar debug del editor
RIVESCRIPT_EDITOR_DEBUG=true

# Ruta de archivos RiveScript
RIVESCRIPT_FILES_PATH=static/rivescript/

# Límite de flujos por usuario
MAX_FLOWS_PER_USER=50
```

### Base de Datos
El editor utiliza la tabla `conversation_flows`:
```sql
CREATE TABLE conversation_flows (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rivescript_content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 1,
    category VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);
```

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. Editor no carga
```bash
# Verificar servidor
curl http://localhost:5001/health

# Verificar endpoints RiveScript
curl http://localhost:5001/rivescript/flows
```

#### 2. Flujos no se guardan
- Verificar permisos de base de datos
- Verificar logs del servidor
- Confirmar sintaxis RiveScript válida

#### 3. Chatbot no responde después de cambios
```bash
# Forzar recarga de flujos
curl -X POST http://localhost:5001/rivescript/reload \
  -H "X-API-Key: dev-api-key"
```

#### 4. Errores de sintaxis RiveScript
- Usar el botón **"Validar"** antes de guardar
- Verificar balance de triggers (+) y respuestas (-)
- Revisar estructura de topics (> y <)

### Logs y Debug
```bash
# Ver logs del editor
tail -f logs/$(date +%Y/%m/%d)/api.log

# Debug en consola del navegador
# F12 -> Console -> buscar errores de JavaScript
```

## 📚 Recursos Adicionales

### Documentación RiveScript
- [RiveScript Documentation](https://www.rivescript.com/docs/)
- [RiveScript Tutorial](https://github.com/aichaos/rivescript-js/blob/master/docs/rivescript.md)

### Ejemplos de Flujos
Revisar archivos en `static/rivescript/`:
- `basic_flow.rive` - Flujo básico de navegación
- `sales_flow.rive` - Flujo de ventas
- `technical_support_flow.rive` - Soporte técnico
- `hr_flow.rive` - Recursos humanos

### Testing
```bash
# Ejecutar todas las pruebas del editor
python test_rivescript_editor.py

# Pruebas específicas
python -m pytest tests/test_rivescript_api.py -v
```

## 🎯 Siguientes Pasos

### Mejoras Planificadas
- [ ] Syntax highlighting completo
- [ ] Autocompletado inteligente
- [ ] Atajos de teclado
- [ ] Sistema de versionado de flujos
- [ ] Colaboración en tiempo real
- [ ] Importación desde URLs
- [ ] Exportación a múltiples formatos

### Integración con IA
- [ ] Generación automática de respuestas con LLM
- [ ] Optimización de flujos con IA
- [ ] Análisis de conversaciones para mejorar flujos

---

## 🏆 Resumen

El **Editor RiveScript Integrado** es una herramienta completa que permite:

1. ✅ **Crear y editar** flujos de conversación visualmente
2. ✅ **Probar en tiempo real** sin afectar el chatbot principal  
3. ✅ **Persistir cambios** en base de datos automáticamente
4. ✅ **Recargar dinámicamente** el chatbot sin reinicio
5. ✅ **Validar sintaxis** para evitar errores
6. ✅ **Importar flujos** desde archivos existentes
7. ✅ **Gestionar múltiples flujos** organizadamente

**¡Perfecto para desarrollo ágil de chatbots!** 🚀
