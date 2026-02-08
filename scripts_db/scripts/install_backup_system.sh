#!/bin/bash
# ============================================
# INSTALADOR SISTEMA DE BACKUP - CANTINATITA
# ============================================

set -e  # Detener en caso de error

echo "🚀 Iniciando instalación del sistema de backup Cantinatita"
echo "========================================================"

# 1. Verificar que estamos como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Por favor ejecutar como root o con sudo"
    exit 1
fi

# 2. Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p /scripts/backup
mkdir -p /backups/mysql
mkdir -p /var/log/mysql_backup

# 3. Copiar script de backup
echo "📝 Copiando script de backup..."
cat > /scripts/backup/backup_cantinatita.sh << 'EOF'
#!/bin/bash
# ============================================
# SCRIPT DE BACKUP AUTOMÁTICO - CANTINATITA
# ============================================

# Configuración
DB_NAME="cantinatitadb"
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_backup_${DATE}.sql"
LATEST_FILE="${BACKUP_DIR}/${DB_NAME}_backup_latest.sql"
LOG_FILE="/var/log/mysql_backup/backup_$(date +%Y%m%d).log"
RETENTION_DAYS=30
MYSQL_CNF="/etc/mysql/backup.cnf"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Función para loguear
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Iniciar backup
log_message "=== INICIANDO BACKUP DE $DB_NAME ==="

# 1. Realizar dump de la base de datos
log_message "Ejecutando mysqldump..."
mysqldump --defaults-extra-file=$MYSQL_CNF \
          --single-transaction \
          --routines \
          --triggers \
          --events \
          $DB_NAME > $BACKUP_FILE 2>> $LOG_FILE

# Verificar éxito del dump
if [ $? -eq 0 ]; then
    log_message "✅ Backup creado: $BACKUP_FILE"
    
    # 2. Comprimir backup
    gzip $BACKUP_FILE
    BACKUP_FILE="${BACKUP_FILE}.gz"
    log_message "✅ Backup comprimido: $BACKUP_FILE"
    
    # 3. Crear enlace simbólico al último backup
    ln -sf $BACKUP_FILE $LATEST_FILE
    log_message "✅ Enlace latest actualizado"
    
    # 4. Actualizar registro en base de datos
    mysql --defaults-extra-file=$MYSQL_CNF $DB_NAME << EOF
    UPDATE configuracion_recuperacion 
    SET valor = '$BACKUP_FILE',
        fecha_actualizacion = NOW()
    WHERE parametro = 'ultimo_backup_completo';
    
    INSERT INTO auditoria_operaciones 
    (Usuario, Tipo_Usuario, Operacion, Tabla_Afectada, Descripcion, IP_Address, Fecha_Operacion, Resultado)
    VALUES 
    ('cron_backup', 'ADMIN', 'BACKUP_AUTOMATICO', 'TODAS', 
     'Backup automático completado', '127.0.0.1', NOW(), 'EXITOSO');
EOF
    
    if [ $? -eq 0 ]; then
        log_message "✅ Registro en BD actualizado"
    else
        log_message "⚠️ Error al actualizar BD, pero backup OK"
    fi
    
    # 5. Limpiar backups antiguos
    log_message "Limpiando backups antiguos (> $RETENTION_DAYS días)..."
    find $BACKUP_DIR -name "${DB_NAME}_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete >> $LOG_FILE 2>&1
    log_message "✅ Limpieza completada"
    
    # 6. Verificar espacio
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    log_message "📊 Tamaño backup: $BACKUP_SIZE"
    
else
    log_message "❌ ERROR: Falló el mysqldump"
    mysql --defaults-extra-file=$MYSQL_CNF $DB_NAME << EOF
    INSERT INTO alertas_sistema (Tipo, Mensaje, Estado)
    VALUES ('SISTEMA', 'Fallo en backup automático', 'Pendiente');
EOF
    exit 1
fi

log_message "=== BACKUP COMPLETADO CON ÉXITO ==="
EOF

# 4. Crear archivo de configuración MySQL seguro
echo "🔐 Creando archivo de configuración seguro..."
read -sp "Ingresa la contraseña de MySQL root: " mysql_password
echo ""
cat > /etc/mysql/backup.cnf << EOF
[client]
user=root
password=$mysql_password
host=localhost
EOF

# 5. Dar permisos seguros
echo "🔒 Aplicando permisos de seguridad..."
chmod 700 /scripts/backup
chmod 600 /etc/mysql/backup.cnf
chmod +x /scripts/backup/backup_cantinatita.sh
chown -R mysql:mysql /backups/mysql /var/log/mysql_backup

# 6. Configurar Cron Job
echo "⏰ Configurando Cron Job..."
(crontab -l 2>/dev/null; echo "# =========================================") | crontab -
(crontab -l 2>/dev/null; echo "# BACKUP CANTINATITA - DIARIO 2:00 AM") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * /scripts/backup/backup_cantinatita.sh") | crontab -
(crontab -l 2>/dev/null; echo "# LIMPIAR LOGS ANTIGUOS - DOMINGOS 3:00 AM") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * 0 find /var/log/mysql_backup/*.log -mtime +30 -delete") | crontab -

# 7. Probar script
echo "🧪 Probando script de backup..."
if /scripts/backup/backup_cantinatita.sh; then
    echo "✅ Script probado exitosamente"
else
    echo "❌ Error al probar script"
    exit 1
fi

# 8. Mostrar resumen
echo ""
echo "========================================================"
echo "🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE"
echo "========================================================"
echo ""
echo "📋 RESUMEN DE INSTALACIÓN:"
echo "   📁 Scripts: /scripts/backup/"
echo "   💾 Backups: /backups/mysql/"
echo "   📊 Logs: /var/log/mysql_backup/"
echo "   ⏰ Cron: Backup diario a las 2:00 AM"
echo ""
echo "🔍 VERIFICACIÓN:"
echo "   Para verificar la instalación ejecuta:"
echo "   1. ls -la /backups/mysql/"
echo "   2. crontab -l"
echo "   3. tail -f /var/log/mysql_backup/backup_$(date +%Y%m%d).log"
echo ""
echo "📝 CONFIGURACIÓN EN MYSQL:"
echo "   Verifica que el backup se registró:"
echo "   mysql -e \"SELECT * FROM cantinatitadb.configuracion_recuperacion\""
echo ""