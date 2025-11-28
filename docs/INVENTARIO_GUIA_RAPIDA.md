# Guía Rápida - Módulo de Inventario

## 🚀 Acceso Rápido

### URLs Principales:
```
Dashboard:      http://127.0.0.1:8000/pos/inventario/
Productos:      http://127.0.0.1:8000/pos/inventario/productos/
Alertas:        http://127.0.0.1:8000/pos/inventario/alertas/
Ajustar Stock:  http://127.0.0.1:8000/pos/inventario/ajuste/
Kardex:         http://127.0.0.1:8000/pos/inventario/kardex/<id>/
```

### Desde el Menú:
1. Click en el avatar (arriba derecha)
2. Seleccionar "📦 Inventario"

---

## 📋 Características Principales

### 1. Dashboard
**¿Qué muestra?**
- Total de productos activos
- Productos con stock normal
- Productos con stock bajo
- Productos sin stock
- Top 10 más vendidos (30 días)
- Stock por categoría

**Acciones rápidas:**
- Ver listado completo
- Ajustar stock
- Ver alertas
- Filtrar stock crítico

### 2. Listado de Productos
**Filtros disponibles:**
- 🔍 Búsqueda por código o descripción
- 📂 Categoría
- 📊 Estado de stock (normal/bajo/sin stock)

**Información mostrada:**
- Código del producto
- Descripción
- Categoría
- Stock actual
- Stock mínimo
- Estado (con badge de color)

**Acciones:**
- 📋 Ver kardex completo

### 3. Sistema de Alertas
**Tres niveles:**

🚨 **CRÍTICO** (Rojo con animación)
- Stock < 50% del mínimo
- Requiere atención INMEDIATA

❌ **SIN STOCK** (Rojo)
- Stock = 0 o negativo
- Requiere reposición urgente

⚠️ **STOCK BAJO** (Amarillo)
- Stock < mínimo configurado
- Requiere planificación de compra

**Información detallada:**
- Código y descripción
- Categoría
- Stock actual vs mínimo
- % del mínimo
- Diferencia a reponer

**Acciones rápidas:**
- Ver kardex del producto
- Ajustar stock directamente

### 4. Kardex de Producto
**Historial completo de movimientos:**
- Fecha y hora
- Tipo (Entrada/Salida/Ajuste)
- Descripción
- Cantidad
- Empleado responsable

**Filtros:**
- Rango de fechas (desde/hasta)

**Resumen:**
- Total entradas
- Total salidas
- Saldo actual

**Funciones:**
- 🖨️ Imprimir (optimizado para papel)

### 5. Ajuste de Inventario
**Pasos:**

1️⃣ **Seleccionar producto**
   - Dropdown con búsqueda
   - Muestra código y descripción

2️⃣ **Elegir tipo de ajuste**
   - ➕ Sumar: Para entradas de mercadería
   - ➖ Restar: Para mermas o ajustes

3️⃣ **Ingresar cantidad**
   - Vista previa en tiempo real
   - Alerta si quedará negativo

4️⃣ **Justificar**
   - Motivo obligatorio (mín. 10 caracteres)
   - Explicar razón del ajuste

5️⃣ **Confirmar**
   - Confirmación adicional si quedará negativo
   - Actualización inmediata

---

## 🎯 Casos de Uso

### Caso 1: Recepción de Mercadería
**Escenario:** Llegó una compra del proveedor

**Pasos:**
1. Ir a "Ajustar Stock"
2. Seleccionar el producto
3. Tipo: ➕ Sumar
4. Cantidad: Según factura
5. Motivo: "Recepción orden de compra #123"
6. Confirmar

**Resultado:** Stock actualizado + registro en kardex

### Caso 2: Merma o Pérdida
**Escenario:** Producto vencido o dañado

**Pasos:**
1. Ir a "Ajustar Stock"
2. Seleccionar el producto
3. Tipo: ➖ Restar
4. Cantidad: Unidades perdidas
5. Motivo: "Producto vencido - fecha XX/XX/XXXX"
6. Confirmar

**Resultado:** Stock descontado + trazabilidad

### Caso 3: Inventario Físico
**Escenario:** Conteo físico no coincide con sistema

**Pasos:**
1. Realizar conteo físico
2. Comparar con sistema
3. Por cada diferencia:
   - Ir a "Ajustar Stock"
   - Sumar o restar según corresponda
   - Motivo: "Ajuste por inventario físico DD/MM/YYYY"

**Resultado:** Sistema sincronizado con realidad

### Caso 4: Revisar Stock Bajo
**Escenario:** Planificación de compras

**Pasos:**
1. Ir a "Alertas" o Dashboard
2. Revisar productos con ⚠️ o ❌
3. Para cada uno:
   - Click en "Ver Kardex"
   - Analizar consumo histórico
   - Determinar cantidad a comprar
4. Realizar orden de compra

**Resultado:** Lista de compras basada en datos reales

---

## ⚙️ Configuración

### Stock Mínimo
**¿Dónde se configura?**
- En el modelo `Producto`, campo `stock_minimo`

**¿Para qué sirve?**
- Define el nivel de alerta
- Cuando stock_actual < stock_minimo → alerta ⚠️
- Cuando stock_actual < (stock_minimo * 0.5) → alerta 🚨

**Recomendación:**
- Basarse en consumo promedio semanal
- Considerar tiempo de reposición
- Ajustar según estacionalidad

### Permite Stock Negativo
**Campo:** `permite_stock_negativo` en Producto

**Si es True:**
- Permite ventas aunque no haya stock
- Útil para productos bajo pedido

**Si es False:**
- Bloquea ventas si no hay stock
- Sistema estándar

---

## 📊 Interpretación de Datos

### Dashboard - Productos Más Vendidos
**Utilidad:**
- Identificar productos estrella
- Asegurar disponibilidad
- Negociar mejores precios por volumen

**Ejemplo:**
```
1. Coca Cola 500ml    - 1,250 unidades
2. Empanadas          -   980 unidades
3. Jugo Natural       -   750 unidades
```
**Acción:** Mantener stock alto de estos productos

### Stock por Categoría
**Utilidad:**
- Ver distribución del inventario
- Identificar categorías con más rotación
- Planificar espacio de almacenamiento

**Ejemplo:**
```
Bebidas:       500 unidades (25 productos)
Snacks:        300 unidades (15 productos)
Almuerzo:      200 unidades (10 productos)
```

### Kardex - Análisis de Movimientos
**Utilidad:**
- Ver patrón de consumo
- Detectar anomalías
- Calcular rotación

**Ejemplo de análisis:**
```
Producto: Agua Mineral 500ml
Últimos 30 días:
- Total salidas: 500 unidades
- Promedio diario: 16.6 unidades
- Stock actual: 50 unidades
- Autonomía: ~3 días
```
**Acción:** Reponer pronto (stock para 3 días)

---

## ⚠️ Alertas Comunes

### "No se encontraron productos"
**Causas:**
- Filtros muy restrictivos
- No hay productos activos
- Categoría sin productos

**Solución:**
- Limpiar filtros (click en ✖️)
- Verificar que productos estén activos
- Revisar configuración de categorías

### "Stock quedará negativo"
**Cuándo aparece:**
- Al restar más de lo que hay
- Es una ADVERTENCIA, no un error

**Opciones:**
- Cancelar y verificar conteo
- Confirmar si es correcto (permite negativos)

### "Motivo muy corto"
**Causa:**
- Menos de 10 caracteres en justificación

**Solución:**
- Escribir descripción más detallada
- Ejemplo: En lugar de "error", escribir "Error en conteo inicial - corrección"

---

## 💡 Buenas Prácticas

### 1. Justificaciones Claras
❌ Malo: "ajuste"
✅ Bueno: "Ajuste por inventario físico 20/01/2025 - diferencia detectada en conteo"

### 2. Revisión Regular de Alertas
- Diario: Revisar productos sin stock
- Semanal: Revisar productos con stock bajo
- Mensual: Análisis de rotación

### 3. Kardex como Auditoría
- Revisar movimientos sospechosos
- Verificar coherencia con ventas
- Documentar hallazgos

### 4. Actualización de Stock Mínimo
- Revisar trimestralmente
- Ajustar según estacionalidad
- Considerar promociones

### 5. Documentación de Ajustes
- Siempre explicar el "por qué"
- Referenciar documentos (facturas, actas)
- Incluir fecha y responsable

---

## 🔍 Troubleshooting

### Problema: Stock no actualiza
**Posibles causas:**
1. Error de conexión
2. Producto sin registro en StockUnico
3. Permisos insuficientes

**Verificación:**
1. Revisar consola del navegador (F12)
2. Verificar que producto tenga stock asociado
3. Confirmar sesión activa

### Problema: Alertas no aparecen
**Posibles causas:**
1. Stock mínimo no configurado
2. Productos inactivos
3. Filtros aplicados

**Verificación:**
1. Revisar campo stock_minimo del producto
2. Verificar campo activo = True
3. Limpiar filtros

### Problema: Kardex vacío
**Posibles causas:**
1. Producto nuevo sin movimientos
2. Filtro de fecha demasiado restrictivo
3. No hay ventas del producto

**Verificación:**
1. Revisar rango de fechas
2. Ampliar período
3. Verificar si hubo ventas realmente

---

## 📞 Soporte

### Documentación Completa:
- `docs/INVENTARIO_AVANZADO.md` - 650+ líneas de documentación técnica

### Archivos de Código:
- `gestion/pos_views.py` - Vistas backend (líneas 1587-1912)
- `templates/pos/inventario_*.html` - 5 templates

### Rutas:
- Definidas en `gestion/pos_urls.py`

---

**Versión:** 1.0.0  
**Última actualización:** 20/01/2025  
**Autor:** Sistema POS - Cantina Tita
