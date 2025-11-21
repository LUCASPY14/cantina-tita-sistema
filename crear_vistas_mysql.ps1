# ================================================================
# Script para crear vistas MySQL - Sistema Cantina Tita
# ================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   CREACION DE VISTAS MYSQL" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "VISTAS A CREAR:" -ForegroundColor Cyan
Write-Host "  1. v_saldo_clientes - Saldos de cuenta corriente" -ForegroundColor White
Write-Host "  2. v_stock_alerta - Productos con stock bajo" -ForegroundColor White
Write-Host ""

# Configuracion MySQL (ajusta segun tu instalacion)
$MYSQL_HOST = "localhost"
$MYSQL_USER = "root"
$MYSQL_DATABASE = "cantinatitadb"
$SQL_FILE = "sql\crear_vistas.sql"

Write-Host "CONFIGURACION:" -ForegroundColor Cyan
Write-Host "  Host: $MYSQL_HOST" -ForegroundColor Gray
Write-Host "  Usuario: $MYSQL_USER" -ForegroundColor Gray
Write-Host "  Base de datos: $MYSQL_DATABASE" -ForegroundColor Gray
Write-Host "  Archivo SQL: $SQL_FILE" -ForegroundColor Gray
Write-Host ""

# Verificar que existe el archivo SQL
if (-not (Test-Path $SQL_FILE)) {
    Write-Host "ERROR: No se encuentra el archivo $SQL_FILE" -ForegroundColor Red
    exit 1
}

Write-Host "Ejecutando SQL..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar el SQL
# OPCION 1: Con contrasena interactiva (mas seguro)
Get-Content $SQL_FILE | mysql -h $MYSQL_HOST -u $MYSQL_USER -p $MYSQL_DATABASE

# OPCION 2: Si tienes contrasena guardada, descomenta y ajusta:
# $MYSQL_PASSWORD = "tu_contrasena"
# Get-Content $SQL_FILE | mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   VISTAS CREADAS EXITOSAMENTE" -ForegroundColor White -BackgroundColor DarkGreen
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "PROXIMOS PASOS:" -ForegroundColor Cyan
    Write-Host "  1. Las vistas MySQL estan activas" -ForegroundColor White
    Write-Host "  2. Ahora vamos a descomentar los modelos Django" -ForegroundColor White
    Write-Host "  3. Reiniciar el servidor Django" -ForegroundColor White
    Write-Host ""
    
    Write-Host "VERIFICAR EN MYSQL:" -ForegroundColor Cyan
    Write-Host "  SELECT * FROM v_saldo_clientes LIMIT 5;" -ForegroundColor Gray
    Write-Host "  SELECT * FROM v_stock_alerta LIMIT 5;" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: No se pudieron crear las vistas" -ForegroundColor Red
    Write-Host "Verifica:" -ForegroundColor Yellow
    Write-Host "  - Usuario y contrasena MySQL correctos" -ForegroundColor Gray
    Write-Host "  - Base de datos 'cantinatitadb' existe" -ForegroundColor Gray
    Write-Host "  - MySQL esta corriendo" -ForegroundColor Gray
    Write-Host "  - Permisos para crear vistas" -ForegroundColor Gray
    Write-Host ""
}
