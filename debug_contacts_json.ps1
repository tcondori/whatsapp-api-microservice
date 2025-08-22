# Script de depuración para endpoint de contactos
Write-Host "=== DEPURACION JSON CONTACTOS ===" -ForegroundColor Yellow

$headers = @{
    "Content-Type" = "application/json"
}

# Contacto básico - primero veamos cómo se genera el JSON
Write-Host "`n1. Generando JSON para contacto básico..." -ForegroundColor Cyan
$basicContact = @{
    to = "5491123456789"
    type = "contacts"
    contacts = @(
        @{
            name = @{
                formatted_name = "Juan Perez"
                first_name = "Juan"
                last_name = "Perez"
            }
            phones = @(
                @{
                    phone = "+5491123456789"
                    type = "WORK"
                    wa_id = "5491123456789"
                }
            )
        }
    )
}

$jsonPayload = $basicContact | ConvertTo-Json -Depth 10
Write-Host "JSON generado:" -ForegroundColor Green
Write-Host $jsonPayload
Write-Host "`nLongitud del JSON: $($jsonPayload.Length) caracteres" -ForegroundColor Yellow

# Verificar si hay caracteres problemáticos
Write-Host "`nCarácter en posición 128 (donde está el error):" -ForegroundColor Red
if ($jsonPayload.Length -gt 128) {
    Write-Host "Carácter 128: '$($jsonPayload[127])'" -ForegroundColor Red
    Write-Host "Contexto alrededor de la posición 128:" -ForegroundColor Red
    $start = [Math]::Max(0, 120)
    $end = [Math]::Min($jsonPayload.Length - 1, 135)
    Write-Host $jsonPayload.Substring($start, $end - $start + 1)
}

Write-Host "`n=== ENVIANDO REQUEST ===" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/v1/messages/contacts" -Method POST -Body $jsonPayload -Headers $headers
    Write-Host "SUCCESS: $($response.StatusCode)" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Respuesta del servidor:" -ForegroundColor Red
        Write-Host $responseBody
    }
}
