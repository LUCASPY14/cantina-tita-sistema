# 📋 ESTÁNDARES DE CÓDIGO - CANTINA TITA

## 🎯 Valores de Campo `estado_pago`

### ✅ ESTÁNDAR DEFINIDO: MAYÚSCULAS

Todos los valores del campo `estado_pago` (en modelos `Ventas` y `Compras`) deben usarse en **MAYÚSCULAS** para coincidir con la base de datos.

#### Valores Válidos:

```python
# ✅ CORRECTO - Usar MAYÚSCULAS
estado_pago__in=['PENDIENTE', 'PARCIAL', 'PAGADA']
estado_pago='PENDIENTE'
estado_pago='PAGADA'

# ❌ INCORRECTO - No usar minúsculas
estado_pago__in=['Pendiente', 'Parcial', 'Pagada']  # ❌
estado_pago='pendiente'  # ❌
```

#### Estados Disponibles:

| Estado | Descripción | Uso |
|--------|-------------|-----|
| `PENDIENTE` | Sin pagos aplicados | Saldo pendiente = Total |
| `PARCIAL` | Pago parcial aplicado | 0 < Saldo pendiente < Total |
| `PAGADA` | Completamente pagada | Saldo pendiente = 0 |
| `ANULADO` | Operación anulada | No se considera en cuentas |

---

## 🔍 Ejemplos de Uso

### Queries en Vistas:

```python
# Obtener ventas pendientes o parciales
ventas_pendientes = Ventas.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL']
)

# Obtener solo ventas pagadas
ventas_pagadas = Ventas.objects.filter(
    estado_pago='PAGADA'
)

# Query con Q objects
from django.db.models import Q
deudas = Compras.objects.filter(
    Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL'),
    saldo_pendiente__gt=0
)
```

### En Reportes:

```python
# ReportesPDF
ventas = Ventas.objects.filter(
    estado_pago__in=['PENDIENTE', 'PARCIAL']
).select_related('id_cliente')
```

### En Templates:

```django
{% if venta.estado_pago == 'PENDIENTE' %}
    <span class="badge badge-error">Pendiente</span>
{% elif venta.estado_pago == 'PARCIAL' %}
    <span class="badge badge-warning">Parcial</span>
{% elif venta.estado_pago == 'PAGADA' %}
    <span class="badge badge-success">Pagada</span>
{% endif %}
```

---

## 🔧 Campos Relacionados

### `saldo_pendiente`

- **Tipo**: `BigIntegerField` (Ventas), `DecimalField` (Compras)
- **Relación con estado_pago**:
  - `PENDIENTE`: `saldo_pendiente == monto_total`
  - `PARCIAL`: `0 < saldo_pendiente < monto_total`
  - `PAGADA`: `saldo_pendiente == 0`

### Validaciones Recomendadas:

```python
# En el modelo
def clean(self):
    if self.estado_pago == 'PAGADA' and self.saldo_pendiente > 0:
        raise ValidationError(
            'Una venta PAGADA no puede tener saldo pendiente'
        )
    
    if self.estado_pago == 'PENDIENTE' and self.saldo_pendiente != self.monto_total:
        raise ValidationError(
            'Una venta PENDIENTE debe tener saldo igual al total'
        )
```

---

## 📊 Definición en Modelos

### Modelo Ventas:

```python
class Ventas(models.Model):
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=[
            ('PENDIENTE', 'Pendiente'), 
            ('PARCIAL', 'Parcial'), 
            ('PAGADA', 'Pagada')
        ],
        default='PENDIENTE'
    )
    saldo_pendiente = models.BigIntegerField(
        db_column='Saldo_Pendiente', 
        blank=True, 
        null=True
    )
```

### Modelo Compras:

```python
class Compras(models.Model):
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('PARCIAL', 'Parcial'),
            ('PAGADA', 'Pagada')
        ],
        default='PENDIENTE'
    )
    saldo_pendiente = models.DecimalField(
        db_column='Saldo_Pendiente',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
```

---

## 🎯 Razón del Estándar

### ¿Por qué MAYÚSCULAS?

1. **Coincide con la Base de Datos**: Los valores en la BD están en mayúsculas
2. **Consistencia**: Un solo estándar en todo el código
3. **Evita Bugs**: No hay problemas de case-sensitivity
4. **Claridad**: Más fácil identificar constantes

### Migración de Código Legacy:

```python
# ❌ ANTES (inconsistente)
estado_pago__in=['Pendiente', 'Parcial']  # Minúsculas
estado_pago='PENDIENTE'  # Mayúsculas
estado_pago__iexact='pendiente'  # Case-insensitive

# ✅ DESPUÉS (consistente)
estado_pago__in=['PENDIENTE', 'PARCIAL']  # Siempre mayúsculas
estado_pago='PENDIENTE'
```

---

## 🧪 Testing

### Test de Validación:

```python
from django.test import TestCase
from gestion.models import Ventas

class EstadoPagoTests(TestCase):
    def test_valores_mayusculas(self):
        """Verificar que estado_pago usa MAYÚSCULAS"""
        venta = Ventas.objects.create(
            estado_pago='PENDIENTE',
            saldo_pendiente=10000,
            monto_total=10000
        )
        
        self.assertEqual(venta.estado_pago, 'PENDIENTE')
        
        # Verificar query con mayúsculas
        pendientes = Ventas.objects.filter(
            estado_pago='PENDIENTE'
        )
        self.assertIn(venta, pendientes)
```

---

## 📝 Checklist para Desarrolladores

Antes de hacer commit, verificar:

- [ ] Todos los valores de `estado_pago` en **MAYÚSCULAS**
- [ ] Queries usan `['PENDIENTE', 'PARCIAL', 'PAGADA']`
- [ ] Templates comparan con valores en mayúsculas
- [ ] Comentarios actualizados con el estándar
- [ ] Tests pasan con los nuevos valores

---

## 🔄 Actualizado

**Fecha**: 2 de diciembre de 2025  
**Versión**: 1.0  
**Responsable**: Equipo de Desarrollo

---

## 📚 Referencias

- Modelos: `gestion/models.py`
- Vistas: `gestion/pos_views.py`
- Reportes: `gestion/reportes.py`
- Tests: `test_final.py`
