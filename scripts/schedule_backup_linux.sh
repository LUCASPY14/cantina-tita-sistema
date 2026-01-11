#!/bin/bash
# Script para configurar backup automático en Linux/Ubuntu
# Ejecutar con: sudo bash schedule_backup_linux.sh

echo "========================================"
echo "CONFIGURAR BACKUP AUTOMÁTICO - LINUX"
echo "========================================"
echo ""

# Configuración
PROJECT_PATH="/var/www/cantina_project"  # Cambia según tu instalación
PYTHON_PATH="/usr/bin/python3"           # O el path de tu virtualenv
BACKUP_COMMAND="manage.py backup_database --compress --keep-days=30 --notify"
CRON_TIME="0 2 * * *"  # Diariamente a las 2:00 AM

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Error: Este script debe ejecutarse como root (sudo)"
    exit 1
fi

echo "📁 Directorio del proyecto: $PROJECT_PATH"
echo "🐍 Python: $PYTHON_PATH"
echo "⏰ Horario: Diario a las 2:00 AM"
echo ""

# Crear script de backup
BACKUP_SCRIPT="$PROJECT_PATH/scripts/run_backup.sh"
cat > $BACKUP_SCRIPT << EOF
#!/bin/bash
cd $PROJECT_PATH
$PYTHON_PATH $BACKUP_COMMAND >> $PROJECT_PATH/logs/backup.log 2>&1
EOF

# Hacer ejecutable
chmod +x $BACKUP_SCRIPT
echo "✅ Script de backup creado: $BACKUP_SCRIPT"

# Agregar a crontab
CRON_JOB="$CRON_TIME $BACKUP_SCRIPT"

# Verificar si ya existe la tarea
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️  La tarea cron ya existe, actualizando..."
    crontab -l | grep -v "$BACKUP_SCRIPT" | crontab -
fi

# Agregar nueva tarea
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "========================================"
echo "✅ TAREA CRON CONFIGURADA"
echo "========================================"
echo ""
echo "📋 Detalles:"
echo "  - Frecuencia: Diaria a las 2:00 AM"
echo "  - Script: $BACKUP_SCRIPT"
echo "  - Logs: $PROJECT_PATH/logs/backup.log"
echo ""
echo "Para ver tareas cron:"
echo "  crontab -l"
echo ""
echo "Para ejecutar manualmente:"
echo "  $BACKUP_SCRIPT"
echo ""
