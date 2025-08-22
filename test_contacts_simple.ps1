# Test script para endpoint de contactos - WhatsApp API
# Compatible con PowerShell Windows

Write-Host "Probando endpoint de contactos..." -ForegroundColor Cyan
Write-Host "URL base: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Endpoint: /v1/messages/contacts" -ForegroundColor Green

$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "`nCaso 1: Contacto basico..." -ForegroundColor Yellow
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
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/v1/messages/contacts" -Method POST -Body $basicContact -Headers $headers
    Write-Host "Contacto basico enviado exitosamente!" -ForegroundColor Green
    Write-Host "Informacion del contacto:" -ForegroundColor Cyan
    Write-Host $response.Content
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Respuesta del servidor: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow

# Contacto completo
Write-Host "Caso 2: Contacto completo..." -ForegroundColor Yellow
$completeContact = @{
    to = "5491123456789"
    type = "contacts"
    contacts = @(
        @{
            name = @{
                formatted_name = "Maria Garcia"
                first_name = "Maria"
                last_name = "Garcia"
                middle_name = "Elena"
                suffix = "Ing."
                prefix = "Dra."
            }
            phones = @(
                @{
                    phone = "+5491123456789"
                    type = "WORK"
                    wa_id = "5491123456789"
                },
                @{
                    phone = "+5491187654321"
                    type = "HOME"
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
                department = "Desarrollo"
                title = "Arquitecta de Software"
            }
            addresses = @(
                @{
                    street = "Av. Corrientes 1234"
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
                    url = "https://www.techsolutions.com.ar"
                    type = "WORK"
                },
                @{
                    url = "https://linkedin.com/in/mariagarcia"
                    type = "HOME"
                }
            )
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/v1/messages/contacts" -Method POST -Body $completeContact -Headers $headers
    Write-Host "Contacto completo enviado exitosamente!" -ForegroundColor Green
    Write-Host "Informacion:" -ForegroundColor Cyan
    Write-Host $response.Content
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Respuesta del servidor: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow

# Multiples contactos (equipo)
Write-Host "Caso 3: Equipo de trabajo (3 contactos)..." -ForegroundColor Yellow
$multipleContacts = @{
    to = "5491123456789"
    type = "contacts"
    contacts = @(
        @{
            name = @{
                formatted_name = "Ana Lopez"
                first_name = "Ana"
                last_name = "Lopez"
            }
            phones = @(
                @{
                    phone = "+5491123456789"
                    type = "WORK"
                    wa_id = "5491123456789"
                }
            )
            org = @{
                company = "DevTeam SA"
                department = "Frontend"
                title = "Desarrolladora Senior"
            }
        },
        @{
            name = @{
                formatted_name = "Carlos Rodriguez"
                first_name = "Carlos"
                last_name = "Rodriguez"
            }
            phones = @(
                @{
                    phone = "+5491187654321"
                    type = "WORK"
                    wa_id = "5491187654321"
                }
            )
            org = @{
                company = "DevTeam SA"
                department = "Backend"
                title = "Arquitecto de Software"
            }
        },
        @{
            name = @{
                formatted_name = "Luis Martinez"
                first_name = "Luis"
                last_name = "Martinez"
            }
            phones = @(
                @{
                    phone = "+5491155443322"
                    type = "WORK"
                    wa_id = "5491155443322"
                }
            )
            org = @{
                company = "DevTeam SA"
                department = "DevOps"
                title = "Especialista en Infraestructura"
            }
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/v1/messages/contacts" -Method POST -Body $multipleContacts -Headers $headers
    Write-Host "Equipo enviado exitosamente!" -ForegroundColor Green
    Write-Host "Informacion del equipo:" -ForegroundColor Cyan
    Write-Host $response.Content
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Respuesta del servidor: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" + "="*60 + "`n" -ForegroundColor Yellow
Write-Host "Para ver todos los endpoints disponibles, ejecuta:" -ForegroundColor Cyan
Write-Host "Invoke-WebRequest -Uri http://127.0.0.1:5000 -Method GET" -ForegroundColor White
