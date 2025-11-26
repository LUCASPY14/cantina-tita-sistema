# 🚀 Guía de Inicio Rápido - Cantina Tita

## 📋 Objetivo
Esta guía te llevará paso a paso desde cero hasta realizar tu primera venta completa en el sistema.

---

## ✅ Estado Actual del Sistema

Ya tienes configurado:
- ✅ Empresa (1)
- ✅ Categorías (6)
- ✅ Tipos de Pago (2): CONTADO, CREDITO
- ✅ Medios de Pago (6): EFECTIVO, TRANSFERENCIA, TARJETAS, etc.

**Faltan por configurar:**
- ⏳ Unidades de Medida
- ⏳ Impuestos (IVA 10%, IVA 5%, Exento)
- ⏳ Tipos de Cliente
- ⏳ Lista de Precios
- ⏳ Tipos de Rol
- ⏳ Cajas
- ⏳ Puntos de Expedición
- ⏳ Timbrados
- ⏳ Empleados
- ⏳ Clientes
- ⏳ Productos

---

## 🎯 Plan de Trabajo

### FASE 1: Configuración Básica (15 minutos)
1. Unidades de medida
2. Impuestos
3. Tipos de cliente
4. Lista de precios
5. Tipos de rol

### FASE 2: Configuración de Ventas (10 minutos)
6. Cajas
7. Puntos de expedición
8. Timbrados

### FASE 3: Datos Operativos (15 minutos)
9. Empleados (cajero)
10. Clientes
11. Productos

### FASE 4: Primera Venta (10 minutos)
12. Registrar stock
13. Asignar precios
14. Abrir caja
15. Realizar venta completa

---

## 📦 FASE 1: Configuración Básica

### 1️⃣ Unidades de Medida (2 minutos)

**URL:** http://localhost:8000/admin/gestion/unidadmedida/add/

Crear estas unidades básicas:

```
Unidad 1:
- Código: UN
- Descripción: Unidad
- Activo: ✓

Unidad 2:
- Código: KG
- Descripción: Kilogramo
- Activo: ✓

Unidad 3:
- Código: L
- Descripción: Litro
- Activo: ✓

Unidad 4:
- Código: PORCION
- Descripción: Porción
- Activo: ✓

Unidad 5:
- Código: PAQUETE
- Descripción: Paquete
- Activo: ✓
```

✅ **Verificar:** Ve a http://localhost:8000/admin/gestion/unidadmedida/ y confirma que tienes 5 unidades.

---

### 2️⃣ Impuestos (3 minutos)

**URL:** http://localhost:8000/admin/gestion/impuesto/add/

⚠️ **IMPORTANTE:** Si da error "restricción impuestos_chk_2", ejecuta primero en MySQL:
```sql
ALTER TABLE impuestos DROP CHECK impuestos_chk_2;
ALTER TABLE impuestos ADD CONSTRAINT impuestos_chk_2 
CHECK (Porcentaje >= 0 AND Porcentaje <= 100);
```

Crear estos impuestos:

```
Impuesto 1:
- Nombre: IVA 10%
- Porcentaje: 10.00
- Vigente desde: 01/01/2025
- Activo: ✓

Impuesto 2:
- Nombre: IVA 5%
- Porcentaje: 5.00
- Vigente desde: 01/01/2025
- Activo: ✓

Impuesto 3:
- Nombre: Exento
- Porcentaje: 0.00
- Vigente desde: 01/01/2025
- Activo: ✓
```

✅ **Verificar:** Deberías tener 3 impuestos registrados.

---

### 3️⃣ Tipos de Cliente (2 minutos)

**URL:** http://localhost:8000/admin/gestion/tipocliente/add/

```
Tipo 1:
- Nombre: Regular
- Descripción: Cliente regular sin descuentos especiales
- Activo: ✓

Tipo 2:
- Nombre: Estudiante
- Descripción: Estudiante con tarjeta precargada
- Activo: ✓

Tipo 3:
- Nombre: Docente
- Descripción: Personal docente de la institución
- Activo: ✓
```

✅ **Verificar:** 3 tipos de cliente creados.

---

### 4️⃣ Lista de Precios (2 minutos)

**URL:** http://localhost:8000/admin/gestion/listaprecios/add/

```
Lista Principal:
- Nombre: Precio General 2025
- Moneda: PYG
- Fecha vigencia: 01/01/2025
- Descripción: Lista de precios general para todos los productos
- Activo: ✓
```

✅ **Verificar:** 1 lista de precios creada.

---

### 5️⃣ Tipos de Rol (3 minutos)

**URL:** http://localhost:8000/admin/gestion/tiporolgeneral/add/

```
Rol 1:
- Nombre: Administrador
- Descripción: Acceso completo al sistema
- Activo: ✓

Rol 2:
- Nombre: Cajero
- Descripción: Registro de ventas y operaciones de caja
- Activo: ✓

Rol 3:
- Nombre: Gerente
- Descripción: Supervisión y reportes
- Activo: ✓
```

✅ **Verificar:** 3 roles creados.

---

## 🏪 FASE 2: Configuración de Ventas

### 6️⃣ Cajas (2 minutos)

**URL:** http://localhost:8000/admin/gestion/cajas/add/

```
Caja Principal:
- Nombre: Caja 1
- Ubicación: Planta Baja - Entrada Principal
- Activo: ✓
```

Si tienes múltiples puntos de venta, crea más cajas:
```
Caja 2:
- Nombre: Caja 2
- Ubicación: Primer Piso - Cafetería
- Activo: ✓
```

✅ **Verificar:** Al menos 1 caja creada.

---

### 7️⃣ Puntos de Expedición (3 minutos)

**URL:** http://localhost:8000/admin/gestion/puntosexpedicion/add/

```
Punto Principal:
- Código establecimiento: 001
- Código punto expedición: 001
- Descripción ubicación: Caja Principal - Planta Baja
- Activo: ✓
```

📝 **Nota:** Los códigos son de 3 dígitos según normativa SET Paraguay.

✅ **Verificar:** 1 punto de expedición creado.

---

### 8️⃣ Timbrados (5 minutos)

**URL:** http://localhost:8000/admin/gestion/timbrados/add/

⚠️ **IMPORTANTE:** Para pruebas, usa números ficticios. En producción, usa timbrados reales de SET.

```
Timbrado Facturas:
- Nro Timbrado: 12345678
- Tipo documento: Factura
- ID Punto: [Selecciona el punto 001-001 creado]
- Nro inicio: 001-001-0000001
- Nro fin: 001-001-0001000
- Fecha inicio: 01/01/2025
- Fecha fin: 31/12/2025
- Es electrónico: ✓ (para factura electrónica) o ✗ (para factura física)
- Activo: ✓
```

✅ **Verificar:** 1 timbrado activo.

---

## 👥 FASE 3: Datos Operativos

### 9️⃣ Empleado Cajero (3 minutos)

**URL:** http://localhost:8000/admin/gestion/empleado/add/

```
Cajero Principal:
- Usuario: cajero01
- Nombre: María
- Apellido: González
- Documento Identidad: 4123456-7
- ID Rol: Cajero
- Email: maria.gonzalez@cantinatita.com
- Teléfono: 0981-123456
- Ciudad: Asunción
- Dirección: Barrio Centro
- Fecha ingreso: 01/01/2025
- Activo: ✓
```

✅ **Verificar:** 1 empleado cajero creado.

---

### 🔟 Clientes de Prueba (5 minutos)

**URL:** http://localhost:8000/admin/gestion/cliente/add/

**Cliente 1 - Cliente regular:**
```
- RUC/CI: 4567891-2
- Nombres: Juan
- Apellidos: Pérez
- Razón Social: (dejar vacío para persona física)
- ID Tipo Cliente: Regular
- Email: juan.perez@example.com
- Teléfono: 0982-654321
- Ciudad: Asunción
- Dirección: Barrio San Vicente
- Activo: ✓
```

**Cliente 2 - Padre/tutor de estudiante:**
```
- RUC/CI: 3456789-1
- Nombres: Carmen
- Apellidos: Rodríguez
- ID Tipo Cliente: Regular
- Email: carmen.rodriguez@example.com
- Teléfono: 0983-111222
- Ciudad: Asunción
- Dirección: Barrio Trinidad
- Activo: ✓
```

**Cliente 3 - Empresa (opcional):**
```
- RUC: 80012345-6
- Nombres: (dejar vacío)
- Apellidos: (dejar vacío)
- Razón Social: Distribuidora ABC S.A.
- ID Tipo Cliente: Regular
- Email: ventas@abc.com.py
- Teléfono: 021-555-1234
- Ciudad: Asunción
- Activo: ✓
```

✅ **Verificar:** Al menos 2 clientes creados.

---

### 1️⃣1️⃣ Productos (7 minutos)

**URL:** http://localhost:8000/admin/gestion/producto/add/

**Producto 1 - Bebida:**
```
- Código: COC500
- Descripción: Coca Cola 500ml
- ID Categoría: Bebidas
- ID Unidad: Unidad (UN)
- ID Impuesto: IVA 10%
- Stock mínimo: 20.000
- Requiere lote: ✗
- Activo: ✓
```

**Producto 2 - Snack:**
```
- Código: EMP001
- Descripción: Empanada de Carne
- ID Categoría: Snacks
- ID Unidad: Unidad (UN)
- ID Impuesto: IVA 10%
- Stock mínimo: 30.000
- Requiere lote: ✗
- Activo: ✓
```

**Producto 3 - Almuerzo:**
```
- Código: ALM001
- Descripción: Almuerzo Completo
- ID Categoría: Almuerzos
- ID Unidad: Porción (PORCION)
- ID Impuesto: IVA 10%
- Stock mínimo: 10.000
- Requiere lote: ✗
- Activo: ✓
```

**Producto 4 - Snack 2:**
```
- Código: CHI001
- Descripción: Chipá
- ID Categoría: Snacks
- ID Unidad: Unidad (UN)
- ID Impuesto: IVA 10%
- Stock mínimo: 50.000
- Requiere lote: ✗
- Activo: ✓
```

**Producto 5 - Bebida 2:**
```
- Código: AGU500
- Descripción: Agua Mineral 500ml
- ID Categoría: Bebidas
- ID Unidad: Unidad (UN)
- ID Impuesto: IVA 5%
- Stock mínimo: 30.000
- Requiere lote: ✗
- Activo: ✓
```

✅ **Verificar:** 5 productos creados.

---

## 💰 FASE 4: Primera Venta Completa

### 1️⃣2️⃣ Registrar Stock Inicial (3 minutos)

**URL:** http://localhost:8000/admin/gestion/stockunico/add/

⚠️ **IMPORTANTE:** Si ya existe stock del producto, NO crear nuevo. Ir a la lista y EDITAR el existente.

```
Stock Coca Cola:
- ID Producto: COC500 - Coca Cola 500ml
- Stock actual: 100.000
- Fecha última actualización: [Hoy - se completa automático]

Stock Empanada:
- ID Producto: EMP001 - Empanada de Carne
- Stock actual: 150.000

Stock Almuerzo:
- ID Producto: ALM001 - Almuerzo Completo
- Stock actual: 50.000

Stock Chipá:
- ID Producto: CHI001 - Chipá
- Stock actual: 200.000

Stock Agua:
- ID Producto: AGU500 - Agua Mineral 500ml
- Stock actual: 120.000
```

✅ **Verificar:** 5 registros de stock creados.

---

### 1️⃣3️⃣ Asignar Precios (3 minutos)

**URL:** http://localhost:8000/admin/gestion/preciosporlista/add/

```
Precio Coca Cola:
- ID Producto: COC500 - Coca Cola 500ml
- ID Lista: Precio General 2025
- Precio unitario neto: 4500 (SIN IVA)
- Fecha vigencia: 01/01/2025
  ➜ Con IVA 10%: 4,950 Gs.

Precio Empanada:
- ID Producto: EMP001 - Empanada de Carne
- ID Lista: Precio General 2025
- Precio unitario neto: 3600 (SIN IVA)
- Fecha vigencia: 01/01/2025
  ➜ Con IVA 10%: 3,960 Gs.

Precio Almuerzo:
- ID Producto: ALM001 - Almuerzo Completo
- ID Lista: Precio General 2025
- Precio unitario neto: 22000 (SIN IVA)
- Fecha vigencia: 01/01/2025
  ➜ Con IVA 10%: 24,200 Gs.

Precio Chipá:
- ID Producto: CHI001 - Chipá
- ID Lista: Precio General 2025
- Precio unitario neto: 1800 (SIN IVA)
- Fecha vigencia: 01/01/2025
  ➜ Con IVA 10%: 1,980 Gs.

Precio Agua:
- ID Producto: AGU500 - Agua Mineral 500ml
- ID Lista: Precio General 2025
- Precio unitario neto: 2857 (SIN IVA)
- Fecha vigencia: 01/01/2025
  ➜ Con IVA 5%: 3,000 Gs.
```

✅ **Verificar:** 5 precios asignados.

---

### 1️⃣4️⃣ Abrir Caja (2 minutos)

**URL:** http://localhost:8000/admin/gestion/cierrescaja/add/

```
Apertura de Caja:
- ID Caja: Caja 1
- ID Empleado: María González (cajero01)
- Fecha hora apertura: [HOY a las 08:00:00]
- Monto inicial: 100000.00 (Gs. 100,000 como fondo inicial)
- Estado: (DEJAR VACÍO = caja abierta)
- Fecha hora cierre: (DEJAR VACÍO)
- Monto final: (DEJAR VACÍO)
- Diferencia efectivo: (DEJAR VACÍO)
```

✅ **Verificar:** Caja abierta y lista para ventas.

---

### 1️⃣5️⃣ REALIZAR PRIMERA VENTA (10 minutos)

**Escenario:** Juan Pérez compra 1 Coca Cola + 2 Empanadas y paga en efectivo.

**Cálculos:**
```
1 Coca Cola:    4,950 Gs.
2 Empanadas:    7,920 Gs. (3,960 × 2)
────────────────────────
TOTAL:         12,870 Gs.

Desglose IVA:
- Monto gravado 10%: 11,700 Gs. (4,500 + 7,200)
- Monto IVA 10%:      1,170 Gs.
- Monto total:       12,870 Gs.
```

---

#### Paso A: Crear Documento Tributario

**URL:** http://localhost:8000/admin/gestion/documentostributarios/add/

```
- Nro timbrado: [Seleccionar "Timbrado 12345678 - Factura"]
- Nro secuencial: 1 (SOLO EL NÚMERO, NO "001-001-0000001")
- Fecha emisión:
  * Fecha: [HOY]
  * Hora: [HORA ACTUAL, ej: 10:30:00]
- Monto total: 12870
- Monto exento: 0 (o dejar vacío)
- Monto gravado 5: 0 (o dejar vacío)
- Monto iva 5: 0 (o dejar vacío)
- Monto gravado 10: 11700
- Monto iva 10: 1170
```

✅ **Guardar** y anotar el ID del documento.

---

#### Paso B: Crear la Venta

**URL:** http://localhost:8000/admin/gestion/ventas/add/

```
- ID Documento: [Seleccionar documento recién creado]
- ID Cliente: Juan Pérez
- ID Hijo: (dejar vacío)
- ID Tipo Pago: CONTADO
- ID Empleado Cajero: María González
- Fecha: [HOY 10:30:00]
- Tipo Venta: Venta Directa
- Monto Total: 12870
- Estado: Completada
```

✅ **Guardar** y anotar el ID de venta.

---

#### Paso C: Agregar Detalles de Venta

**URL:** http://localhost:8000/admin/gestion/detalleventa/add/

**Detalle 1 - Coca Cola:**
```
- ID Venta: [Venta recién creada]
- ID Producto: COC500 - Coca Cola 500ml
- Cantidad: 1.000
- Precio unitario neto: 4500 (sin IVA)
- Precio unitario total: 4950 (con IVA)
- Subtotal neto: 4500
- Subtotal total: 4950
- Monto IVA: 450
```

**Detalle 2 - Empanadas:**
```
- ID Venta: [Venta recién creada]
- ID Producto: EMP001 - Empanada de Carne
- Cantidad: 2.000
- Precio unitario neto: 3600 (sin IVA)
- Precio unitario total: 3960 (con IVA)
- Subtotal neto: 7200
- Subtotal total: 7920
- Monto IVA: 720
```

✅ **Verificar:** 2 detalles agregados, total = 12,870 Gs.

---

#### Paso D: Registrar Movimientos de Stock

**URL:** http://localhost:8000/admin/gestion/movimientosstock/add/

**Movimiento 1 - Coca Cola:**
```
- ID Producto: COC500 - Coca Cola 500ml
- Tipo movimiento: Venta
- Cantidad: 1.000
- Fecha hora: [HOY 10:30:00]
- ID Empleado responsable: María González
- ID Empleado autoriza: María González
- ID Venta: [Venta creada]
- Stock resultante: 99.000 (100 - 1)
- Observaciones: Venta #1 - Juan Pérez
```

**Movimiento 2 - Empanadas:**
```
- ID Producto: EMP001 - Empanada de Carne
- Tipo movimiento: Venta
- Cantidad: 2.000
- Fecha hora: [HOY 10:30:00]
- ID Empleado responsable: María González
- ID Empleado autoriza: María González
- ID Venta: [Venta creada]
- Stock resultante: 148.000 (150 - 2)
- Observaciones: Venta #1 - Juan Pérez
```

✅ **Verificar:** 2 movimientos registrados.

---

#### Paso E: Registrar Pago

**URL:** http://localhost:8000/admin/gestion/pagosventa/add/

```
- ID Venta: [Venta creada]
- ID Medio Pago: EFECTIVO
- ID Cierre: [Seleccionar apertura de caja del día]
- Monto aplicado: 12870
- Referencia transacción: (dejar vacío para efectivo)
- Fecha pago: [HOY 10:30:00]
```

✅ **Guardar** - Pago registrado.

---

#### Paso F: Actualizar Stock (Verificación)

**URL:** http://localhost:8000/admin/gestion/stockunico/

Buscar y EDITAR los productos:

```
Stock Coca Cola:
- Stock actual: 99.000 (100 - 1) ✓

Stock Empanada:
- Stock actual: 148.000 (150 - 2) ✓
```

✅ **Verificar:** Stock actualizado correctamente.

---

## 🎉 ¡PRIMERA VENTA COMPLETADA!

### Resumen de la Venta:

```
═══════════════════════════════════════
          CANTINA TITA
═══════════════════════════════════════
Factura: 001-001-0000001
Cliente: Juan Pérez
Fecha: [HOY] 10:30
Cajero: María González

Productos:
  1 Coca Cola 500ml      Gs.  4,950
  2 Empanada Carne       Gs.  7,920
                        ───────────
Subtotal (sin IVA):      Gs. 11,700
IVA 10%:                 Gs.  1,170
                        ═══════════
TOTAL:                   Gs. 12,870

Pago: EFECTIVO           Gs. 12,870
Cambio:                  Gs.      0

═══════════════════════════════════════
        ¡GRACIAS POR SU COMPRA!
═══════════════════════════════════════
```

---

## 🔍 Verificaciones Post-Venta

### 1. Verificar la Venta
```
URL: http://localhost:8000/admin/gestion/ventas/

Deberías ver:
- 1 venta registrada
- Estado: Completada
- Monto: Gs. 12,870
```

### 2. Verificar Stock Actualizado
```
URL: http://localhost:8000/admin/gestion/stockunico/

Coca Cola: 99.000 (de 100.000)
Empanada:  148.000 (de 150.000)
```

### 3. Verificar Movimientos
```
URL: http://localhost:8000/admin/gestion/movimientosstock/

2 movimientos de tipo "Venta" registrados
```

### 4. Verificar Documento Tributario
```
URL: http://localhost:8000/admin/gestion/documentostributarios/

Documento 001-001-0000001 emitido
Monto: Gs. 12,870
```

### 5. Verificar Pago
```
URL: http://localhost:8000/admin/gestion/pagosventa/

Pago en EFECTIVO por Gs. 12,870
```

---

## 📊 Próximos Pasos

Ahora que completaste tu primera venta, puedes:

1. **Realizar más ventas** siguiendo el mismo proceso
2. **Crear tarjetas estudiantiles** (ver Escenario 2 de guía completa)
3. **Registrar compras a proveedores** (ver Escenario 4)
4. **Crear planes de almuerzo** (ver Escenario 5)
5. **Cerrar la caja** al final del día

---

## 🔚 Cerrar Caja al Final del Día

**URL:** http://localhost:8000/admin/gestion/cierrescaja/[id]/change/

```
Cierre de Caja:
- Fecha hora cierre: [HOY 18:00:00]
- Monto final: [Contar efectivo físico en caja]
  Ejemplo: 100,000 (inicial) + 12,870 (venta) = 112,870
- Diferencia efectivo: [Se calcula automático]
  Si contaste exacto 112,870: diferencia = 0 ✓
- Estado: Cerrada
```

✅ **Guardar** - Caja cerrada correctamente.

---

## 🆘 Problemas Comunes

### ❌ Error: "Ya existe Stock con este Id producto"
**Solución:** No crear nuevo, ir a la lista de stock y EDITAR el existente.

### ❌ Error: "Nro secuencial inválido"
**Solución:** Usar solo el número (1, 2, 3...), NO "001-001-0000001"

### ❌ Error: "Este campo es obligatorio" en Monto total
**Solución:** Completar TODOS los campos de montos del documento tributario

### ❌ Error: "Datos truncados para la columna"
**Solución:** Ya aplicado en versión actual. Si persiste, revisar scripts SQL.

### ❌ Error: "No hay caja abierta"
**Solución:** Crear apertura de caja antes de registrar ventas.

---

## 📚 Documentación Adicional

- **Guía Completa:** `GUIA_TRANSACCIONES_COMPLETAS.md` (6 escenarios detallados)
- **Problemas y Soluciones:** Ver sección "Problemas Comunes" en guía completa
- **Scripts SQL:** Carpeta `sql/` con correcciones aplicadas

---

## ✅ Checklist Final

- [ ] 5 Unidades de medida creadas
- [ ] 3 Impuestos configurados (10%, 5%, Exento)
- [ ] 3 Tipos de cliente creados
- [ ] 1 Lista de precios activa
- [ ] 3 Tipos de rol creados
- [ ] 1 Caja configurada
- [ ] 1 Punto de expedición creado
- [ ] 1 Timbrado activo
- [ ] 1 Empleado cajero registrado
- [ ] 2+ Clientes de prueba
- [ ] 5 Productos con stock
- [ ] 5 Precios asignados
- [ ] Caja abierta
- [ ] ✨ PRIMERA VENTA COMPLETADA ✨

---

**¡Felicidades! Ya tienes tu sistema Cantina Tita funcionando.** 🎊

**Fecha:** 24/11/2025  
**Sistema:** Cantina Tita - Gestión Integral  
**Versión Django:** 5.2.8  
**Base de Datos:** MySQL 8.0.44
