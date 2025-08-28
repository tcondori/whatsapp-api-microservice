# ================================================
# 🚀 SCRIPT PRINCIPAL DE INICIO - FLASK RUN
# ================================================
# Punto de entrada recomendado que usa .env automáticamente
# Incluye TODOS los componentes del microservicio
# ================================================

Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "🚀 WHATSAPP API MICROSERVICE - FLASK RUN" -ForegroundColor Green  
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 60) -ForegroundColor Green
Write-Host ""
Write-Host "💡 COMPONENTES INCLUIDOS:" -ForegroundColor Cyan
Write-Host "  📱 API REST completa (/v1/*)" -ForegroundColor White
Write-Host "  🗨️  Simulador de chat (/chat)" -ForegroundColor White  
Write-Host "  📚 Documentación Swagger (/docs)" -ForegroundColor White
Write-Host "  📊 Sistema de logging dual" -ForegroundColor White
Write-Host "  🔧 Configuración desde .env" -ForegroundColor White
Write-Host ""

# Verificar que existe .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ ERROR: Archivo .env no encontrado" -ForegroundColor Red
    Write-Host "   Asegúrate de tener el archivo .env en el directorio raíz" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
try {
    # Intentar activar venv local
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
        Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  No se encontró venv local, continuando..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️  Error activando venv, continuando..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 URLS DEL SERVIDOR:" -ForegroundColor Cyan
Write-Host "  • Principal:     http://localhost:5001" -ForegroundColor White
Write-Host "  • Simulador:     http://localhost:5001/chat" -ForegroundColor White
Write-Host "  • API Test:      http://localhost:5001/v1/messages/test" -ForegroundColor White
Write-Host "  • Documentación: http://localhost:5001/docs" -ForegroundColor White
Write-Host "  • Health Check:  http://localhost:5001/health" -ForegroundColor White
Write-Host ""
Write-Host "🔑 API Key de prueba: dev-api-key" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "✨ Iniciando Flask con configuración completa..." -ForegroundColor Green
Write-Host "   🛑 Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 60) -ForegroundColor Green
Write-Host ""

# Ejecutar flask run (lee automáticamente del .env)
flask run
