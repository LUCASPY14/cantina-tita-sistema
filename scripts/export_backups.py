"""
Script para exportar tablas backup a archivos SQL
Paso 1 de recomendaciones: Exportar y archivar backups
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
import django
django.setup()

from django.db import connection
from django.conf import settings

def export_backup_tables():
    """Exporta tablas backup a archivos SQL individuales"""
    
    print("\n" + "="*80)
    print("EXPORTAR TABLAS BACKUP - PASO 1".center(80))
    print("="*80 + "\n")
    
    backup_tables = [
        'compras_backup_20251202_203443',
        'cta_corriente_backup_20251202_203443',
        'cta_corriente_backup_20251202_222340',
        'cta_corriente_prov_backup_20251202_203443',
        'cta_corriente_prov_backup_20251202_222340',
        'pagos_venta_backup_20251202_203443',
        'ventas_backup_20251202_203443'
    ]
    
    backup_dir = BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    print(f"📁 Directorio de backup: {backup_dir}\n")
    
    exported = 0
    total_size = 0
    
    with connection.cursor() as cursor:
        for table in backup_tables:
            try:
                # Obtener estructura de la tabla
                cursor.execute(f"SHOW CREATE TABLE {table}")
                create_statement = cursor.fetchone()[1]
                
                # Obtener datos
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Crear archivo SQL
                sql_file = backup_dir / f"{table}.sql"
                
                with open(sql_file, 'w', encoding='utf-8') as f:
                    # Header
                    f.write(f"-- Backup de tabla: {table}\n")
                    f.write(f"-- Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"-- Registros: {len(rows)}\n\n")
                    
                    # DROP y CREATE
                    f.write(f"DROP TABLE IF EXISTS `{table}`;\n\n")
                    f.write(create_statement + ";\n\n")
                    
                    # INSERT statements
                    if rows:
                        # Obtener nombres de columnas
                        cursor.execute(f"DESCRIBE {table}")
                        columns = [col[0] for col in cursor.fetchall()]
                        columns_str = ', '.join([f"`{col}`" for col in columns])
                        
                        f.write(f"INSERT INTO `{table}` ({columns_str}) VALUES\n")
                        
                        for i, row in enumerate(rows):
                            # Formatear valores
                            values = []
                            for val in row:
                                if val is None:
                                    values.append('NULL')
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                elif isinstance(val, datetime):
                                    values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                                else:
                                    # Escapar comillas
                                    val_str = str(val).replace("'", "\\'")
                                    values.append(f"'{val_str}'")
                            
                            values_str = ', '.join(values)
                            separator = ',' if i < len(rows) - 1 else ';'
                            f.write(f"  ({values_str}){separator}\n")
                
                file_size = sql_file.stat().st_size / 1024  # KB
                total_size += file_size
                
                print(f"  ✓ {table:45} → {file_size:.2f} KB ({len(rows)} registros)")
                exported += 1
                
            except Exception as e:
                print(f"  ✗ {table:45} → Error: {str(e)[:50]}")
    
    print(f"\n✅ Exportadas: {exported}/{len(backup_tables)} tablas")
    print(f"📊 Tamaño total: {total_size:.2f} KB ({total_size/1024:.2f} MB)")
    
    # Crear archivo consolidado
    print(f"\n📦 Creando archivo consolidado...")
    
    consolidated_file = backup_dir / 'backup_all_legacy_20251202.sql'
    
    with open(consolidated_file, 'w', encoding='utf-8') as outfile:
        outfile.write("-- =====================================================\n")
        outfile.write("-- BACKUP CONSOLIDADO DE TABLAS LEGACY\n")
        outfile.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write(f"-- Tablas: {len(backup_tables)}\n")
        outfile.write("-- =====================================================\n\n")
        
        for table in backup_tables:
            sql_file = backup_dir / f"{table}.sql"
            if sql_file.exists():
                with open(sql_file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")
    
    consolidated_size = consolidated_file.stat().st_size / 1024
    print(f"  ✓ {consolidated_file.name} → {consolidated_size:.2f} KB")
    
    print("\n" + "="*80 + "\n")

def drop_backup_tables():
    """Elimina las tablas backup después de exportar"""
    
    print("\n" + "="*80)
    print("ELIMINAR TABLAS BACKUP - PASO 1 (CONTINUACIÓN)".center(80))
    print("="*80 + "\n")
    
    backup_tables = [
        'compras_backup_20251202_203443',
        'cta_corriente_backup_20251202_203443',
        'cta_corriente_backup_20251202_222340',
        'cta_corriente_prov_backup_20251202_203443',
        'cta_corriente_prov_backup_20251202_222340',
        'pagos_venta_backup_20251202_203443',
        'ventas_backup_20251202_203443'
    ]
    
    print("⚠️  ¿Deseas eliminar las tablas backup de la base de datos?")
    print("   Los archivos SQL ya fueron exportados a /backups/\n")
    
    print("Para eliminar manualmente, ejecuta:\n")
    with connection.cursor() as cursor:
        for table in backup_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  DROP TABLE IF EXISTS `{table}`;  -- {count} registros")
            except:
                pass
    
    print("\n💡 TIP: Puedes eliminar todas de una vez con:")
    print("  SET FOREIGN_KEY_CHECKS=0;")
    for table in backup_tables:
        print(f"  DROP TABLE IF EXISTS `{table}`;")
    print("  SET FOREIGN_KEY_CHECKS=1;")
    
    print("\n" + "="*80 + "\n")

def main():
    """Función principal"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " PASO 1: EXPORTAR Y ARCHIVAR BACKUPS".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        export_backup_tables()
        drop_backup_tables()
        
        print("="*80)
        print("CONCLUSIÓN".center(80))
        print("="*80)
        print("\n✅ Paso 1 completado exitosamente")
        print("\nARCHIVOS GENERADOS:")
        print("  • backups/backup_all_legacy_20251202.sql (consolidado)")
        print("  • backups/[tabla].sql (individuales)")
        print("\nPRÓXIMOS PASOS:")
        print("  2. Monitorear rendimiento con Django Debug Toolbar")
        print("  3. Usar EXPLAIN en queries lentas")
        print("  4. Revisar índices cada 3-6 meses")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
