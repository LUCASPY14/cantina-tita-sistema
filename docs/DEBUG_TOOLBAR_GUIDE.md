# Guía de Django Debug Toolbar

## ✅ Instalación Completada

Django Debug Toolbar ha sido instalado y configurado exitosamente en el proyecto.

## 📋 Configuración Aplicada

### 1. INSTALLED_APPS (settings.py)
```python
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
    # ...
]
```

### 2. MIDDLEWARE (settings.py)
```python
MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # Al final
]
```

### 3. INTERNAL_IPS (settings.py)
```python
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]
```

### 4. URLs (urls.py)
```python
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
```

## 🚀 Cómo Usar

### Iniciar el servidor de desarrollo:
```bash
python manage.py runserver
```

### Acceder a cualquier vista HTML:
```
http://127.0.0.1:8000/pos/venta/
http://127.0.0.1:8000/reportes/ventas/
http://127.0.0.1:8000/admin/
```

### Usar la barra de herramientas:
1. **Aparece automáticamente** en el lado derecho de la página
2. Haz clic en las pestañas para ver información detallada
3. Pestañas principales:
   - **SQL**: Ver todas las queries ejecutadas
   - **Time**: Medir tiempo de ejecución
   - **Templates**: Ver templates renderizados
   - **Cache**: Información de caché
   - **Signals**: Señales de Django disparadas
   - **Logging**: Logs del request

## 🔍 Analizar Queries SQL

### Panel SQL:
- Muestra **todas las queries** ejecutadas en el request
- Indica **queries duplicadas** (N+1 problem)
- Muestra **tiempo de ejecución** de cada query
- Permite **ver el EXPLAIN** de cada query

### Identificar problemas:
```
🔴 Señales de alerta:
- Más de 50 queries por página
- Queries duplicadas (mismo SQL repetido)
- Queries lentas (>100ms)
- SELECT con muchas columnas sin usar
```

### Ejemplo de análisis:
```python
# ❌ MAL - N+1 problem (100 queries)
productos = Producto.objects.all()
for p in productos:
    print(p.categoria.nombre)  # Query por cada producto

# ✅ BIEN - select_related (2 queries)
productos = Producto.objects.select_related('categoria')
for p in productos:
    print(p.categoria.nombre)  # Sin query adicional
```

## 📊 Métricas Importantes

### Queries por Vista:
- **< 10 queries**: Excelente ✅
- **10-30 queries**: Aceptable ⚠️
- **30-50 queries**: Mejorar 🔶
- **> 50 queries**: Optimizar urgente 🔴

### Tiempo de Respuesta:
- **< 100ms**: Rápido ✅
- **100-300ms**: Aceptable ⚠️
- **300-500ms**: Lento 🔶
- **> 500ms**: Muy lento 🔴

## 🛠️ Optimizaciones Comunes

### 1. Relaciones ForeignKey (select_related)
```python
# Antes: N+1 queries
ventas = Venta.objects.all()

# Después: 1 query
ventas = Venta.objects.select_related('cliente', 'empleado')
```

### 2. Relaciones ManyToMany/Reverse (prefetch_related)
```python
# Antes: N+1 queries
ventas = Venta.objects.all()
for v in ventas:
    print(v.detalle_venta.all())

# Después: 2 queries
ventas = Venta.objects.prefetch_related('detalle_venta')
for v in ventas:
    print(v.detalle_venta.all())
```

### 3. Agregaciones (annotate)
```python
# Antes: 1 query por venta para calcular total
ventas = Venta.objects.all()
for v in ventas:
    total = sum([d.subtotal for d in v.detalle_venta.all()])

# Después: 1 query con cálculo en DB
from django.db.models import Sum
ventas = Venta.objects.annotate(
    total=Sum('detalle_venta__subtotal')
)
```

### 4. Filtros en Prefetch (Prefetch object)
```python
from django.db.models import Prefetch

# Solo cargar detalles con cantidad > 1
ventas = Venta.objects.prefetch_related(
    Prefetch(
        'detalle_venta',
        queryset=DetalleVenta.objects.filter(cantidad__gt=1)
    )
)
```

## 📈 Monitoreo Continuo

### Vistas críticas a monitorear:
1. **POS - Punto de Venta** (`/pos/venta/`)
   - Esperado: < 15 queries, < 200ms
   
2. **Cuenta Corriente Unificada** (`/pos/cuenta-corriente-unificada/<id>/`)
   - Esperado: < 25 queries, < 300ms
   
3. **Reportes de Ventas** (`/reportes/ventas/`)
   - Esperado: < 30 queries, < 400ms
   
4. **API - Lista de Productos** (`/api/v1/productos/`)
   - Esperado: < 10 queries, < 150ms

### Procedimiento de revisión:
```
1. Navegar a la vista
2. Abrir Debug Toolbar
3. Revisar panel SQL:
   - ¿Cuántas queries?
   - ¿Hay duplicadas?
   - ¿Alguna lenta (>100ms)?
4. Si hay problemas:
   - Copiar la query problemática
   - Ejecutar EXPLAIN en MySQL
   - Aplicar select_related/prefetch_related
   - Agregar índices si es necesario
```

## 🔧 Desactivar en Producción

**IMPORTANTE**: Debug Toolbar solo debe estar activo en desarrollo.

### La configuración actual es segura:
```python
# settings.py
DEBUG = True  # False en producción

# urls.py
if settings.DEBUG:  # Solo se carga si DEBUG=True
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
```

### Verificar antes de deploy:
```bash
# Revisar que DEBUG=False en producción
grep "DEBUG = " cantina_project/settings.py
```

## 📚 Recursos Adicionales

- **Documentación oficial**: https://django-debug-toolbar.readthedocs.io/
- **Query optimization**: https://docs.djangoproject.com/en/5.2/topics/db/optimization/
- **EXPLAIN MySQL**: https://dev.mysql.com/doc/refman/8.0/en/explain.html

## 🎯 Próximos Pasos

1. ✅ Django Debug Toolbar instalado
2. ⏭️ Ejecutar servidor y verificar toolbar en navegador
3. ⏭️ Revisar queries en vistas principales
4. ⏭️ Documentar queries lentas con EXPLAIN
5. ⏭️ Programar revisión trimestral de índices
