"""
Genera reporte de uso de índices de MySQL
Identifica índices no utilizados y su tamaño
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection


def generate_index_report():
    """
    Genera reporte completo de uso de índices
    """
    with connection.cursor() as cursor:
        print("=" * 80)
        print(f"REPORTE DE ÍNDICES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # 1. Índices no utilizados
        cursor.execute("""
            SELECT 
                object_name AS table_name,
                index_name,
                COUNT_STAR AS times_used
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE object_schema = 'cantinatitadb'
            AND index_name IS NOT NULL
            AND index_name != 'PRIMARY'
            AND COUNT_STAR = 0
            ORDER BY table_name, index_name
        """)
        
        unused = cursor.fetchall()
        
        if unused:
            print("🗑️  ÍNDICES NO UTILIZADOS (Candidatos a eliminar)")
            print("-" * 80)
            for table, index, _ in unused:
                print(f"  DROP INDEX {index} ON {table};")
            print()
        else:
            print("✅ No se encontraron índices sin uso")
            print()
        
        # 2. Índices poco utilizados
        cursor.execute("""
            SELECT 
                object_name AS table_name,
                index_name,
                COUNT_STAR AS times_used,
                COUNT_READ AS times_read,
                COUNT_WRITE AS times_write
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE object_schema = 'cantinatitadb'
            AND index_name IS NOT NULL
            AND index_name != 'PRIMARY'
            AND COUNT_STAR > 0
            AND COUNT_STAR < 100
            ORDER BY COUNT_STAR ASC
            LIMIT 10
        """)
        
        low_usage = cursor.fetchall()
        
        if low_usage:
            print("⚠️  ÍNDICES CON BAJO USO (< 100 lecturas)")
            print("-" * 80)
            print(f"{'Tabla':<30} {'Índice':<35} {'Usos':>10}")
            print("-" * 80)
            for table, index, used, reads, writes in low_usage:
                print(f"{table:<30} {index:<35} {used:>10}")
            print()
        
        # 3. Tamaño de índices
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS size_mb
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND INDEX_LENGTH > 0
            ORDER BY INDEX_LENGTH DESC
            LIMIT 10
        """)
        
        sizes = cursor.fetchall()
        
        print("📊 TOP 10 TABLAS CON ÍNDICES MÁS GRANDES")
        print("-" * 80)
        print(f"{'Tabla':<30} {'Índice':<35} {'Tamaño (MB)':>12}")
        print("-" * 80)
        for table, index, size in sizes:
            print(f"{table:<30} {index or 'N/A':<35} {size:>12.2f}")
        print()
        
        # 4. Total de índices
        cursor.execute("""
            SELECT COUNT(DISTINCT CONCAT(TABLE_NAME, '.', INDEX_NAME)) AS total
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND INDEX_NAME != 'PRIMARY'
        """)
        
        total = cursor.fetchone()[0]
        
        # 5. Tamaño total de índices
        cursor.execute("""
            SELECT ROUND(SUM(INDEX_LENGTH) / 1024 / 1024, 2) AS total_mb
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'cantinatitadb'
        """)
        
        total_size = cursor.fetchone()[0]
        
        print("📈 RESUMEN")
        print("-" * 80)
        print(f"  Total de índices: {total}")
        print(f"  Tamaño total: {total_size} MB")
        print(f"  Índices no utilizados: {len(unused)}")
        print(f"  Índices con bajo uso: {len(low_usage)}")
        print()
        
        # 6. Recomendaciones
        print("💡 RECOMENDACIONES")
        print("-" * 80)
        if len(unused) > 0:
            print(f"  • Eliminar {len(unused)} índices no utilizados")
            print(f"    Espacio recuperable: ~{len(unused) * 0.5:.1f} MB estimado")
        if len(low_usage) > 0:
            print(f"  • Revisar {len(low_usage)} índices con bajo uso")
            print(f"    Determinar si son necesarios para queries específicas")
        if len(unused) == 0 and len(low_usage) == 0:
            print("  ✅ Todos los índices están siendo utilizados eficientemente")
        print()
        
        print("=" * 80)


def detect_redundant_indexes():
    """
    Detecta índices redundantes o duplicados
    """
    with connection.cursor() as cursor:
        print()
        print("=" * 80)
        print("ANÁLISIS DE ÍNDICES REDUNDANTES")
        print("=" * 80)
        print()
        
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS columns
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND INDEX_NAME != 'PRIMARY'
            GROUP BY TABLE_NAME, INDEX_NAME
            ORDER BY TABLE_NAME, INDEX_NAME
        """)
        
        indexes = {}
        for table, index, columns in cursor.fetchall():
            if table not in indexes:
                indexes[table] = []
            indexes[table].append({'name': index, 'columns': columns})
        
        redundant_found = False
        
        for table, table_indexes in indexes.items():
            for i, idx1 in enumerate(table_indexes):
                for idx2 in table_indexes[i+1:]:
                    cols1 = idx1['columns']
                    cols2 = idx2['columns']
                    
                    # Verificar si un índice es prefijo del otro
                    if cols1.startswith(cols2) or cols2.startswith(cols1):
                        if not redundant_found:
                            print("⚠️  ÍNDICES POTENCIALMENTE REDUNDANTES")
                            print("-" * 80)
                            redundant_found = True
                        
                        print(f"  Tabla: {table}")
                        print(f"    - {idx1['name']}: ({cols1})")
                        print(f"    - {idx2['name']}: ({cols2})")
                        print(f"    💡 Considerar mantener solo el índice más específico")
                        print()
        
        if not redundant_found:
            print("✅ No se detectaron índices redundantes")
        
        print("=" * 80)


if __name__ == '__main__':
    try:
        generate_index_report()
        detect_redundant_indexes()
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()
