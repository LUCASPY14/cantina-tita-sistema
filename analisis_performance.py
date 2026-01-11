#!/usr/bin/env python
"""
ANÁLISIS DE PERFORMANCE DEL SISTEMA CANTINA POS
Analiza: Queries SQL, Índices BD, Performance Django, Optimizaciones
Fecha: 2026-01-10
"""

import os
import sys
import django
import time
from pathlib import Path
from collections import defaultdict

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection, connections
from django.conf import settings
from django.core.cache import cache
import pymysql


def analizar_conexion_bd():
    """Analiza configuración de conexión BD"""
    print("\n" + "="*80)
    print("1. ANÁLISIS DE CONEXIÓN A BASE DE DATOS")
    print("="*80)
    
    db_config = settings.DATABASES['default']
    
    print(f"\n[CONFIGURACIÓN]")
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Database: {db_config['NAME']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Port: {db_config['PORT']}")
    
    # Test de conexión
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        connection_time = (time.time() - start_time) * 1000
        
        print(f"\n[TEST DE CONEXIÓN]")
        print(f"  ✅ Conexión exitosa")
        print(f"  ⏱️  Tiempo: {connection_time:.2f}ms")
    except Exception as e:
        print(f"\n[TEST DE CONEXIÓN]")
        print(f"  ❌ Error: {e}")
        return False
    
    return True


def analizar_tablas_bd():
    """Analiza las tablas de la BD"""
    print("\n" + "="*80)
    print("2. ANÁLISIS DE TABLAS Y TAMAÑO BD")
    print("="*80)
    
    try:
        connection_mysql = pymysql.connect(
            host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
            port=int(settings.DATABASES['default']['PORT'])
        )
        
        cursor = connection_mysql.cursor()
        
        # Obtener info de tablas
        query = """
        SELECT 
            TABLE_NAME,
            TABLE_ROWS,
            ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
            ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS total_mb
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = %s
        ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC
        LIMIT 20
        """
        
        cursor.execute(query, (settings.DATABASES['default']['NAME'],))
        results = cursor.fetchall()
        
        print(f"\n[TOP 20 TABLAS MÁS GRANDES]")
        print(f"{'Tabla':<40} {'Rows':>10} {'Data MB':>10} {'Index MB':>10} {'Total MB':>10}")
        print("-" * 85)
        
        total_rows = 0
        total_data = 0
        total_index = 0
        
        for row in results:
            table, rows, data_mb, index_mb, total_mb = row
            total_rows += rows or 0
            total_data += data_mb or 0
            total_index += index_mb or 0
            
            print(f"{table:<40} {rows or 0:>10} {data_mb or 0:>10.2f} {index_mb or 0:>10.2f} {total_mb or 0:>10.2f}")
        
        print("-" * 85)
        print(f"{'TOTAL':<40} {total_rows:>10} {total_data:>10.2f} {total_index:>10.2f} {total_data + total_index:>10.2f}")
        
        # Obtener total de tablas
        cursor.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s", 
                      (settings.DATABASES['default']['NAME'],))
        total_tables = cursor.fetchone()[0]
        print(f"\n📊 Total de tablas en BD: {total_tables}")
        
        cursor.close()
        connection_mysql.close()
        
    except Exception as e:
        print(f"❌ Error analizando tablas: {e}")


def analizar_indices_bd():
    """Analiza índices de la BD"""
    print("\n" + "="*80)
    print("3. ANÁLISIS DE ÍNDICES")
    print("="*80)
    
    try:
        connection_mysql = pymysql.connect(
            host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
            port=int(settings.DATABASES['default']['PORT'])
        )
        
        cursor = connection_mysql.cursor()
        
        # Tablas sin índices (excepto PRIMARY)
        query = """
        SELECT DISTINCT TABLE_NAME
        FROM information_schema.TABLES t
        WHERE TABLE_SCHEMA = %s
        AND TABLE_TYPE = 'BASE TABLE'
        AND NOT EXISTS (
            SELECT 1 
            FROM information_schema.STATISTICS s
            WHERE s.TABLE_SCHEMA = t.TABLE_SCHEMA
            AND s.TABLE_NAME = t.TABLE_NAME
            AND s.INDEX_NAME != 'PRIMARY'
        )
        ORDER BY TABLE_NAME
        """
        
        cursor.execute(query, (settings.DATABASES['default']['NAME'],))
        tables_without_indexes = cursor.fetchall()
        
        print(f"\n[TABLAS SIN ÍNDICES (excepto PRIMARY)]")
        if tables_without_indexes:
            print(f"⚠️  {len(tables_without_indexes)} tablas sin índices adicionales:")
            for (table,) in tables_without_indexes[:10]:
                print(f"  - {table}")
            if len(tables_without_indexes) > 10:
                print(f"  ... y {len(tables_without_indexes) - 10} más")
        else:
            print(f"✅ Todas las tablas tienen índices")
        
        # Índices duplicados o redundantes
        query = """
        SELECT 
            TABLE_NAME,
            INDEX_NAME,
            GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as columns,
            CARDINALITY
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s
        AND INDEX_NAME != 'PRIMARY'
        GROUP BY TABLE_NAME, INDEX_NAME
        ORDER BY TABLE_NAME, INDEX_NAME
        """
        
        cursor.execute(query, (settings.DATABASES['default']['NAME'],))
        indexes = cursor.fetchall()
        
        print(f"\n[ESTADÍSTICAS DE ÍNDICES]")
        print(f"Total de índices (no PRIMARY): {len(indexes)}")
        
        # Buscar índices con baja cardinalidad (potencialmente ineficientes)
        low_cardinality = [idx for idx in indexes if idx[3] and idx[3] < 10]
        if low_cardinality:
            print(f"\n⚠️  Índices con baja cardinalidad (< 10):")
            for table, index, columns, card in low_cardinality[:5]:
                print(f"  - {table}.{index} ({columns}) - Cardinalidad: {card}")
        
        cursor.close()
        connection_mysql.close()
        
    except Exception as e:
        print(f"❌ Error analizando índices: {e}")


def analizar_queries_lentas():
    """Analiza queries potencialmente lentas"""
    print("\n" + "="*80)
    print("4. ANÁLISIS DE QUERIES LENTAS")
    print("="*80)
    
    try:
        connection_mysql = pymysql.connect(
            host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
            port=int(settings.DATABASES['default']['PORT'])
        )
        
        cursor = connection_mysql.cursor()
        
        # Verificar si slow query log está habilitado
        cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
        slow_log = cursor.fetchone()
        
        print(f"\n[SLOW QUERY LOG]")
        if slow_log:
            print(f"  Estado: {slow_log[1]}")
            if slow_log[1] == 'OFF':
                print(f"  ⚠️  Recomendación: Habilitar slow query log para análisis")
                print(f"     SET GLOBAL slow_query_log = 'ON';")
                print(f"     SET GLOBAL long_query_time = 2;")
        
        # Tablas más consultadas (estimación basada en performance_schema si está disponible)
        try:
            cursor.execute("SHOW VARIABLES LIKE 'performance_schema'")
            perf_schema = cursor.fetchone()
            
            if perf_schema and perf_schema[1] == 'ON':
                query = """
                SELECT 
                    OBJECT_SCHEMA,
                    OBJECT_NAME,
                    COUNT_READ,
                    COUNT_WRITE,
                    COUNT_READ + COUNT_WRITE as total_ops
                FROM performance_schema.table_io_waits_summary_by_table
                WHERE OBJECT_SCHEMA = %s
                ORDER BY total_ops DESC
                LIMIT 10
                """
                
                cursor.execute(query, (settings.DATABASES['default']['NAME'],))
                results = cursor.fetchall()
                
                if results:
                    print(f"\n[TABLAS MÁS CONSULTADAS]")
                    print(f"{'Tabla':<40} {'Lecturas':>12} {'Escrituras':>12} {'Total':>12}")
                    print("-" * 80)
                    for schema, table, reads, writes, total in results:
                        print(f"{table:<40} {reads:>12} {writes:>12} {total:>12}")
        except:
            print(f"\n  ℹ️  Performance Schema no disponible")
        
        cursor.close()
        connection_mysql.close()
        
    except Exception as e:
        print(f"❌ Error analizando queries: {e}")


def analizar_cache():
    """Analiza configuración de cache"""
    print("\n" + "="*80)
    print("5. ANÁLISIS DE CACHE")
    print("="*80)
    
    cache_config = settings.CACHES.get('default', {})
    
    print(f"\n[CONFIGURACIÓN DE CACHE]")
    print(f"  Backend: {cache_config.get('BACKEND', 'No configurado')}")
    print(f"  Location: {cache_config.get('LOCATION', 'N/A')}")
    
    # Test de cache
    try:
        test_key = 'performance_test'
        test_value = 'test_data_12345'
        
        # Test de escritura
        start = time.time()
        cache.set(test_key, test_value, 10)
        write_time = (time.time() - start) * 1000
        
        # Test de lectura
        start = time.time()
        cached = cache.get(test_key)
        read_time = (time.time() - start) * 1000
        
        # Limpiar
        cache.delete(test_key)
        
        print(f"\n[TEST DE PERFORMANCE]")
        if cached == test_value:
            print(f"  ✅ Cache funcionando correctamente")
            print(f"  ⏱️  Escritura: {write_time:.2f}ms")
            print(f"  ⏱️  Lectura: {read_time:.2f}ms")
            
            if read_time > 10:
                print(f"  ⚠️  Lectura lenta - Considerar usar Redis")
        else:
            print(f"  ❌ Cache no está guardando datos correctamente")
    except Exception as e:
        print(f"  ❌ Error probando cache: {e}")
    
    # Recomendaciones
    print(f"\n[RECOMENDACIONES]")
    backend = cache_config.get('BACKEND', '')
    if 'locmem' in backend.lower():
        print(f"  ⚠️  Usando LocMemCache (no persistente)")
        print(f"     Recomendación: Migrar a Redis para mejor performance")
    elif 'redis' in backend.lower():
        print(f"  ✅ Usando Redis - Excelente elección")
    else:
        print(f"  ℹ️  Backend: {backend}")


def analizar_modelos_django():
    """Analiza modelos Django y sus relaciones"""
    print("\n" + "="*80)
    print("6. ANÁLISIS DE MODELOS DJANGO")
    print("="*80)
    
    from django.apps import apps
    
    all_models = apps.get_models()
    gestion_models = [m for m in all_models if m._meta.app_label == 'gestion']
    
    print(f"\n[ESTADÍSTICAS DE MODELOS]")
    print(f"  Total modelos: {len(all_models)}")
    print(f"  Modelos 'gestion' app: {len(gestion_models)}")
    
    # Analizar modelos con muchas relaciones (potencial N+1)
    print(f"\n[MODELOS CON MUCHAS RELACIONES]")
    print(f"{'Modelo':<35} {'ForeignKey':>12} {'ManyToMany':>12} {'OneToOne':>12}")
    print("-" * 75)
    
    for model in sorted(gestion_models, key=lambda m: m._meta.model_name)[:20]:
        fks = len([f for f in model._meta.get_fields() if f.many_to_one and not f.auto_created])
        m2m = len([f for f in model._meta.get_fields() if f.many_to_many])
        o2o = len([f for f in model._meta.get_fields() if f.one_to_one])
        
        if fks + m2m + o2o > 0:
            print(f"{model._meta.model_name:<35} {fks:>12} {m2m:>12} {o2o:>12}")
    
    # Modelos sin __str__ definido (mala práctica)
    models_without_str = []
    for model in gestion_models:
        if not hasattr(model, '__str__') or model.__str__ is object.__str__:
            models_without_str.append(model._meta.model_name)
    
    if models_without_str:
        print(f"\n⚠️  Modelos sin __str__ definido ({len(models_without_str)}):")
        for m in models_without_str[:5]:
            print(f"  - {m}")


def generar_recomendaciones():
    """Genera recomendaciones de optimización"""
    print("\n" + "="*80)
    print("7. RECOMENDACIONES DE OPTIMIZACIÓN")
    print("="*80)
    
    recomendaciones = {
        'CRÍTICAS (Implementar YA)': [
            '✅ Backups automáticos - YA IMPLEMENTADO',
            '✅ Monitoring y health checks - YA IMPLEMENTADO',
            '✅ Redis cache - YA IMPLEMENTADO',
            '✅ Rate limiting - YA IMPLEMENTADO',
        ],
        'ALTAS (Esta semana)': [
            'Agregar índices en tablas grandes (gestion_ventas, gestion_producto)',
            'Optimizar queries con select_related() y prefetch_related()',
            'Habilitar slow query log para identificar queries lentas',
            'Implementar paginación en listados grandes',
        ],
        'MEDIAS (Este mes)': [
            'Implementar query caching para reportes',
            'Optimizar templates con {% cache %} tags',
            'Agregar índices compuestos para queries frecuentes',
            'Implementar lazy loading en relaciones ManyToMany',
        ],
        'BAJAS (Futuro)': [
            'Considerar particionamiento de tablas grandes',
            'Implementar database connection pooling',
            'Usar materialized views para reportes complejos',
            'Implementar full-text search con Elasticsearch',
        ],
    }
    
    for prioridad, items in recomendaciones.items():
        print(f"\n{prioridad}")
        for item in items:
            if '✅' in item:
                print(f"  {item}")
            else:
                print(f"  - {item}")


def generar_queries_optimizacion():
    """Genera queries SQL para optimización"""
    print("\n" + "="*80)
    print("8. QUERIES PARA OPTIMIZACIÓN")
    print("="*80)
    
    print("\n[CREAR ÍNDICES RECOMENDADOS]")
    print("""
-- Índices para tabla gestion_ventas
CREATE INDEX idx_ventas_fecha ON gestion_ventas(fecha);
CREATE INDEX idx_ventas_usuario ON gestion_ventas(usuario_id);
CREATE INDEX idx_ventas_tarjeta ON gestion_ventas(tarjeta_id);

-- Índices para tabla gestion_detalleventa
CREATE INDEX idx_detalleventa_venta ON gestion_detalleventa(venta_id);
CREATE INDEX idx_detalleventa_producto ON gestion_detalleventa(producto_id);

-- Índices para tabla gestion_producto
CREATE INDEX idx_producto_categoria ON gestion_producto(categoria_id);
CREATE INDEX idx_producto_activo ON gestion_producto(activo);

-- Índices para tabla gestion_tarjeta
CREATE INDEX idx_tarjeta_hijo ON gestion_tarjeta(hijo_id);
CREATE INDEX idx_tarjeta_activa ON gestion_tarjeta(activa);

-- Índice compuesto para búsquedas frecuentes
CREATE INDEX idx_ventas_fecha_usuario ON gestion_ventas(fecha, usuario_id);
    """)
    
    print("\n[HABILITAR SLOW QUERY LOG]")
    print("""
-- Habilitar log de queries lentas (queries > 2 segundos)
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';
    """)
    
    print("\n[ANALIZAR QUERIES ESPECÍFICAS]")
    print("""
-- Ver estadísticas de tablas
ANALYZE TABLE gestion_ventas, gestion_producto, gestion_tarjeta;

-- Ver plan de ejecución de queries
EXPLAIN SELECT * FROM gestion_ventas WHERE fecha >= '2026-01-01';
    """)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("ANÁLISIS DE PERFORMANCE - SISTEMA CANTINA POS")
    print("Fecha: 2026-01-10")
    print("="*80)
    
    try:
        if analizar_conexion_bd():
            analizar_tablas_bd()
            analizar_indices_bd()
            analizar_queries_lentas()
            analizar_cache()
            analizar_modelos_django()
            generar_recomendaciones()
            generar_queries_optimizacion()
            
            print("\n" + "="*80)
            print("✅ ANÁLISIS DE PERFORMANCE COMPLETADO")
            print("="*80)
            print("\nPróximos pasos:")
            print("1. Revisar recomendaciones de índices")
            print("2. Ejecutar queries de optimización en BD")
            print("3. Habilitar slow query log")
            print("4. Monitorear performance después de cambios")
            print("="*80)
        else:
            print("\n❌ No se pudo conectar a la BD")
            
    except Exception as e:
        print(f"\n❌ Error durante análisis: {e}")
        import traceback
        traceback.print_exc()
