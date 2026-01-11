# Script para reintentar facturas rechazadas por SET
# Se ejecuta cada 15 minutos vía Task Scheduler

$ErrorActionPreference = "Stop"
$LogFile = "D:\anteproyecto20112025\logs\reintentos_set.log"

# Crear directorio de logs si no existe
$LogDir = Split-Path $LogFile -Parent
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Función para escribir en log
function Write-Log {
    param($Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Add-Content -Path $LogFile
}

try {
    Write-Log "========== INICIO REINTENTO AUTOMÁTICO =========="
    
    # Cambiar al directorio del proyecto
    Set-Location "D:\anteproyecto20112025"
    
    # Activar entorno virtual y ejecutar comando
    & "D:\anteproyecto20112025\.venv\Scripts\python.exe" manage.py reintentar_facturas --limite=20 2>&1 | ForEach-Object {
        Write-Log $_
    }
    
    Write-Log "✓ Reintento completado exitosamente"
    Write-Log "========== FIN REINTENTO =========="
    
} catch {
    Write-Log "❌ ERROR: $_"
    Write-Log "StackTrace: $($_.ScriptStackTrace)"
    exit 1
}
