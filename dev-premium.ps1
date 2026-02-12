# 🚀 Script Premium de Desarrollo - Cantina TITA
# ================================================
# PowerShell script para inicializar el entorno de desarrollo completo

param(
    [switch]$SkipChecks = $false,
    [switch]$ShowHelp = $false
)

# Configuración de colores
$Colors = @{
    Header = "Magenta"
    Success = "Green"
    Info = "Cyan" 
    Warning = "Yellow"
    Error = "Red"
    Highlight = "White"
}

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Show-Banner {
    Write-ColorText "╔══════════════════════════════════════════╗" "Header"
    Write-ColorText "║  🍽️  CANTINA TITA - DESARROLLO PREMIUM  ║" "Header"  
    Write-ColorText "║                                          ║" "Header"
    Write-ColorText "║  Sistema de Gestión Completo             ║" "Header"
    Write-ColorText "║  Django 5.2.8 + Vite Frontend          ║" "Header"
    Write-ColorText "╚══════════════════════════════════════════╝" "Header"
    Write-Host ""
}

function Show-Help {
    Write-ColorText "📋 AYUDA - Script de Desarrollo Premium" "Info"
    Write-ColorText "═══════════════════════════════════════" "Info"
    Write-Host ""
    Write-ColorText "SINTAXIS:" "Highlight"
    Write-Host "  .\dev-premium.ps1 [PARÁMETROS]"
    Write-Host ""
    Write-ColorText "PARÁMETROS:" "Highlight"
    Write-Host "  -SkipChecks    Omite las verificaciones iniciales"
    Write-Host "  -ShowHelp      Muestra esta ayuda"
    Write-Host ""
    Write-ColorText "EJEMPLOS:" "Highlight"
    Write-Host "  .\dev-premium.ps1                  # Ejecutar normal"
    Write-Host "  .\dev-premium.ps1 -SkipChecks      # Ejecutar sin verificaciones"
    Write-Host "  .\dev-premium.ps1 -ShowHelp        # Mostrar ayuda"
    Write-Host ""
    Write-ColorText "URLs DE DESARROLLO:" "Success"
    Write-Host "  • Backend Django:  http://localhost:8000/"
    Write-Host "  • Admin Django:    http://localhost:8000/admin/"  
    Write-Host "  • Frontend Vite:   http://localhost:5173/"
    Write-Host "  • Demo Premium:    http://localhost:5173/demo-premium.html"
    Write-Host "  • Demo Mobile:     http://localhost:5173/demo-mobile.html"
}

function Test-Requirements {
    Write-ColorText "🔍 Verificando requisitos del sistema..." "Info"
    
    $errors = @()
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                $errors += "Python 3.8+ requerido (encontrado: $pythonVersion)"
            } else {
                Write-ColorText "✅ Python: $pythonVersion" "Success"
            }
        }
    } catch {
        $errors += "Python no encontrado"
    }
    
    # Verificar Node.js
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v(\d+)") {
            $major = [int]$matches[1]
            if ($major -lt 16) {
                $errors += "Node.js 16+ requerido (encontrado: $nodeVersion)"
            } else {
                Write-ColorText "✅ Node.js: $nodeVersion" "Success"
            }
        }
    } catch {
        $errors += "Node.js no encontrado"
    }
    
    # Verificar directorios
    if (-not (Test-Path "backend")) {
        $errors += "Directorio 'backend' no encontrado"
    } else {
        Write-ColorText "✅ Directorio backend encontrado" "Success"
    }
    
    if (-not (Test-Path "frontend")) {
        $errors += "Directorio 'frontend' no encontrado" 
    } else {
        Write-ColorText "✅ Directorio frontend encontrado" "Success"
    }
    
    # Verificar archivo manage.py
    if (-not (Test-Path "backend/manage.py")) {
        $errors += "manage.py no encontrado en backend/"
    }
    
    # Verificar package.json
    if (-not (Test-Path "frontend/package.json")) {
        $errors += "package.json no encontrado en frontend/"
    }
    
    if ($errors.Count -gt 0) {
        Write-ColorText "❌ Errores encontrados:" "Error"
        foreach ($error in $errors) {
            Write-ColorText "   • $error" "Error"
        }
        Write-ColorText "Por favor, resuelve estos problemas antes de continuar." "Warning"
        return $false
    }
    
    Write-ColorText "✅ Todos los requisitos verificados correctamente" "Success"
    return $true
}

function Show-DevelopmentInfo {
    Write-ColorText "📋 INFORMACIÓN DE DESARROLLO" "Header"
    Write-ColorText "═══════════════════════════════════════════" "Info"
    Write-Host ""
    
    Write-ColorText "🌐 URLs Principales:" "Success"
    Write-Host "  • Backend Django:  http://localhost:8000/"
    Write-Host "  • Admin Django:    http://localhost:8000/admin/"
    Write-Host "  • Frontend Vite:   http://localhost:5173/"
    Write-Host "  • Demo Premium:    http://localhost:5173/demo-premium.html"
    Write-Host "  • Demo Mobile:     http://localhost:5173/demo-mobile.html"
    Write-Host ""
    
    Write-ColorText "📱 Funcionalidades Implementadas:" "Info"
    Write-Host "  ✅ Sistema POS completo"
    Write-Host "  ✅ Gestión de inventario"
    Write-Host "  ✅ Sistema de tarjetas recargables"
    Write-Host "  ✅ Portal web responsive"
    Write-Host "  ✅ Dashboard analytics"
    Write-Host "  ✅ Admin interface con 40+ modelos"
    Write-Host "  ✅ UI/UX premium con Glassmorphism"
    Write-Host "  ✅ Animaciones y efectos avanzados"
    Write-Host "  ✅ PWA capabilities"
    Write-Host "  ✅ Mobile-first design"
    Write-Host ""
    
    Write-ColorText "🔧 Comandos Útiles (ejecutar en otra terminal):" "Warning"
    Write-Host "  • Django Shell:    python backend/manage.py shell"
    Write-Host "  • Crear Usuario:   python backend/manage.py createsuperuser"
    Write-Host "  • Migraciones:     python backend/manage.py makemigrations"
    Write-Host "  • Aplicar Migr:    python backend/manage.py migrate"
    Write-Host "  • Collectstatic:   python backend/manage.py collectstatic"
    Write-Host ""
    
    Write-ColorText "🎨 Arquitectura Tecnológica:" "Header"
    Write-Host "  • Backend: Django 5.2.8 + MySQL"
    Write-Host "  • Frontend: Vite 5.4.21 + TypeScript"
    Write-Host "  • Estilos: Tailwind CSS + DaisyUI"
    Write-Host "  • Interactividad: Alpine.js + HTMX"
    Write-Host "  • Diseño: Glassmorphism + Animaciones Premium"
    Write-Host ""
    
    Write-ColorText "💡 Estado del Desarrollo:" "Success"
    Write-Host "  🔥 Hot Reload activado en ambos servidores"
    Write-Host "  🎨 CSS se recompila automáticamente"
    Write-Host "  📱 Responsive design optimizado"
    Write-Host "  ⚡ TypeScript con validación en tiempo real"
    Write-Host "  ✨ Componentes premium listos para usar"
    Write-Host ""
}

function Start-DjangoServer {
    Write-ColorText "🐍 Iniciando servidor Django..." "Info"
    
    Push-Location "backend"
    try {
        # Aplicar migraciones
        Write-ColorText "📦 Aplicando migraciones..." "Info"
        python manage.py migrate
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "🚀 Django iniciado exitosamente en http://localhost:8000/" "Success"
            Write-Host ""
            Write-ColorText "Presiona Ctrl+C para detener los servidores" "Warning"
            python manage.py runserver 8000
        } else {
            Write-ColorText "❌ Error al aplicar migraciones" "Error"
        }
    } catch {
        Write-ColorText "❌ Error inesperado: $($_.Exception.Message)" "Error"
    } finally {
        Pop-Location
    }
}

function Start-ViteServer {
    Write-ColorText "⚡ Preparando servidor Vite..." "Info"
    
    Push-Location "frontend"
    try {
        # Instalar dependencias si es necesario
        if (-not (Test-Path "node_modules")) {
            Write-ColorText "📦 Instalando dependencias de NPM..." "Info"
            npm install
            if ($LASTEXITCODE -ne 0) {
                Write-ColorText "❌ Error al instalar dependencias" "Error"
                return
            }
        }
        
        Write-ColorText "⚡ Vite iniciado exitosamente en http://localhost:5173/" "Success"
        npm run dev
    } catch {
        Write-ColorText "❌ Error al iniciar Vite: $($_.Exception.Message)" "Error"
    } finally {
        Pop-Location  
    }
}

function Start-Development {
    Write-ColorText "⚙️  Iniciando entorno de desarrollo completo..." "Info"
    Write-Host ""
    
    # Iniciar servidores en paralelo usando PowerShell Jobs
    $djangoJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & ".\dev-premium.ps1" -StartDjango
    }
    
    Start-Sleep -Seconds 3  # Dar tiempo a Django para iniciar
    
    $viteJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD  
        & ".\dev-premium.ps1" -StartVite
    }
    
    Write-ColorText "🌟 Ambos servidores iniciándose..." "Success"
    Write-ColorText "Presiona Ctrl+C para detener ambos servidores" "Warning"
    Write-Host ""
    
    try {
        # Esperar a que terminen los trabajos
        Wait-Job $djangoJob, $viteJob
    } finally {
        # Limpiar trabajos
        Remove-Job $djangoJob -Force -ErrorAction SilentlyContinue
        Remove-Job $viteJob -Force -ErrorAction SilentlyContinue
        Write-ColorText "🛑 Servidores detenidos" "Warning"
        Write-ColorText "✨ ¡Desarrollo completado! ¡Hasta la próxima!" "Success"
    }
}

# Parámetros internos para jobs
param(
    [switch]$StartDjango = $false,
    [switch]$StartVite = $false
)

# Función principal
function Main {
    if ($ShowHelp) {
        Show-Help
        return
    }
    
    if ($StartDjango) {
        Start-DjangoServer
        return
    }
    
    if ($StartVite) {
        Start-ViteServer
        return
    }
    
    Show-Banner
    
    if (-not $SkipChecks) {
        if (-not (Test-Requirements)) {
            Write-ColorText "Usa -SkipChecks para omitir las verificaciones" "Info"
            return
        }
    }
    
    Show-DevelopmentInfo
    
    # Preguntar si continuar
    Write-ColorText "¿Deseas iniciar los servidores de desarrollo? (S/N): " "Highlight" -NoNewline
    $response = Read-Host
    
    if ($response -match "^[SsYy]") {
        Start-Development
    } else {
        Write-ColorText "👋 ¡Desarrollo cancelado! Ejecuta el script cuando estés listo." "Info"
    }
}

# Ejecutar función principal
Main