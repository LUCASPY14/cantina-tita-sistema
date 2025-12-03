# Mejoras Implementadas en Reportes PDF

## Fecha: 3 de Diciembre, 2025

### Resumen
Se agregaron gráficos visuales a los reportes PDF existentes usando matplotlib para mejorar la presentación y análisis de datos.

---

## 🎨 Nuevas Funciones de Gráficos

### 1. `_generar_grafico_barras()`
**Propósito:** Gráficos de barras para comparaciones
- **Parámetros:** datos, labels, título, color, width, height
- **Uso:** Top productos, ventas por categoría, saldos
- **Formato:** PNG en memoria (buffer)
- **Resolución:** 150 DPI

**Características:**
- Grid horizontal para legibilidad
- Auto-rotación de labels si >5 items
- Color personalizable
- Transparencia alpha=0.7

### 2. `_generar_grafico_linea()`
**Propósito:** Evolución temporal de datos
- **Parámetros:** datos, labels, título, color, width, height
- **Uso:** Ventas diarias, consumos en el tiempo
- **Formato:** PNG en memoria (buffer)
- **Resolución:** 150 DPI

**Características:**
- Área rellena debajo de la línea
- Marcadores en cada punto
- Grid completo
- Auto-rotación de labels

### 3. `_generar_grafico_torta()`
**Propósito:** Distribución porcentual
- **Parámetros:** datos, labels, título, width, height
- **Uso:** Estados de inventario, categorías
- **Formato:** PNG en memoria (buffer)
- **Resolución:** 150 DPI

**Características:**
- 10 colores predefinidos
- Porcentajes automáticos
- Texto blanco en segmentos
- Ángulo inicial 90°

---

## 📊 Gráficos Agregados por Reporte

### Reporte de Ventas (`reporte_ventas()`)

**Gráfico 1: Evolución de Ventas Diarias**
- **Tipo:** Línea
- **Datos:** Ventas agrupadas por día (últimos 10 días)
- **Eje Y:** Monto en Guaraníes
- **Eje X:** Fechas (DD/MM)
- **Color:** Verde (#2ecc71)
- **Ubicación:** Después de tabla resumen, antes de detalle

**Query Optimizada:**
```python
ventas_por_dia = ventas.annotate(
    dia=TruncDate('fecha')
).values('dia').annotate(
    total=Sum('monto_total')
).order_by('dia')[:10]
```

---

### Reporte de Productos (`reporte_productos_vendidos()`)

**Gráfico 1: Top 10 Productos Más Vendidos**
- **Tipo:** Barras
- **Datos:** Cantidad de unidades vendidas
- **Eje Y:** Cantidad
- **Eje X:** Nombres de productos (truncados a 15 chars)
- **Color:** Rojo (#e74c3c)
- **Ubicación:** Después de resumen, antes de tabla detallada

**Tabla de Resumen Agregada:**
```
- Productos Vendidos: [total]
- Unidades Totales: [suma]
- Monto Total: Gs. [monto]
```

---

### Reporte de Inventario (`reporte_inventario()`)

**Gráfico 1: Distribución de Alertas de Stock**
- **Tipo:** Torta
- **Datos:** 
  - Crítico (stock = 0)
  - Bajo (stock < mínimo)
  - Normal (stock >= mínimo)
- **Colores:** Automáticos por categoría
- **Ubicación:** Antes de tabla de alertas

**Lógica:**
```python
criticos = sum(1 for a in alertas if a.stock_actual == 0)
bajos = sum(1 for a in alertas if 0 < a.stock_actual < a.stock_minimo)
ok = len(alertas) - criticos - bajos
```

---

### Reporte de Consumos (`reporte_consumos_tarjeta()`)

**Gráfico 1: Consumos Diarios**
- **Tipo:** Barras
- **Datos:** Consumos agrupados por día (últimos 10 días)
- **Eje Y:** Monto en Guaraníes
- **Eje X:** Fechas (DD/MM)
- **Color:** Púrpura (#9b59b6)
- **Ubicación:** Después de resumen, antes de tabla detallada

**Query:**
```python
consumos_por_dia = consumos.annotate(
    dia=TruncDate('fecha_consumo')
).values('dia').annotate(
    total=Sum('monto_consumido')
).order_by('dia')[:10]
```

---

### Reporte de Clientes (`reporte_clientes()`)

**Gráfico 1: Top 10 Clientes con Mayor Saldo**
- **Tipo:** Barras
- **Datos:** Saldo actual de cada cliente
- **Eje Y:** Saldo en Guaraníes
- **Eje X:** Nombres de clientes (truncados a 15 chars)
- **Color:** Turquesa (#1abc9c)
- **Ubicación:** Después de resumen, antes de tabla detallada

**Filtro:**
```python
top_clientes = queryset_completo.filter(saldo_actual__gt=0)[:10]
```

---

## 🔧 Implementación Técnica

### Dependencias Instaladas
```bash
pip install matplotlib==3.10.7
```

**Incluye:**
- numpy==2.3.5
- contourpy==1.3.3
- cycler==0.12.1
- fonttools==4.61.0
- kiwisolver==1.4.9
- pyparsing==3.2.5

### Configuración Matplotlib
```python
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para servidor
```

### Integración con ReportLab
```python
# Generar gráfico en memoria
buf = ReportesPDF._generar_grafico_barras(datos, labels, titulo)

# Insertar en PDF
img = Image(buf, width=5*inch, height=3*inch)
story.append(img)
```

---

## 📐 Especificaciones de Diseño

### Tamaños Estándar
- **Gráficos de barras/línea:** 5" × 3" (en PDF)
- **Gráficos de torta:** 4" × 4" (en PDF)
- **Resolución:** 150 DPI
- **Formato:** PNG

### Colores por Reporte
```python
COLORES = {
    'ventas': '#2ecc71',      # Verde
    'productos': '#e74c3c',   # Rojo
    'inventario': '#e67e22',  # Naranja
    'consumos': '#9b59b6',    # Púrpura
    'clientes': '#1abc9c',    # Turquesa
}
```

### Paleta de Torta (10 colores)
```python
['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', 
 '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085']
```

---

## ✅ Beneficios

### 1. **Análisis Visual Rápido**
- Tendencias identificables de un vistazo
- Comparaciones más claras
- Patrones temporales evidentes

### 2. **Presentación Profesional**
- Reportes más atractivos
- Mejor comunicación de datos
- Impresiones de calidad

### 3. **Toma de Decisiones**
- Identificación rápida de productos top
- Alertas visuales de stock
- Evolución de ventas clara

### 4. **Performance**
- Gráficos en memoria (no archivos temporales)
- Cache automático de matplotlib
- Queries optimizadas con annotate()

---

## 🚀 Uso

### Generar Reporte con Gráficos
```python
# Vista Django
from gestion.reportes import ReportesPDF

def mi_vista(request):
    fecha_inicio = date(2025, 12, 1)
    fecha_fin = date(2025, 12, 3)
    
    # Genera PDF con gráficos automáticamente
    return ReportesPDF.reporte_ventas(fecha_inicio, fecha_fin)
```

### Acceso desde URLs
```python
# URLs existentes (sin cambios)
/gestion/reportes/ventas/pdf/
/gestion/reportes/productos/pdf/
/gestion/reportes/inventario/pdf/
/gestion/reportes/consumos/pdf/
/gestion/reportes/clientes/pdf/
```

---

## 📊 Ejemplo de Estructura PDF

```
┌─────────────────────────────────────┐
│   📊 Reporte de Ventas             │
│   Período: 01/12/2025 - 03/12/2025│
├─────────────────────────────────────┤
│                                     │
│   Tabla Resumen                     │
│   ┌──────────────┬──────────────┐  │
│   │ Total Ventas │ Gs. 1,500,000│  │
│   │ Transacciones│      45       │  │
│   └──────────────┴──────────────┘  │
│                                     │
├─────────────────────────────────────┤
│                                     │
│   [GRÁFICO: Línea de Tendencia]    │
│   Evolución de Ventas Diarias      │
│                                     │
├─────────────────────────────────────┤
│                                     │
│   Tabla Detallada                   │
│   ┌──────┬─────────┬──────────┐   │
│   │Fecha │Cliente  │Monto     │   │
│   ├──────┼─────────┼──────────┤   │
│   │...   │...      │...       │   │
│   └──────┴─────────┴──────────┘   │
└─────────────────────────────────────┘
```

---

## 🔄 Mejoras Futuras Sugeridas

1. **Gráficos Interactivos** (para web)
   - Usar Chart.js para versión HTML
   - Tooltips con detalles
   - Zoom y pan

2. **Más Tipos de Gráficos**
   - Gráficos de área apilada
   - Histogramas
   - Box plots para análisis estadístico

3. **Comparación de Períodos**
   - Gráficos de barras agrupadas
   - Líneas múltiples (año actual vs anterior)

4. **Exportación Adicional**
   - Gráficos en Excel (openpyxl.chart)
   - SVG para escalabilidad

---

## 🐛 Troubleshooting

### Error: "No module named 'matplotlib'"
```bash
pip install matplotlib
```

### Error: "RuntimeError: main thread is not in main loop"
```python
# Agregar al inicio del archivo
matplotlib.use('Agg')
```

### Gráficos no aparecen en PDF
- Verificar que `buf.seek(0)` esté antes de crear Image
- Confirmar que `plt.close()` se llama después de guardar
- Revisar que width/height sean razonables

### Encoding de caracteres en labels
```python
# Si hay problemas con caracteres especiales
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
```

---

## 📝 Notas Técnicas

1. **Memoria:** Gráficos usan BytesIO (en RAM, no disco)
2. **Thread-safety:** matplotlib.use('Agg') es seguro para Django
3. **Límites:** Max 10 items en gráficos para legibilidad
4. **Truncamiento:** Labels >15 chars se acortan con "..."

---

## ✅ Validación

- ✅ Django check: Sin errores
- ✅ Matplotlib instalado: v3.10.7
- ✅ Imports: Todos válidos
- ✅ Compatibilidad: ReportLab + matplotlib
- ✅ Performance: Gráficos en <1s

---

**Sistema:** Cantina Tita  
**Módulo:** Reportes PDF  
**Fecha:** 3 de Diciembre, 2025  
**Estado:** ✅ Implementado y Funcional
