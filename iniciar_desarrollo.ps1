# Script para iniciar desarrollo completo del sistema POS (Windows)
# Archivo: iniciar_desarrollo.ps1

Write-Host "🚀 INICIANDO SISTEMA POS COMPLETO" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Blue

Write-Host "📦 Verificando dependencias..." -ForegroundColor Cyan

# Verificar Python
try {
    python --version | Out-Null
    Write-Host "✅ Python OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    exit 1
}

# Verificar Node.js
try {
    node --version | Out-Null
    Write-Host "✅ Node.js OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Cyan

# Activar entorno virtual si existe
if (Test-Path ".venv\Scripts\activate.ps1") {
    & .venv\Scripts\activate.ps1
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
} elseif (Test-Path "env\Scripts\activate.ps1") {
    & env\Scripts\activate.ps1
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "⚠️ No se encontró entorno virtual" -ForegroundColor Yellow
}

Write-Host "🗄️ Iniciando servidor Django (Backend)..." -ForegroundColor Cyan

# Iniciar Django en background
$djangoJob = Start-Job -ScriptBlock {
    Set-Location "backend"
    python manage.py collectstatic --noinput *> $null
    python manage.py migrate --run-syncdb *> $null
    python manage.py runserver 8000
} -Name "DjangoServer"

# Esperar un momento para que Django se inicie
Start-Sleep -Seconds 3

Write-Host "🌐 Iniciando servidor Vite (Frontend)..." -ForegroundColor Cyan

# Iniciar Vite en background
$viteJob = Start-Job -ScriptBlock {
    Set-Location "frontend"
    npm run dev
} -Name "ViteServer"

# Esperar un poco más para que Vite se inicie
Start-Sleep -Seconds 2

Write-Host "✅ SERVIDORES INICIADOS" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Blue
Write-Host "🔗 Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "🔗 Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "🔗 POS Sistema: http://localhost:5173/pos-completo.html" -ForegroundColor Green
Write-Host "🔗 API POS: http://localhost:8000/api/pos/" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Blue
Write-Host "💡 Presiona Ctrl+C para detener ambos servidores" -ForegroundColor Yellow

# Función para limpiar al salir
function Stop-Development {
    Write-Host "🛑 Deteniendo servidores..." -ForegroundColor Yellow
    Stop-Job $djangoJob, $viteJob -ErrorAction SilentlyContinue
    Remove-Job $djangoJob, $viteJob -ErrorAction SilentlyContinue
}

# Configurar handler para Ctrl+C
Register-ObjectEvent -InputObject ([Console]) -EventName "CancelKeyPress" -Action {
    Stop-Development
    exit 0
}

try {
    # Monitor jobs and keep script running
    while ($djangoJob.State -eq "Running" -or $viteJob.State -eq "Running") {
        Start-Sleep -Seconds 1
        
        # Mostrar output ocasionalmente
        if ($djangoJob.State -eq "Failed" -or $viteJob.State -eq "Failed") {
            Write-Host "❌ Error en uno de los servidores" -ForegroundColor Red
            break
        }
    }
} finally {
    Stop-Development
}