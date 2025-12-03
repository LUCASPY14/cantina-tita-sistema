# Guía de EXPLAIN para Optimización de Queries

## 📊 ¿Qué es EXPLAIN?

`EXPLAIN` es un comando de MySQL que muestra cómo el motor de base de datos ejecutará una query SQL. Te permite identificar problemas de rendimiento **antes** de que se conviertan en cuellos de botella.

## 🎯 Cuándo Usar EXPLAIN

### Usar EXPLAIN cuando:
- ✅ Una query tarda más de **100ms** en ejecutarse
- ✅ Django Debug Toolbar muestra **queries duplicadas**
- ✅ Una vista carga más de **30 queries**
- ✅ Los usuarios reportan **lentitud** en una funcionalidad
- ✅ Trabajas con **tablas grandes** (>10,000 registros)
- ✅ Agregas **nuevos índices** y quieres verificar que se usan

### No necesitas EXPLAIN cuando:
- ❌ La query es simple y rápida (<10ms)
- ❌ Solo retorna pocos registros (<100)
- ❌ Ya está optimizada con índices apropiados

## 🔧 Cómo Usar EXPLAIN

### 1. Desde Django Debug Toolbar

**Pasos:**
1. Ejecuta el servidor: `python manage.py runserver`
2. Navega a la vista problemática
3. Abre Django Debug Toolbar (barra lateral derecha)
4. Ve al panel **SQL**
5. Haz clic en la query lenta
6. Busca el botón **"Explain"** o **"Analyze"**
7. Revisa el plan de ejecución

### 2. Desde Django Shell

```python
# Abrir shell
python manage.py shell

# Importar el modelo
from gestion.models import Venta
from django.db import connection

# Ejecutar query
ventas = Venta.objects.select_related('cliente', 'empleado')

# Obtener SQL
sql = str(ventas.query)
print(sql)

# Ejecutar EXPLAIN
with connection.cursor() as cursor:
    cursor.execute(f"EXPLAIN {sql}")
    columns = [col[0] for col in cursor.description]
    results = cursor.fetchall()
    
    for row in results:
        print(dict(zip(columns, row)))
```

### 3. Desde MySQL Workbench o CLI

```sql
-- Conectar a la base de datos
mysql -u root -p cantinatitadb

-- Ejecutar EXPLAIN
EXPLAIN SELECT v.*, c.Nombre, c.Apellido, e.Nombre AS emp_nombre
FROM ventas v
INNER JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
INNER JOIN empleados e ON v.ID_Empleado = e.ID_Empleado
WHERE v.Fecha >= '2025-01-01'
ORDER BY v.Fecha DESC;
```

## 📋 Interpretar Resultados de EXPLAIN

### Columnas Importantes

#### 1. **id**
- Identifica cada SELECT en la query
- Número más alto = ejecuta primero

#### 2. **select_type**
- `SIMPLE`: Query simple sin subqueries
- `PRIMARY`: Query principal en una unión
- `SUBQUERY`: Subquery en WHERE o SELECT
- `DERIVED`: Tabla derivada (FROM subquery)

#### 3. **table**
- Nombre de la tabla que se está leyendo

#### 4. **type** (MUY IMPORTANTE ⚠️)
Orden de mejor a peor rendimiento:

```
✅ system    > const    > eq_ref   > ref       ✅ Excelente
⚠️  range     > index    > ALL                 ❌ Mejorar
```

**Detalles:**
- **system/const**: Tabla con 1 registro (óptimo)
- **eq_ref**: Lee 1 fila por JOIN usando PRIMARY KEY (óptimo)
- **ref**: Lee varias filas usando índice (bueno)
- **range**: Lee rango de filas (ej: BETWEEN, IN) (aceptable)
- **index**: Escanea todo el índice (lento)
- **ALL**: Escanea toda la tabla (MUY LENTO ❌)

#### 5. **possible_keys**
- Índices que MySQL **podría** usar
- Si está vacío, considera agregar índices

#### 6. **key**
- Índice que MySQL **realmente usa**
- Si es NULL, no usa ningún índice ❌

#### 7. **key_len**
- Longitud del índice usado
- Mayor longitud = más específico

#### 8. **ref**
- Columnas o constantes comparadas con el índice

#### 9. **rows** (MUY IMPORTANTE ⚠️)
- **Estimación** de filas que MySQL examinará
- Menor número = mejor
- >10,000 filas = problema potencial

#### 10. **filtered**
- Porcentaje de filas filtradas por condición WHERE
- 100% = todas las filas cumplen (óptimo)
- <10% = muchas filas descartadas (considerar índice)

#### 11. **Extra**
Información adicional importante:

**✅ BUENO:**
- `Using index`: Solo lee del índice (muy rápido)
- `Using where`: Aplica filtros (normal)
- `Using index condition`: Usa índice para filtrar (bueno)

**⚠️ REVISAR:**
- `Using filesort`: Ordenamiento en memoria (lento si muchas filas)
- `Using temporary`: Crea tabla temporal (lento)

**❌ MALO:**
- `Using where; Using join buffer`: JOIN sin índice (OPTIMIZAR)
- `Full table scan`: Lee toda la tabla (AGREGAR ÍNDICE)

## 🚨 Señales de Alerta

### 🔴 URGENTE - Optimizar Ya
```
type = ALL              # Escaneo completo de tabla
rows > 10,000           # Examina muchas filas
key = NULL              # No usa ningún índice
Extra = Using filesort  # Ordena en memoria (con muchas filas)
Extra = Using temporary # Crea tabla temporal
```

### 🟡 MEJORAR - Revisar Pronto
```
type = index            # Lee todo el índice
rows > 1,000            # Examina bastantes filas
filtered < 20%          # Descarta 80% de filas leídas
```

### 🟢 BIEN - Mantener Vigilancia
```
type = ref/eq_ref       # Usa índices eficientemente
rows < 100              # Pocas filas examinadas
key != NULL             # Usa algún índice
filtered > 80%          # Filtra eficientemente
```

## 📝 Ejemplos Prácticos

### Ejemplo 1: Query Sin Índice (MALO ❌)

```sql
EXPLAIN SELECT * FROM ventas WHERE Fecha >= '2025-01-01';
```

**Resultado:**
```
+----+-------------+--------+------+---------------+------+---------+------+-------+-------------+
| id | select_type | table  | type | possible_keys | key  | key_len | ref  | rows  | Extra       |
+----+-------------+--------+------+---------------+------+---------+------+-------+-------------+
|  1 | SIMPLE      | ventas | ALL  | NULL          | NULL | NULL    | NULL | 15420 | Using where |
+----+-------------+--------+------+---------------+------+---------+------+-------+-------------+
```

**Problemas:**
- ❌ `type = ALL`: Escanea toda la tabla
- ❌ `key = NULL`: No usa ningún índice
- ❌ `rows = 15420`: Lee 15,420 filas

**Solución:**
```sql
-- Crear índice en Fecha
CREATE INDEX idx_ventas_fecha ON ventas(Fecha);
```

### Ejemplo 2: Query Con Índice (BUENO ✅)

```sql
EXPLAIN SELECT * FROM ventas WHERE Fecha >= '2025-01-01';
```

**Resultado después del índice:**
```
+----+-------------+--------+-------+-------------------+-------------------+---------+------+------+-----------------------+
| id | select_type | table  | type  | possible_keys     | key               | key_len | ref  | rows | Extra                 |
+----+-------------+--------+-------+-------------------+-------------------+---------+------+------+-----------------------+
|  1 | SIMPLE      | ventas | range | idx_ventas_fecha  | idx_ventas_fecha  | 3       | NULL | 428  | Using index condition |
+----+-------------+--------+-------+-------------------+-------------------+---------+------+------+-----------------------+
```

**Mejoras:**
- ✅ `type = range`: Usa índice para rango
- ✅ `key = idx_ventas_fecha`: Usa el índice creado
- ✅ `rows = 428`: Solo examina 428 filas (97% reducción)

### Ejemplo 3: JOIN Sin Índice (MALO ❌)

```sql
EXPLAIN SELECT v.*, c.Nombre
FROM ventas v
JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
WHERE v.Estado_Pago = 'Pendiente';
```

**Resultado:**
```
+----+-------------+-------+------+---------------+---------+---------+-----------------------+-------+----------------------------------------------------+
| id | select_type | table | type | possible_keys | key     | key_len | ref                   | rows  | Extra                                              |
+----+-------------+-------+------+---------------+---------+---------+-----------------------+-------+----------------------------------------------------+
|  1 | SIMPLE      | v     | ALL  | NULL          | NULL    | NULL    | NULL                  | 15420 | Using where                                        |
|  1 | SIMPLE      | c     | ALL  | PRIMARY       | NULL    | NULL    | NULL                  | 3245  | Using where; Using join buffer (Block Nested Loop) |
+----+-------------+-------+------+---------------+---------+---------+-----------------------+-------+----------------------------------------------------+
```

**Problemas:**
- ❌ `type = ALL` en ambas tablas
- ❌ `Using join buffer`: JOIN ineficiente
- ❌ `rows = 15420 * 3245`: Examina 50 millones de combinaciones

**Solución:**
```sql
-- Índice compuesto: Fecha + Estado
CREATE INDEX idx_ventas_estado_fecha ON ventas(Estado_Pago, Fecha);
```

### Ejemplo 4: JOIN Con Índice (BUENO ✅)

```sql
EXPLAIN SELECT v.*, c.Nombre
FROM ventas v
JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
WHERE v.Estado_Pago = 'Pendiente';
```

**Resultado después del índice:**
```
+----+-------------+-------+--------+---------------------------+---------------------------+---------+-----------------------+------+-----------------------+
| id | select_type | table | type   | possible_keys             | key                       | key_len | ref                   | rows | Extra                 |
+----+-------------+-------+--------+---------------------------+---------------------------+---------+-----------------------+------+-----------------------+
|  1 | SIMPLE      | v     | ref    | idx_ventas_estado_fecha   | idx_ventas_estado_fecha   | 50      | const                 | 85   | Using index condition |
|  1 | SIMPLE      | c     | eq_ref | PRIMARY                   | PRIMARY                   | 4       | cantinatitadb.v.ID_Cliente | 1    | NULL                  |
+----+-------------+-------+--------+---------------------------+---------------------------+---------+-----------------------+------+-----------------------+
```

**Mejoras:**
- ✅ `type = ref` en ventas (usa índice)
- ✅ `type = eq_ref` en clientes (1 fila por JOIN)
- ✅ `rows = 85`: Solo examina 85 filas (99.4% reducción)

## 🛠️ Estrategias de Optimización

### 1. Agregar Índices Simples

**Cuando:**
- Filtras frecuentemente por una columna
- Ordenas por una columna

**Ejemplo:**
```sql
-- Filtrar por fecha
CREATE INDEX idx_ventas_fecha ON ventas(Fecha);

-- Filtrar por estado de pago
CREATE INDEX idx_ventas_estado ON ventas(Estado_Pago);
```

### 2. Agregar Índices Compuestos

**Cuando:**
- Filtras por múltiples columnas simultáneamente
- WHERE con varias condiciones AND

**Orden de columnas:**
1. Columnas de igualdad (=) primero
2. Columnas de rango (>, <, BETWEEN) después
3. Columnas de ordenamiento (ORDER BY) al final

**Ejemplo:**
```sql
-- WHERE Estado = 'X' AND Fecha > 'Y' ORDER BY Fecha
CREATE INDEX idx_ventas_estado_fecha ON ventas(Estado_Pago, Fecha);
```

### 3. Usar select_related() (Django)

**Cuando:**
- JOINs con ForeignKey
- EXPLAIN muestra type = ALL en tablas relacionadas

**Ejemplo:**
```python
# Antes (N+1 queries)
ventas = Venta.objects.filter(estado_pago='Pendiente')
for v in ventas:
    print(v.cliente.nombre)  # Query por cada venta

# Después (2 queries)
ventas = Venta.objects.select_related('cliente').filter(estado_pago='Pendiente')
for v in ventas:
    print(v.cliente.nombre)  # Sin query adicional
```

### 4. Usar prefetch_related() (Django)

**Cuando:**
- Relaciones ManyToMany o Reverse ForeignKey
- EXPLAIN muestra muchas queries para la misma tabla

**Ejemplo:**
```python
# Antes (N+1 queries)
ventas = Venta.objects.all()
for v in ventas:
    print(v.detalle_venta.all())  # Query por cada venta

# Después (2 queries)
ventas = Venta.objects.prefetch_related('detalle_venta')
for v in ventas:
    print(v.detalle_venta.all())  # Sin query adicional
```

### 5. Limitar Columnas con only()

**Cuando:**
- EXPLAIN muestra muchas columnas en SELECT *
- Solo necesitas pocas columnas

**Ejemplo:**
```python
# Antes (lee 20 columnas)
ventas = Venta.objects.all()

# Después (lee 3 columnas)
ventas = Venta.objects.only('id', 'fecha', 'total')
```

### 6. Agregaciones en Base de Datos

**Cuando:**
- Calculas sumas/promedios en Python
- EXPLAIN muestra que lees muchas filas para agregaciones

**Ejemplo:**
```python
# Antes (lee todas las filas)
ventas = Venta.objects.all()
total = sum([v.total for v in ventas])

# Después (calcula en DB)
from django.db.models import Sum
total = Venta.objects.aggregate(total=Sum('total'))['total']
```

## 📊 Workflow de Optimización

### Paso 1: Identificar Query Lenta
```
Django Debug Toolbar → Panel SQL → Query > 100ms
```

### Paso 2: Ejecutar EXPLAIN
```sql
EXPLAIN [query copiada de Debug Toolbar]
```

### Paso 3: Analizar Resultados
```
¿type = ALL?           → Agregar índice
¿rows > 10,000?        → Agregar índice o filtrar más
¿key = NULL?           → Crear índice apropiado
¿Using filesort?       → Agregar índice en ORDER BY
¿Using temporary?      → Revisar GROUP BY y JOINs
¿Using join buffer?    → Agregar índice en columnas de JOIN
```

### Paso 4: Aplicar Optimización
```python
# Opción 1: Agregar índice en DB
CREATE INDEX idx_tabla_columna ON tabla(columna);

# Opción 2: Optimizar query Django
queryset = Model.objects.select_related('fk').prefetch_related('m2m')
```

### Paso 5: Verificar Mejora
```sql
-- Ejecutar EXPLAIN nuevamente
EXPLAIN [query optimizada]

-- Comparar:
-- - type mejoró (ALL → ref)
-- - rows disminuyó (10000 → 100)
-- - key tiene valor (NULL → idx_tabla_columna)
```

### Paso 6: Medir en Producción
```
Django Debug Toolbar → Verificar tiempo < 100ms
```

## 📈 Casos de Uso Comunes

### Caso 1: Reporte de Ventas por Fecha

**Query Lenta:**
```python
ventas = Venta.objects.filter(
    fecha__gte='2025-01-01',
    fecha__lte='2025-12-31'
).order_by('-fecha')
```

**EXPLAIN muestra:**
- type = ALL
- rows = 50,000
- Extra = Using filesort

**Solución:**
```sql
CREATE INDEX idx_ventas_fecha ON ventas(Fecha DESC);
```

### Caso 2: Cuenta Corriente de Cliente

**Query Lenta:**
```python
movimientos = CtaCorriente.objects.filter(
    cliente_id=123
).select_related('venta', 'pago')
```

**EXPLAIN muestra:**
- type = ALL en cta_corriente
- rows = 100,000
- No usa índice

**Solución:**
```sql
CREATE INDEX idx_ctacte_cliente ON cta_corriente(ID_Cliente, Fecha DESC);
```

### Caso 3: Stock de Productos

**Query Lenta:**
```python
productos = Producto.objects.filter(
    stock_unico__stock_actual__lt=10
).select_related('categoria', 'stock_unico')
```

**EXPLAIN muestra:**
- type = ALL en stock_unico
- rows = 20,000

**Solución:**
```sql
CREATE INDEX idx_stock_actual ON stock_unico(Stock_Actual);
```

## 🔍 Herramientas Adicionales

### EXPLAIN ANALYZE (MySQL 8.0+)
```sql
-- Ejecuta la query Y muestra tiempos reales
EXPLAIN ANALYZE SELECT * FROM ventas WHERE Fecha >= '2025-01-01';
```

**Ventajas:**
- Muestra tiempo de ejecución **real** (no estimado)
- Identifica qué parte de la query es más lenta

### EXPLAIN FORMAT=JSON
```sql
-- Salida en formato JSON (más detallada)
EXPLAIN FORMAT=JSON SELECT * FROM ventas WHERE Fecha >= '2025-01-01';
```

**Ventajas:**
- Más información sobre el plan de ejecución
- Fácil de parsear programáticamente

## 📚 Checklist de Optimización

### Antes de Optimizar:
- [ ] Query tarda >100ms según Debug Toolbar
- [ ] Identificada la query problemática
- [ ] Copiado el SQL exacto

### Durante Optimización:
- [ ] Ejecutado EXPLAIN en la query
- [ ] Analizado columnas: type, rows, key, Extra
- [ ] Identificado el problema (sin índice, type=ALL, etc.)
- [ ] Aplicada solución (índice, select_related, etc.)
- [ ] Ejecutado EXPLAIN nuevamente

### Después de Optimizar:
- [ ] type mejoró (ALL → ref/eq_ref)
- [ ] rows disminuyó significativamente
- [ ] key tiene valor (usa índice)
- [ ] Query tarda <100ms
- [ ] Documentada la optimización

## 🎯 Métricas de Éxito

### Mejoras Esperadas:

**Agregar índice simple:**
- Reducción de rows: 80-99%
- Reducción de tiempo: 70-95%

**Agregar índice compuesto:**
- Reducción de rows: 90-99.9%
- Reducción de tiempo: 80-98%

**select_related():**
- Reducción de queries: N+1 → 2
- Reducción de tiempo: 50-90%

**prefetch_related():**
- Reducción de queries: N*M → 2
- Reducción de tiempo: 60-95%

## 📖 Recursos

- **MySQL EXPLAIN**: https://dev.mysql.com/doc/refman/8.0/en/explain.html
- **Django Optimization**: https://docs.djangoproject.com/en/5.2/topics/db/optimization/
- **Query Performance**: https://use-the-index-luke.com/

## 🚀 Próximos Pasos

1. ✅ Instalar Django Debug Toolbar
2. ✅ Documentar uso de EXPLAIN
3. ⏭️ Revisar queries en vistas principales
4. ⏭️ Programar revisión trimestral de índices
