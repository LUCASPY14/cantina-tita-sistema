"""
Script para limpiar tablas legacy y backup de la base de datos
PRIORIDAD MEDIA
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
import django
django.setup()

from django.db import connection

def execute_sql(sql, description):
    """Ejecuta un comando SQL y maneja errores"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            print(f"  ✓ {description}")
            return True
    except Exception as e:
        print(f"  ✗ {description}")
        print(f"    Error: {str(e)[:100]}")
        return False

def cleanup_legacy_tables():
    """Limpia tablas legacy gestion_* que no se usan"""
    
    print("\n" + "="*80)
    print("LIMPIEZA DE TABLAS LEGACY - PRIORIDAD MEDIA".center(80))
    print("="*80 + "\n")
    
    # Lista de tablas legacy a eliminar
    legacy_tables = [
        'gestion_categoria',
        'gestion_cliente',
        'gestion_compraproveedor',
        'gestion_detallecompra',
        'gestion_detalleventa',
        'gestion_producto',
        'gestion_proveedor',
        'gestion_venta'
    ]
    
    print("📋 Tablas legacy identificadas para eliminación:\n")
    for table in legacy_tables:
        print(f"   • {table}")
    
    print(f"\n⚠️  IMPORTANTE: Estas tablas fueron generadas por migraciones antiguas de Django")
    print(f"   y han sido reemplazadas por las tablas sin prefijo 'gestion_'")
    
    # Verificar existencia y contar registros
    print("\n🔍 Verificando existencia y contenido...\n")
    
    tables_to_drop = []
    with connection.cursor() as cursor:
        for table in legacy_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table:35} - {count:>6} registros")
                tables_to_drop.append((table, count))
            except Exception as e:
                print(f"   {table:35} - No existe o error")
    
    if not tables_to_drop:
        print("\n✅ No se encontraron tablas legacy para eliminar")
        return
    
    # Crear backup de seguridad antes de eliminar
    print(f"\n💾 Creando backup de seguridad...\n")
    
    backup_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_success = 0
    
    for table, count in tables_to_drop:
        if count > 0:
            backup_table = f"{table}_backup_{backup_date}"
            sql = f"CREATE TABLE {backup_table} AS SELECT * FROM {table}"
            if execute_sql(sql, f"Backup: {backup_table}"):
                backup_success += 1
    
    print(f"\n✅ {backup_success} tablas con datos respaldadas")
    
    # Eliminar tablas legacy
    print(f"\n🗑️  Eliminando tablas legacy...\n")
    
    dropped = 0
    failed = 0
    
    for table, count in tables_to_drop:
        sql = f"DROP TABLE IF EXISTS {table}"
        if execute_sql(sql, f"DROP TABLE {table}"):
            dropped += 1
        else:
            failed += 1
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE LIMPIEZA - TABLAS LEGACY".center(80))
    print("="*80)
    print(f"\n✅ Tablas eliminadas: {dropped}")
    print(f"💾 Tablas respaldadas: {backup_success}")
    print(f"❌ Errores: {failed}")
    
    if failed == 0:
        print("\n🎉 ¡Limpieza de tablas legacy completada exitosamente!")
    
    print("\n" + "="*80 + "\n")

def cleanup_backup_tables():
    """Archiva y limpia tablas backup antiguas"""
    
    print("\n" + "="*80)
    print("LIMPIEZA DE TABLAS BACKUP - PRIORIDAD MEDIA".center(80))
    print("="*80 + "\n")
    
    # Lista de tablas backup del 2 de diciembre 2025
    backup_tables = [
        'compras_backup_20251202_203443',
        'cta_corriente_backup_20251202_203443',
        'cta_corriente_backup_20251202_222340',
        'cta_corriente_prov_backup_20251202_203443',
        'cta_corriente_prov_backup_20251202_222340',
        'pagos_venta_backup_20251202_203443',
        'ventas_backup_20251202_203443'
    ]
    
    print("📋 Tablas backup identificadas (2025-12-02):\n")
    for table in backup_tables:
        print(f"   • {table}")
    
    print(f"\n⚠️  RECOMENDACIÓN: Estas son tablas de backup del 2 de diciembre de 2025")
    print(f"   Se recomienda exportarlas a archivos SQL antes de eliminar")
    
    # Verificar existencia y contar registros
    print("\n🔍 Verificando existencia y contenido...\n")
    
    tables_found = []
    total_size = 0
    
    with connection.cursor() as cursor:
        for table in backup_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # Estimar tamaño de la tabla
                cursor.execute(f"""
                    SELECT ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                    FROM information_schema.TABLES
                    WHERE table_schema = DATABASE()
                    AND table_name = '{table}'
                """)
                size = cursor.fetchone()
                size_mb = size[0] if size and size[0] else 0
                
                print(f"   {table:45} - {count:>6} registros ({size_mb:.2f} MB)")
                tables_found.append((table, count, size_mb))
                total_size += size_mb
            except Exception as e:
                print(f"   {table:45} - No existe")
    
    if not tables_found:
        print("\n✅ No se encontraron tablas backup para procesar")
        return
    
    print(f"\n📊 Tamaño total de backups: {total_size:.2f} MB")
    
    # Información sobre exportación
    print(f"\n💡 GUÍA DE EXPORTACIÓN:")
    print(f"   Para exportar estas tablas antes de eliminar, ejecuta:")
    print(f"   ")
    print(f"   mysqldump -u root -p cantinatitadb \\")
    for i, (table, _, _) in enumerate(tables_found):
        end = " \\" if i < len(tables_found) - 1 else ""
        print(f"     {table}{end}")
    print(f"     > backups/backup_legacy_20251202.sql")
    print(f"   ")
    print(f"   gzip backups/backup_legacy_20251202.sql")
    
    # Por seguridad, NO eliminar automáticamente
    print(f"\n⚠️  ACCIÓN REQUERIDA:")
    print(f"   Por seguridad, las tablas backup NO se eliminarán automáticamente.")
    print(f"   Para eliminarlas manualmente después de exportar:")
    print(f"   ")
    for table, _, _ in tables_found:
        print(f"   DROP TABLE IF EXISTS {table};")
    
    print("\n" + "="*80 + "\n")

def main():
    """Función principal"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " LIMPIEZA DE BASE DE DATOS - PRIORIDAD MEDIA".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # 1. Limpiar tablas legacy
        cleanup_legacy_tables()
        
        # 2. Procesar tablas backup
        cleanup_backup_tables()
        
        print("\n" + "="*80)
        print("CONCLUSIÓN FINAL".center(80))
        print("="*80)
        print("\n✅ Proceso de limpieza completado")
        print("\nPRÓXIMOS PASOS:")
        print("  1. Las tablas legacy fueron eliminadas (con backup)")
        print("  2. Exportar tablas backup antes de eliminarlas")
        print("  3. Mantener backups por 30 días antes de eliminar definitivamente")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
