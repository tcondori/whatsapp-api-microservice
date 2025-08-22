# Test de Ubicación usando PowerShell
# Ejecutar desde PowerShell en la carpeta del proyecto

# Ubicación básica (solo coordenadas)
Write-Host "🗺️ Probando ubicación básica..." -ForegroundColor Cyan
$headers = @{"X-API-Key"="dev-api-key"}
$body = @{
    to = "5491123456789"
    type = "location"
    location = @{
        latitude = -34.6037
        longitude = -58.3816
    }
    messaging_line_id = 1
} | ConvertTo-Json -Depth 3

$response1 = Invoke-RestMethod -Uri "http://localhost:5000/v1/messages/location" -Method POST -Headers $headers -Body $body -ContentType "application/json"
Write-Host "✅ Respuesta:" -ForegroundColor Green
$response1 | ConvertTo-Json -Depth 5

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow

# Ubicación completa (con nombre y dirección)
Write-Host "🏢 Probando ubicación completa..." -ForegroundColor Cyan
$body2 = @{
    to = "5491123456789"
    type = "location"
    location = @{
        latitude = -34.6037
        longitude = -58.3816
        name = "Obelisco de Buenos Aires"
        address = "Av. 9 de Julio s/n, C1043 CABA, Argentina"
    }
    messaging_line_id = 1
} | ConvertTo-Json -Depth 3

$response2 = Invoke-RestMethod -Uri "http://localhost:5000/v1/messages/location" -Method POST -Headers $headers -Body $body2 -ContentType "application/json"
Write-Host "✅ Respuesta:" -ForegroundColor Green
$response2 | ConvertTo-Json -Depth 5

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow

# Ubicación internacional (Times Square)
Write-Host "🗽 Probando ubicación internacional..." -ForegroundColor Cyan
$body3 = @{
    to = "5491123456789"
    type = "location"
    location = @{
        latitude = 40.7128
        longitude = -74.0060
        name = "Times Square"
        address = "Times Square, New York, NY 10036, USA"
    }
} | ConvertTo-Json -Depth 3

$response3 = Invoke-RestMethod -Uri "http://localhost:5000/v1/messages/location" -Method POST -Headers $headers -Body $body3 -ContentType "application/json"
Write-Host "✅ Respuesta:" -ForegroundColor Green
$response3 | ConvertTo-Json -Depth 5

Write-Host "`n🎉 Todas las pruebas completadas exitosamente!" -ForegroundColor Green
