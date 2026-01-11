# ========================================
# INSTALACIÓN Y CONFIGURACIÓN RÁPIDA
# Dashboard Unificado + Mejoras Críticas
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   INSTALACIÓN DASHBOARD UNIFICADO" -ForegroundColor Yellow
Write-Host "   + Mejoras Críticas" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que estamos en el directorio correcto
$projectRoot = "D:\anteproyecto20112025"
if (!(Test-Path $projectRoot)) {
    Write-Host "❌ ERROR: No se encuentra el directorio del proyecto" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

# 2. Activar entorno virtual
Write-Host "✓ Activando entorno virtual..." -ForegroundColor Green
& "$projectRoot\.venv\Scripts\Activate.ps1"

# 3. Instalar dependencias Python (ya instaladas)
Write-Host "✓ Dependencias Python ya instaladas" -ForegroundColor Green

# 4. Verificar instalación de Redis
Write-Host ""
Write-Host "Verificando Redis..." -ForegroundColor Yellow

$redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue

if ($null -eq $redisService) {
    Write-Host "⚠️  Redis NO está instalado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPCIONES:" -ForegroundColor Cyan
    Write-Host "  1. Instalar Redis (recomendado para producción)"
    Write-Host "  2. Continuar sin Redis (usar cache en memoria)"
    Write-Host ""
    $choice = Read-Host "Seleccione opción (1 o 2)"
    
    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "Para instalar Redis en Windows:" -ForegroundColor Cyan
        Write-Host "1. Descargar: https://github.com/tporadowski/redis/releases" -ForegroundColor White
        Write-Host "2. Ejecutar instalador Redis-x64-X.X.XXX.msi" -ForegroundColor White
        Write-Host "3. Volver a ejecutar este script" -ForegroundColor White
        Write-Host ""
        Write-Host "Presione Enter para abrir el navegador en la página de descarga..."
        Read-Host
        Start-Process "https://github.com/tporadowski/redis/releases"
        exit 0
    } else {
        Write-Host "✓ Continuando sin Redis (se usará LocMemCache)" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ Redis instalado: $($redisService.Status)" -ForegroundColor Green
    
    # Iniciar Redis si no está corriendo
    if ($redisService.Status -ne "Running") {
        Write-Host "Iniciando Redis..." -ForegroundColor Yellow
        Start-Service -Name "Redis"
        Start-Sleep -Seconds 2
        Write-Host "✓ Redis iniciado correctamente" -ForegroundColor Green
    }
}

# 5. Crear directorios necesarios
Write-Host ""
Write-Host "Creando directorios necesarios..." -ForegroundColor Yellow

$dirs = @("backups", "logs", "media", "static")
foreach ($dir in $dirs) {
    $fullPath = Join-Path $projectRoot $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath | Out-Null
        Write-Host "✓ Creado: $dir\" -ForegroundColor Green
    } else {
        Write-Host "✓ Existe: $dir\" -ForegroundColor Gray
    }
}

# 6. Migrar base de datos
Write-Host ""
Write-Host "Aplicando migraciones de base de datos..." -ForegroundColor Yellow
& "$projectRoot\.venv\Scripts\python.exe" manage.py migrate --noinput

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migraciones aplicadas correctamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error en migraciones (puede ser normal si ya están aplicadas)" -ForegroundColor Yellow
}

# 7. Recolectar archivos estáticos
Write-Host ""
Write-Host "Recolectando archivos estáticos..." -ForegroundColor Yellow
& "$projectRoot\.venv\Scripts\python.exe" manage.py collectstatic --noinput

# 8. Prueba de importaciones críticas
Write-Host ""
Write-Host "Verificando módulos críticos..." -ForegroundColor Yellow

$testScript = @"
import sys
try:
    import redis
    print('✓ Redis: OK')
except ImportError as e:
    print(f'❌ Redis: {e}')
    
try:
    import psutil
    print('✓ psutil: OK')
except ImportError as e:
    print(f'❌ psutil: {e}')
    
try:
    from django.core.cache import cache
    cache.set('test', 'ok', 10)
    result = cache.get('test')
    if result == 'ok':
        print('✓ Django Cache: OK')
    else:
        print('⚠️ Django Cache: No funciona correctamente')
except Exception as e:
    print(f'❌ Django Cache: {e}')

try:
    from gestion.dashboard_views import dashboard_unificado
    print('✓ Dashboard views: OK')
except Exception as e:
    print(f'❌ Dashboard views: {e}')

try:
    from gestion.health_views import health_check
    print('✓ Health check views: OK')
except Exception as e:
    print(f'❌ Health check views: {e}')
"@

$testScript | & "$projectRoot\.venv\Scripts\python.exe" -

# 9. Instrucciones finales
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 DASHBOARD UNIFICADO" -ForegroundColor Yellow
Write-Host "   URL: http://localhost:8000/dashboard/" -ForegroundColor White
Write-Host ""

Write-Host "❤️  HEALTH CHECKS" -ForegroundColor Yellow
Write-Host "   Health: http://localhost:8000/health/" -ForegroundColor White
Write-Host "   Ready:  http://localhost:8000/ready/" -ForegroundColor White
Write-Host "   Alive:  http://localhost:8000/alive/" -ForegroundColor White
Write-Host ""

Write-Host "🚀 INICIAR SERVIDOR:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""

Write-Host "🔧 COMANDOS ÚTILES:" -ForegroundColor Yellow
Write-Host "   Backup manual:      python manage.py backup_database --compress --notify" -ForegroundColor White
Write-Host "   Health check:       python manage.py health_check --verbose" -ForegroundColor White
Write-Host "   Ver cache:          python manage.py shell" -ForegroundColor White
Write-Host ""

Write-Host "📚 DOCUMENTACIÓN:" -ForegroundColor Yellow
Write-Host "   GUIA_INSTALACION_MEJORAS_CRITICAS.md" -ForegroundColor White
Write-Host "   SESION_10_ENERO_2026.md" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Presione Enter para iniciar el servidor Django..."
Read-Host

& "$projectRoot\.venv\Scripts\python.exe" manage.py runserver
