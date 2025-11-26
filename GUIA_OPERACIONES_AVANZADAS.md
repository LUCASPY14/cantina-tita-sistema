# 📚 Guía de Operaciones Avanzadas - Cantina Tita

## 📋 Índice

1. [Gestión de Proveedores y Compras](#1-gestión-de-proveedores-y-compras)
2. [Sistema de Tarjetas Estudiantiles](#2-sistema-de-tarjetas-estudiantiles)
3. [Registro de Hijos (Estudiantes)](#3-registro-de-hijos-estudiantes)
4. [Ventas con Tarjetas](#4-ventas-con-tarjetas)
5. [Control de Almuerzos](#5-control-de-almuerzos)
6. [Reportes y Consultas](#6-reportes-y-consultas)

---

## 1️⃣ Gestión de Proveedores y Compras

### 📦 Escenario: Compra de Productos a Proveedor

**Objetivo:** Registrar una compra de productos e incrementar el stock.

### Paso 1: Crear Proveedor

**URL:** http://localhost:8000/admin/gestion/proveedor/add/

```
Proveedor 1 - Distribuidora de Alimentos:
- RUC: 80023456-1
- Razón Social: Distribuidora La Estrella S.A.
- Nombre Contacto: Roberto Martínez
- Email: ventas@laestrella.com.py
- Teléfono: 021-555-2000
- Ciudad: Asunción
- Dirección: Av. Artigas 1234
- Activo: ✓

Proveedor 2 - Bebidas:
- RUC: 80034567-2
- Razón Social: Embotelladora del Sur S.R.L.
- Nombre Contacto: Ana López
- Email: pedidos@embotelladoras.com.py
- Teléfono: 021-555-3000
- Ciudad: Asunción
- Dirección: Ruta 2 Km 15
- Activo: ✓

Proveedor 3 - Snacks y Golosinas:
- RUC: 80045678-3
- Razón Social: Snacks Paraguay S.A.
- Nombre Contacto: Carlos Benítez
- Email: comercial@snacksparaguay.com.py
- Teléfono: 021-555-4000
- Ciudad: Fernando de la Mora
- Dirección: Zona Industrial
- Activo: ✓
```

✅ **Verificar:** http://localhost:8000/admin/gestion/proveedor/ - 3 proveedores creados.

---

### Paso 2: Registrar Compra

**URL:** http://localhost:8000/admin/gestion/compras/add/

```
Compra #1:
- ID Proveedor: Distribuidora La Estrella S.A.
- Fecha: 27/11/2025 14:00:00
- Nro Factura: 001-001-0012345 (número de factura del proveedor)
- Monto Total: 1595000 (se calculará automáticamente)
```

✅ **Guardar** y anotar el ID de la compra.

---

### Paso 3: Agregar Detalles de la Compra

**URL:** http://localhost:8000/admin/gestion/detallecompra/add/

**Ejemplo: Compra de Ingredientes para Almuerzos**

```
Detalle 1 - Carne:
- ID Compra: [Compra recién creada]
- ID Producto: [Crear producto "Carne molida" si no existe]
  * Código: CAR001
  * Descripción: Carne Molida x Kg
  * Categoría: Ingredientes
  * Unidad: KG
  * Impuesto: IVA 10%
  * Stock mínimo: 50.000
- Cantidad: 20.000 (kg)
- Costo Unitario Neto: 35000 (Gs. 35,000 por kg sin IVA)
- Subtotal Neto: 700000 (Gs. 700,000)

Detalle 2 - Arroz:
- ID Compra: [Compra recién creada]
- ID Producto: Arroz x Kg
  * Código: ARR001
  * Descripción: Arroz Blanco x Kg
  * Categoría: Ingredientes
  * Unidad: KG
  * Impuesto: IVA 10%
  * Stock mínimo: 100.000
- Cantidad: 50.000 (kg)
- Costo Unitario Neto: 8000 (Gs. 8,000 por kg sin IVA)
- Subtotal Neto: 400000 (Gs. 400,000)

Detalle 3 - Coca Cola:
- ID Compra: [Compra recién creada]
- ID Producto: COC500 - Coca Cola 500ml
- Cantidad: 100.000
- Costo Unitario Neto: 3500 (Gs. 3,500 costo sin IVA)
- Subtotal Neto: 350000 (Gs. 350,000)
```

**Total Compra:** Gs. 1,450,000 (+ IVA = Gs. 1,595,000)

✅ **Verificar:** 3 detalles agregados.

---

### Paso 4: Registrar Movimientos de Stock (Entrada)

**URL:** http://localhost:8000/admin/gestion/movimientosstock/add/

**Por cada producto de la compra:**

```
Movimiento 1 - Carne:
- ID Producto: CAR001 - Carne Molida
- Tipo Movimiento: Compra
- Cantidad: 20.000
- Fecha hora: 27/11/2025 14:00:00
- ID Empleado Autoriza: [Usuario admin]
- Stock Resultante: (se calcula automáticamente) ⚙️
- Observaciones: Compra #1 - Factura 001-001-0012345 - Distribuidora La Estrella

Movimiento 2 - Arroz:
- ID Producto: ARR001 - Arroz Blanco
- Tipo Movimiento: Compra
- Cantidad: 50.000
- Fecha hora: 27/11/2025 14:00:00
- Stock Resultante: (automático) ⚙️
- Observaciones: Compra #1 - Distribuidora La Estrella

Movimiento 3 - Coca Cola:
- ID Producto: COC500 - Coca Cola 500ml
- Tipo Movimiento: Compra
- Cantidad: 100.000
- Fecha hora: 27/11/2025 14:00:00
- Stock Resultante: (automático) ⚙️
- Observaciones: Compra #1 - Distribuidora La Estrella
```

⚙️ **IMPORTANTE:** El campo `Stock_Resultante` se calcula automáticamente mediante el trigger `trg_stock_unico_after_movement`. Solo debes ingresar el `Tipo_Movimiento` y la `Cantidad`.

⚠️ **NUNCA llenes manualmente el campo "Stock Resultante"** - El sistema lo marca como solo lectura para evitar errores. El trigger actualiza automáticamente la tabla `stock_unico` después de guardar el movimiento.

**Tipos de movimiento:**
- ➕ **ENTRADA** (suma): Compra, Entrada, Ajuste Entrada, Devolución de Cliente
- ➖ **SALIDA** (resta): Venta, Salida, Uso Interno, Ajuste Salida, Devolución a Proveedor, Merma

✅ **Verificar:** Stock actualizado en http://localhost:8000/admin/gestion/stockunico/

📝 **Nota:** La factura del proveedor ya se registró en el campo `Nro_Factura` de la compra.

---

## 2️⃣ Sistema de Tarjetas Estudiantiles

### 💳 Escenario: Crear Tarjeta para Estudiante

**Objetivo:** Emitir tarjeta precargada para que un estudiante pueda consumir.

### Paso 1: Crear Cliente (Padre/Tutor)

**URL:** http://localhost:8000/admin/gestion/cliente/add/

```
Cliente - Padre de Estudiante:
- RUC/CI: 5678901-2
- Nombres: María
- Apellidos: Fernández
- ID Tipo Cliente: Regular
- Email: maria.fernandez@example.com
- Teléfono: 0984-555-1234
- Ciudad: Asunción
- Dirección: Barrio Manorá
- Activo: ✓
```

✅ **Guardar** y anotar el ID del cliente.

---

### Paso 2: Registrar Hijo (Estudiante)

Ver sección [3. Registro de Hijos](#3-registro-de-hijos-estudiantes)

---

### Paso 3: Crear Tarjeta Estudiantil

**URL:** http://localhost:8000/admin/gestion/tarjetas/add/

```
Tarjeta Estudiantil:
- Nro Tarjeta: 1001 (número único)
- ID Hijo: [Hijo recién creado]
- Saldo Actual: 0 (se cargará después)
- Estado: Activa
- Fecha Vencimiento: 31/12/2025
- Saldo Alerta: 20000 (aviso cuando saldo < Gs. 20,000)
```

✅ **Guardar** y anotar el número de tarjeta.

---

### Paso 4: Cargar Saldo a la Tarjeta

**URL:** http://localhost:8000/admin/gestion/cargassaldo/add/

```
Carga #1 - Saldo Inicial:
- Nro Tarjeta: 1001
- ID Cliente Origen: María Fernández (padre que paga)
- ID Nota Credito Origen: (dejar vacío)
- Fecha Carga: 25/11/2025 08:00:00
- Monto Cargado: 150000.00 (Gs. 150,000)
- Referencia: (se llenará automáticamente)
```

⚙️ **AUTOMÁTICO:** Al guardar, el sistema ejecuta el trigger `trg_carga_saldo_genera_venta` que:
1. ✅ Crea automáticamente una **VENTA** (Tipo: "Recarga Tarjeta")
2. ✅ Genera **FACTURA** (Documento tributario exento de IVA)
3. ✅ Crea **DETALLE DE VENTA** (Producto: REC-TAR - Recarga Tarjeta)
4. ✅ Registra **PAGO en EFECTIVO**
5. ✅ El efectivo **INGRESA A CAJA** del día
6. ✅ Actualiza **SALDO DE TARJETA**: 0 → 150,000

✅ **Verificar:** 
- Tarjeta ahora tiene saldo: Gs. 150,000
- Se creó una venta automáticamente
- Se generó factura (exenta)
- El efectivo ingresó a caja

---

## 3️⃣ Registro de Hijos (Estudiantes)

### 👨‍👩‍👧‍👦 Escenario: Registrar Estudiante como Hijo de Cliente

**Objetivo:** Vincular estudiante con padre/tutor para control de consumo.

### Crear Hijo

**URL:** http://localhost:8000/admin/gestion/hijo/add/

```
Estudiante #1:
- ID Cliente: María Fernández (padre/tutor)
- Nombre: Sofía
- Apellido: Fernández
- CI: 9876543-2 (o dejar vacío si es menor)
- Fecha Nacimiento: 15/05/2012
- Grado: 7° Grado
- Seccion: A
- Turno: Mañana
- Activo: ✓

Estudiante #2:
- ID Cliente: María Fernández
- Nombre: Lucas
- Apellido: Fernández
- CI: 9876544-3
- Fecha Nacimiento: 20/08/2014
- Grado: 5° Grado
- Seccion: B
- Turno: Mañana
- Activo: ✓
```

✅ **Verificar:** 2 hijos asociados a María Fernández.

---

## 4️⃣ Ventas con Tarjetas

### 💳 Escenario: Consumo con Tarjeta Estudiantil

**Objetivo:** Registrar consumo usando saldo de tarjeta precargada (SIN generar nueva venta).

⚠️ **IMPORTANTE:** Cuando un estudiante consume con tarjeta **NO se crea una venta nueva** porque:
- La factura ya se emitió cuando se cargó el saldo
- El efectivo ya ingresó a caja en ese momento
- Solo se descuenta el saldo de la tarjeta como control de consumo

### Consumo con Tarjeta - Proceso Simplificado

**Escenario:** Sofía Fernández consume 1 Almuerzo + 1 Coca Cola con su tarjeta 1001.

**Cálculos:**
```
1 Almuerzo Completo:  24,200 Gs. (22,000 + IVA 10%)
1 Coca Cola 500ml:     4,950 Gs. (4,500 + IVA 10%)
────────────────────────────────
TOTAL:                29,150 Gs.

Saldo tarjeta antes:  150,000 Gs.
Saldo después:        120,850 Gs. (150,000 - 29,150)
```

---

#### Paso A: Registrar Movimientos de Stock SOLAMENTE

**URL:** http://localhost:8000/admin/gestion/movimientosstock/add/

```
Movimiento 1:
- ID Producto: ALM002 - Almuerzo Completo
- Tipo Movimiento: Uso Interno
- Cantidad: 1.000
- Fecha hora: 25/11/2025 12:30:00
- ID Empleado Autoriza: María González
- Stock Resultante: (automático) ⚙️
- Observaciones: Consumo Tarjeta 1001 - Sofía Fernández

Movimiento 2:
- ID Producto: COC500 - Coca Cola 500ml
- Tipo Movimiento: Salida
- Cantidad: 1.000
- Stock Resultante: (automático) ⚙️
- Observaciones: Consumo Tarjeta 1001 - Sofía Fernández
```

✅ **Verificar:** Stock actualizado.

---

#### Paso B: Descontar Saldo de Tarjeta

**Opción 1: Actualizar manualmente**

**URL:** http://localhost:8000/admin/gestion/tarjetas/1001/change/

```
Actualizar Tarjeta:
- Saldo Actual: 120850 (150,000 - 29,150)
```

**Opción 2: Crear tabla de consumos (recomendado para mejor control)**

Crear una tabla `consumos_tarjeta` para registrar cada consumo:
```sql
CREATE TABLE consumos_tarjeta (
    ID_Consumo BIGINT AUTO_INCREMENT PRIMARY KEY,
    Nro_Tarjeta VARCHAR(20),
    Fecha_Consumo DATETIME,
    Monto_Consumido DECIMAL(10,2),
    Detalle VARCHAR(200),
    Saldo_Anterior DECIMAL(10,2),
    Saldo_Posterior DECIMAL(10,2),
    FOREIGN KEY (Nro_Tarjeta) REFERENCES tarjetas(Nro_Tarjeta)
);
```

---

### 📊 Resumen Consumo con Tarjeta:

```
═══════════════════════════════════════
          CANTINA TITA
      COMPROBANTE DE CONSUMO
═══════════════════════════════════════
Cliente: María Fernández
Estudiante: Sofía Fernández (7° Grado A)
Tarjeta: 1001
Fecha: 25/11/2025 12:30
Cajero: María González

Productos consumidos:
  1 Almuerzo Completo    Gs. 24,200
  1 Coca Cola 500ml      Gs.  4,950
                        ───────────
TOTAL CONSUMIDO:         Gs. 29,150

Saldo anterior:          Gs. 150,000
Monto consumido:         Gs.  29,150
                        ───────────
Saldo actual:            Gs. 120,850

═══════════════════════════════════════
 NOTA: Factura emitida al cargar saldo
═══════════════════════════════════════
        ¡BUEN PROVECHO!
═══════════════════════════════════════
```

📝 **Nota:** Este es un comprobante interno, NO una factura. La factura legal se emitió cuando se cargó el saldo a la tarjeta.

---

## 5️⃣ Control de Almuerzos

### 🍽️ Escenario: Gestión y Control de Almuerzos

**Objetivo:** Registrar pedidos de almuerzo, preparación y entrega.

### Paso 1: Crear Plan de Almuerzo Mensual

**URL:** http://localhost:8000/admin/gestion/planesalmuerzo/add/

```
Plan Diciembre 2025:
- Nombre Plan: Plan Almuerzo Diciembre 2025
- Descripción: Plan mensual de almuerzos estudiantes
- Fecha Inicio: 01/12/2025
- Fecha Fin: 31/12/2025
- Precio Mensual: 440000 (Gs. 440,000 por 20 días hábiles)
- Incluye Bebida: ✓
- Incluye Postre: ✓
- Dias Semana: Lunes a Viernes
- Activo: ✓
```

✅ **Guardar** - ID Plan (ej: 1)

---

### Paso 2: Inscribir Estudiante en Plan (Suscripción)

**URL:** http://localhost:8000/admin/gestion/suscripcionesalmuerzo/add/

```
Suscripción Sofía:
- ID Hijo: Sofía Fernández
- ID Plan Almuerzo: Plan Diciembre 2025
- Fecha Inicio: 01/12/2025
- Fecha Fin: 31/12/2025
- Estado: Activa
```

✅ **Guardar** - ID Suscripción (ej: 1)

---

### Paso 3: Registrar Pago de Plan Mensual

**URL:** http://localhost:8000/admin/gestion/pagosalmuerzomensual/add/

```
Pago Plan Diciembre:
- ID Hijo: Sofía Fernández
- ID Plan Almuerzo: Plan Diciembre 2025
- ID Medio Pago: EFECTIVO (o TARJETA según corresponda)
- Monto Pagado: 440000
- Fecha Pago: 25/11/2025
- Mes Pagado: Diciembre
- Anio Pagado: 2025
```

✅ **Guardar**

---

### Paso 4: Registrar Consumo Diario de Almuerzo

**URL:** http://localhost:8000/admin/gestion/registroconsumoalmuerzo/add/

```
Consumo 02/12/2025:
- ID Hijo: Sofía Fernández
- Fecha Consumo: 02/12/2025
- ID Suscripcion: [Suscripción de Sofía]
```

✅ **Guardar** - Marca que Sofía consumió su almuerzo ese día

---

### Paso 5: Registrar Movimiento de Stock (Almuerzo)

**URL:** http://localhost:8000/admin/gestion/movimientosstock/add/

```
Movimiento Almuerzo:
- ID Producto: ALM002 - Almuerzo Completo
- Tipo Movimiento: Uso Interno
- Cantidad: 1.000
- Fecha hora: 02/12/2025 11:35:00
- ID Empleado Autoriza: [Cajero]
- Stock Resultante: (automático - negativo OK) ⚙️✓
- Observaciones: Plan Almuerzo Mensual - Sofía Fernández - 02/12/2025
```

📝 **Nota:** Los almuerzos permiten stock negativo porque se preparan bajo demanda.

✅ **Verificar:** Stock de almuerzos actualizado.

---

### 📊 Control Diario de Almuerzos

**Reporte diario - Ejemplo:**

```
═══════════════════════════════════════
   CONTROL DE ALMUERZOS - 02/12/2025
═══════════════════════════════════════

TURNO MAÑANA (11:30):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Sofía Fernández - 7°A - Plan Mensual
✓ Lucas Fernández - 5°B - Plan Mensual
✓ Ana García - 6°A - Venta Individual
✗ Pedro López - 8°A - NO RETIRÓ

TURNO TARDE (13:00):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ María Benítez - 4°C - Plan Mensual
✓ José Ramírez - 9°B - Venta Individual

RESUMEN:
─────────────────────────────────────
Total Solicitados:     6
Total Entregados:      5
No Retirados:          1
Plan Mensual:          4
Venta Individual:      2

STOCK UTILIZADO:
─────────────────────────────────────
Almuerzo Completo:     5 porciones
Jugo Naranja:          5 unidades
Postre (Flan):         5 unidades

═══════════════════════════════════════
```

---

## 6️⃣ Reportes y Consultas

### 📊 Reportes Útiles

#### Reporte 1: Saldo de Tarjetas

**SQL:**
```sql
SELECT 
    t.Nro_Tarjeta,
    h.Nombre,
    h.Apellido,
    h.Grado,
    t.Saldo_Actual,
    t.Estado,
    c.Nombres as Padre_Nombres,
    c.Apellidos as Padre_Apellidos
FROM tarjetas_estudiante t
JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
JOIN cliente c ON h.ID_Cliente = c.ID_Cliente
WHERE t.Estado = 'Activa'
ORDER BY t.Nro_Tarjeta;
```

---

#### Reporte 2: Consumo Diario por Estudiante

**SQL:**
```sql
SELECT 
    h.Nombre,
    h.Apellido,
    h.Grado,
    DATE(v.Fecha) as Fecha_Venta,
    SUM(v.Monto_Total) as Total_Consumido
FROM ventas v
JOIN hijos h ON v.ID_Hijo = h.ID_Hijo
WHERE DATE(v.Fecha) = CURDATE()
GROUP BY h.ID_Hijo, DATE(v.Fecha)
ORDER BY Total_Consumido DESC;
```

---

#### Reporte 3: Almuerzos Pendientes de Entrega

**SQL:**
```sql
SELECT 
    h.Nombre,
    h.Apellido,
    h.Grado,
    pa.Fecha_Pedido,
    pa.Turno,
    pa.Menu_Dia,
    pa.Estado
FROM pedidos_almuerzo pa
JOIN inscripciones_plan ip ON pa.ID_Inscripcion = ip.ID_Inscripcion
JOIN hijos h ON ip.ID_Hijo = h.ID_Hijo
WHERE pa.Estado IN ('Solicitado', 'En Preparacion')
  AND DATE(pa.Fecha_Pedido) = CURDATE()
ORDER BY pa.Turno, h.Grado, h.Apellido;
```

---

#### Reporte 4: Stock Bajo Mínimo

**SQL:**
```sql
SELECT 
    p.Codigo,
    p.Descripcion,
    c.Nombre as Categoria,
    s.Stock_Actual,
    p.Stock_Minimo,
    (p.Stock_Minimo - s.Stock_Actual) as Faltante
FROM productos p
JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
JOIN categorias c ON p.ID_Categoria = c.ID_Categoria
WHERE s.Stock_Actual < p.Stock_Minimo
  AND p.Permite_Stock_Negativo = FALSE
ORDER BY Faltante DESC;
```

---

#### Reporte 5: Ventas del Día por Forma de Pago

**SQL:**
```sql
SELECT 
    mp.Descripcion as Medio_Pago,
    COUNT(pv.ID_Pago) as Cantidad_Transacciones,
    SUM(pv.Monto_Aplicado) as Total_Recaudado
FROM pagos_venta pv
JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
WHERE DATE(pv.Fecha_Pago) = CURDATE()
GROUP BY mp.ID_Medio_Pago
ORDER BY Total_Recaudado DESC;
```

---

## 🆘 Problemas Comunes

### ❌ Error: "Saldo insuficiente en tarjeta"
**Solución:** 
1. Verificar saldo actual: http://localhost:8000/admin/gestion/tarjetas/
2. Realizar carga de saldo: http://localhost:8000/admin/gestion/cargassaldo/add/
3. Consultar historial de cargas y ventas asociadas al hijo

---

### ❌ Error: "Stock insuficiente" para productos normales
**Solución:** 
1. Verificar stock actual: http://localhost:8000/admin/gestion/stockunico/
2. Si es bajo, registrar compra a proveedor
3. Solo almuerzos (ALM001, ALM002) permiten stock negativo

---

### ❌ Error: "Tarjeta vencida"
**Solución:** 
1. Ir a http://localhost:8000/admin/gestion/tarjetas/[nro]/change/
2. Actualizar "Fecha Vencimiento" a fecha futura
3. Verificar que "Estado" sea "Activa"

---

### ❌ Error: "No hay caja abierta"
**Solución:** 
1. Abrir caja del día: http://localhost:8000/admin/gestion/cierrescaja/add/
2. Monto inicial: Gs. 100,000 (o el que corresponda)
3. Dejar vacíos: Fecha cierre, Monto final, Diferencia

---

## ✅ Checklist de Operaciones Diarias

### Apertura (8:00 AM):
- [ ] Abrir caja con fondo inicial
- [ ] Verificar stock de productos perecederos
- [ ] Revisar pedidos de almuerzo del día
- [ ] Verificar timbrados vigentes

### Durante el día:
- [ ] Registrar ventas con documento tributario
- [ ] Procesar recargas de tarjetas
- [ ] Preparar y entregar almuerzos
- [ ] Actualizar estado de pedidos
- [ ] Monitorear stock bajo mínimo

### Cierre (18:00 PM):
- [ ] Contar efectivo físico en caja
- [ ] Registrar monto final
- [ ] Verificar diferencia = 0
- [ ] Cerrar caja con estado "Cerrada"
- [ ] Generar reporte de ventas del día
- [ ] Backup de datos

---

## 📚 Referencias

- **Guía Inicio Rápido:** `GUIA_INICIO_RAPIDO.md`
- **Transacciones Completas:** `GUIA_TRANSACCIONES_COMPLETAS.md`
- **Configuración Paraguay:** `CONFIGURACION_PARAGUAY.md`
- **Stock Negativo:** `SOLUCION_STOCK_NEGATIVO.md`

---

**Fecha:** 25/11/2025  
**Sistema:** Cantina Tita - Gestión Integral  
**Versión Django:** 5.2.8  
**Base de Datos:** MySQL 8.0.44

---

## 🎓 Conceptos Clave

### Diferencia: Plan de Almuerzo vs Venta Individual

| Aspecto | Plan Mensual | Venta Individual |
|---------|-------------|------------------|
| **Pago** | Adelantado (mensual) | Al momento del consumo |
| **Precio** | Gs. 22,000/día (x20 días) | Gs. 24,200/día |
| **Descuento** | 10% aprox | Sin descuento |
| **Registro** | Inscripción en plan | Venta directa |
| **Control** | Por pedido diario | Por venta |
| **Uso Tarjeta** | Opcional (si tiene saldo) | Sí (requiere saldo) |

---

### Flujo de Dinero: Recarga vs Consumo con Tarjeta

#### 📥 RECARGA DE TARJETA (Ingreso de efectivo + Factura)
```
1. Padre paga Gs. 150,000 en EFECTIVO
   ↓
2. Se registra en cargas_saldo
   ↓
3. ⚙️ TRIGGER AUTOMÁTICO crea:
   - VENTA (Tipo: "Recarga Tarjeta")
   - FACTURA LEGAL (Documento exento de IVA)
   - DETALLE VENTA (Producto: REC-TAR)
   - PAGO EFECTIVO
   ↓
4. Saldo de tarjeta: 0 → 150,000
   ↓
5. EFECTIVO INGRESA A CAJA (ese día)
```

#### 💳 CONSUMO CON TARJETA (Solo descuento de saldo)
```
1. Estudiante consume Gs. 29,150
   ↓
2. Se registra MOVIMIENTO DE STOCK (Salida/Uso Interno)
   ↓
3. Saldo de tarjeta: 150,000 → 120,850
   ↓
4. NO se crea venta (ya se facturó en la recarga)
   ↓
5. NO ingresa efectivo (ya ingresó en la recarga)
   ↓
6. Solo se lleva control de consumo
```

**⚠️ VENTAJAS DEL NUEVO SISTEMA:**
- ✅ Cumple con ley tributaria (factura al momento del pago)
- ✅ Efectivo ingresa cuando realmente entra
- ✅ Caja cuadra correctamente
- ✅ Simplifica el proceso de consumo
- ✅ No duplica registros de ventas

---

### Flujo Completo: Compra → Stock → Venta

```
1. REGISTRO COMPRA + FACTURA PROVEEDOR
   ↓
2. DETALLE DE COMPRA (productos y cantidades)
   ↓
3. MOVIMIENTO STOCK "Compra" (Entrada)
   ↓
4. STOCK ACTUALIZADO
   ↓
5. VENTA A CLIENTE
   ↓
6. DOCUMENTO TRIBUTARIO (factura propia)
   ↓
7. DETALLE DE VENTA
   ↓
8. MOVIMIENTO STOCK "Venta" (Salida)
   ↓
9. STOCK ACTUALIZADO
   ↓
10. PAGO REGISTRADO EN CAJA
```

---

¡Guía completa de operaciones lista para usar! 🚀
