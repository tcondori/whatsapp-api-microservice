# Script PowerShell para probar integración de webhooks de WhatsApp
# Este script verifica que todos los endpoints de webhook funcionan correctamente

$BASE_URL = "http://localhost:5000"
$API_KEY = "dev-api-key"

function Test-WebhookVerification {
    Write-Host "🔍 Probando verificación de webhook..." -ForegroundColor Cyan
    
    $params = @{
        'hub.mode' = 'subscribe'
        'hub.verify_token' = 'test_verify_token'
        'hub.challenge' = 'test_challenge_123'
    }
    
    $queryString = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '&'
    $url = "$BASE_URL/v1/webhooks?$queryString"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method GET
        Write-Host "✅ Verificación exitosa: $response" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Error en verificación: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-WebhookMessageReceived {
    Write-Host "`n📨 Probando mensaje entrante..." -ForegroundColor Cyan
    
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $messageId = "wamid.test_$timestamp"
    
    $payload = @{
        object = "whatsapp_business_account"
        entry = @(
            @{
                id = "WHATSAPP_BUSINESS_ACCOUNT_ID"
                changes = @(
                    @{
                        field = "messages"
                        value = @{
                            messaging_product = "whatsapp"
                            metadata = @{
                                display_phone_number = "+1234567890"
                                phone_number_id = "123456789012345"
                            }
                            contacts = @(
                                @{
                                    profile = @{
                                        name = "Usuario Test PowerShell"
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
                                        body = "Hola desde PowerShell - mensaje de prueba webhook"
                                    }
                                }
                            )
                        }
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 10
    
    $headers = @{
        'Content-Type' = 'application/json'
        'X-API-Key' = $API_KEY
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/webhooks/test" -Method POST -Body $payload -Headers $headers
        Write-Host "✅ Mensaje entrante procesado:" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 3)
        return $true
    }
    catch {
        Write-Host "❌ Error procesando mensaje: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $responseBody = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($responseBody)
            Write-Host "Response body: $($reader.ReadToEnd())" -ForegroundColor Red
        }
        return $false
    }
}

function Test-WebhookMessageStatus {
    Write-Host "`n📊 Probando actualización de estado..." -ForegroundColor Cyan
    
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $messageId = "wamid.status_test_$timestamp"
    
    $payload = @{
        object = "whatsapp_business_account"
        entry = @(
            @{
                id = "WHATSAPP_BUSINESS_ACCOUNT_ID"
                changes = @(
                    @{
                        field = "message_status"
                        value = @{
                            messaging_product = "whatsapp"
                            metadata = @{
                                display_phone_number = "+1234567890"
                                phone_number_id = "123456789012345"
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
    
    $headers = @{
        'Content-Type' = 'application/json'
        'X-API-Key' = $API_KEY
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/webhooks/test" -Method POST -Body $payload -Headers $headers
        Write-Host "✅ Estado actualizado:" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 3)
        return $true
    }
    catch {
        Write-Host "❌ Error actualizando estado: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-WebhookInteractiveResponse {
    Write-Host "`n🔘 Probando respuesta interactiva..." -ForegroundColor Cyan
    
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $messageId = "wamid.interactive_$timestamp"
    
    $payload = @{
        object = "whatsapp_business_account"
        entry = @(
            @{
                id = "WHATSAPP_BUSINESS_ACCOUNT_ID"
                changes = @(
                    @{
                        field = "messages"
                        value = @{
                            messaging_product = "whatsapp"
                            metadata = @{
                                display_phone_number = "+1234567890"
                                phone_number_id = "123456789012345"
                            }
                            contacts = @(
                                @{
                                    profile = @{
                                        name = "Usuario Interactive"
                                    }
                                    wa_id = "5491123456789"
                                }
                            )
                            messages = @(
                                @{
                                    from = "5491123456789"
                                    id = $messageId
                                    timestamp = $timestamp.ToString()
                                    type = "interactive"
                                    interactive = @{
                                        type = "button_reply"
                                        button_reply = @{
                                            id = "btn_help_ps"
                                            title = "Ayuda desde PowerShell"
                                        }
                                    }
                                }
                            )
                        }
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 10
    
    $headers = @{
        'Content-Type' = 'application/json'
        'X-API-Key' = $API_KEY
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/webhooks/test" -Method POST -Body $payload -Headers $headers
        Write-Host "✅ Respuesta interactiva procesada:" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 3)
        return $true
    }
    catch {
        Write-Host "❌ Error en respuesta interactiva: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-WebhookHealth {
    Write-Host "`n🏥 Probando health check de webhooks..." -ForegroundColor Cyan
    
    $headers = @{
        'X-API-Key' = $API_KEY
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/webhooks/health" -Method GET -Headers $headers
        Write-Host "✅ Health check exitoso:" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 3)
        return $true
    }
    catch {
        Write-Host "❌ Error en health check: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Función principal
function Main {
    Write-Host "🚀 INICIANDO PRUEBAS DE INTEGRACIÓN DE WEBHOOKS" -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Yellow
    
    $tests = @(
        @{ Name = "Verificación de Webhook"; Function = { Test-WebhookVerification } },
        @{ Name = "Health Check"; Function = { Test-WebhookHealth } },
        @{ Name = "Mensaje Entrante"; Function = { Test-WebhookMessageReceived } },
        @{ Name = "Estado de Mensaje"; Function = { Test-WebhookMessageStatus } },
        @{ Name = "Respuesta Interactiva"; Function = { Test-WebhookInteractiveResponse } }
    )
    
    $results = @()
    
    foreach ($test in $tests) {
        try {
            Write-Host "`n--- Ejecutando: $($test.Name) ---" -ForegroundColor Magenta
            $result = & $test.Function
            $results += $result
            Start-Sleep -Seconds 1
        }
        catch {
            Write-Host "❌ Error ejecutando $($test.Name): $($_.Exception.Message)" -ForegroundColor Red
            $results += $false
        }
    }
    
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 60) -ForegroundColor Yellow
    Write-Host "📊 RESUMEN DE PRUEBAS:" -ForegroundColor Yellow
    $successful = ($results | Where-Object { $_ -eq $true }).Count
    $total = $results.Count
    Write-Host "✅ Exitosas: $successful/$total" -ForegroundColor Green
    Write-Host "❌ Fallidas: $($total - $successful)/$total" -ForegroundColor Red
    
    if ($successful -eq $total) {
        Write-Host "`n🎉 ¡Todas las pruebas pasaron exitosamente!" -ForegroundColor Green
        Write-Host "El sistema de webhooks está funcionando correctamente." -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Algunas pruebas fallaron." -ForegroundColor Yellow
        Write-Host "Verifica que el servidor esté ejecutándose en $BASE_URL" -ForegroundColor Yellow
        Write-Host "Revisar logs del servidor para más detalles." -ForegroundColor Yellow
    }
}

# Verificar que el servidor esté corriendo
Write-Host "Verificando conexión con el servidor..." -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET -Headers @{'X-API-Key' = $API_KEY}
    Write-Host "✅ Servidor conectado y funcionando" -ForegroundColor Green
    Main
}
catch {
    Write-Host "❌ No se puede conectar al servidor en $BASE_URL" -ForegroundColor Red
    Write-Host "Asegúrate de que el servidor esté ejecutándose:" -ForegroundColor Yellow
    Write-Host "  python run_server.py" -ForegroundColor Cyan
    exit 1
}
