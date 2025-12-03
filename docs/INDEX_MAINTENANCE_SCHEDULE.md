# Programa de Mantenimiento de Índices

## 📅 Frecuencia de Revisión

**Recomendado:** Cada **3-6 meses**

**Factores que determinan la frecuencia:**
- Crecimiento de datos (más registros = revisar más seguido)
- Cambios en patrones de uso
- Nuevas funcionalidades agregadas
- Reportes de lentitud de usuarios

## 🎯 Objetivos de la Revisión

1. **Identificar índices no utilizados** → Eliminar (liberan espacio y mejoran escrituras)
2. **Detectar índices redundantes** → Consolidar
3. **Encontrar queries lentas nuevas** → Agregar índices faltantes
4. **Verificar fragmentación** → Optimizar índices existentes
5. **Revisar tamaño de índices** → Asegurar uso eficiente del espacio

## 🔍 Proceso de Revisión

### Fase 1: Análisis de Uso de Índices (30 min)

#### 1.1 Identificar Índices No Utilizados

```sql
-- Conectar a MySQL
mysql -u root -p cantinatitadb

-- Ver estadísticas de uso de índices
SELECT 
    object_schema AS database_name,
    object_name AS table_name,
    index_name,
    COUNT_STAR AS times_used,
    COUNT_READ AS times_read,
    COUNT_WRITE AS times_write
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'cantinatitadb'
AND index_name IS NOT NULL
AND index_name != 'PRIMARY'
ORDER BY COUNT_STAR ASC
LIMIT 50;
```

**Criterios de Eliminación:**
- `times_used = 0` → **Candidato a eliminar**
- `times_read < 100` y han pasado 3+ meses → **Considerar eliminar**
- `times_write > times_read * 100` → **Índice costoso, revisar necesidad**

#### 1.2 Detectar Índices Redundantes

```sql
-- Índices duplicados o redundantes
SELECT 
    s1.TABLE_NAME,
    s1.INDEX_NAME AS index1,
    GROUP_CONCAT(s1.COLUMN_NAME ORDER BY s1.SEQ_IN_INDEX) AS columns1,
    s2.INDEX_NAME AS index2,
    GROUP_CONCAT(s2.COLUMN_NAME ORDER BY s2.SEQ_IN_INDEX) AS columns2
FROM information_schema.STATISTICS s1
JOIN information_schema.STATISTICS s2 
    ON s1.TABLE_SCHEMA = s2.TABLE_SCHEMA
    AND s1.TABLE_NAME = s2.TABLE_NAME
    AND s1.INDEX_NAME < s2.INDEX_NAME
WHERE s1.TABLE_SCHEMA = 'cantinatitadb'
GROUP BY s1.TABLE_NAME, s1.INDEX_NAME, s2.INDEX_NAME
HAVING columns1 = LEFT(columns2, LENGTH(columns1));
```

**Ejemplos de Redundancia:**

```
✅ MANTENER:
- idx_ventas_fecha_estado (Fecha, Estado_Pago)
❌ ELIMINAR:
- idx_ventas_fecha (Fecha)  ← Redundante, ya cubierto por el compuesto
```

**Excepción:** Mantener índice simple si las queries lo usan frecuentemente.

#### 1.3 Listar Todos los Índices del Proyecto

```sql
-- Ver todos los índices con tamaño
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    INDEX_TYPE,
    ROUND(
        (stat_value * @@innodb_page_size) / 1024 / 1024, 2
    ) AS size_mb
FROM information_schema.STATISTICS
LEFT JOIN mysql.innodb_index_stats 
    ON STATISTICS.TABLE_NAME = innodb_index_stats.table_name
    AND STATISTICS.INDEX_NAME = innodb_index_stats.index_name
WHERE TABLE_SCHEMA = 'cantinatitadb'
AND INDEX_NAME != 'PRIMARY'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
```

### Fase 2: Análisis de Queries Lentas (45 min)

#### 2.1 Habilitar Slow Query Log

```sql
-- Configurar umbral de slow query (queries > 1 segundo)
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- Ver configuración actual
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';
```

**Archivo de log:** Generalmente en `/var/log/mysql/mysql-slow.log` (Linux) o `C:\ProgramData\MySQL\MySQL Server X.X\Data\hostname-slow.log` (Windows)

#### 2.2 Revisar Django Debug Toolbar

**Vistas críticas a revisar:**

1. **POS - Punto de Venta** (`/pos/venta/`)
   ```
   Umbral: < 15 queries, < 200ms
   ```

2. **Cuenta Corriente Unificada** (`/pos/cuenta-corriente-unificada/<id>/`)
   ```
   Umbral: < 25 queries, < 300ms
   ```

3. **Reportes de Ventas** (`/reportes/ventas/`)
   ```
   Umbral: < 30 queries, < 400ms
   ```

4. **API - Lista de Productos** (`/api/v1/productos/`)
   ```
   Umbral: < 10 queries, < 150ms
   ```

**Proceso:**
1. Navegar a cada vista
2. Abrir Debug Toolbar → Panel SQL
3. Anotar queries > 100ms
4. Copiar SQL de queries lentas
5. Ejecutar EXPLAIN (ver `EXPLAIN_QUERIES_GUIDE.md`)

#### 2.3 Analizar Slow Query Log

```bash
# Resumen de queries lentas (mysqldumpslow)
mysqldumpslow -s t -t 10 /ruta/al/mysql-slow.log

# Parámetros:
# -s t: Ordenar por tiempo total
# -t 10: Top 10 queries
```

**Alternativa Python:**
```python
# scripts/analyze_slow_queries.py
import re
from collections import defaultdict

def parse_slow_log(log_file):
    queries = defaultdict(list)
    
    with open(log_file, 'r') as f:
        current_query = None
        for line in f:
            if line.startswith('# Query_time:'):
                time = float(re.search(r'Query_time: ([\d.]+)', line).group(1))
                current_query = {'time': time}
            elif line.startswith('SELECT') or line.startswith('UPDATE') or line.startswith('DELETE'):
                if current_query:
                    current_query['sql'] = line.strip()
                    queries[line.strip()].append(current_query['time'])
    
    # Top 10 por tiempo total
    for sql, times in sorted(queries.items(), key=lambda x: sum(x[1]), reverse=True)[:10]:
        print(f"Total: {sum(times):.2f}s | Avg: {sum(times)/len(times):.2f}s | Count: {len(times)}")
        print(f"SQL: {sql[:100]}...")
        print()

if __name__ == '__main__':
    parse_slow_log('/ruta/al/mysql-slow.log')
```

### Fase 3: Optimización (60-90 min)

#### 3.1 Eliminar Índices No Utilizados

```sql
-- Respaldar antes de eliminar
SELECT CONCAT(
    'DROP INDEX ', INDEX_NAME, ' ON ', TABLE_NAME, ';'
) AS drop_statement
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'cantinatitadb'
AND INDEX_NAME IN (
    -- Índices identificados como no utilizados
    'idx_old_unused',
    'idx_legacy_column'
);

-- Ejecutar DROP INDEX manualmente después de revisar
DROP INDEX idx_old_unused ON tabla_ejemplo;
```

**⚠️ Precaución:**
- Respaldar base de datos antes de eliminar índices
- Eliminar de a uno por vez
- Monitorear rendimiento por 1 semana
- Si hay problemas, recrear el índice

#### 3.2 Consolidar Índices Redundantes

```sql
-- Ejemplo: Eliminar índice simple si hay compuesto
-- ANTES:
-- idx_ventas_fecha (Fecha)
-- idx_ventas_fecha_estado (Fecha, Estado_Pago)

-- DESPUÉS: Mantener solo el compuesto
DROP INDEX idx_ventas_fecha ON ventas;
-- Mantener: idx_ventas_fecha_estado
```

#### 3.3 Agregar Índices Faltantes

**Para queries identificadas como lentas:**

```sql
-- Ejecutar EXPLAIN en cada query lenta
EXPLAIN [query_lenta];

-- Si type = ALL o rows > 10,000, agregar índice
-- Ejemplo: Query filtra por Estado_Pago y ordena por Fecha
CREATE INDEX idx_ventas_estado_fecha ON ventas(Estado_Pago, Fecha DESC);
```

**Reglas para índices compuestos:**
1. Columnas de igualdad (=) primero
2. Columnas de rango (>, <, BETWEEN) después
3. Columnas de ORDER BY al final

#### 3.4 Optimizar Índices Fragmentados

```sql
-- Ver fragmentación de índices
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
    ROUND(DATA_FREE / 1024 / 1024, 2) AS free_mb
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'cantinatitadb'
AND DATA_FREE > 0
ORDER BY DATA_FREE DESC;
```

**Si fragmentación > 20%:**
```sql
-- Optimizar tabla (reconstruye índices)
OPTIMIZE TABLE ventas;
OPTIMIZE TABLE detalle_venta;
OPTIMIZE TABLE productos;
```

**⚠️ Nota:** `OPTIMIZE TABLE` puede tardar varios minutos en tablas grandes y bloquea la tabla durante la operación. Ejecutar en horario de baja actividad.

### Fase 4: Documentación (15 min)

#### 4.1 Registrar Cambios

Crear archivo: `docs/index_maintenance/YYYY-MM-DD.md`

```markdown
# Mantenimiento de Índices - [Fecha]

## 📊 Estadísticas Previas
- Total índices: X
- Tamaño total: X MB
- Queries lentas detectadas: X

## 🗑️ Índices Eliminados
- `idx_tabla_columna`: No utilizado en 6 meses (0 lecturas)
- `idx_tabla_old`: Redundante con idx_tabla_old_new

## ➕ Índices Agregados
- `idx_ventas_estado_fecha`: Optimiza reporte de ventas pendientes
  - Reducción de rows: 15,420 → 85 (99.4%)
  - Reducción de tiempo: 2.3s → 0.08s (96.5%)

## 🔧 Índices Optimizados
- `ventas`: OPTIMIZE TABLE completado (liberados 12 MB)
- `detalle_venta`: OPTIMIZE TABLE completado (liberados 5 MB)

## 📈 Resultados
- Total índices: X → Y
- Tamaño total: X MB → Y MB
- Queries lentas: X → Y
- Mejora promedio: Z%

## ⏭️ Acciones Pendientes
- [ ] Monitorear rendimiento por 1 semana
- [ ] Revisar nuevamente en [Fecha +3 meses]
```

#### 4.2 Actualizar Script de Análisis

Agregar índices nuevos a `scripts/analyze_database.py` si es necesario.

## 📋 Checklist Completo

### Antes de Empezar:
- [ ] Respaldar base de datos completa
- [ ] Notificar a usuarios de posible mantenimiento
- [ ] Elegir horario de baja actividad (noche/fin de semana)

### Durante Revisión:
- [ ] Ejecutar queries de análisis de uso
- [ ] Identificar índices no utilizados (times_used = 0)
- [ ] Detectar índices redundantes
- [ ] Revisar Django Debug Toolbar en vistas críticas
- [ ] Analizar slow query log
- [ ] Ejecutar EXPLAIN en queries lentas
- [ ] Listar índices a eliminar
- [ ] Listar índices a agregar
- [ ] Listar tablas a optimizar

### Aplicar Cambios:
- [ ] Eliminar índices no utilizados (uno por uno)
- [ ] Consolidar índices redundantes
- [ ] Crear índices faltantes
- [ ] Ejecutar OPTIMIZE TABLE en tablas fragmentadas
- [ ] Verificar que no hay errores

### Después de Cambios:
- [ ] Ejecutar Django check: `python manage.py check`
- [ ] Probar vistas críticas manualmente
- [ ] Verificar tiempos en Debug Toolbar
- [ ] Ejecutar tests: `python manage.py test`
- [ ] Documentar cambios en `docs/index_maintenance/`
- [ ] Commit y push a repositorio
- [ ] Monitorear rendimiento por 1 semana

### Seguimiento:
- [ ] Revisar métricas después de 1 semana
- [ ] Revisar métricas después de 1 mes
- [ ] Programar próxima revisión en [Fecha +3 meses]

## 🛠️ Scripts Útiles

### Script 1: Reporte de Uso de Índices

Crear archivo: `scripts/index_usage_report.py`

```python
"""
Genera reporte de uso de índices de MySQL
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def generate_index_report():
    with connection.cursor() as cursor:
        # Índices no utilizados
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
        
        print("=" * 80)
        print(f"REPORTE DE ÍNDICES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        if unused:
            print("🗑️  ÍNDICES NO UTILIZADOS (Candidatos a eliminar)")
            print("-" * 80)
            for table, index, _ in unused:
                print(f"  • {table}.{index}")
            print()
        else:
            print("✅ No se encontraron índices sin uso")
            print()
        
        # Tamaño de índices
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                ROUND(stat_value * @@innodb_page_size / 1024 / 1024, 2) AS size_mb
            FROM information_schema.STATISTICS
            LEFT JOIN mysql.innodb_index_stats 
                ON STATISTICS.TABLE_NAME = innodb_index_stats.table_name
                AND STATISTICS.INDEX_NAME = innodb_index_stats.index_name
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND INDEX_NAME != 'PRIMARY'
            GROUP BY TABLE_NAME, INDEX_NAME
            ORDER BY size_mb DESC
            LIMIT 10
        """)
        
        sizes = cursor.fetchall()
        
        print("📊 TOP 10 ÍNDICES MÁS GRANDES")
        print("-" * 80)
        for table, index, size in sizes:
            print(f"  {table}.{index}: {size} MB")
        print()
        
        # Total
        cursor.execute("""
            SELECT COUNT(DISTINCT INDEX_NAME) AS total
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND INDEX_NAME != 'PRIMARY'
        """)
        
        total = cursor.fetchone()[0]
        print(f"📈 TOTAL DE ÍNDICES: {total}")
        print("=" * 80)

if __name__ == '__main__':
    generate_index_report()
```

**Uso:**
```bash
D:/anteproyecto20112025/.venv/Scripts/python.exe scripts/index_usage_report.py
```

### Script 2: Sugerencias de Índices

Crear archivo: `scripts/suggest_indexes.py`

```python
"""
Sugiere índices basándose en queries lentas de Django Debug Toolbar
"""
import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def suggest_indexes():
    """
    Analiza las queries más frecuentes y sugiere índices
    """
    print("=" * 80)
    print("SUGERENCIAS DE ÍNDICES")
    print("=" * 80)
    print()
    
    suggestions = []
    
    # Análisis basado en modelos comunes
    common_filters = {
        'ventas': ['Fecha', 'Estado_Pago', 'ID_Cliente', 'ID_Empleado'],
        'detalle_venta': ['ID_Venta', 'ID_Producto'],
        'productos': ['ID_Categoria', 'Descripcion'],
        'clientes': ['Nombre', 'Apellido', 'Tipo_Cliente'],
        'stock_unico': ['ID_Producto', 'Stock_Actual'],
        'consumos_tarjeta': ['ID_Tarjeta', 'Fecha', 'Estado'],
        'cargas_saldo': ['ID_Tarjeta', 'Fecha'],
        'cta_corriente': ['ID_Cliente', 'Fecha', 'Estado'],
    }
    
    with connection.cursor() as cursor:
        for table, columns in common_filters.items():
            # Verificar si la tabla existe
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = 'cantinatitadb'
                AND TABLE_NAME = '{table}'
            """)
            
            if cursor.fetchone()[0] == 0:
                continue
            
            for col in columns:
                # Verificar si ya existe índice en esta columna
                cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM information_schema.STATISTICS
                    WHERE TABLE_SCHEMA = 'cantinatitadb'
                    AND TABLE_NAME = '{table}'
                    AND COLUMN_NAME = '{col}'
                    AND INDEX_NAME != 'PRIMARY'
                """)
                
                if cursor.fetchone()[0] == 0:
                    suggestions.append({
                        'table': table,
                        'column': col,
                        'reason': f'Filtrado frecuente por {col}'
                    })
    
    if suggestions:
        print("💡 ÍNDICES SUGERIDOS:")
        print("-" * 80)
        for s in suggestions:
            print(f"  CREATE INDEX idx_{s['table']}_{s['column'].lower()} ")
            print(f"    ON {s['table']}({s['column']});")
            print(f"  -- Razón: {s['reason']}")
            print()
    else:
        print("✅ No se encontraron sugerencias adicionales")
    
    print("=" * 80)

if __name__ == '__main__':
    suggest_indexes()
```

## 📆 Calendario de Mantenimiento

### Primera Revisión: [Fecha actual + 3 meses]
- [ ] Ejecutar scripts de análisis
- [ ] Revisar vistas críticas con Debug Toolbar
- [ ] Analizar slow query log
- [ ] Aplicar optimizaciones
- [ ] Documentar cambios

### Segunda Revisión: [Fecha actual + 6 meses]
- [ ] Repetir proceso completo
- [ ] Comparar con revisión anterior
- [ ] Ajustar frecuencia si es necesario

### Revisiones Continuas: Cada 3-6 meses
- [ ] Mantener calendario actualizado
- [ ] Revisar después de lanzar nuevas funcionalidades
- [ ] Revisar si usuarios reportan lentitud

## 🎯 Métricas de Éxito

### Después de cada revisión, deberías ver:
- ✅ Reducción de queries lentas (> 100ms)
- ✅ Reducción de tiempo promedio de respuesta
- ✅ Menos índices no utilizados
- ✅ Tamaño de índices optimizado
- ✅ Sin errores en producción

### Alertas de problemas:
- 🔴 Queries nuevas > 500ms
- 🔴 Incremento de slow queries > 20%
- 🔴 Tamaño de índices crece sin control
- 🔴 Usuarios reportan lentitud consistentemente

## 📚 Referencias

- **MySQL Performance Schema**: https://dev.mysql.com/doc/refman/8.0/en/performance-schema.html
- **Index Optimization**: https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html
- **Django Database Optimization**: https://docs.djangoproject.com/en/5.2/topics/db/optimization/

## ✅ Próxima Revisión Programada

**Fecha:** [3 meses desde hoy]

**Responsable:** [Tu nombre o equipo]

**Recordatorio:** Agregar a calendario con 1 semana de anticipación
