# Script para configurar tarea programada de reintentos SET
# Ejecutar como Administrador

$ErrorActionPreference = "Stop"

Write-Host "Configurando tarea programada para reintentos SET..." -ForegroundColor Cyan

# Parámetros de la tarea
$TaskName = "CantinaReintentarFacturasSET"
$TaskDescription = "Reintenta automáticamente el envío de facturas rechazadas por SET cada 15 minutos"
$ScriptPath = "D:\anteproyecto20112025\scripts\reintentar_facturas_automatico.ps1"
$TaskPath = "\Cantina\"

# Verificar que el script existe
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR - No se encuentra el script en $ScriptPath" -ForegroundColor Red
    exit 1
}

# Eliminar tarea existente si existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Eliminando tarea existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Crear acción (ejecutar PowerShell con el script)
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$ScriptPath`""

# Crear trigger (cada 15 minutos, indefinidamente)
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)

# Configuración de la tarea
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# Crear principal (usuario actual)
$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Limited

# Registrar la tarea
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -TaskPath $TaskPath `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description $TaskDescription `
        -Force | Out-Null
    
    Write-Host "OK - Tarea programada creada exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalles de la tarea:" -ForegroundColor Cyan
    Write-Host "  Nombre: $TaskName" -ForegroundColor White
    Write-Host "  Ubicacion: $TaskPath$TaskName" -ForegroundColor White
    Write-Host "  Frecuencia: Cada 15 minutos" -ForegroundColor White
    Write-Host "  Script: $ScriptPath" -ForegroundColor White
    Write-Host "  Logs: D:\anteproyecto20112025\logs\reintentos_set.log" -ForegroundColor White
    Write-Host ""
    
    # Mostrar proximas ejecuciones
    $Task = Get-ScheduledTask -TaskName $TaskName
    $TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    
    Write-Host "Proxima ejecucion: $($TaskInfo.NextRunTime)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para ver el estado de la tarea ejecute:" -ForegroundColor Cyan
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo" -ForegroundColor White
    Write-Host ""
    Write-Host "Para ejecutar manualmente:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "Para desactivar la tarea:" -ForegroundColor Cyan
    Write-Host "  Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "Para eliminar la tarea:" -ForegroundColor Cyan
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor White
    
} catch {
    Write-Host "ERROR - Error al crear la tarea: $_" -ForegroundColor Red
    exit 1
}
