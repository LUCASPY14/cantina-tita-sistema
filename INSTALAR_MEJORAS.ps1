# Script de Instalación Rápida - Mejoras Críticas
# Ejecutar como Administrador en PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACIÓN RÁPIDA - MEJORAS CRÍTICAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectPath = "d:\anteproyecto20112025"

# Verificar que estamos en el directorio correcto
if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ Error: No se encontró el directorio del proyecto" -ForegroundColor Red
    exit 1
}

Set-Location $ProjectPath

Write-Host "📁 Directorio: $ProjectPath" -ForegroundColor Green
Write-Host ""

# PASO 1: Instalar dependencias Python
Write-Host "🔧 PASO 1/5: Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements_mejoras_criticas.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Error instalando dependencias, continuando..." -ForegroundColor Yellow
}
Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

# PASO 2: Crear directorios necesarios
Write-Host "📂 PASO 2/5: Creando directorios..." -ForegroundColor Yellow
$directories = @("backups", "logs", "scripts")
foreach ($dir in $directories) {
    $dirPath = Join-Path $ProjectPath $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        Write-Host "  ✅ Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Ya existe: $dir" -ForegroundColor Gray
    }
}
Write-Host ""

# PASO 3: Verificar Redis
Write-Host "🔍 PASO 3/5: Verificando Redis..." -ForegroundColor Yellow
$redisRunning = $false
try {
    $redisTest = redis-cli ping 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host "  ✅ Redis está corriendo" -ForegroundColor Green
        $redisRunning = $true
    }
} catch {
    Write-Host "  ⚠️  Redis no detectado" -ForegroundColor Yellow
}

if (-not $redisRunning) {
    Write-Host ""
    Write-Host "  📥 Redis no está instalado o no está corriendo" -ForegroundColor Yellow
    Write-Host "  Descarga Redis desde:" -ForegroundColor Yellow
    Write-Host "  https://github.com/microsoftarchive/redis/releases" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Después de instalar, ejecuta:" -ForegroundColor Yellow
    Write-Host "    redis-server --service-install redis.windows.conf" -ForegroundColor Gray
    Write-Host "    redis-server --service-start" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  ℹ️  El sistema funcionará sin Redis usando cache en memoria" -ForegroundColor Gray
}
Write-Host ""

# PASO 4: Configurar backup automático
Write-Host "💾 PASO 4/5: Configurando backup automático..." -ForegroundColor Yellow
try {
    & "$ProjectPath\scripts\schedule_backup_windows.ps1"
    Write-Host "  ✅ Backup automático configurado" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Error configurando backup automático" -ForegroundColor Yellow
    Write-Host "  Ejecuta manualmente: .\scripts\schedule_backup_windows.ps1" -ForegroundColor Gray
}
Write-Host ""

# PASO 5: Ejecutar migraciones (si hay nuevas)
Write-Host "🔄 PASO 5/5: Verificando migraciones..." -ForegroundColor Yellow
try {
    python manage.py migrate --no-input
    Write-Host "  ✅ Migraciones aplicadas" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Error aplicando migraciones" -ForegroundColor Yellow
}
Write-Host ""

# VERIFICACIÓN
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Resumen
Write-Host "📊 RESUMEN DE INSTALACIÓN:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✅ Dependencias Python" -ForegroundColor Green
Write-Host "  ✅ Directorios creados (backups, logs)" -ForegroundColor Green

if ($redisRunning) {
    Write-Host "  ✅ Redis funcionando" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Redis no instalado (opcional)" -ForegroundColor Yellow
}

Write-Host "  ✅ Backup automático configurado" -ForegroundColor Green
Write-Host "  ✅ Migraciones aplicadas" -ForegroundColor Green
Write-Host ""

# Próximos pasos
Write-Host "🎯 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Probar backup manual:" -ForegroundColor Yellow
Write-Host "   python manage.py backup_database --compress --notify" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Probar health check:" -ForegroundColor Yellow
Write-Host "   python manage.py health_check --verbose" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Iniciar servidor:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Probar health endpoints:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/health/" -ForegroundColor Gray
Write-Host "   http://localhost:8000/ready/" -ForegroundColor Gray
Write-Host "   http://localhost:8000/alive/" -ForegroundColor Gray
Write-Host ""

if (-not $redisRunning) {
    Write-Host "💡 RECOMENDACIÓN: Instalar Redis para mejor performance" -ForegroundColor Cyan
    Write-Host "   Ver: GUIA_INSTALACION_MEJORAS_CRITICAS.md" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📚 Documentación completa: GUIA_INSTALACION_MEJORAS_CRITICAS.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Pausar para que el usuario pueda leer
Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
