# Test de Contactos usando PowerShell
# Ejecutar desde PowerShell en la carpeta del proyecto
# ¡IMPORTANTE! Reiniciar el servidor con "python run_server.py" antes de ejecutar

Write-Host "👥 Probando endpoint de contactos..." -ForegroundColor Cyan

# Configuración
$headers = @{"X-API-Key"="dev-api-key"}

# Contacto básico
Write-Host "`n📞 Caso 1: Contacto básico..." -ForegroundColor Yellow
$contactBasic = @{
    to = "5491123456789"
    type = "contacts"
    contacts = @(
        @{
            name = @{
                formatted_name = "Juan Pérez"
                first_name = "Juan"
                last_name = "Pérez"
            }
            phones = @(
                @{
                    phone = "+5491123456789"
                    type = "CELL"
                    wa_id = "5491123456789"
                }
            )
        }
    )
    messaging_line_id = 1
} | ConvertTo-Json -Depth 4

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:5000/v1/messages/contacts" -Method POST -Headers $headers -Body $contactBasic -ContentType "application/json"
    Write-Host "✅ Contacto básico enviado exitosamente!" -ForegroundColor Green
    Write-Host "📄 Información del contacto:" -ForegroundColor Cyan
    $response1.data.contacts_info | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "📄 Respuesta del servidor: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow

# Contacto completo
Write-Host "💼 Caso 2: Contacto empresarial completo..." -ForegroundColor Yellow
$contactComplete = @{
    to = "5491123456789"
    type = "contacts"
    contacts = @(
        @{
            name = @{
                formatted_name = "María García"
                first_name = "María"
                last_name = "García"
                prefix = "Lic."
            }
            phones = @(
                @{
                    phone = "+5491155667788"
                    type = "CELL"
                    wa_id = "5491155667788"
                },
                @{
                    phone = "+541143334444"
                    type = "WORK"
                }
            )
            emails = @(
                @{
                    email = "maria.garcia@empresa.com"
                    type = "WORK"
                },
                @{
                    email = "maria.personal@gmail.com"
                    type = "HOME"
                }
            )
            org = @{
                company = "Tech Solutions SA"
                department = "Marketing Digital"
                title = "Gerente de Marketing"
            }
            addresses = @(
                @{
                    street = "Av. Corrientes 1234, Piso 8"
                    city = "Buenos Aires"
                    state = "CABA"
                    zip = "C1043AAZ"
                    country = "Argentina"
                    country_code = "AR"
                    type = "WORK"
                }
            )
            urls = @(
                @{
                    url = "https://www.linkedin.com/in/mariagarcia"
                    type = "WORK"
                }
            )
        }
    )
    messaging_line_id = 1
} | ConvertTo-Json -Depth 5

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:5000/v1/messages/contacts" -Method POST -Headers $headers -Body $contactComplete -ContentType "application/json"
    Write-Host "✅ Contacto completo enviado exitosamente!" -ForegroundColor Green
    Write-Host "📄 Información:" -ForegroundColor Cyan
    $response2.data.contacts_info | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "📄 Respuesta del servidor: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow

# Múltiples contactos (equipo)
Write-Host "Caso 3: Equipo de trabajo (3 contactos)..." -ForegroundColor Yellow
$multipleContacts = @{
    to = "5491123456789"
    type = "contacts"
    contacts = @(
        @{
            name = @{
                formatted_name = "Ana López"
                first_name = "Ana"
                last_name = "López"
            }
            phones = @(
                @{
                    phone = "+5491166778899"
                    type = "CELL"
                    wa_id = "5491166778899"
                }
            )
            emails = @(
                @{
                    email = "ana.lopez@empresa.com"
                    type = "WORK"
                }
            )
            org = @{
                company = "Tech Solutions SA"
                title = "Desarrolladora Senior"
            }
        },
        @{
            name = @{
                formatted_name = "Carlos Ruiz"
                first_name = "Carlos"
                last_name = "Ruiz"
            }
            phones = @(
                @{
                    phone = "+5491177889900"
                    type = "CELL"
                    wa_id = "5491177889900"
                }
            )
            emails = @(
                @{
                    email = "carlos.ruiz@empresa.com"
                    type = "WORK"
                }
            )
            org = @{
                company = "Tech Solutions SA"
                title = "Project Manager"
            }
        },
        @{
            name = @{
                formatted_name = "Laura Martín"
                first_name = "Laura"
                last_name = "Martín"
            }
            phones = @(
                @{
                    phone = "+5491188990011"
                    type = "CELL"
                    wa_id = "5491188990011"
                }
            )
            emails = @(
                @{
                    email = "laura.martin@empresa.com"
                    type = "WORK"
                }
            )
            org = @{
                company = "Tech Solutions SA"
                title = "UX Designer"
            }
        }
    )
} | ConvertTo-Json -Depth 4

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:5000/v1/messages/contacts" -Method POST -Headers $headers -Body $multipleContacts -ContentType "application/json"
    Write-Host "✅ Equipo enviado exitosamente!" -ForegroundColor Green
    Write-Host "📄 Información del equipo:" -ForegroundColor Cyan
    $response3.data.contacts_info | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "📄 Respuesta del servidor: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Pruebas de contactos completadas!" -ForegroundColor Green
Write-Host "📋 Para ver todos los endpoints disponibles, ejecuta:" -ForegroundColor Cyan
Write-Host "   Invoke-RestMethod -Uri 'http://localhost:5000/v1/messages/test' -Headers @{'X-API-Key'='dev-api-key'}" -ForegroundColor White
