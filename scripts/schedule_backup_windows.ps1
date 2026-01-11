# Script de PowerShell para programar backup automático en Windows
# Ejecutar como Administrador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURAR BACKUP AUTOMÁTICO - WINDOWS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$ProjectPath = "d:\anteproyecto20112025"
$PythonPath = "python"  # Cambia si usas un entorno virtual específico
$BackupCommand = "manage.py backup_database --compress --keep-days=30 --notify"

# Verificar que el directorio del proyecto existe
if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ Error: Directorio del proyecto no encontrado: $ProjectPath" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Directorio del proyecto: $ProjectPath" -ForegroundColor Green
Write-Host "🐍 Python: $PythonPath" -ForegroundColor Green
Write-Host ""

# Crear script batch que ejecutará el backup
$BatchFile = Join-Path $ProjectPath "scripts\run_backup.bat"
$BatchContent = @"
@echo off
cd /d $ProjectPath
$PythonPath $BackupCommand
"@

# Guardar el archivo batch
$BatchContent | Out-File -FilePath $BatchFile -Encoding ASCII
Write-Host "✅ Script batch creado: $BatchFile" -ForegroundColor Green

# Configurar Tarea Programada
$TaskName = "Cantina_Backup_Diario"
$TaskDescription = "Backup automático diario de la base de datos Cantina POS"

# Eliminar tarea si ya existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "🗑️  Eliminando tarea existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Crear trigger para ejecutar diariamente a las 2:00 AM
$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00"

# Crear acción
$Action = New-ScheduledTaskAction -Execute $BatchFile

# Configurar settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -DontStopOnIdleEnd

# Registrar la tarea programada
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -User "SYSTEM" `
    -RunLevel Highest

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ TAREA PROGRAMADA CONFIGURADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Detalles:" -ForegroundColor Cyan
Write-Host "  - Nombre: $TaskName"
Write-Host "  - Frecuencia: Diaria a las 2:00 AM"
Write-Host "  - Retención: 30 días"
Write-Host "  - Compresión: Habilitada"
Write-Host "  - Notificaciones: Habilitadas"
Write-Host ""
Write-Host "Para ver la tarea:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "Para ejecutar manualmente:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "Para desactivar:" -ForegroundColor Yellow
Write-Host "  Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host ""
