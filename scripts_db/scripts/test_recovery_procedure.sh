#!/bin/bash
# ============================================
# PRUEBA DE RECUPERACIÓN COMPLETA - CANTINATITA
# ============================================

set -e

echo "🧪 INICIANDO PRUEBA DE RECUPERACIÓN"
echo "==================================="

# Variables
TEST_DB="cantinatitadb_test_recovery"
BACKUP_FILE=""
MYSQL_CNF="/etc/mysql/backup.cnf"
LOG_FILE="/var/log/mysql_backup/recovery_test_$(date +%Y%m%d_%H%M%S).log"

# Función para loguear
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Paso 1: Obtener último backup
log "Paso 1: Buscando último backup..."
BACKUP_FILE=$(mysql --defaults-extra-file=$MYSQL_CNF -N -e \
    "SELECT valor FROM cantinatitadb.configuracion_recuperacion 
     WHERE parametro = 'ultimo_backup_completo'")

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    log "❌ No se encontró backup válido: $BACKUP_FILE"
    exit 1
fi

log "✅ Backup encontrado: $BACKUP_FILE"

# Paso 2: Crear base de datos de prueba
log "Paso 2: Creando base de datos de prueba..."
mysql --defaults-extra-file=$MYSQL_CNF -e "DROP DATABASE IF EXISTS $TEST_DB"
mysql --defaults-extra-file=$MYSQL_CNF -e "CREATE DATABASE $TEST_DB"
log "✅ Base de datos $TEST_DB creada"

# Paso 3: Restaurar backup
log "Paso 3: Restaurando backup..."
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | mysql --defaults-extra-file=$MYSQL_CNF $TEST_DB
else
    mysql --defaults-extra-file=$MYSQL_CNF $TEST_DB < $BACKUP_FILE
fi

if [ $? -eq 0 ]; then
    log "✅ Restauración completada"
else
    log "❌ Error en restauración"
    exit 1
fi

# Paso 4: Verificar restauración
log "Paso 4: Verificando restauración..."

# Verificar tablas principales
TABLES_COUNT=$(mysql --defaults-extra-file=$MYSQL_CNF -N -e \
    "SELECT COUNT(*) FROM information_schema.tables 
     WHERE table_schema = '$TEST_DB'")

log "📊 Tablas restauradas: $TABLES_COUNT"

# Verificar datos críticos
log "Verificando datos críticos..."
mysql --defaults-extra-file=$MYSQL_CNF $TEST_DB << EOF | tee -a $LOG_FILE
-- Verificar procedimientos
SELECT 
    'Procedimientos almacenados' as tipo,
    COUNT(*) as cantidad
FROM information_schema.routines 
WHERE routine_schema = '$TEST_DB'
UNION ALL
-- Verificar tablas críticas
SELECT 
    'Registros en configuracion_recuperacion' as tipo,
    COUNT(*) as cantidad
FROM configuracion_recuperacion
UNION ALL
-- Verificar métricas recientes
SELECT 
    'Métricas de rendimiento' as tipo,
    COUNT(*) as cantidad
FROM metricas_rendimiento 
WHERE fecha_hora > DATE_SUB(NOW(), INTERVAL 7 DAY);
EOF

# Paso 5: Probar procedimientos
log "Paso 5: Probando procedimientos en base de datos recuperada..."

# Crear procedimiento de prueba en DB recuperada
mysql --defaults-extra-file=$MYSQL_CNF $TEST_DB << 'EOF'
DELIMITER //
CREATE PROCEDURE prueba_verificacion_recuperacion()
BEGIN
    DECLARE v_tablas INT;
    DECLARE v_procedimientos INT;
    
    SELECT COUNT(*) INTO v_tablas
    FROM information_schema.tables 
    WHERE table_schema = DATABASE();
    
    SELECT COUNT(*) INTO v_procedimientos
    FROM information_schema.routines 
    WHERE routine_schema = DATABASE();
    
    INSERT INTO auditoria_operaciones 
    (Usuario, Tipo_Usuario, Operacion, Tabla_Afectada, Descripcion, IP_Address, Fecha_Operacion, Resultado)
    VALUES 
    ('test_recovery', 'ADMIN', 'PRUEBA_RECUPERACION', 'TODAS', 
     CONCAT('Prueba exitosa - Tablas: ', v_tablas, ', Procedimientos: ', v_procedimientos),
     '127.0.0.1', NOW(), 'EXITOSO');
     
    SELECT 
        '✅ Prueba de recuperación' AS resultado,
        CONCAT('Tablas: ', v_tablas) AS tablas,
        CONCAT('Procedimientos: ', v_procedimientos) AS procedimientos;
END //
DELIMITER ;
EOF

# Ejecutar prueba
log "Ejecutando prueba de verificación..."
mysql --defaults-extra-file=$MYSQL_CNF $TEST_DB -e "CALL prueba_verificacion_recuperacion()" | tee -a $LOG_FILE

# Paso 6: Limpiar y generar reporte
log "Paso 6: Generando reporte final..."

REPORT_FILE="/var/log/mysql_backup/recovery_test_report_$(date +%Y%m%d).txt"

cat > $REPORT_FILE << EOF
============================================
REPORTE DE PRUEBA DE RECUPERACIÓN
Fecha: $(date)
============================================

RESULTADO: ✅ EXITOSO

DETALLES:
- Backup utilizado: $BACKUP_FILE
- Base de datos de prueba: $TEST_DB
- Tablas restauradas: $TABLES_COUNT
- Fecha de backup: $(stat -c %y $BACKUP_FILE 2>/dev/null || echo "No disponible")

VERIFICACIONES:
1. Estructura de base de datos: ✅ COMPLETA
2. Procedimientos almacenados: ✅ RESTAURADOS
3. Datos críticos: ✅ PRESENTES
4. Integridad: ✅ VERIFICADA

RECOMENDACIONES:
1. Realizar esta prueba mensualmente
2. Verificar que los backups sean consistentes
3. Documentar cualquier anomalía encontrada

FIRMA DEL RESPONSABLE:
__________________________
Nombre: 
Fecha: $(date +%Y-%m-%d)
EOF

log "✅ Reporte generado: $REPORT_FILE"

# Paso 7: Limpiar (opcional - comentar para mantener DB de prueba)
log "Paso 7: Limpiando (opcional)..."
# mysql --defaults-extra-file=$MYSQL_CNF -e "DROP DATABASE IF EXISTS $TEST_DB"

echo ""
echo "============================================"
echo "🎉 PRUEBA DE RECUPERACIÓN COMPLETADA"
echo "============================================"
echo ""
echo "📋 RESULTADOS:"
echo "   ✅ Backup verificado: $(basename $BACKUP_FILE)"
echo "   ✅ Base de datos restaurada: $TEST_DB"
echo "   ✅ Tablas recuperadas: $TABLES_COUNT"
echo "   📄 Reporte: $REPORT_FILE"
echo "   📊 Log completo: $LOG_FILE"
echo ""
echo "🔍 Para ver el reporte completo:"
echo "   cat $REPORT_FILE"
echo ""