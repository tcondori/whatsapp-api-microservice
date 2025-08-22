# Script de prueba de webhook con ngrok para WhatsApp API
# URL de ngrok: https://193fa34e7248.ngrok-free.app

$NGROK_URL = "https://193fa34e7248.ngrok-free.app"
$API_KEY = "dev-api-key"
$WEBHOOK_VERIFY_TOKEN = "Nicole07"

Write-Host "🚀 PRUEBAS DE WEBHOOK CON NGROK" -ForegroundColor Yellow
Write-Host "Ngrok URL: $NGROK_URL" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Yellow

# Headers necesarios para ngrok
$commonHeaders = @{
    'ngrok-skip-browser-warning' = 'true'
    'X-API-Key' = $API_KEY
}

function Test-NgrokWebhookVerification {
    Write-Host "`n🔍 1. Probando verificación de webhook (GET)..." -ForegroundColor Cyan
    
    try {
        $url = "$NGROK_URL/v1/webhooks?hub.mode=subscribe&hub.verify_token=$WEBHOOK_VERIFY_TOKEN&hub.challenge=meta_test_challenge"
        $response = Invoke-RestMethod -Uri $url -Method GET -Headers @{'ngrok-skip-browser-warning' = 'true'}
        
        if ($response -eq "meta_test_challenge") {
            Write-Host "✅ Verificación exitosa - Meta podrá configurar el webhook" -ForegroundColor Green
            Write-Host "   URL para Meta: $NGROK_URL/v1/webhooks" -ForegroundColor Green
            Write-Host "   Verify Token: $WEBHOOK_VERIFY_TOKEN" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Respuesta inesperada: $response" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error en verificación: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-NgrokWebhookHealth {
    Write-Host "`n🏥 2. Probando health check de webhook..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "$NGROK_URL/v1/webhooks/health" -Method GET -Headers $commonHeaders
        Write-Host "✅ Health check exitoso:" -ForegroundColor Green
        Write-Host "   Status: $($response.data.webhook_processor)" -ForegroundColor White
        Write-Host "   WhatsApp API: $($response.data.whatsapp_api_service)" -ForegroundColor White
        Write-Host "   Verify Token configurado: $($response.data.webhook_verify_token_configured)" -ForegroundColor White
        Write-Host "   Webhook Secret configurado: $($response.data.webhook_secret_configured)" -ForegroundColor White
        return $true
    }
    catch {
        Write-Host "❌ Error en health check: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-NgrokWebhookMessageProcessing {
    Write-Host "`n📨 3. Probando procesamiento de mensaje de prueba..." -ForegroundColor Cyan
    
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $messageId = "wamid.ngrok_test_$timestamp"
    
    $payload = @{
        object = "whatsapp_business_account"
        entry = @(
            @{
                id = "TEST_BUSINESS_ID"
                changes = @(
                    @{
                        field = "messages"
                        value = @{
                            messaging_product = "whatsapp"
                            metadata = @{
                                display_phone_number = "+59167028778"
                                phone_number_id = "137474306106595"
                            }
                            contacts = @(
                                @{
                                    profile = @{
                                        name = "Usuario Ngrok Test"
                                    }
                                    wa_id = "5491123456789"
                                }
                            )
                            messages = @(
                                @{
                                    from = "5491123456789"
                                    id = $messageId
                                    timestamp = $timestamp.ToString()
                                    type = "text"
                                    text = @{
                                        body = "Hola desde ngrok - mensaje de prueba webhook"
                                    }
                                }
                            )
                        }
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 10
    
    $headers = $commonHeaders.Clone()
    $headers['Content-Type'] = 'application/json'
    
    try {
        $response = Invoke-RestMethod -Uri "$NGROK_URL/v1/webhooks/test" -Method POST -Body $payload -Headers $headers
        Write-Host "✅ Mensaje procesado exitosamente:" -ForegroundColor Green
        Write-Host "   Message ID: $messageId" -ForegroundColor White
        Write-Host "   Respuesta: $($response.message)" -ForegroundColor White
        return $true
    }
    catch {
        Write-Host "❌ Error procesando mensaje: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "   Detalles del error: $responseBody" -ForegroundColor Red
        }
        return $false
    }
}

function Test-NgrokWebhookStatusUpdate {
    Write-Host "`n📊 4. Probando actualización de estado..." -ForegroundColor Cyan
    
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $messageId = "wamid.status_test_$timestamp"
    
    $payload = @{
        object = "whatsapp_business_account"
        entry = @(
            @{
                id = "TEST_BUSINESS_ID"
                changes = @(
                    @{
                        field = "message_status"
                        value = @{
                            messaging_product = "whatsapp"
                            metadata = @{
                                display_phone_number = "+59167028778"
                                phone_number_id = "137474306106595"
                            }
                            statuses = @(
                                @{
                                    id = $messageId
                                    status = "delivered"
                                    timestamp = $timestamp.ToString()
                                    recipient_id = "5491123456789"
                                }
                            )
                        }
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 10
    
    $headers = $commonHeaders.Clone()
    $headers['Content-Type'] = 'application/json'
    
    try {
        $response = Invoke-RestMethod -Uri "$NGROK_URL/v1/webhooks/test" -Method POST -Body $payload -Headers $headers
        Write-Host "✅ Estado actualizado exitosamente:" -ForegroundColor Green
        Write-Host "   Message ID: $messageId" -ForegroundColor White
        Write-Host "   Status: delivered" -ForegroundColor White
        return $true
    }
    catch {
        Write-Host "❌ Error actualizando estado: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Show-MetaConfiguration {
    Write-Host "`n🔧 CONFIGURACIÓN PARA META DEVELOPERS:" -ForegroundColor Yellow
    Write-Host ("=" * 50) -ForegroundColor Yellow
    Write-Host "1. Ve a: https://developers.facebook.com/" -ForegroundColor Cyan
    Write-Host "2. Tu App → WhatsApp → Configuration" -ForegroundColor Cyan
    Write-Host "3. En la sección Webhook:" -ForegroundColor Cyan
    Write-Host "   📍 Callback URL: $NGROK_URL/v1/webhooks" -ForegroundColor Green
    Write-Host "   🔑 Verify Token: $WEBHOOK_VERIFY_TOKEN" -ForegroundColor Green
    Write-Host "4. Webhook Fields a activar:" -ForegroundColor Cyan
    Write-Host "   ✅ messages" -ForegroundColor White
    Write-Host "   ✅ message_status" -ForegroundColor White
    Write-Host "   ✅ message_reactions" -ForegroundColor White
    Write-Host "   ✅ message_template_status_update" -ForegroundColor White
    Write-Host ("=" * 50) -ForegroundColor Yellow
}

function Show-TestingInstructions {
    Write-Host "`n📱 CÓMO PROBAR CON WHATSAPP REAL:" -ForegroundColor Yellow
    Write-Host ("=" * 40) -ForegroundColor Yellow
    Write-Host "1. Configura el webhook en Meta (instrucciones arriba)" -ForegroundColor Cyan
    Write-Host "2. Desde tu teléfono (agregado al Business Manager):" -ForegroundColor Cyan
    Write-Host "   • Envía: 'hola' → Respuesta automática" -ForegroundColor White
    Write-Host "   • Envía: 'ayuda' → Menú de comandos" -ForegroundColor White
    Write-Host "   • Envía una imagen → Se procesará" -ForegroundColor White
    Write-Host "3. Verifica logs en la consola del servidor" -ForegroundColor Cyan
    Write-Host "4. Verifica la base de datos:" -ForegroundColor Cyan
    Write-Host "   SELECT * FROM messages ORDER BY created_at DESC;" -ForegroundColor White
    Write-Host ("=" * 40) -ForegroundColor Yellow
}

# Ejecutar todas las pruebas
$tests = @(
    @{ Name = "Verificación"; Function = { Test-NgrokWebhookVerification } },
    @{ Name = "Health Check"; Function = { Test-NgrokWebhookHealth } },
    @{ Name = "Procesamiento de Mensaje"; Function = { Test-NgrokWebhookMessageProcessing } },
    @{ Name = "Actualización de Estado"; Function = { Test-NgrokWebhookStatusUpdate } }
)

$results = @()

foreach ($test in $tests) {
    try {
        $result = & $test.Function
        $results += $result
        Start-Sleep -Seconds 1
    }
    catch {
        Write-Host "❌ Error ejecutando $($test.Name): $($_.Exception.Message)" -ForegroundColor Red
        $results += $false
    }
}

# Resumen
Write-Host "`n" -NoNewline
Write-Host ("=" * 60) -ForegroundColor Yellow
Write-Host "📊 RESUMEN DE PRUEBAS DE NGROK:" -ForegroundColor Yellow
$successful = ($results | Where-Object { $_ -eq $true }).Count
$total = $results.Count
Write-Host "✅ Exitosas: $successful/$total" -ForegroundColor Green
Write-Host "❌ Fallidas: $($total - $successful)/$total" -ForegroundColor Red

if ($successful -eq $total) {
    Write-Host "`n🎉 ¡WEBHOOK LISTO PARA CONFIGURAR EN META!" -ForegroundColor Green
    Show-MetaConfiguration
    Show-TestingInstructions
} elseif ($successful -ge 2) {
    Write-Host "`n⚠️  Webhook parcialmente funcional" -ForegroundColor Yellow
    Write-Host "La verificación funciona - puedes configurar en Meta" -ForegroundColor Yellow
    Show-MetaConfiguration
} else {
    Write-Host "`n❌ Webhook no está listo" -ForegroundColor Red
    Write-Host "Revisa que el servidor esté ejecutándose en puerto 5000" -ForegroundColor Yellow
    Write-Host "Verifica que ngrok esté redirigiendo correctamente" -ForegroundColor Yellow
}

Write-Host "`n🔗 Enlaces útiles:" -ForegroundColor Cyan
Write-Host "• Dashboard ngrok: http://127.0.0.1:4040" -ForegroundColor White
Write-Host "• Tu webhook: $NGROK_URL/v1/webhooks" -ForegroundColor White
Write-Host "• Meta Developers: https://developers.facebook.com/" -ForegroundColor White
