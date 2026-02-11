# Script de desarrollo para PowerShell - Cantina Tita Sistema
param(
    [Parameter(HelpMessage="Ejecutar solo backend")]
    [switch]$Backend,
    
    [Parameter(HelpMessage="Ejecutar solo frontend")]
    [switch]$Frontend,
    
    [Parameter(HelpMessage="Instalar dependencias")]
    [switch]$Setup,
    
    [Parameter(HelpMessage="Mostrar ayuda")]
    [switch]$Help
)

function Write-Banner {
    Write-Host ""
    Write-Host "🚀 ========================================" -ForegroundColor Cyan
    Write-Host "   CANTINA TITA - ENTORNO DE DESARROLLO" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Show-Help {
    Write-Banner
    Write-Host "OPCIONES DISPONIBLES:" -ForegroundColor White
    Write-Host ""
    Write-Host "  .\dev.ps1                 " -NoNewline; Write-Host "Ejecutar frontend + backend simultáneamente" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 -Backend        " -NoNewline; Write-Host "Ejecutar solo backend (Django)" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 -Frontend       " -NoNewline; Write-Host "Ejecutar solo frontend (Vite)" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 -Setup          " -NoNewline; Write-Host "Instalar todas las dependencias" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 -Help           " -NoNewline; Write-Host "Mostrar esta ayuda" -ForegroundColor Gray
    Write-Host ""
    Write-Host "PUERTOS:" -ForegroundColor White
    Write-Host "  📡 Backend:  http://localhost:8000/" -ForegroundColor Cyan
    Write-Host "  🎨 Frontend: http://localhost:3000/" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    $allGood = $true
    
    # Verificar Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Success "Node.js $nodeVersion instalado"
        } else {
            throw "Node.js no encontrado"
        }
    } catch {
        Write-Error "Node.js no está instalado"
        Write-Info "Instale desde: https://nodejs.org/"
        $allGood = $false
    }
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Success "Python $pythonVersion disponible"
        } else {
            throw "Python no encontrado"
        }
    } catch {
        Write-Error "Python no está disponible"
        Write-Info "Active el entorno virtual o instale Python"
        $allGood = $false
    }
    
    # Verificar entorno virtual
    if (Test-Path ".venv\Scripts\activate.ps1") {
        Write-Success "Entorno virtual encontrado"
    } else {
        Write-Warning "Entorno virtual no encontrado"
        Write-Info "Cree con: python -m venv .venv"
    }
    
    return $allGood
}

function Install-Dependencies {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
    
    # Dependencias frontend
    if (Test-Path "frontend\package.json") {
        Write-Host "🎨 Instalando dependencias frontend..."
        Set-Location frontend
        npm install
        Set-Location ..
        Write-Success "Dependencias frontend instaladas"
    }
    
    # Dependencias backend
    if (Test-Path "backend\requirements.txt") {
        Write-Host "🐍 Instalando dependencias backend..."
        if (Test-Path ".venv\Scripts\activate.ps1") {
            & .venv\Scripts\activate.ps1
        }
        Set-Location backend
        pip install -r requirements.txt
        Set-Location ..
        Write-Success "Dependencias backend instaladas"
    }
}

function Start-Development {
    param([string]$Mode = "both")
    
    switch ($Mode) {
        "backend" {
            Write-Host "🚀 Iniciando solo backend..." -ForegroundColor Green
            Write-Host "📡 Backend: http://localhost:8000/" -ForegroundColor Cyan
            npm run dev:only-backend
        }
        "frontend" {
            Write-Host "🚀 Iniciando solo frontend..." -ForegroundColor Green
            Write-Host "🎨 Frontend: http://localhost:3000/" -ForegroundColor Cyan
            npm run dev:only-frontend
        }
        "both" {
            Write-Host "🚀 Iniciando entorno completo..." -ForegroundColor Green
            Write-Host "📡 Backend: http://localhost:8000/" -ForegroundColor Cyan
            Write-Host "🎨 Frontend: http://localhost:3000/" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "💡 Presione Ctrl+C para detener ambos servidores" -ForegroundColor Yellow
            Write-Host ""
            npm run dev
        }
    }
}

# Ejecutar script principal
if ($Help) {
    Show-Help
    exit 0
}

Write-Banner

if ($Setup) {
    if (Test-Prerequisites) {
        Install-Dependencies
        Write-Success "Configuración completada"
    }
    exit 0
}

if (!(Test-Prerequisites)) {
    Write-Error "Prerrequisitos no cumplidos. Use -Setup para instalar dependencias."
    exit 1
}

if ($Backend) {
    Start-Development "backend"
} elseif ($Frontend) {
    Start-Development "frontend"
} else {
    Start-Development "both"
}

Write-Host ""
Write-Host "⛔ Desarrollo finalizado" -ForegroundColor Red