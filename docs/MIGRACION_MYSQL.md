# Migración de PostgreSQL a MySQL/MariaDB

Este documento describe los cambios necesarios para migrar el sistema de PostgreSQL a MySQL/MariaDB.

## Estado Actual

El proyecto actualmente usa **PostgreSQL** en `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'escolar',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Configuración para MySQL

### 1. Instalar Driver MySQL

```bash
pip install mysqlclient
# O alternativa:
pip install PyMySQL
```

### 2. Actualizar settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'escolar',
        'USER': 'root',  # O tu usuario MySQL
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### 3. Si usas PyMySQL (alternativa):

Agregar al inicio de `__init__.py` en la carpeta del proyecto:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

## Compatibilidad de Queries

### ✅ Queries Compatibles (Usados en el Proyecto)

Todas estas funcionalidades del ORM de Django funcionan tanto en PostgreSQL como en MySQL:

1. **Aggregate Functions:**
   ```python
   .aggregate(Sum('campo'), Count('campo'), Avg('campo'))
   ```
   ✅ Compatible

2. **F() Expressions:**
   ```python
   stock.stock_actual = F('stock_actual') - cantidad
   ```
   ✅ Compatible

3. **Q() Objects:**
   ```python
   Q(descripcion__icontains=query) | Q(codigo__icontains=query)
   ```
   ✅ Compatible

4. **Annotate:**
   ```python
   .annotate(empleado_nombre=F('id_empleado__nombre'))
   ```
   ✅ Compatible

5. **Values & Values_list:**
   ```python
   .values('campo').annotate(total=Sum('otro_campo'))
   ```
   ✅ Compatible

### ⚠️ Diferencias a Considerar

#### 1. EXTRACT con fechas

**PostgreSQL:**
```python
.extra(select={'hora': 'EXTRACT(HOUR FROM fecha)'})
```

**MySQL equivalente:**
```python
.extra(select={'hora': 'HOUR(fecha)'})
```

**Solución universal (recomendada):**
```python
from django.db.models.functions import ExtractHour
.annotate(hora=ExtractHour('fecha'))
```

#### 2. DATE() function

**PostgreSQL:**
```python
.extra(select={'dia': 'DATE(fecha)'})
```

**MySQL equivalente:**
```python
.extra(select={'dia': 'DATE(fecha)'})
```
✅ Mismo sintaxis, compatible

**Solución universal (recomendada):**
```python
from django.db.models.functions import TruncDate
.annotate(dia=TruncDate('fecha'))
```

#### 3. Auto-increment

- **PostgreSQL:** Usa `SERIAL` o `SEQUENCE`
- **MySQL:** Usa `AUTO_INCREMENT`

Django maneja esto automáticamente en modelos con `AutoField`.

#### 4. Boolean Fields

- **PostgreSQL:** `BOOLEAN` nativo
- **MySQL:** `TINYINT(1)` (0 o 1)

Django maneja esto automáticamente con `BooleanField`.

## Cambios Recomendados en el Código

### 1. Dashboard View (pos_views.py línea ~280)

**Actual:**
```python
ventas_por_hora_raw = ventas_hoy.extra(
    select={'hora': 'EXTRACT(HOUR FROM fecha)'}
).values('hora').annotate(
    total=Count('id_venta')
).order_by('hora')
```

**Mejorado (compatible con ambos):**
```python
from django.db.models.functions import ExtractHour

ventas_por_hora_raw = ventas_hoy.annotate(
    hora=ExtractHour('fecha')
).values('hora').annotate(
    total=Count('id_venta')
).order_by('hora')
```

### 2. Dashboard View - Ventas Semanales (línea ~300)

**Actual:**
```python
ventas_semanales_raw = Ventas.objects.filter(
    fecha__date__gte=week_ago
).extra(
    select={'dia': 'DATE(fecha)'}
).values('dia').annotate(
    total=Sum('monto_total'),
    cantidad=Count('id_venta')
).order_by('dia')
```

**Mejorado (compatible con ambos):**
```python
from django.db.models.functions import TruncDate

ventas_semanales_raw = Ventas.objects.filter(
    fecha__date__gte=week_ago
).annotate(
    dia=TruncDate('fecha')
).values('dia').annotate(
    total=Sum('monto_total'),
    cantidad=Count('id_venta')
).order_by('dia')
```

## Testing con MySQL

### 1. Exportar datos desde PostgreSQL

```bash
# Con pg_dump
pg_dump -U postgres -d escolar -F c -b -v -f escolar_backup.dump

# O con Django
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
```

### 2. Importar a MySQL

```bash
# Crear base de datos
mysql -u root -p -e "CREATE DATABASE escolar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Importar schema (si tienes SQL)
mysql -u root -p escolar < schema.sql

# O usar Django fixtures
python manage.py loaddata data.json
```

### 3. Verificar migración

```bash
# Ejecutar tests
python manage.py test

# Verificar queries problemáticas
python manage.py shell
>>> from gestion.models import *
>>> # Probar queries críticas
```

## Configuración Recomendada en MySQL

### my.ini / my.cnf

```ini
[mysqld]
# Charset
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# SQL Mode (compatible con Django)
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION

# InnoDB (recomendado)
default-storage-engine = InnoDB

# Tamaño de packet (para grandes queries)
max_allowed_packet = 64M

# Timezone
default-time-zone = '-04:00'  # Paraguay

# Performance
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
```

## Checklist de Migración

- [ ] Instalar mysqlclient o PyMySQL
- [ ] Actualizar DATABASES en settings.py
- [ ] Cambiar EXTRACT → ExtractHour/ExtractDay
- [ ] Cambiar .extra() → .annotate() cuando sea posible
- [ ] Exportar datos de PostgreSQL
- [ ] Crear base de datos MySQL
- [ ] Importar schema y datos
- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Probar todas las vistas del POS
- [ ] Probar dashboard y reportes
- [ ] Verificar exportación Excel/PDF
- [ ] Probar API REST completa
- [ ] Ejecutar test suite: `python manage.py test`

## Notas Importantes

1. **Collation:** Usar `utf8mb4_unicode_ci` para soporte completo de caracteres (incluyendo emojis)

2. **Strict Mode:** Mantener SQL strict mode activado para comportamiento consistente

3. **InnoDB:** Preferir InnoDB sobre MyISAM para integridad referencial

4. **Timezone:** Configurar timezone en MySQL para evitar problemas con fechas

5. **Max Connections:** Ajustar `max_connections` según carga esperada

## Ventajas de MySQL para este Proyecto

✅ Ampliamente soportado en hosting compartido
✅ Excelente con MySQL Workbench (mencionado por usuario)
✅ Mejor rendimiento en lecturas simples
✅ Menor consumo de recursos
✅ Más fácil de administrar para equipos pequeños

## Soporte

Si encuentras problemas durante la migración:

1. Verificar versión de MySQL: Mínimo 5.7 o MariaDB 10.2
2. Revisar logs de Django: `DEBUG = True`
3. Verificar charset en base de datos: `SHOW VARIABLES LIKE 'character_set%';`
4. Probar queries directamente en MySQL Workbench

## Referencias

- Django Database Backends: https://docs.djangoproject.com/en/5.2/ref/databases/
- MySQL for Django: https://docs.djangoproject.com/en/5.2/ref/databases/#mysql-notes
- Database Functions: https://docs.djangoproject.com/en/5.2/ref/models/database-functions/
