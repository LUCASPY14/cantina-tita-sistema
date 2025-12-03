# 📚 Sistema de Cuenta Corriente - Documentación

## 🎯 Introducción

El sistema de cuenta corriente permite gestionar las deudas y pagos de clientes y proveedores de manera automatizada, eliminando la necesidad de llevar un registro manual.

---

## 🏗️ Arquitectura del Sistema

### Sistema Actual (Implementado)

```
┌─────────────────────────────────────────────────────────┐
│                    CUENTA CORRIENTE                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CLIENTES (Ventas)          PROVEEDORES (Compras)       │
│  ┌─────────────────┐        ┌─────────────────┐        │
│  │ Tabla: ventas   │        │ Tabla: compras  │        │
│  │                 │        │                 │        │
│  │ - saldo_pendiente│        │ - saldo_pendiente│       │
│  │ - estado_pago   │        │ - estado_pago   │        │
│  └─────────────────┘        └─────────────────┘        │
│         │                            │                  │
│         ▼                            ▼                  │
│  ┌─────────────────┐        ┌─────────────────┐        │
│  │ pagos_venta     │        │ pagos_proveedor │        │
│  │ aplicacion_     │        │                 │        │
│  │ pagos_ventas    │        │                 │        │
│  └─────────────────┘        └─────────────────┘        │
│                                                          │
│  [Triggers Automáticos en Base de Datos]                │
│  - Actualización automática de saldo_pendiente          │
│  - Actualización automática de estado_pago              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Campos Principales

### 1. `estado_pago` (CharField)

**Valores válidos** (siempre en MAYÚSCULAS):

| Estado | Descripción | Condición |
|--------|-------------|-----------|
| `PENDIENTE` | Sin pagos aplicados | `saldo_pendiente == monto_total` |
| `PARCIAL` | Pago parcial | `0 < saldo_pendiente < monto_total` |
| `PAGADA` | Completamente pagada | `saldo_pendiente == 0` |
| `ANULADO` | Operación anulada | No se considera en cuentas |

**⚠️ Importante:** Siempre usar MAYÚSCULAS en queries:
```python
✅ estado_pago__in=['PENDIENTE', 'PARCIAL']
❌ estado_pago__in=['Pendiente', 'Parcial']
```

### 2. `saldo_pendiente`

**Tipo de dato:**
- **Ventas**: `BigIntegerField` (entero, en guaraníes)
- **Compras**: `DecimalField` (decimal, max_digits=12, decimal_places=2)

**Lógica:**
- Al crear una venta/compra: `saldo_pendiente = total`
- Al aplicar un pago: `saldo_pendiente -= monto_pago`
- Cuando `saldo_pendiente == 0`: `estado_pago = 'PAGADA'`

---

## 🔄 Flujo de Operaciones

### Crear una Venta

```python
from gestion.models import Ventas

venta = Ventas.objects.create(
    nro_factura_venta=1001,
    id_cliente=cliente,
    id_tipo_pago=tipo_pago,
    id_empleado_cajero=empleado,
    fecha=timezone.now(),
    monto_total=100000,
    saldo_pendiente=100000,  # Igual al total
    estado_pago='PENDIENTE',  # Estado inicial
    estado='PROCESADO',
    tipo_venta='Venta Directa'
)
```

### Aplicar un Pago

```python
from gestion.models import PagosVenta, AplicacionPagosVentas

# 1. Crear el pago
pago = PagosVenta.objects.create(
    id_cliente=cliente,
    monto_pago=50000,
    fecha_pago=timezone.now(),
    id_medio_pago=medio_pago,
    observaciones='Pago parcial'
)

# 2. Aplicar a la venta
aplicacion = AplicacionPagosVentas.objects.create(
    id_pago_venta=pago,
    id_venta=venta,
    monto_aplicado=50000
)

# 3. Los triggers actualizan automáticamente:
# - venta.saldo_pendiente = 50000
# - venta.estado_pago = 'PARCIAL'
```

---

## 📝 Queries Comunes

### Obtener Deuda de Clientes

```python
from django.db.models import Sum, Q

# Todas las ventas pendientes
ventas_pendientes = Ventas.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL']
)

# Total de deuda
total_deuda = Ventas.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL']
).aggregate(total=Sum('saldo_pendiente'))['total'] or 0

# Deuda por cliente
from django.db.models import Count

deuda_por_cliente = Ventas.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL'],
    saldo_pendiente__gt=0
).values(
    'id_cliente__nombres',
    'id_cliente__apellidos'
).annotate(
    saldo_total=Sum('saldo_pendiente'),
    cantidad_ventas=Count('id_venta')
).order_by('-saldo_total')
```

### Obtener Deuda con Proveedores

```python
# Todas las compras pendientes
compras_pendientes = Compras.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL']
)

# Total de deuda
total_deuda = Compras.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL']
).aggregate(total=Sum('saldo_pendiente'))['total'] or 0

# Deuda por proveedor
deuda_por_proveedor = Compras.objects.filter(
    Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL'),
    saldo_pendiente__gt=0
).values(
    'id_proveedor__id_proveedor',
    'id_proveedor__razon_social'
).annotate(
    saldo=Sum('saldo_pendiente'),
    cantidad_compras=Count('id_compra')
).order_by('-saldo')
```

---

## 🎨 Vistas Disponibles

### 1. Dashboard de Compras (`compras_dashboard_view`)

**URL:** `/pos/compras-dashboard/`

**Contexto:**
```python
{
    'compras_recientes': QuerySet,  # Últimas 10 compras
    'total_mes': Decimal,           # Total comprado en el mes
    'cantidad_mes': int,            # Cantidad de compras del mes
    'compras_pendientes': int,      # Cantidad pendientes de pago
    'deuda_total': Decimal          # Suma de saldos pendientes
}
```

### 2. Deuda con Proveedores (`deuda_proveedores_view`)

**URL:** `/pos/deuda-proveedores/`

**Contexto:**
```python
{
    'deudas': QuerySet,  # Compras agrupadas por proveedor
    'total_deuda': Decimal
}
```

**Estructura de `deudas`:**
```python
[
    {
        'id_proveedor__id_proveedor': 1,
        'id_proveedor__razon_social': 'Proveedor A',
        'saldo': Decimal('500000.00'),
        'cantidad_compras': 5
    },
    ...
]
```

### 3. Cuenta Corriente Cliente (`cuenta_corriente_view`)

**URL:** `/pos/cuenta-corriente/`

Muestra listado de clientes con límite de crédito y estado.

### 4. Detalle Cliente (`cc_detalle_view`)

**URL:** `/pos/cc-detalle/<int:cliente_id>/`

Muestra ventas y recargas de un cliente específico.

---

## 📊 Reportes

### Generar Reporte PDF

```python
from gestion.reportes import ReportesPDF

# Reporte de clientes
response = ReportesPDF.reporte_cta_corriente_cliente(
    id_cliente=1,           # Opcional: None = todos
    fecha_inicio='2025-01-01',  # Opcional
    fecha_fin='2025-12-31'      # Opcional
)

# Reporte de proveedores
response = ReportesPDF.reporte_cta_corriente_proveedor(
    id_proveedor=1,
    fecha_inicio='2025-01-01',
    fecha_fin='2025-12-31'
)
```

### Generar Reporte Excel

```python
from gestion.reportes import ReportesExcel

# Reporte de clientes
response = ReportesExcel.reporte_cta_corriente_cliente(
    id_cliente=1,
    fecha_inicio='2025-01-01',
    fecha_fin='2025-12-31'
)

# Reporte de proveedores
response = ReportesExcel.reporte_cta_corriente_proveedor(
    id_proveedor=1,
    fecha_inicio='2025-01-01',
    fecha_fin='2025-12-31'
)
```

---

## ⚙️ Triggers de Base de Datos

El sistema utiliza 4 triggers en MySQL que actualizan automáticamente los campos:

### 1. `trg_ventas_insert`
Ejecuta al insertar una venta:
- Establece `saldo_pendiente = monto_total`
- Establece `estado_pago = 'PENDIENTE'`

### 2. `trg_aplicacion_pagos_insert`
Ejecuta al aplicar un pago a una venta:
- Resta el monto aplicado de `saldo_pendiente`
- Actualiza `estado_pago` según el saldo

### 3. `trg_compras_insert`
Ejecuta al insertar una compra:
- Establece `saldo_pendiente = total`
- Establece `estado_pago = 'PENDIENTE'`

### 4. `trg_pagos_proveedor_insert`
Ejecuta al aplicar un pago a una compra:
- Resta el monto aplicado de `saldo_pendiente`
- Actualiza `estado_pago` según el saldo

---

## 🔒 Validaciones

### Validaciones en el Modelo

```python
class Ventas(models.Model):
    # ... campos ...
    
    def clean(self):
        """Validaciones de negocio"""
        from django.core.exceptions import ValidationError
        
        # Saldo no puede ser mayor al total
        if self.saldo_pendiente > self.monto_total:
            raise ValidationError({
                'saldo_pendiente': 'El saldo no puede exceder el total'
            })
        
        # PAGADA debe tener saldo 0
        if self.estado_pago == 'PAGADA' and self.saldo_pendiente > 0:
            raise ValidationError({
                'estado_pago': 'Una venta PAGADA debe tener saldo 0'
            })
```

### Validaciones Recomendadas en Vistas

```python
def aplicar_pago(venta, monto):
    """Aplicar pago a una venta"""
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")
    
    if monto > venta.saldo_pendiente:
        raise ValueError("El monto excede el saldo pendiente")
    
    # Aplicar pago...
```

---

## 📈 Optimización de Queries

### Usar `select_related()` para Foreign Keys

```python
# ❌ Malo (N+1 queries)
ventas = Ventas.objects.filter(estado_pago='PENDIENTE')
for venta in ventas:
    print(venta.id_cliente.nombres)  # Query adicional

# ✅ Bueno (1 query)
ventas = Ventas.objects.filter(
    estado_pago='PENDIENTE'
).select_related('id_cliente', 'id_empleado_cajero')

for venta in ventas:
    print(venta.id_cliente.nombres)  # Sin query adicional
```

### Usar `prefetch_related()` para Relaciones Inversas

```python
# ✅ Optimizado
clientes = Cliente.objects.prefetch_related('ventas').all()
for cliente in clientes:
    for venta in cliente.ventas.all():
        print(venta.monto_total)
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python manage.py test gestion

# Tests específicos
python manage.py test gestion.tests.VentasModelTest

# Con verbosidad
python manage.py test gestion --verbosity=2
```

### Cobertura de Tests

```bash
# Instalar coverage
pip install coverage

# Ejecutar con coverage
coverage run --source='.' manage.py test gestion
coverage report
coverage html  # Genera reporte HTML
```

---

## 🔍 Troubleshooting

### Problema: Saldo inconsistente

**Síntomas:** `saldo_pendiente` no coincide con pagos aplicados

**Solución:**
```python
from django.db.models import Sum
from gestion.models import Ventas, AplicacionPagosVentas

venta = Ventas.objects.get(id_venta=123)

# Calcular pagos aplicados
pagos_aplicados = AplicacionPagosVentas.objects.filter(
    id_venta=venta
).aggregate(total=Sum('monto_aplicado'))['total'] or 0

# Recalcular saldo
saldo_correcto = venta.monto_total - pagos_aplicados
print(f"Saldo actual: {venta.saldo_pendiente}")
print(f"Saldo correcto: {saldo_correcto}")

# Corregir si es necesario
if venta.saldo_pendiente != saldo_correcto:
    venta.saldo_pendiente = saldo_correcto
    venta.save()
```

### Problema: Estado no actualiza automáticamente

**Causa probable:** Triggers deshabilitados o no existen

**Verificación:**
```sql
-- En MySQL
SHOW TRIGGERS WHERE `Table` = 'ventas';
SHOW TRIGGERS WHERE `Table` = 'compras';
```

---

## 📚 Referencias

- **Modelos:** `gestion/models.py`
- **Vistas:** `gestion/pos_views.py`
- **Reportes:** `gestion/reportes.py`
- **Tests:** `gestion/tests.py`
- **Estándares:** `docs/ESTANDARES_CODIGO.md`

---

## 🤝 Contribuir

Al trabajar con el sistema de cuenta corriente:

1. ✅ Usar siempre MAYÚSCULAS para `estado_pago`
2. ✅ Validar que `saldo_pendiente <= monto_total`
3. ✅ Usar `select_related()` para optimizar queries
4. ✅ Escribir tests para cambios importantes
5. ✅ Documentar funciones con docstrings

---

**Última actualización:** 2 de diciembre de 2025  
**Versión del sistema:** 2.0
