# Migración: Cuenta Corriente con Modelo Intermedio

**Fecha:** 2025-12-02  
**Sistema:** Cantina Tita  
**Objetivo:** Implementar modelo profesional de cuenta corriente con tablas intermedias

---

## 📋 Resumen Ejecutivo

Esta migración transforma el sistema de cuenta corriente actual (que registra movimientos directos) a un modelo más robusto que:

- ✅ Permite pagos parciales
- ✅ Permite aplicar un pago a múltiples facturas
- ✅ Mantiene historial detallado de aplicaciones
- ✅ Facilita conciliaciones y reportes
- ✅ Sigue mejores prácticas contables

---

## 🔄 Cambios Principales

### 1. Nuevas Tablas

#### `pagos_proveedores`
**Propósito:** Registrar pagos realizados a proveedores  
**Relación:** Actualmente NO existe forma de registrar pagos de compras

```sql
Campos principales:
- ID_Pago_Proveedor (PK)
- ID_Proveedor (FK)
- Numero_Comprobante
- Fecha
- Monto_Total
- ID_Medio_Pago (FK)
```

#### `aplicacion_pagos_ventas`
**Propósito:** Tabla intermedia entre `pagos_venta` y `ventas`  
**Beneficio:** Permite un pago aplicarse a múltiples ventas

```sql
Campos principales:
- ID_Aplicacion (PK)
- ID_Pago_Venta (FK)
- ID_Venta (FK)
- Monto_Aplicado
```

**Ejemplo de uso:**
```
Cliente paga 150,000 Gs:
- 100,000 Gs → Venta #1234
- 50,000 Gs  → Venta #1235
```

#### `aplicacion_pagos_compras`
**Propósito:** Tabla intermedia entre `pagos_proveedores` y `compras`  
**Beneficio:** Permite un pago aplicarse a múltiples compras

```sql
Campos principales:
- ID_Aplicacion (PK)
- ID_Pago_Proveedor (FK)
- ID_Compra (FK)
- Monto_Aplicado
```

### 2. Campos Agregados

#### Tabla `ventas`
```sql
ALTER TABLE ventas ADD COLUMN:
- Saldo_Pendiente BIGINT
- Estado_Pago ENUM('PENDIENTE','PARCIAL','PAGADA')
```

#### Tabla `compras`
```sql
ALTER TABLE compras ADD COLUMN:
- Saldo_Pendiente DECIMAL(12,2)
- Estado_Pago ENUM('PENDIENTE','PARCIAL','PAGADA')
```

### 3. Nuevas Vistas

#### `vista_movimientos_cta_cte_clientes`
**Propósito:** Ver todos los movimientos (ventas + pagos) de cada cliente  
**Uso:** Consultar historial completo de cuenta corriente

```sql
Columnas:
- ID_Cliente
- Cliente (Nombre + Apellido)
- Fecha_Movimiento
- Referencia
- Tipo_Movimiento ('VENTA' o 'PAGO')
- Debe
- Haber
- Estado_Pago
- Saldo_Documento
```

#### `vista_saldo_clientes`
**Propósito:** Resumen de saldo actual por cliente  
**Uso:** Dashboard, reportes, alertas de mora

```sql
Columnas:
- ID_Cliente
- Nombre, Apellido, Documento
- Total_Debe (suma de ventas)
- Total_Haber (suma de pagos)
- Saldo_Actual (debe - haber)
- Facturas_Pendientes (cantidad)
```

#### `vista_movimientos_cta_cte_proveedores`
**Propósito:** Ver todos los movimientos (compras + pagos) de cada proveedor

#### `vista_saldo_proveedores`
**Propósito:** Resumen de deuda actual con proveedores

---

## 🔍 Comparación: Antes vs Después

### ANTES (Situación Actual)

```
TABLA: pagos_venta
- ID_Pago_Venta → ID_Venta (directo, 1 a 1)
- Problema: Un pago solo puede ir a UNA venta
- Problema: No hay pagos a proveedores

TABLA: cta_corriente
- Registra movimientos manualmente
- Riesgo de inconsistencias
```

### DESPUÉS (Con Migración)

```
TABLA: pagos_venta → TABLA: aplicacion_pagos_ventas
- Relación flexible muchos-a-muchos
- Un pago puede dividirse entre varias ventas
- Una venta puede recibir varios pagos

NUEVA: pagos_proveedores + aplicacion_pagos_compras
- Permite registrar pagos a proveedores
- Control de deuda con proveedores

VISTAS: Calculan saldos automáticamente
- No requiere actualización manual
- Siempre sincronizadas con datos reales
```

---

## 📊 Flujo de Datos Nuevo

### Ventas y Cobros (Clientes)

```
1. Se registra VENTA
   └→ ventas.Estado_Pago = 'PENDIENTE'
   └→ ventas.Saldo_Pendiente = Monto_Total

2. Cliente realiza PAGO
   └→ Se crea registro en pagos_venta
   └→ Se crea aplicación en aplicacion_pagos_ventas
       ├→ Vincula pago con venta(s)
       └→ Especifica monto aplicado a cada venta

3. Sistema ACTUALIZA automáticamente:
   └→ ventas.Saldo_Pendiente -= Monto_Aplicado
   └→ ventas.Estado_Pago = 'PARCIAL' o 'PAGADA'
   └→ vista_saldo_clientes se actualiza (automático)
```

### Compras y Pagos (Proveedores)

```
1. Se registra COMPRA
   └→ compras.Estado_Pago = 'PENDIENTE'
   └→ compras.Saldo_Pendiente = Monto_Total

2. Se realiza PAGO a proveedor
   └→ Se crea registro en pagos_proveedores
   └→ Se crea aplicación en aplicacion_pagos_compras
       ├→ Vincula pago con compra(s)
       └→ Especifica monto aplicado a cada compra

3. Sistema ACTUALIZA automáticamente:
   └→ compras.Saldo_Pendiente -= Monto_Aplicado
   └→ compras.Estado_Pago = 'PARCIAL' o 'PAGADA'
   └→ vista_saldo_proveedores se actualiza (automático)
```

---

## 🚀 Ejecución de la Migración

### Opción 1: Script Python Automático (Recomendado)

```bash
python ejecutar_migracion_cta_cte.py
```

**Características:**
- ✅ Crea backups automáticos
- ✅ Valida pre-requisitos
- ✅ Ejecuta todo en una transacción (rollback si falla)
- ✅ Valida resultados al final
- ✅ Muestra resumen detallado

### Opción 2: MySQL Workbench Manual

1. Abrir `migracion_cta_corriente.sql` en Workbench
2. Ejecutar todo el script
3. Verificar resultados con las consultas al final

---

## ⚠️ Consideraciones Importantes

### 1. Datos Existentes

**La migración NO migra datos automáticamente.**

Después de ejecutar la migración estructural, necesitarás:

```sql
-- Migrar pagos existentes a la tabla intermedia
INSERT INTO aplicacion_pagos_ventas 
    (ID_Pago_Venta, ID_Venta, Monto_Aplicado)
SELECT 
    ID_Pago_Venta,
    ID_Venta,
    Monto_Aplicado
FROM pagos_venta
WHERE ID_Venta IS NOT NULL;

-- Actualizar saldos de ventas
UPDATE ventas v
SET 
    Saldo_Pendiente = v.Monto_Total - COALESCE(
        (SELECT SUM(a.Monto_Aplicado) 
         FROM aplicacion_pagos_ventas a 
         WHERE a.ID_Venta = v.ID_Venta), 0
    ),
    Estado_Pago = CASE
        WHEN v.Monto_Total = COALESCE(
            (SELECT SUM(a.Monto_Aplicado) 
             FROM aplicacion_pagos_ventas a 
             WHERE a.ID_Venta = v.ID_Venta), 0
        ) THEN 'PAGADA'
        WHEN COALESCE(
            (SELECT SUM(a.Monto_Aplicado) 
             FROM aplicacion_pagos_ventas a 
             WHERE a.ID_Venta = v.ID_Venta), 0
        ) > 0 THEN 'PARCIAL'
        ELSE 'PENDIENTE'
    END;
```

### 2. Triggers Necesarios

Se recomienda crear triggers para mantener sincronización automática:

```sql
-- Trigger: Al aplicar un pago, actualizar saldo de venta
CREATE TRIGGER after_aplicacion_pago_venta
AFTER INSERT ON aplicacion_pagos_ventas
FOR EACH ROW
BEGIN
    UPDATE ventas 
    SET Saldo_Pendiente = Saldo_Pendiente - NEW.Monto_Aplicado
    WHERE ID_Venta = NEW.ID_Venta;
    
    -- Actualizar estado
    UPDATE ventas
    SET Estado_Pago = CASE
        WHEN Saldo_Pendiente = 0 THEN 'PAGADA'
        WHEN Saldo_Pendiente < Monto_Total THEN 'PARCIAL'
        ELSE 'PENDIENTE'
    END
    WHERE ID_Venta = NEW.ID_Venta;
END;
```

### 3. Impacto en Django

#### Nuevos Modelos Necesarios

```python
# gestion/models.py

class PagosProveedores(models.Model):
    id_pago_proveedor = models.BigAutoField(primary_key=True, db_column='ID_Pago_Proveedor')
    id_proveedor = models.ForeignKey('Proveedor', db_column='ID_Proveedor')
    numero_comprobante = models.CharField(max_length=20, db_column='Numero_Comprobante')
    fecha = models.DateField(db_column='Fecha')
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, db_column='Monto_Total')
    id_medio_pago = models.ForeignKey('MediosPago', db_column='ID_Medio_Pago', null=True)
    observacion = models.CharField(max_length=255, db_column='Observacion', null=True)
    
    class Meta:
        managed = False
        db_table = 'pagos_proveedores'

class AplicacionPagosVentas(models.Model):
    id_aplicacion = models.BigAutoField(primary_key=True, db_column='ID_Aplicacion')
    id_pago_venta = models.ForeignKey('PagosVenta', db_column='ID_Pago_Venta')
    id_venta = models.ForeignKey('Ventas', db_column='ID_Venta')
    monto_aplicado = models.BigIntegerField(db_column='Monto_Aplicado')
    
    class Meta:
        managed = False
        db_table = 'aplicacion_pagos_ventas'

class AplicacionPagosCompras(models.Model):
    id_aplicacion = models.BigAutoField(primary_key=True, db_column='ID_Aplicacion')
    id_pago_proveedor = models.ForeignKey('PagosProveedores', db_column='ID_Pago_Proveedor')
    id_compra = models.ForeignKey('Compras', db_column='ID_Compra')
    monto_aplicado = models.DecimalField(max_digits=12, decimal_places=2, db_column='Monto_Aplicado')
    
    class Meta:
        managed = False
        db_table = 'aplicacion_pagos_compras'
```

#### Actualizar Modelos Existentes

```python
# Agregar campos a Ventas
class Ventas(models.Model):
    # ... campos existentes ...
    saldo_pendiente = models.BigIntegerField(db_column='Saldo_Pendiente', null=True)
    estado_pago = models.CharField(
        max_length=10, 
        db_column='Estado_Pago',
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('PARCIAL', 'Pago Parcial'),
            ('PAGADA', 'Pagada')
        ],
        default='PENDIENTE'
    )

# Agregar campos a Compras
class Compras(models.Model):
    # ... campos existentes ...
    saldo_pendiente = models.DecimalField(
        max_digits=12, decimal_places=2,
        db_column='Saldo_Pendiente', 
        null=True
    )
    estado_pago = models.CharField(
        max_length=10, 
        db_column='Estado_Pago',
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('PARCIAL', 'Pago Parcial'),
            ('PAGADA', 'Pagada')
        ],
        default='PENDIENTE'
    )
```

---

## ✅ Checklist Post-Migración

- [ ] Ejecutar script de migración
- [ ] Verificar que todas las tablas se crearon
- [ ] Verificar que todas las vistas funcionan
- [ ] Migrar datos de pagos_venta a aplicacion_pagos_ventas
- [ ] Actualizar saldos de ventas existentes
- [ ] Crear triggers para sincronización automática
- [ ] Actualizar models.py en Django
- [ ] Probar creación de pagos nuevos
- [ ] Probar aplicación de pagos parciales
- [ ] Verificar vistas de cuenta corriente
- [ ] Actualizar reportes para usar nuevas vistas
- [ ] Documentar cambios para el equipo

---

## 📞 Soporte

Si encuentras problemas durante la migración:

1. Revisa los backups creados (timestamp en nombre de tabla)
2. Consulta los logs del script Python
3. Verifica integridad de datos con queries de validación

---

**Última actualización:** 2025-12-02
