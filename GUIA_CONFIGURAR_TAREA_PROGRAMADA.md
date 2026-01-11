# =============================================================================
# GUÍA PARA CONFIGURAR TAREA PROGRAMADA DE REINTENTOS SET
# =============================================================================

## OPCIÓN 1: Ejecutar script PowerShell (Recomendado)

1. Abrir PowerShell COMO ADMINISTRADOR (clic derecho > "Ejecutar como administrador")

2. Navegar al directorio del proyecto:
   ```powershell
   cd D:\anteproyecto20112025
   ```

3. Ejecutar el script de configuración:
   ```powershell
   .\scripts\configurar_tarea_programada.ps1
   ```

4. Verificar que la tarea fue creada:
   ```powershell
   Get-ScheduledTask -TaskName "CantinaReintentarFacturasSET"
   ```

---

## OPCIÓN 2: Configuración Manual por Task Scheduler (GUI)

### Paso 1: Abrir Task Scheduler
- Presionar `Win + R`
- Escribir: `taskschd.msc`
- Presionar Enter

### Paso 2: Crear nueva tarea
1. Clic en "Crear tarea..." (no "Crear tarea básica")

### Paso 3: Pestaña "General"
- **Nombre**: CantinaReintentarFacturasSET
- **Descripción**: Reintenta automáticamente el envío de facturas rechazadas por SET cada 15 minutos
- **Ejecutar solo cuando el usuario haya iniciado sesión**: Activado
- **Ejecutar con los privilegios más altos**: Desactivado

### Paso 4: Pestaña "Desencadenadores"
1. Clic en "Nuevo..."
2. **Comenzar la tarea**: En una programación
3. **Configuración**: Una vez
4. **Fecha de inicio**: Hoy
5. **Hora de inicio**: Ahora (o la hora deseada)
6. Marcar: ✓ **Repetir la tarea cada**: 15 minutos
7. **Durante**: Indefinidamente
8. Marcar: ✓ **Habilitado**
9. Clic en "Aceptar"

### Paso 5: Pestaña "Acciones"
1. Clic en "Nuevo..."
2. **Acción**: Iniciar un programa
3. **Programa o script**: `powershell.exe`
4. **Agregar argumentos (opcional)**:
   ```
   -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "D:\anteproyecto20112025\scripts\reintentar_facturas_automatico.ps1"
   ```
5. Clic en "Aceptar"

### Paso 6: Pestaña "Condiciones"
- Desmarcar: ☐ Iniciar la tarea solo si el equipo está conectado a la CA
- Marcar: ✓ Iniciar la tarea solo si la siguiente conexión de red está disponible: Cualquiera

### Paso 7: Pestaña "Configuración"
- Marcar: ✓ Permitir ejecutar la tarea a petición
- Marcar: ✓ Ejecutar la tarea lo antes posible si se omitió un inicio programado
- Si la tarea ya se está ejecutando: No iniciar una nueva instancia
- Detener la tarea si se ejecuta durante: 5 minutos

### Paso 8: Finalizar
1. Clic en "Aceptar"
2. Si se solicita contraseña, ingresar credenciales de Windows

---

## VERIFICACIÓN

### Probar ejecución manual:
```powershell
Start-ScheduledTask -TaskName "CantinaReintentarFacturasSET"
```

### Ver estado de la tarea:
```powershell
Get-ScheduledTask -TaskName "CantinaReintentarFacturasSET" | Get-ScheduledTaskInfo
```

### Ver logs de ejecuciones:
```powershell
Get-Content D:\anteproyecto20112025\logs\reintentos_set.log -Tail 50
```

### Ver próximas ejecuciones:
```powershell
(Get-ScheduledTaskInfo -TaskName "CantinaReintentarFacturasSET").NextRunTime
```

---

## ADMINISTRACIÓN DE LA TAREA

### Desactivar temporalmente:
```powershell
Disable-ScheduledTask -TaskName "CantinaReintentarFacturasSET"
```

### Reactivar:
```powershell
Enable-ScheduledTask -TaskName "CantinaReintentarFacturasSET"
```

### Eliminar la tarea:
```powershell
Unregister-ScheduledTask -TaskName "CantinaReintentarFacturasSET" -Confirm:$false
```

---

## NOTAS IMPORTANTES

1. **Logs**: Todas las ejecuciones se registran en:
   - `D:\anteproyecto20112025\logs\reintentos_set.log`

2. **Frecuencia**: La tarea se ejecuta cada 15 minutos automáticamente

3. **Límite de reintentos**: Cada ejecución procesa máximo 20 facturas

4. **Notificaciones**: Los errores se envían por email automáticamente

5. **Supervisión**: Revisar los logs periódicamente para detectar problemas

---

## TROUBLESHOOTING

### Error: "Acceso denegado"
- Abrir PowerShell como Administrador

### La tarea no aparece en Task Scheduler
- Verificar en la carpeta `\Cantina\` dentro del Task Scheduler

### La tarea no se ejecuta
- Verificar que el usuario tiene permisos de ejecución de PowerShell
- Verificar que el path al script es correcto
- Verificar logs del sistema: Event Viewer > Windows Logs > Application

### Los logs no se generan
- Verificar que existe el directorio: `D:\anteproyecto20112025\logs\`
- Verificar permisos de escritura en el directorio

---

## ALTERNATIVA: Ejecución Manual Periódica

Si no se puede configurar Task Scheduler, ejecutar manualmente:

```powershell
cd D:\anteproyecto20112025
.\.venv\Scripts\python.exe manage.py reintentar_facturas --limite=20
```

Se recomienda ejecutar este comando cada 15-30 minutos durante el horario de operación.
