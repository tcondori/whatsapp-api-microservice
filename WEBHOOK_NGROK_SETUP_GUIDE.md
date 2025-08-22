# 🔗 GUÍA COMPLETA: CONFIGURAR WEBHOOK CON NGROK + META

## 🚀 PASO 1: INSTALAR NGROK

### **Opción A: Descarga desde el sitio oficial**
1. Ve a https://ngrok.com/download
2. Descarga la versión para Windows
3. Extrae el archivo `ngrok.exe` a tu carpeta del proyecto
4. (Opcional) Añade ngrok al PATH del sistema

### **Opción B: Con Chocolatey (si lo tienes instalado)**
```powershell
choco install ngrok
```

### **Opción C: Con Winget**
```powershell
winget install ngrok.ngrok
```

## 🚀 PASO 2: CONFIGURAR NGROK

### **2.1. Crear cuenta en ngrok (gratuita)**
1. Ve a https://dashboard.ngrok.com/signup
2. Crea una cuenta gratuita
3. Ve a "Your Authtoken"
4. Copia tu authtoken

### **2.2. Autenticar ngrok**
```powershell
ngrok config add-authtoken TU_AUTHTOKEN_AQUI
```

## 🚀 PASO 3: EXPONER TU SERVIDOR LOCAL

### **3.1. Asegúrate que tu servidor esté corriendo**
```powershell
# En una terminal (manténla abierta)
python run_server.py
```

### **3.2. Exponer con ngrok**
```powershell
# En OTRA terminal (nueva)
ngrok http 5000
```

**Esto te dará una URL como:**
```
https://abc123def456.ngrok-free.app
```

## 🚀 PASO 4: CONFIGURAR EN META DEVELOPERS

### **4.1. Ir a Meta for Developers**
1. Ve a https://developers.facebook.com/
2. Inicia sesión con tu cuenta de Facebook/Meta
3. Ve a "Mis Apps" → Tu aplicación de WhatsApp Business

### **4.2. Configurar Webhook**
1. En el panel izquierdo: **WhatsApp** → **Configuration**
2. En la sección **Webhook**:
   - **Callback URL**: `https://TU_URL_NGROK.ngrok-free.app/v1/webhooks`
   - **Verify Token**: `Nicole07` (el que está en tu .env)
3. Clic en **"Verify and Save"**

### **4.3. Suscribirse a eventos**
En la misma página, en **Webhook fields**:
- ✅ **messages** (mensajes entrantes)
- ✅ **message_status** (estados: enviado, entregado, leído)
- ✅ **message_reactions** (reacciones a mensajes)
- ✅ **message_template_status_update** (estados de plantillas)

## 🧪 PASO 5: PROBAR WEBHOOK REAL

### **5.1. Enviar mensaje de prueba**
Desde tu teléfono (agregado al WhatsApp Business):
1. Envía: "Hola" → Debería responder automáticamente
2. Envía: "ayuda" → Debería mostrar menú de comandos

### **5.2. Verificar logs**
En tu terminal del servidor verás:
```
INFO - Webhook recibido: whatsapp_business_account
INFO - Procesando mensaje entrante: wamid.xxx
INFO - Respuesta automática enviada a +5491123456789
```

### **5.3. Verificar en Meta**
En **Meta for Developers** → **WhatsApp** → **API Calls**:
- Deberías ver las llamadas entrantes y salientes
- Estados de mensajes actualizándose

## 🛠️ PASO 6: COMANDOS ÚTILES

### **Reiniciar ngrok con nueva URL**
```powershell
# Detener ngrok actual (Ctrl+C)
ngrok http 5000
# Copiar nueva URL y actualizar en Meta
```

### **Ver logs detallados de ngrok**
```powershell
ngrok http 5000 --log=stdout --log-level=debug
```

### **Usar subdominio personalizado (plan pago)**
```powershell
ngrok http 5000 --subdomain=mi-whatsapp-webhook
```

## 🔒 PASO 7: SEGURIDAD ADICIONAL

### **7.1. Validar origen de webhook**
Tu código ya incluye validación de firma HMAC con `WEBHOOK_SECRET`.

### **7.2. Whitelist de IPs (opcional)**
Meta usa estas IPs para webhooks:
```
173.252.74.22
173.252.74.23
...
```

### **7.3. Rate limiting**
Tu servidor ya incluye rate limiting con Flask-Limiter.

## 📊 PASO 8: MONITOREO

### **8.1. Dashboard de ngrok**
Ve a http://127.0.0.1:4040 para ver:
- Requests en tiempo real
- Respuestas y errores
- Tiempo de respuesta

### **8.2. Logs del servidor**
```powershell
tail -f logs/whatsapp_api.log  # Si usas logging a archivo
```

### **8.3. Health checks**
```powershell
curl -X GET "https://TU_URL_NGROK.ngrok-free.app/v1/webhooks/health" -H "X-API-Key: dev-api-key"
```

## 🐛 PASO 9: TROUBLESHOOTING

### **Error: "Webhook verification failed"**
- Verificar que `WEBHOOK_VERIFY_TOKEN` coincide
- Verificar que la URL es correcta
- Revisar logs de ngrok para ver la request

### **Error: "Webhook signature invalid"**
- Verificar que `WEBHOOK_SECRET` esté configurado
- Meta debe usar el mismo secret para firmar

### **Ngrok se desconecta**
- Plan gratuito: sesiones de 2 horas
- Plan pago: sesiones permanentes
- Usar `ngrok http 5000 --region=us` para mejor latencia

### **Mensajes no llegan**
- Verificar suscripciones en Meta
- Revisar que el número esté en la lista de test
- Verificar Business Manager settings

## 📱 PASO 10: TESTING COMPLETO

### **10.1. Tests manuales desde teléfono**
```
• "hola" → respuesta automática
• "ayuda" → menú de comandos  
• Enviar imagen → procesamiento
• Enviar ubicación → almacenamiento
```

### **10.2. Tests automatizados**
```powershell
# Actualizar URL en script de pruebas
python test_webhook_integration.py
```

### **10.3. Verificar base de datos**
```sql
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
SELECT * FROM messaging_lines;
```

## 🎉 PASO 11: ¡LISTO PARA PRODUCCIÓN!

Una vez que todo funcione:

1. **Documenta la URL de ngrok** que funciona
2. **Exporta configuración** de Meta
3. **Haz backup** de la base de datos
4. **Considera** migrar a un servidor permanente (no ngrok)

## 🌐 ALTERNATIVAS A NGROK

- **localtunnel**: `npm install -g localtunnel` → `lt --port 5000`
- **serveo**: `ssh -R 80:localhost:5000 serveo.net`  
- **PageKite**: `pagekite.py 5000 yourname.pagekite.me`

## 📞 URLs IMPORTANTES

- **Meta for Developers**: https://developers.facebook.com/
- **WhatsApp Business API Docs**: https://developers.facebook.com/docs/whatsapp/
- **ngrok Dashboard**: https://dashboard.ngrok.com/
- **Tu webhook URL**: `https://TU_NGROK.ngrok-free.app/v1/webhooks`

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

1. **Instalar ngrok**
2. **Crear cuenta y authtoken**  
3. **Exponer servidor local**
4. **Configurar en Meta**
5. **Probar desde teléfono**

¿Te ayudo con algún paso específico? ¿Tienes ya cuenta en Meta for Developers?
