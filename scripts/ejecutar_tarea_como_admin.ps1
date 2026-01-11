# Script PowerShell para ejecutar tarea programada como Administrador
# Archivo: ejecutar_tarea_como_admin.ps1

<#
.SYNOPSIS
    Ejecuta la tarea programada de backup con privilegios de administrador

.DESCRIPTION
    Este script verifica privilegios, eleva si es necesario, y ejecuta
    la tarea programada de backup de Cantina Tita

.NOTES
    Autor: Sistema Cantina Tita
    Fecha: Enero 2026
#>

# === VERIFICAR SI SE ESTÁ EJECUTANDO COMO ADMINISTRADOR ===
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# === ELEVAR PRIVILEGIOS SI ES NECESARIO ===
if (-not (Test-Administrator)) {
    Write-Host "⚠️  Este script requiere privilegios de Administrador" -ForegroundColor Yellow
    Write-Host "🔄 Elevando privilegios..." -ForegroundColor Cyan
    
    # Re-ejecutar este script como administrador
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "✅ Ejecutando como Administrador" -ForegroundColor Green
Write-Host ""

# === CONFIGURACIÓN ===
$NOMBRE_TAREA = "CantinaBackupDiario"
$PROYECTO_PATH = "D:\anteproyecto20112025"
$PYTHON_EXE = "$PROYECTO_PATH\.venv\Scripts\python.exe"
$MANAGE_PY = "$PROYECTO_PATH\manage.py"

# === VERIFICAR EXISTENCIA DE ARCHIVOS ===
Write-Host "🔍 Verificando archivos..." -ForegroundColor Cyan

if (-not (Test-Path $PYTHON_EXE)) {
    Write-Host "❌ ERROR: No se encuentra Python en: $PYTHON_EXE" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

if (-not (Test-Path $MANAGE_PY)) {
    Write-Host "❌ ERROR: No se encuentra manage.py en: $MANAGE_PY" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Archivos verificados" -ForegroundColor Green
Write-Host ""

# === VERIFICAR SI LA TAREA EXISTE ===
Write-Host "🔍 Verificando tarea programada..." -ForegroundColor Cyan

try {
    $tarea = Get-ScheduledTask -TaskName $NOMBRE_TAREA -ErrorAction Stop
    Write-Host "✅ Tarea encontrada: $NOMBRE_TAREA" -ForegroundColor Green
    
    # Mostrar información de la tarea
    Write-Host ""
    Write-Host "📋 INFORMACIÓN DE LA TAREA:" -ForegroundColor Cyan
    Write-Host "   Nombre: $($tarea.TaskName)"
    Write-Host "   Estado: $($tarea.State)"
    Write-Host "   Última ejecución: $($tarea.LastRunTime)"
    Write-Host "   Próxima ejecución: $($tarea.NextRunTime)"
    Write-Host "   Resultado última ejecución: $($tarea.LastTaskResult)"
    Write-Host ""
    
} catch {
    Write-Host "❌ ERROR: La tarea '$NOMBRE_TAREA' no existe" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 SOLUCIÓN: Ejecuta primero el script de configuración:" -ForegroundColor Yellow
    Write-Host "   .\scripts\configurar_tarea_programada.ps1" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

# === MENÚ DE OPCIONES ===
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   ADMINISTRACIÓN DE TAREA PROGRAMADA - CANTINA TITA" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Selecciona una opción:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  [1] Ejecutar tarea AHORA" -ForegroundColor White
Write-Host "  [2] Ver historial de ejecuciones" -ForegroundColor White
Write-Host "  [3] Habilitar tarea" -ForegroundColor White
Write-Host "  [4] Deshabilitar tarea" -ForegroundColor White
Write-Host "  [5] Ver configuración completa" -ForegroundColor White
Write-Host "  [6] Probar comando manualmente" -ForegroundColor White
Write-Host "  [0] Salir" -ForegroundColor Gray
Write-Host ""

$opcion = Read-Host "Opción"

switch ($opcion) {
    "1" {
        # EJECUTAR TAREA AHORA
        Write-Host ""
        Write-Host "🚀 EJECUTANDO TAREA: $NOMBRE_TAREA" -ForegroundColor Cyan
        Write-Host "   Esto puede tardar varios minutos..." -ForegroundColor Yellow
        Write-Host ""
        
        try {
            Start-ScheduledTask -TaskName $NOMBRE_TAREA
            Write-Host "✅ Tarea iniciada exitosamente" -ForegroundColor Green
            Write-Host ""
            Write-Host "⏳ Esperando 5 segundos para verificar estado..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            # Verificar estado
            $tareaActualizada = Get-ScheduledTask -TaskName $NOMBRE_TAREA
            Write-Host ""
            Write-Host "📊 ESTADO ACTUAL:" -ForegroundColor Cyan
            Write-Host "   Estado: $($tareaActualizada.State)" -ForegroundColor White
            Write-Host "   Última ejecución: $($tareaActualizada.LastRunTime)" -ForegroundColor White
            
            if ($tareaActualizada.State -eq "Running") {
                Write-Host ""
                Write-Host "⚠️  La tarea está ejecutándose en segundo plano" -ForegroundColor Yellow
                Write-Host "   Revisa los logs en: $PROYECTO_PATH\logs\" -ForegroundColor White
            } else {
                Write-Host ""
                Write-Host "✅ Tarea completada" -ForegroundColor Green
                
                # Mostrar resultado
                $resultado = $tareaActualizada.LastTaskResult
                if ($resultado -eq 0) {
                    Write-Host "   Resultado: EXITOSO (código 0)" -ForegroundColor Green
                } else {
                    Write-Host "   Resultado: ERROR (código $resultado)" -ForegroundColor Red
                    Write-Host "   Revisa los logs para más detalles" -ForegroundColor Yellow
                }
            }
            
        } catch {
            Write-Host "❌ ERROR al ejecutar la tarea: $_" -ForegroundColor Red
        }
    }
    
    "2" {
        # VER HISTORIAL
        Write-Host ""
        Write-Host "📜 HISTORIAL DE EJECUCIONES (Últimas 20)" -ForegroundColor Cyan
        Write-Host ""
        
        try {
            # Obtener eventos del Visor de eventos
            $eventos = Get-WinEvent -FilterHashtable @{
                LogName = 'Microsoft-Windows-TaskScheduler/Operational'
                ID = 102  # Tarea completada
            } -MaxEvents 20 -ErrorAction SilentlyContinue | Where-Object { $_.Message -like "*$NOMBRE_TAREA*" }
            
            if ($eventos) {
                foreach ($evento in $eventos) {
                    $tiempo = $evento.TimeCreated
                    Write-Host "   [$tiempo] Tarea ejecutada" -ForegroundColor White
                }
            } else {
                Write-Host "   No se encontraron eventos recientes" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "   ⚠️  No se pudo acceder al historial: $_" -ForegroundColor Yellow
        }
    }
    
    "3" {
        # HABILITAR TAREA
        Write-Host ""
        Write-Host "✅ Habilitando tarea..." -ForegroundColor Cyan
        try {
            Enable-ScheduledTask -TaskName $NOMBRE_TAREA
            Write-Host "✅ Tarea habilitada exitosamente" -ForegroundColor Green
        } catch {
            Write-Host "❌ ERROR: $_" -ForegroundColor Red
        }
    }
    
    "4" {
        # DESHABILITAR TAREA
        Write-Host ""
        Write-Host "⚠️  Deshabilitando tarea..." -ForegroundColor Yellow
        try {
            Disable-ScheduledTask -TaskName $NOMBRE_TAREA
            Write-Host "✅ Tarea deshabilitada" -ForegroundColor Green
        } catch {
            Write-Host "❌ ERROR: $_" -ForegroundColor Red
        }
    }
    
    "5" {
        # VER CONFIGURACIÓN COMPLETA
        Write-Host ""
        Write-Host "⚙️  CONFIGURACIÓN COMPLETA" -ForegroundColor Cyan
        Write-Host ""
        
        $tareaCompleta = Get-ScheduledTask -TaskName $NOMBRE_TAREA
        $tareaInfo = Get-ScheduledTaskInfo -TaskName $NOMBRE_TAREA
        
        Write-Host "GENERAL:" -ForegroundColor Yellow
        Write-Host "   Nombre: $($tareaCompleta.TaskName)" -ForegroundColor White
        Write-Host "   Estado: $($tareaCompleta.State)" -ForegroundColor White
        Write-Host "   Autor: $($tareaCompleta.Author)" -ForegroundColor White
        Write-Host "   Descripción: $($tareaCompleta.Description)" -ForegroundColor White
        Write-Host ""
        
        Write-Host "HISTORIAL:" -ForegroundColor Yellow
        Write-Host "   Última ejecución: $($tareaInfo.LastRunTime)" -ForegroundColor White
        Write-Host "   Próxima ejecución: $($tareaInfo.NextRunTime)" -ForegroundColor White
        Write-Host "   Resultado: $($tareaInfo.LastTaskResult)" -ForegroundColor White
        Write-Host ""
        
        Write-Host "TRIGGER:" -ForegroundColor Yellow
        foreach ($trigger in $tareaCompleta.Triggers) {
            Write-Host "   Tipo: Daily" -ForegroundColor White
            Write-Host "   Hora: $($trigger.StartBoundary)" -ForegroundColor White
        }
        Write-Host ""
        
        Write-Host "ACCIÓN:" -ForegroundColor Yellow
        foreach ($accion in $tareaCompleta.Actions) {
            Write-Host "   Ejecutable: $($accion.Execute)" -ForegroundColor White
            Write-Host "   Argumentos: $($accion.Arguments)" -ForegroundColor White
            Write-Host "   Directorio: $($accion.WorkingDirectory)" -ForegroundColor White
        }
    }
    
    "6" {
        # PROBAR COMANDO MANUALMENTE
        Write-Host ""
        Write-Host "🧪 PROBANDO COMANDO MANUALMENTE" -ForegroundColor Cyan
        Write-Host "   Esto ejecutará el comando exacto de la tarea programada" -ForegroundColor Yellow
        Write-Host ""
        
        $comando = "$PYTHON_EXE $MANAGE_PY ejecutar_backup"
        Write-Host "📋 Comando: $comando" -ForegroundColor White
        Write-Host ""
        
        Write-Host "⏳ Ejecutando..." -ForegroundColor Yellow
        
        try {
            # Cambiar al directorio del proyecto
            Push-Location $PROYECTO_PATH
            
            # Ejecutar comando
            & $PYTHON_EXE $MANAGE_PY ejecutar_backup
            
            Pop-Location
            
            Write-Host ""
            Write-Host "✅ Comando ejecutado" -ForegroundColor Green
            Write-Host "   Revisa la salida arriba para verificar si fue exitoso" -ForegroundColor Yellow
            
        } catch {
            Write-Host "❌ ERROR: $_" -ForegroundColor Red
            Pop-Location
        }
    }
    
    "0" {
        Write-Host ""
        Write-Host "👋 Saliendo..." -ForegroundColor Gray
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Opción inválida" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ""
Read-Host "Presiona Enter para salir"
