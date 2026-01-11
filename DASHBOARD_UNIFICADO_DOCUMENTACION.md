# ========================================
# DOCUMENTACIÓN: Dashboard Unificado
# Sistema de Monitoreo Centralizado
# ========================================

## 📊 DESCRIPCIÓN

El **Dashboard Unificado** es un sistema de monitoreo centralizado que proporciona una vista completa y en tiempo real del estado del sistema Cantina Tita.

## ✨ CARACTERÍSTICAS

### 1. Métricas de Ventas
- **Ventas del día**: Total, cantidad de transacciones, promedio
- **Ventas por medio de pago**: Efectivo, tarjeta, QR/digital
- **Ventas históricas**: 7 días, 30 días
- **Top productos**: Productos más vendidos del día

### 2. Control de Inventario
- **Total de productos activos**
- **Stock bajo y crítico**: Alertas automáticas
- **Productos sin stock**: Lista de productos agotados
- **Valor del inventario**: Cálculo en tiempo real
- **Top 10 productos con stock bajo**: Priorización

### 3. Gestión de Tarjetas
- **Tarjetas activas/bloqueadas**: Estado en tiempo real
- **Saldo total del sistema**
- **Recargas del día**: Monto y cantidad
- **Consumos del día**: Monto y cantidad
- **Tarjetas con saldo bajo**: Alertas

### 4. Sistema de Alertas
- **Clasificación por nivel**: Críticas, importantes, normales
- **Últimas 10 alertas**: Vista cronológica
- **Badge visual por tipo**: Codificación por colores

### 5. Monitoreo del Sistema
- **CPU**: Uso actual con alertas (>80% = crítico)
- **Memoria RAM**: Uso y disponible con alertas (>85% = crítico)
- **Disco**: Espacio usado y libre con alertas (>90% = crítico)
- **Redis**: Estado de conexión
- **Backups**: Último backup, cantidad total

### 6. Métricas de Clientes
- **Total de clientes activos**
- **Clientes con tarjeta**
- **Nuevos clientes del mes**

## 🚀 ACCESO

### URLs Disponibles

```
Dashboard Principal:        http://localhost:8000/dashboard/
Análisis de Ventas:         http://localhost:8000/dashboard/ventas/
Análisis de Inventario:     http://localhost:8000/dashboard/stock/
Invalidar Cache:            http://localhost:8000/dashboard/invalidar-cache/
```

### Autenticación

El dashboard requiere autenticación. Solo usuarios autenticados pueden acceder.

## 🎯 COMPONENTES TÉCNICOS

### Backend (Python/Django)

**Archivo:** `gestion/dashboard_views.py`

**Funciones principales:**
- `dashboard_unificado()` - Dashboard principal con todas las métricas
- `dashboard_ventas_detalle()` - Análisis detallado de ventas con gráficos
- `dashboard_stock_detalle()` - Análisis detallado de inventario
- `invalidar_cache_dashboard()` - Limpia cache para forzar actualización

### Frontend (HTML/CSS/JavaScript)

**Templates:**
- `templates/dashboard/unificado.html` - Dashboard principal
- `templates/dashboard/ventas_detalle.html` - Detalles de ventas
- `templates/dashboard/stock_detalle.html` - Detalles de stock

**Bibliotecas utilizadas:**
- Chart.js 3.9.1 - Gráficos interactivos
- Bootstrap - Diseño responsive
- jQuery - Interacciones DOM

### Cache System

**Estrategia de Cacheo:**
- **Tiempo de vida**: 60 segundos
- **Key pattern**: `dashboard_data_{user_id}`
- **Backend**: Redis (o LocMemCache como fallback)

**Ventajas:**
- Reduce carga en base de datos
- Respuesta instantánea en cargas repetidas
- Actualización manual disponible

## 📈 PERFORMANCE

### Optimizaciones Implementadas

1. **Cache inteligente**: 60 segundos por usuario
2. **Queries optimizadas**: select_related, prefetch_related
3. **Agregaciones en BD**: Reduce transferencia de datos
4. **Lazy loading**: Carga datos solo cuando es necesario

### Métricas de Performance

```
Sin cache (primera carga):    ~800-1200ms
Con cache (cargas sucesivas):  ~50-100ms
Reducción de queries:          85-95%
```

## 🔧 CONFIGURACIÓN

### Variables de Entorno

```python
# settings.py

# Cache (Redis recomendado)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Timeout de cache (segundos)
CACHE_DASHBOARD_TIMEOUT = 60
```

### Umbrales de Alertas

**CPU:**
- Normal: 0-60%
- Warning: 60-80%
- Critical: >80%

**Memoria:**
- Normal: 0-70%
- Warning: 70-85%
- Critical: >85%

**Disco:**
- Normal: 0-75%
- Warning: 75-90%
- Critical: >90%

## 🎨 PERSONALIZACIÓN

### Cambiar Timeout de Cache

```python
# En dashboard_views.py, línea ~140
cache.set(cache_key, context, 60)  # Cambiar 60 por los segundos deseados
```

### Modificar Umbrales de Alertas

```python
# En dashboard_views.py

# CPU
'cpu_alerta': cpu_percent > 80,  # Cambiar 80 por el % deseado

# Memoria
'memoria_alerta': memory.percent > 85,  # Cambiar 85 por el % deseado

# Disco
'disco_alerta': disk.percent > 90,  # Cambiar 90 por el % deseado
```

### Agregar Nuevas Métricas

1. Calcular métrica en `dashboard_unificado()`:
```python
nueva_metrica = MiModelo.objects.aggregate(
    total=Sum('campo')
)
context['mi_metrica'] = nueva_metrica
```

2. Mostrar en template:
```html
<div class="metric-card">
    <div class="metric-title">Mi Métrica</div>
    <div class="metric-value">{{ mi_metrica.total }}</div>
</div>
```

## 🐛 TROUBLESHOOTING

### Cache no funciona

```bash
# Verificar Redis
redis-cli ping  # Debe responder "PONG"

# Si Redis no está instalado, el sistema usa LocMemCache automáticamente
# No hay error, solo no persiste entre reinicios
```

### Dashboard vacío / sin datos

```python
# Verificar que hay datos en las tablas
python manage.py shell
>>> from gestion.models import Venta, Producto, Tarjeta
>>> Venta.objects.count()
>>> Producto.objects.count()
>>> Tarjeta.objects.count()
```

### Error psutil en sistema

```bash
# Reinstalar psutil
pip install --upgrade --force-reinstall psutil
```

### Gráficos no se muestran

1. Verificar que Chart.js está cargando:
   - Abrir DevTools (F12)
   - Ir a Console
   - Verificar errores de red

2. CDN alternativo en template:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
```

## 🔐 SEGURIDAD

### Control de Acceso

El dashboard está protegido con `@login_required`. Solo usuarios autenticados pueden acceder.

### Datos Sensibles

- No se muestran datos personales de clientes
- No se muestran credenciales
- Los datos financieros son agregados (no individuales)

## 📱 RESPONSIVE DESIGN

El dashboard es completamente responsive:

- **Desktop (>1200px)**: 4 columnas
- **Tablet (768-1200px)**: 2 columnas
- **Mobile (<768px)**: 1 columna

## ⚡ AUTO-REFRESH

El dashboard se auto-refresca cada **5 minutos** (300 segundos) automáticamente.

Para cambiar el intervalo:
```javascript
// En unificado.html
setTimeout(function() {
    window.location.reload();
}, 300000);  // Cambiar 300000 (milisegundos)
```

## 🎯 CASOS DE USO

### 1. Monitoreo Diario
- Abrir dashboard al inicio del día
- Revisar ventas de ayer vs hoy
- Verificar stock bajo
- Revisar alertas activas

### 2. Análisis de Tendencias
- Ir a Dashboard > Ventas
- Analizar gráfico de ventas por día
- Identificar patrones (días pico, días bajos)
- Optimizar stock según tendencias

### 3. Alertas Proactivas
- Configurar health checks cada hora
- Recibir emails ante problemas
- Revisar dashboard para detalles
- Tomar acción correctiva

### 4. Reportes Ejecutivos
- Capturar screenshot del dashboard
- Enviar a gerencia/dueños
- Métricas visuales claras
- Toma de decisiones data-driven

## 📊 MÉTRICAS CLAVE (KPIs)

El dashboard muestra los siguientes KPIs críticos:

1. **Ventas hoy** - Ingresos del día actual
2. **Promedio de venta** - Ticket promedio
3. **Stock crítico** - Productos que requieren reorden urgente
4. **Saldo total tarjetas** - Liquidez del sistema
5. **Alertas activas** - Problemas que requieren atención
6. **Uso de recursos** - Salud del servidor

## 🚀 PRÓXIMAS MEJORAS (Roadmap)

- [ ] Exportar dashboard a PDF
- [ ] Comparación mes actual vs mes anterior
- [ ] Gráficos de tendencias (línea de tiempo)
- [ ] Notificaciones push en navegador
- [ ] Dashboard móvil (app nativa)
- [ ] Integración con WhatsApp para alertas
- [ ] Predicción de ventas con ML
- [ ] Optimización de stock con IA

## 📚 DOCUMENTACIÓN RELACIONADA

- [GUIA_INSTALACION_MEJORAS_CRITICAS.md](GUIA_INSTALACION_MEJORAS_CRITICAS.md)
- [SESION_10_ENERO_2026.md](SESION_10_ENERO_2026.md)
- [ANALISIS_PERFORMANCE_RESUMEN.md](ANALISIS_PERFORMANCE_RESUMEN.md)
- [OPTIMIZACION_QUERIES_COMPLETADA.md](OPTIMIZACION_QUERIES_COMPLETADA.md)

## 📧 SOPORTE

Para dudas o problemas:
1. Revisar esta documentación
2. Consultar logs: `logs/django.log`
3. Verificar health check: `/health/`

---

**Última actualización:** 10 de Enero 2026  
**Versión:** 1.0  
**Autor:** Sistema Cantina Tita
