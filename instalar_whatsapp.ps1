# ============================================================================
# INSTALADOR WHATSAPP-WEB.JS PARA CANTITITA
# ============================================================================

Write-Host "`n" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR WHATSAPP-WEB.JS - CANTITITA" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Verificar si Node.js esta instalado
Write-Host "Verificando Node.js..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "Node.js instalado: $nodeVersion" -ForegroundColor Green
    Write-Host "NPM instalado: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js NO encontrado" -ForegroundColor Red
    Write-Host "`nPor favor instala Node.js desde: https://nodejs.org/`n" -ForegroundColor Yellow
    Write-Host "Descarga la version LTS (recomendada)`n" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Ir a carpeta whatsapp-server
$serverPath = Join-Path $PSScriptRoot "whatsapp-server"

if (-not (Test-Path $serverPath)) {
    Write-Host "Carpeta whatsapp-server no encontrada" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Set-Location $serverPath
Write-Host "Ubicacion: $serverPath`n" -ForegroundColor Cyan

# Verificar si ya esta instalado
if (Test-Path "node_modules") {
    Write-Host "Las dependencias ya estan instaladas" -ForegroundColor Yellow
    $reinstall = Read-Host "Reinstalar? (s/n)"
    if ($reinstall -ne "s") {
        Write-Host "`nInstalacion omitida`n" -ForegroundColor Green
        Read-Host "Presiona Enter para continuar"
        exit 0
    }
    Write-Host "`nEliminando node_modules..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
}

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
Write-Host "(Esto puede tomar 2-3 minutos)`n" -ForegroundColor Gray

npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "   INSTALACION COMPLETADA" -ForegroundColor Green
    Write-Host "============================================`n" -ForegroundColor Green
    
    Write-Host "Siguiente paso:" -ForegroundColor Cyan
    Write-Host "   1. Ejecuta: node server.js" -ForegroundColor Yellow
    Write-Host "   2. Escanea el QR con WhatsApp SECUNDARIO" -ForegroundColor White
    Write-Host "   3. Listo para usar`n" -ForegroundColor White
    
    Write-Host "IMPORTANTE:" -ForegroundColor Red
    Write-Host "   - Usa SOLO numero secundario" -ForegroundColor Yellow
    Write-Host "   - NO usar numero principal de negocio" -ForegroundColor Yellow
    Write-Host "   - Riesgo de BAN si se usa numero principal`n" -ForegroundColor Yellow
    
    $iniciar = Read-Host "Iniciar servidor ahora? (s/n)"
    if ($iniciar -eq "s") {
        Write-Host "`nIniciando servidor...`n" -ForegroundColor Cyan
        node server.js
    }
    
} else {
    Write-Host "`n============================================" -ForegroundColor Red
    Write-Host "   ERROR EN LA INSTALACION" -ForegroundColor Red
    Write-Host "============================================`n" -ForegroundColor Red
    Write-Host "Por favor verifica tu conexion a internet e intenta de nuevo`n" -ForegroundColor Yellow
}

Read-Host "`nPresiona Enter para salir"
