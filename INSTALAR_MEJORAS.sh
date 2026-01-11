#!/bin/bash
# Script de Instalación Rápida - Mejoras Críticas
# Ejecutar con: sudo bash INSTALAR_MEJORAS.sh

echo "========================================"
echo "INSTALACIÓN RÁPIDA - MEJORAS CRÍTICAS"
echo "========================================"
echo ""

PROJECT_PATH="/var/www/cantina_project"  # Ajusta según tu instalación

# Verificar que somos root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Error: Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Verificar directorio del proyecto
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Error: No se encontró el directorio del proyecto: $PROJECT_PATH"
    echo "Edita el script y ajusta PROJECT_PATH"
    exit 1
fi

cd $PROJECT_PATH
echo "📁 Directorio: $PROJECT_PATH"
echo ""

# PASO 1: Actualizar sistema
echo "🔄 PASO 1/7: Actualizando sistema..."
apt update -qq
echo "✅ Sistema actualizado"
echo ""

# PASO 2: Instalar Redis
echo "🔧 PASO 2/7: Instalando Redis..."
if ! command -v redis-cli &> /dev/null; then
    apt install -y redis-server
    systemctl start redis-server
    systemctl enable redis-server
    echo "✅ Redis instalado"
else
    echo "ℹ️  Redis ya está instalado"
fi
echo ""

# PASO 3: Verificar Redis
echo "🔍 PASO 3/7: Verificando Redis..."
if redis-cli ping | grep -q PONG; then
    echo "✅ Redis está funcionando"
else
    echo "⚠️  Redis no responde"
fi
echo ""

# PASO 4: Instalar dependencias Python
echo "🐍 PASO 4/7: Instalando dependencias Python..."
pip3 install -r requirements_mejoras_criticas.txt
echo "✅ Dependencias instaladas"
echo ""

# PASO 5: Crear directorios
echo "📂 PASO 5/7: Creando directorios..."
mkdir -p backups logs scripts
chmod 755 backups logs scripts
echo "✅ Directorios creados"
echo ""

# PASO 6: Configurar backup automático
echo "💾 PASO 6/7: Configurando backup automático..."
bash scripts/schedule_backup_linux.sh
echo "✅ Backup automático configurado"
echo ""

# PASO 7: Aplicar migraciones
echo "🔄 PASO 7/7: Aplicando migraciones..."
python3 manage.py migrate --no-input
echo "✅ Migraciones aplicadas"
echo ""

# VERIFICACIÓN
echo "========================================"
echo "✅ INSTALACIÓN COMPLETADA"
echo "========================================"
echo ""

# Resumen
echo "📊 RESUMEN:"
echo ""
echo "  ✅ Redis instalado y funcionando"
echo "  ✅ Dependencias Python instaladas"
echo "  ✅ Directorios creados"
echo "  ✅ Backup automático configurado (2:00 AM)"
echo "  ✅ Migraciones aplicadas"
echo ""

# Próximos pasos
echo "🎯 PRÓXIMOS PASOS:"
echo ""
echo "1. Probar backup manual:"
echo "   python3 manage.py backup_database --compress --notify"
echo ""
echo "2. Probar health check:"
echo "   python3 manage.py health_check --verbose"
echo ""
echo "3. Configurar variables de entorno (.env)"
echo ""
echo "4. Iniciar servidor:"
echo "   gunicorn cantina_project.wsgi:application"
echo ""
echo "📚 Ver: GUIA_INSTALACION_MEJORAS_CRITICAS.md"
echo ""
echo "========================================"
