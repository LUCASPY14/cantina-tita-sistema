#!/usr/bin/env python
"""
Script de backup automático para la base de datos MySQL
Crea backups comprimidos con timestamp
"""
import os
import subprocess
import gzip
from datetime import datetime
from pathlib import Path

# Configuración
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Cambiar por contraseña si es necesario
DB_NAME = 'cantina_bd'
BACKUP_DIR = Path(__file__).parent / 'backups'
COMPRESS = True
KEEP_DAYS = 30  # Mantener backups de últimos 30 días

def crear_backup():
    """Crear backup de la base de datos"""
    
    # Crear directorio de backups si no existe
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Generar nombre del archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'backup_{DB_NAME}_{timestamp}.sql'
    
    print(f"🔄 Iniciando backup de {DB_NAME}...")
    print(f"📁 Directorio: {BACKUP_DIR}")
    print(f"📄 Archivo: {backup_file.name}")
    
    try:
        # Comando mysqldump
        cmd = [
            'mysqldump',
            f'--host={DB_HOST}',
            f'--user={DB_USER}',
            f'--no-password' if not DB_PASSWORD else f'--password={DB_PASSWORD}',
            '--single-transaction',  # Para consistencia sin locks
            '--quick',               # Optimizar para bases de datos grandes
            '--lock-tables=false',   # No bloquear tablas
            '--result-file=' + str(backup_file),
            DB_NAME
        ]
        
        # Ejecutar mysqldump
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error en mysqldump: {result.stderr}")
            return False
        
        # Obtener tamaño del archivo
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"✅ Backup creado: {size_mb:.2f} MB")
        
        # Comprimir si está habilitado
        if COMPRESS:
            print("🗜️  Comprimiendo archivo...")
            backup_gz = Path(str(backup_file) + '.gz')
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(backup_gz, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Eliminar archivo sin comprimir
            backup_file.unlink()
            
            size_gz_mb = backup_gz.stat().st_size / (1024 * 1024)
            ratio = (1 - size_gz_mb / size_mb) * 100
            print(f"✅ Comprimido: {size_gz_mb:.2f} MB (reducción: {ratio:.1f}%)")
            print(f"💾 Archivo final: {backup_gz.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante backup: {str(e)}")
        return False


def limpiar_backups_antiguos():
    """Eliminar backups más antiguos que KEEP_DAYS"""
    print(f"\n🧹 Limpiando backups más antiguos que {KEEP_DAYS} días...")
    
    from datetime import timedelta
    
    fecha_limite = datetime.now() - timedelta(days=KEEP_DAYS)
    
    archivos_eliminados = 0
    
    for archivo in BACKUP_DIR.glob('backup_*.sql*'):
        fecha_archivo = datetime.fromtimestamp(archivo.stat().st_mtime)
        
        if fecha_archivo < fecha_limite:
            try:
                archivo.unlink()
                archivos_eliminados += 1
                print(f"   ❌ Eliminado: {archivo.name}")
            except Exception as e:
                print(f"   ⚠️  Error al eliminar {archivo.name}: {str(e)}")
    
    if archivos_eliminados == 0:
        print("   ✅ No hay archivos antiguos para eliminar")
    else:
        print(f"✅ {archivos_eliminados} archivo(s) eliminado(s)")


def listar_backups():
    """Listar todos los backups disponibles"""
    print(f"\n📋 Backups disponibles en {BACKUP_DIR}:\n")
    
    archivos = sorted(BACKUP_DIR.glob('backup_*.sql*'), reverse=True)
    
    if not archivos:
        print("   (No hay backups disponibles)")
        return
    
    for archivo in archivos:
        tamaño_mb = archivo.stat().st_size / (1024 * 1024)
        fecha = datetime.fromtimestamp(archivo.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   📄 {archivo.name:<50} | {tamaño_mb:>8.2f} MB | {fecha}")


def restaurar_backup(nombre_archivo):
    """Restaurar un backup específico"""
    print(f"\n🔄 Restaurando desde {nombre_archivo}...")
    
    backup_file = BACKUP_DIR / nombre_archivo
    
    if not backup_file.exists():
        print(f"❌ Archivo no encontrado: {backup_file}")
        return False
    
    try:
        # Si es .gz, descomprimir primero
        if backup_file.suffix == '.gz':
            print("📦 Descomprimiendo...")
            sql_file = Path(str(backup_file)[:-3])  # Quitar .gz
            with gzip.open(backup_file, 'rb') as f_in:
                with open(sql_file, 'wb') as f_out:
                    f_out.writelines(f_in)
        else:
            sql_file = backup_file
        
        # Comando para restaurar
        cmd = [
            'mysql',
            f'--host={DB_HOST}',
            f'--user={DB_USER}',
            f'--no-password' if not DB_PASSWORD else f'--password={DB_PASSWORD}',
            DB_NAME
        ]
        
        with open(sql_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error en restauración: {result.stderr}")
            return False
        
        print(f"✅ Base de datos restaurada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante restauración: {str(e)}")
        return False


if __name__ == '__main__':
    import sys
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                   BACKUP AUTOMÁTICO - CANTINA BD                       ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Procesar argumentos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == 'backup':
            if crear_backup():
                limpiar_backups_antiguos()
                listar_backups()
            
        elif comando == 'listar':
            listar_backups()
            
        elif comando == 'restaurar' and len(sys.argv) > 2:
            archivo = sys.argv[2]
            restaurar_backup(archivo)
            
        elif comando == 'limpiar':
            limpiar_backups_antiguos()
            
        else:
            print("❌ Comando no reconocido")
            print_help()
    
    else:
        # Sin argumentos: mostrar menú
        print("""
Uso:
  python crear_backup_automatico.py backup      # Crear nuevo backup
  python crear_backup_automatico.py listar      # Listar todos los backups
  python crear_backup_automatico.py limpiar     # Eliminar backups antiguos
  python crear_backup_automatico.py restaurar <archivo>  # Restaurar un backup

Ejemplos:
  python crear_backup_automatico.py backup
  python crear_backup_automatico.py restaurar backup_cantina_bd_20260109_143000.sql.gz

Configuración:
  Base de datos: {0}
  Host: {1}
  Directorio: {2}
  Compresión: {'Habilitada' if COMPRESS else 'Deshabilitada'}
  Retención: {3} días
        """.format(DB_NAME, DB_HOST, BACKUP_DIR, KEEP_DAYS))
        
        # Crear backup por defecto
        print("\n▶️  Ejecutando backup por defecto...\n")
        if crear_backup():
            limpiar_backups_antiguos()
            listar_backups()
