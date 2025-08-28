# test_api_examples.ps1 - Ejemplos de prueba de API con PowerShell
# filepath: e:\DSW\proyectos\proy04\test_api_examples.ps1

Write-Host "=" -NoNewline; for($i=0; $i -lt 70; $i++){ Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "🧪 EJEMPLOS DE PRUEBA - API WHATSAPP CHATBOT"
Write-Host "=" -NoNewline; for($i=0; $i -lt 70; $i++){ Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""

Write-Host "🔍 1. HEALTH CHECK"
Write-Host "curl -H 'X-API-Key: dev-api-key' http://localhost:5000/health"
Write-Host ""

Write-Host "🤖 2. TEST DEL CHATBOT"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"hola\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "💰 3. PRUEBA DE VENTAS"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"ventas\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "🛠️ 4. PRUEBA DE SOPORTE"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"soporte tecnico\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "👥 5. PRUEBA DE RECURSOS HUMANOS"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"recursos humanos\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "💳 6. PRUEBA DE FACTURACIÓN"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"facturacion\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "📋 7. PRUEBA DEL MENÚ"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"menu\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "🔄 8. CERRAR CONVERSACIÓN"
Write-Host "curl -X POST -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{\"phone_number\":\"+595987000001\",\"message\":\"cerrar conversacion\"}' http://localhost:5000/v1/messages/text"
Write-Host ""

Write-Host "📊 9. DOCUMENTACIÓN SWAGGER"
Write-Host "Abre en tu navegador: http://localhost:5000/docs"
Write-Host ""

Write-Host "=" -NoNewline; for($i=0; $i -lt 70; $i++){ Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "💡 COPIA Y PEGA LOS COMANDOS curl PARA PROBAR"
Write-Host "=" -NoNewline; for($i=0; $i -lt 70; $i++){ Write-Host "=" -NoNewline }; Write-Host ""
