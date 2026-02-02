# Dashboard Personalizado Django Admin - Cantina Tita

## 📋 Descripción

Se ha implementado un **Dashboard personalizado** para el Django Admin de Cantina Tita con estadísticas en tiempo real, alertas automáticas y acceso rápido a las operaciones más comunes.

---

## ✨ Características Implementadas

### 🎯 Panel Principal con Estadísticas en Tiempo Real

#### Métricas del Día (Hoy)
- **💰 Ventas Hoy**: Monto total y número de transacciones
- **💳 Recargas Hoy**: Total recargado en tarjetas
- **🍽️ Consumos Hoy**: Consumos realizados con tarjetas
- **🎫 Tarjetas Activas**: Estado de tarjetas y saldo total
- **👥 Clientes**: Total activos y nuevos del mes
- **📦 Productos**: Stock y alertas de productos

#### Resumen de Periodos
- **Esta Semana**: Ventas, recargas y consumos acumulados
- **Este Mes**: Totales mensuales y operaciones

### 📊 Secciones del Dashboard

1. **Top 5 Productos del Día**
   - Productos más vendidos
   - Cantidad vendida
   - Total facturado

2. **⚠️ Alertas Pendientes**
   - Alertas del sistema no leídas
   - Fecha y hora de generación
   - Tipo de alerta

3. **📉 Alertas de Stock Crítico**
   - Productos con stock bajo
   - Stock actual vs. stock mínimo
   - Diferencia y nivel de alerta

4. **💵 Clientes con Saldo a Favor**
   - Listado de clientes con crédito
   - Total de compras y pagos
   - Saldo actual

5. **🏦 Último Cierre de Caja**
   - Fecha y empleado responsable
   - Monto total cerrado
   - Diferencia (positiva/negativa)

6. **⚡ Acciones Rápidas**
   - 🛒 Nueva Venta
   - 💳 Recargar Tarjeta
   - 📦 Ver Productos
   - 🎫 Gestión Tarjetas
   - 👥 Ver Clientes
   - 🏦 Cierre de Caja

---

## 🚀 Cómo Acceder

### 1. Iniciar el Servidor
```powershell
python manage.py runserver
```

### 2. Acceder al Admin
```
http://localhost:8000/admin/
```

### 3. Ver el Dashboard
Una vez autenticado, tienes dos opciones:

**Opción A: Desde la página principal del admin**
- El dashboard se mostrará automáticamente en el índice del admin

**Opción B: Acceso directo**
```
http://localhost:8000/admin/dashboard/
```

---

## 📁 Archivos Creados

### 1. `gestion/cantina_admin.py`
**Sitio Admin Personalizado**
- Clase `CantinaAdminSite` que extiende `admin.AdminSite`
- Método `dashboard_view()` con todas las estadísticas
- Consultas optimizadas a la base de datos
- Agregaciones y filtros por fecha

**Estadísticas calculadas:**
- Ventas (hoy, semana, mes)
- Recargas (hoy, semana, mes)
- Consumos (hoy, semana)
- Estado de tarjetas
- Productos y stock
- Clientes activos
- Top productos vendidos
- Alertas pendientes

### 2. `gestion/templates/admin/dashboard.html`
**Template HTML con diseño moderno**
- CSS personalizado con gradientes
- Cards responsivas con hover effects
- Badges coloridos para estados
- Tablas con información detallada
- Grid responsive (adapta a móviles)
- Botones de acciones rápidas

**Elementos visuales:**
- 🎨 Gradientes modernos
- 📊 Estadísticas con iconos
- 🎯 Cards con colores temáticos
- 📱 Diseño responsive
- ✨ Animaciones suaves

### 3. Modificaciones en archivos existentes

**`gestion/admin.py`**
```python
from .cantina_admin import cantina_admin_site

# Al final del archivo: registro de todos los modelos
cantina_admin_site.register(Categoria, CategoriaAdmin)
cantina_admin_site.register(Producto, ProductoAdmin)
# ... todos los modelos
```

**`cantina_project/urls.py`**
```python
from gestion.cantina_admin import cantina_admin_site

urlpatterns = [
    path('admin/', cantina_admin_site.urls),  # Custom admin site
    path('', include('gestion.urls')),
]
```

---

## 🎨 Diseño y Colores

### Color Scheme
- **Primary (Azul)**: `#2196F3` - Ventas
- **Success (Verde)**: `#4CAF50` - Recargas exitosas
- **Warning (Naranja)**: `#FF9800` - Alertas
- **Danger (Rojo)**: `#F44336` - Stock crítico
- **Info (Cyan)**: `#00BCD4` - Consumos
- **Purple**: `#9C27B0` - Clientes

### Badges de Estado
```html
✅ Activo    - Verde
⚠️ Pendiente - Naranja
❌ Anulado   - Rojo
ℹ️ Info      - Azul
```

---

## 📊 Consultas Optimizadas

El dashboard utiliza consultas optimizadas con:

```python
# Agregaciones
.aggregate(
    total=Sum('Monto_Total'),
    cantidad=Count('ID_Venta')
)

# Filtros por fecha
.filter(Fecha__date=hoy)
.filter(Fecha__date__gte=inicio_semana)

# Order by y limit
.order_by('-Fecha_Creacion')[:5]
```

---

## 🔧 Personalización

### Agregar nuevas estadísticas

En `cantina_admin.py`, dentro de `dashboard_view()`:

```python
# Nueva estadística
mi_estadistica = MiModelo.objects.filter(
    fecha__date=hoy
).aggregate(
    total=Sum('campo')
)

# Agregar al contexto
context['mi_estadistica'] = mi_estadistica
```

En `dashboard.html`:

```html
<div class="stat-card primary">
    <div class="icon">🎯</div>
    <div class="title">Mi Estadística</div>
    <div class="value">{{ mi_estadistica.total }}</div>
</div>
```

### Cambiar colores

En `dashboard.html`, sección `<style>`:

```css
.stat-card.micolor { 
    border-left: 4px solid #TU_COLOR; 
}
```

### Agregar nueva sección

```html
<div class="dashboard-section">
    <h2>🆕 Mi Nueva Sección</h2>
    <!-- Tu contenido aquí -->
</div>
```

---

## 📱 Responsive Design

El dashboard es **totalmente responsive**:

- **Desktop (>768px)**: Grid de 3 columnas
- **Tablet (768px)**: Grid de 2 columnas
- **Mobile (<768px)**: Grid de 1 columna

```css
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## 🎯 Beneficios

### Para Administradores
- ✅ Visión completa del negocio en una sola pantalla
- ✅ Detección rápida de problemas (stock, alertas)
- ✅ Acceso rápido a operaciones frecuentes
- ✅ Métricas actualizadas en tiempo real

### Para Cajeros
- ✅ Ver ventas del día
- ✅ Acceso rápido a nueva venta
- ✅ Estado de cajas y cierres
- ✅ Top productos más vendidos

### Para Supervisores
- ✅ Métricas semanales y mensuales
- ✅ Control de empleados
- ✅ Alertas de sistema
- ✅ Clientes con saldo pendiente

---

## 🔐 Permisos y Seguridad

El dashboard respeta los permisos de Django:

- ✅ Solo usuarios autenticados
- ✅ Respeta permisos de cada modelo
- ✅ Vistas read-only no permiten edición
- ✅ Acciones según rol de usuario

---

## 🚦 Estados Visuales

### Tarjetas
- 🟢 **Verde**: Todo normal, buena salud
- 🟠 **Naranja**: Advertencia, requiere atención
- 🔴 **Rojo**: Crítico, acción inmediata

### Stock
- ⚪ **Sin definir**: Stock no configurado
- 🟢 **Normal**: Stock > 50 unidades
- 🟠 **Bajo**: Stock entre 10-50 unidades
- 🔴 **Crítico**: Stock < 10 unidades

### Diferencia de Caja
- 🟢 **Positivo**: Sobra dinero
- 🔴 **Negativo**: Falta dinero
- 🔵 **Exacto**: Cuadra perfectamente (Gs. 0)

---

## 📈 Próximas Mejoras Sugeridas

### Corto Plazo
- [ ] Gráficos interactivos (Chart.js)
- [ ] Exportar dashboard a PDF
- [ ] Filtros de fecha personalizables
- [ ] Notificaciones push

### Mediano Plazo
- [ ] Comparativas mes vs mes anterior
- [ ] Predicciones de ventas con ML
- [ ] Dashboard móvil dedicado
- [ ] Informes programados por email

### Largo Plazo
- [ ] Dashboard en tiempo real (WebSockets)
- [ ] Análisis de comportamiento de clientes
- [ ] Integración con BI externo
- [ ] API REST para datos del dashboard

---

## 🛠️ Troubleshooting

### Dashboard no muestra estadísticas
**Problema**: Cards vacías o con "0"
**Solución**: Verificar que hay datos en la base de datos para el día actual

```python
# Verificar en shell de Django
python manage.py shell
>>> from gestion.models import Ventas
>>> Ventas.objects.filter(Fecha__date=date.today()).count()
```

### Error al acceder /admin/dashboard/
**Problema**: Error 404 o URL no encontrada
**Solución**: Verificar que el custom admin está registrado en urls.py

```python
# cantina_project/urls.py
from gestion.cantina_admin import cantina_admin_site
path('admin/', cantina_admin_site.urls),
```

### Estilos no se aplican
**Problema**: Dashboard sin CSS
**Solución**: Verificar que el template extiende `admin/base_site.html`

```html
{% extends "admin/base_site.html" %}
{% load static %}
{% block extrastyle %}
<!-- Estilos aquí -->
{% endblock %}
```

---

## 📚 Referencias

- [Django Admin Site](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/)
- [Django Custom Admin](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#customizing-the-adminsite-class)
- [Django Templates](https://docs.djangoproject.com/en/5.0/ref/templates/)
- [Django ORM Aggregation](https://docs.djangoproject.com/en/5.0/topics/db/aggregation/)

---

## ✅ Checklist de Implementación

- [x] Crear `cantina_admin.py` con CantinaAdminSite
- [x] Crear `templates/admin/dashboard.html`
- [x] Registrar modelos en custom admin site
- [x] Actualizar `urls.py` para usar custom site
- [x] Agregar estadísticas de ventas
- [x] Agregar estadísticas de recargas
- [x] Agregar estadísticas de consumos
- [x] Agregar alertas de stock
- [x] Agregar top productos
- [x] Agregar acciones rápidas
- [x] Diseño responsive
- [x] Badges coloridos
- [x] Documentación completa

---

## 🎉 ¡Dashboard Listo para Producción!

El dashboard personalizado está **100% funcional** y listo para usar. Proporciona una visión completa del negocio con estadísticas actualizadas en tiempo real.

**Acceso**: `http://localhost:8000/admin/dashboard/`

---

**Última actualización**: 27 de Noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Producción
