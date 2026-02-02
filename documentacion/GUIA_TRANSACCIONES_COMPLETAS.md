# 🍽️ Guía de Transacciones Completas - Sistema Cantina Tita

## 📋 Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Escenario 1: Venta Directa con Efectivo](#escenario-1-venta-directa-con-efectivo)
3. [Escenario 2: Consumo con Tarjeta Estudiantil](#escenario-2-consumo-con-tarjeta-estudiantil)
4. [Escenario 3: Carga de Saldo a Tarjeta](#escenario-3-carga-de-saldo-a-tarjeta)
5. [Escenario 4: Compra a Proveedor](#escenario-4-compra-a-proveedor)
6. [Escenario 5: Plan de Almuerzo Mensual](#escenario-5-plan-de-almuerzo-mensual)
7. [Escenario 6: Nota de Crédito](#escenario-6-nota-de-crédito)
8. [Flujos de Validación](#flujos-de-validación)

---

## 💳 Diferencia: Tipo de Pago vs Medio de Pago

### 📊 Entendiendo la Estructura

**TIPO DE PAGO** = CONDICIÓN de la venta
- Responde: ¿Cuándo se paga?
- Opciones:
  * **CONTADO**: Pago inmediato al momento de la venta
  * **CREDITO**: Pago diferido (a plazo, cuenta corriente)

**MEDIO DE PAGO** = FORMA específica de pago
- Responde: ¿Cómo se paga?
- Opciones:
  * **EFECTIVO**: Dinero en efectivo
  * **TRANSFERENCIA BANCARIA**: Transferencia electrónica
  * **TARJETA DEBITO /QR**: Tarjeta de débito o QR code
  * **TARJETA CREDITO / QR**: Tarjeta de crédito o QR code
  * **GIROS TIGO**: Sistema de giros Tigo Money
  * **TARJETA ESTUDIANTIL**: Tarjeta precargada del estudiante

---

### 🔄 Flujo de Registro en el Sistema

**1. Al crear la VENTA:**
```
Tabla: ventas
Campo: ID_Tipo_Pago
Valores: CONTADO o CREDITO
```

**2. Al registrar el PAGO:**
```
Tabla: pagos_venta
Campo: ID_Medio_Pago
Valores: EFECTIVO, TRANSFERENCIA BANCARIA, TARJETA DEBITO /QR, etc.
```

---

### 📝 Ejemplos Prácticos

**Ejemplo 1: Venta al contado en efectivo**
```
Paso 1 - Crear venta:
  - Tipo Pago: CONTADO
  - Monto: 10,000

Paso 2 - Registrar pago:
  - Medio Pago: EFECTIVO
  - Monto: 10,000
```

**Ejemplo 2: Venta al contado con tarjeta**
```
Paso 1 - Crear venta:
  - Tipo Pago: CONTADO
  - Monto: 50,000

Paso 2 - Registrar pago:
  - Medio Pago: TARJETA CREDITO / QR
  - Monto: 50,000
  - Referencia: Comprobante del POS
```

**Ejemplo 3: Venta a crédito (pago diferido)**
```
Paso 1 - Crear venta:
  - Tipo Pago: CREDITO
  - Monto: 100,000

Paso 2 - Registrar pago (cuando pague):
  - Medio Pago: TRANSFERENCIA BANCARIA
  - Monto: 100,000
  - Referencia: Comprobante bancario
```

**Ejemplo 4: Venta con tarjeta estudiantil**
```
Paso 1 - Crear venta:
  - Tipo Pago: CONTADO
  - Monto: 8,910

Paso 2 - Registrar pago:
  - Medio Pago: TARJETA ESTUDIANTIL
  - Nro tarjeta usada: 1000000001
  - Monto: 8,910
```

---

### ⚙️ Características de Medios de Pago

| Medio de Pago | Genera Comisión | Requiere Validación | Uso Típico |
|---------------|----------------|-------------------|-----------|
| EFECTIVO | ❌ No | ❌ No | Ventas directas en efectivo |
| TRANSFERENCIA BANCARIA | ❌ No | ✅ Sí | Pagos grandes, planes mensuales |
| TARJETA DEBITO /QR | ✅ Sí | ✅ Sí | Ventas con tarjeta débito o QR |
| TARJETA CREDITO / QR | ✅ Sí | ✅ Sí | Ventas con tarjeta crédito o QR |
| GIROS TIGO | ✅ Sí | ✅ Sí | Pagos mediante Tigo Money |
| TARJETA ESTUDIANTIL | ❌ No | ❌ No | Consumos de estudiantes |

**Genera Comisión = Sí**: El sistema puede calcular comisiones bancarias/procesadora
**Requiere Validación = Sí**: Necesita conciliación con extracto bancario/procesadora

---

### 🔧 Configuración de Comisiones

Para medios que generan comisión, configurar en:
```
URL: /admin/gestion/tarifascomision/add/

Ejemplo - Tarjeta de Crédito:
- ID Medio Pago: TARJETA CREDITO / QR
- Fecha inicio vigencia: 01/01/2025
- Porcentaje comisión: 0.0350 (3.5%)
- Monto fijo comisión: 0 (o un monto fijo si aplica)
- Activo: Sí
```

**Cálculo de comisión:**
```
Venta: Gs. 100,000
Comisión 3.5%: Gs. 3,500
Neto a recibir: Gs. 96,500
```

---

## 🚀 Configuración Inicial

### Datos Maestros Necesarios

#### 1. Datos de la Empresa
```
URL: /admin/gestion/datosempresa/add/

Datos requeridos:
- RUC: 80012345-6
- Razón Social: Cantina Tita S.R.L.
- Dirección: Av. Principal 123
- Ciudad: Asunción
- País: Paraguay
- Teléfono: 021-123-4567
- Email: info@cantinatita.com.py
- Activo: 1 (Sí)
```

#### 2. Categorías de Productos
```
URL: /admin/gestion/categoria/add/

Ejemplos:
1. Bebidas (ID: 1)
2. Snacks (ID: 2)
3. Almuerzos (ID: 3)
4. Postres (ID: 4)
```

#### 3. Unidades de Medida
```
URL: /admin/gestion/unidadmedida/add/

Ejemplos:
- Unidad (UN)
- Kilogramo (KG)
- Litro (L)
- Porción (PORCION)
```

#### 4. Impuestos
```
URL: /admin/gestion/impuesto/add/

Configuración Paraguay:
1. IVA 10%
   - Nombre: IVA 10%
   - Porcentaje: 10.00
   - Vigente desde: 01/01/2024
   - Activo: Sí

2. IVA 5%
   - Nombre: IVA 5%
   - Porcentaje: 5.00
   - Vigente desde: 01/01/2024
   - Activo: Sí

3. Exento
   - Nombre: Exento
   - Porcentaje: 0.00
   - Vigente desde: 01/01/2024
   - Activo: Sí
```

#### 5. Tipos de Cliente
```
URL: /admin/gestion/tipocliente/add/

Ejemplos:
- Regular
- VIP
- Estudiante
- Empleado
```

#### 6. Lista de Precios
```
URL: /admin/gestion/listaprecios/add/

Ejemplo:
- Nombre: Precio General
- Moneda: PYG
- Fecha vigencia: 01/11/2025
- Activo: Sí
```

#### 7. Tipos de Rol
```
URL: /admin/gestion/tiporolgeneral/add/

Ejemplos:
- Administrador
- Cajero
- Gerente
```

#### 8. Tipos de Pago
```
URL: /admin/gestion/tipospago/add/

IMPORTANTE: Los Tipos de Pago representan la CONDICIÓN de la venta.

Tipos requeridos:
1. CONTADO - Para ventas pagadas inmediatamente
2. CREDITO - Para ventas con pago diferido

Campos:
- Descripción: CONTADO o CREDITO
- Activo: Sí
```

#### 9. Medios de Pago
```
URL: /admin/gestion/mediospago/add/

IMPORTANTE: Los Medios de Pago son las FORMAS específicas de pago.

Medios requeridos:
1. EFECTIVO
   - Descripción: EFECTIVO
   - Genera comisión: No
   - Requiere validación: No
   - Activo: Sí

2. TRANSFERENCIA BANCARIA
   - Descripción: TRANSFERENCIA BANCARIA
   - Genera comisión: No
   - Requiere validación: Sí
   - Activo: Sí

3. TARJETA DEBITO /QR
   - Descripción: TARJETA DEBITO /QR
   - Genera comisión: Sí
   - Requiere validación: Sí
   - Activo: Sí

4. TARJETA CREDITO / QR
   - Descripción: TARJETA CREDITO / QR
   - Genera comisión: Sí
   - Requiere validación: Sí
   - Activo: Sí

5. GIROS TIGO
   - Descripción: GIROS TIGO
   - Genera comisión: Sí
   - Requiere validación: Sí
   - Activo: Sí

6. TARJETA ESTUDIANTIL
   - Descripción: TARJETA ESTUDIANTIL
   - Genera comisión: No
   - Requiere validación: No
   - Activo: Sí

NOTA IMPORTANTE:
- "Genera comisión" = Sí: El medio cobra comisión (tarjetas, giros)
- "Requiere validación" = Sí: Necesita conciliación/confirmación del banco
```

#### 10. Cajas
```
URL: /admin/gestion/cajas/add/

Ejemplo:
- Nombre: Caja 1
- Ubicación: Planta Baja
- Activo: 1
```

#### 11. Puntos de Expedición
```
URL: /admin/gestion/puntosexpedicion/add/

Ejemplo:
- Código establecimiento: 001
- Código punto expedición: 001
- Descripción ubicación: Caja Principal
- Activo: Sí
```

#### 12. Timbrados
```
URL: /admin/gestion/timbrados/add/

Ejemplo:
- Nro Timbrado: 12345678
- Tipo documento: Factura
- Nro inicio: 001-001-0000001
- Nro fin: 001-001-0001000
- Fecha inicio: 01/01/2025
- Fecha fin: 31/12/2025
- Es electrónico: Sí
- ID Punto: [Seleccionar punto]
- Activo: Sí
```

---

## 📦 Escenario 1: Venta Directa con Efectivo

### Flujo Completo: Cliente compra productos y paga en efectivo

#### **Paso 1: Crear Empleado Cajero**
```
URL: /admin/gestion/empleado/add/

Datos:
- Usuario: cajero01
- Nombre: María
- Apellido: González
- ID Rol: Cajero
- Email: maria.gonzalez@cantinatita.com.py
- Teléfono: 0981-123456
- Ciudad: Asunción
- Dirección: Barrio Centro
- Fecha ingreso: 01/11/2025
- Activo: Sí
```

#### **Paso 2: Crear Cliente**
```
URL: /admin/gestion/cliente/add/

Datos:
- RUC/CI: 4567891-2
- Nombres: Juan
- Apellidos: Pérez
- Razón Social: (dejar vacío para persona física)
- ID Tipo Cliente: Regular
- Email: juan.perez@example.com
- Teléfono: 0982-654321
- Ciudad: Asunción
- Activo: Sí
```

#### **Paso 3: Crear Productos**
```
URL: /admin/gestion/producto/add/

Producto 1: Coca Cola 500ml
- Código: COC500
- Descripción: Coca Cola 500ml
- ID Categoría: Bebidas
- ID Unidad: Unidad
- ID Impuesto: IVA 10%
- Stock mínimo: 20.000
- Requiere lote: No
- Activo: Sí

Producto 2: Empanada de Carne
- Código: EMP001
- Descripción: Empanada de Carne
- ID Categoría: Snacks
- ID Unidad: Unidad
- ID Impuesto: IVA 10%
- Stock mínimo: 50.000
- Requiere lote: No
- Activo: Sí
```

#### **Paso 4: Registrar Stock Inicial**
```
URL: /admin/gestion/stockunico/add/

Para Coca Cola:
- ID Producto: Coca Cola 500ml
- Stock actual: 100.000
- Fecha última actualización: [automático]

Para Empanada:
- ID Producto: Empanada de Carne
- Stock actual: 200.000
```

#### **Paso 5: Asignar Precios**
```
URL: /admin/gestion/preciosporlista/add/

Para Coca Cola:
- ID Producto: Coca Cola 500ml
- ID Lista: Precio General
- Precio unitario neto: 4500 (sin IVA)
- Fecha vigencia: 01/11/2025

Para Empanada:
- ID Producto: Empanada de Carne
- ID Lista: Precio General
- Precio unitario neto: 3600 (sin IVA)
- Fecha vigencia: 01/11/2025
```

#### **Paso 6: Abrir Caja**
```
URL: /admin/gestion/cierrescaja/add/

Datos:
- ID Caja: Caja 1
- ID Empleado: María González (cajero)
- Fecha hora apertura: 24/11/2025 08:00:00
- Monto inicial: 50000.00
- Estado: (dejar vacío = caja abierta)
```

#### **Paso 7: Crear Documento Tributario**
```
URL: /admin/gestion/documentostributarios/add/

Datos obligatorios:
- Nro timbrado: [Seleccionar timbrado activo, ej: "Timbrado 12345678 - Factura"]
- Nro secuencial: 1 (IMPORTANTE: Solo número entero, NO "001-001-0000001")
- Fecha emisión:
  * Fecha: 24/11/2025
  * Hora: 10:30:00
- Monto total: 8910

Cálculo de IVA (para productos gravados 10%):
- Monto exento: 0 (o dejar vacío si no aplica)
- Monto gravado 5: 0 (o dejar vacío si no aplica)
- Monto iva 5: 0 (o dejar vacío si no aplica)
- Monto gravado 10: 8100 (suma de precios netos: 4500 + 3600)
- Monto iva 10: 810 (10% de 8100)

NOTA: El número de documento completo (001-001-0000001) se forma automáticamente
combinando el timbrado con el número secuencial.
```

**⚠️ ERRORES COMUNES:**

1. **Error: "Nro secuencial inválido"**
   - ❌ Incorrecto: "001-001-0000001" o "001-001-"
   - ✅ Correcto: 1 (solo el número)

2. **Error: "Este campo es obligatorio" en Monto total**
   - Debes calcular y completar TODOS los montos
   - Monto total = Suma de todos los subtotales con IVA

3. **Stock ya existe al crear productos**
   - En lugar de crear nuevo stock en /add/
   - Ve a /admin/gestion/stockunico/ y EDITA el existente

#### **Paso 8: Crear la Venta**
```
URL: /admin/gestion/ventas/add/

Datos:
- ID Documento: [Seleccionar documento creado]
- ID Cliente: Juan Pérez
- ID Tipo Pago: CONTADO (condición de venta)
- ID Empleado Cajero: María González
- Fecha: 24/11/2025 10:30:00
- Tipo Venta: Venta Directa
- Monto Total: 8910 (4950 Coca + 3960 Empanada)
  * Coca: 4500 + 10% = 4950
  * Empanada: 3600 + 10% = 3960
  * Total: 8910
- Estado: Completada

NOTA: ID Tipo Pago es CONTADO o CREDITO (condición de venta).
      El medio de pago específico (EFECTIVO, TARJETA, etc.) 
      se registra en el Paso 11.
```

#### **Paso 9: Agregar Detalle de Venta**
```
URL: /admin/gestion/detalleventa/add/

Detalle 1 - Coca Cola:
- ID Venta: [Venta recién creada]
- ID Producto: Coca Cola 500ml
- Cantidad: 1.000
- Precio unitario total: 4950 (con IVA)
- Subtotal total: 4950
- Monto IVA: 450

Detalle 2 - Empanada:
- ID Venta: [Venta recién creada]
- ID Producto: Empanada de Carne
- Cantidad: 1.000
- Precio unitario total: 3960 (con IVA)
- Subtotal total: 3960
- Monto IVA: 360
```

#### **Paso 10: Registrar Movimiento de Stock**
```
URL: /admin/gestion/movimientosstock/add/

Movimiento 1 - Coca Cola:
- ID Producto: Coca Cola 500ml
- Tipo movimiento: Venta
- Cantidad: 1.000
- Fecha hora: 24/11/2025 10:30:00
- ID Empleado responsable: María González
- Observaciones: Venta #1 - Juan Pérez

Movimiento 2 - Empanada:
- ID Producto: Empanada de Carne
- Tipo movimiento: Venta
- Cantidad: 1.000
- Fecha hora: 24/11/2025 10:30:00
- ID Empleado responsable: María González
```

#### **Paso 11: Registrar Pago**
```
URL: /admin/gestion/pagosventa/add/

Datos:
- ID Venta: [Venta recién creada]
- ID Medio Pago: EFECTIVO (forma específica de pago)
- Monto: 8910
- Fecha hora: 24/11/2025 10:30:00
- Nro transacción: (dejar vacío para efectivo)

NOTA IMPORTANTE:
Aquí se registra el MEDIO DE PAGO específico usado:
- EFECTIVO: No requiere validación
- TRANSFERENCIA BANCARIA: Requiere validación
- TARJETA DEBITO /QR: Genera comisión, requiere validación
- TARJETA CREDITO / QR: Genera comisión, requiere validación
- GIROS TIGO: Genera comisión, requiere validación
- TARJETA ESTUDIANTIL: Para consumos con tarjeta precargada
```

#### **Paso 12: Actualizar Stock**
```
URL: /admin/gestion/stockunico/[id]/change/

Stock Coca Cola:
- Stock actual: 99.000 (100 - 1)

Stock Empanada:
- Stock actual: 199.000 (200 - 1)
```

### ✅ Resultado Esperado:
- ✓ Cliente registrado
- ✓ Venta completada
- ✓ Factura emitida (001-001-0000001)
- ✓ Stock actualizado
- ✓ Pago registrado en efectivo
- ✓ Caja actualizada con ingreso

---

## 🎴 Escenario 2: Consumo con Tarjeta Estudiantil

### Flujo Completo: Estudiante compra con tarjeta precargada

#### **Paso 1: Registrar Cliente Padre/Tutor**
```
URL: /admin/gestion/cliente/add/

Datos:
- RUC/CI: 3456789-1
- Nombres: Carmen
- Apellidos: Rodríguez
- ID Tipo Cliente: Regular
- Email: carmen.rodriguez@example.com
- Teléfono: 0983-111222
- Ciudad: Asunción
- Activo: Sí
```

#### **Paso 2: Registrar Hijo/Estudiante**
```
URL: /admin/gestion/hijo/add/

Datos:
- Nombre: Pedro
- Apellido: Rodríguez
- Fecha nacimiento: 15/05/2010
- ID Cliente Responsable: Carmen Rodríguez
- Curso: 7mo Grado
- Institucion educativa: Colegio Nacional
- Activo: Sí
```

#### **Paso 3: Emitir Tarjeta Estudiantil**
```
URL: /admin/gestion/tarjeta/add/

Datos:
- Nro Tarjeta: 1000000001
- ID Hijo: Pedro Rodríguez
- Saldo Actual: 0 (se cargará después)
- Fecha creación: 24/11/2025
- Estado: Activa
```

#### **Paso 4: Cargar Saldo Inicial a la Tarjeta**
```
URL: /admin/gestion/cargassaldo/add/

Datos:
- Nro Tarjeta: 1000000001
- ID Cliente Origen: Carmen Rodríguez
- Fecha carga: 24/11/2025 08:00:00
- Monto cargado: 50000.00
- Referencia: Carga inicial - Efectivo
```

#### **Paso 5: Actualizar Saldo de Tarjeta**
```
URL: /admin/gestion/tarjeta/[id]/change/

- Saldo Actual: 50000.00
```

#### **Paso 6: Crear Documento para Consumo**
```
URL: /admin/gestion/documentostributarios/add/

Datos:
- ID Timbrado: [Timbrado activo]
- Nro documento: 001-001-0000002
- Tipo documento: Factura
- Condición venta: Contado
- Fecha emisión: 24/11/2025 12:00:00
- Estado documento: Emitido
```

#### **Paso 7: Registrar Venta con Tarjeta**
```
URL: /admin/gestion/ventas/add/

Datos:
- ID Documento: 001-001-0000002
- ID Cliente: Carmen Rodríguez
- ID Hijo: Pedro Rodríguez
- ID Tipo Pago: CONTADO (condición de venta)
- ID Empleado Cajero: María González
- Fecha: 24/11/2025 12:00:00
- Tipo Venta: Consumo Tarjeta
- Monto Total: 8910
- Estado: Completada

NOTA: El medio de pago TARJETA ESTUDIANTIL se registra en el paso siguiente.
```

#### **Paso 8: Agregar Detalles de Consumo**
```
URL: /admin/gestion/detalleventa/add/

(Usar mismos productos del Escenario 1)
- Coca Cola: 4950
- Empanada: 3960
```

#### **Paso 9: Registrar Movimientos de Stock**
```
(Igual que Escenario 1)
```

#### **Paso 10: Registrar Pago con Tarjeta**
```
URL: /admin/gestion/pagosventa/add/

Datos:
- ID Venta: [Venta recién creada]
- ID Medio Pago: TARJETA ESTUDIANTIL
- Nro tarjeta usada: 1000000001 (seleccionar tarjeta)
- Monto: 8910
- Fecha hora: 24/11/2025 12:00:00
- Nro transacción: CONSUMO-1000000001
```

#### **Paso 11: Actualizar Saldo de Tarjeta**
```
URL: /admin/gestion/tarjeta/[id]/change/

- Saldo Actual: 41090.00 (50000 - 8910)
```

#### **Paso 12: Registrar en Cuenta Corriente**
```
URL: /admin/gestion/ctacorriente/add/

Datos:
- ID Cliente: Carmen Rodríguez
- ID Venta: [Venta recién creada]
- Tipo Movimiento: Cargo
- Monto: 8910
- Fecha: 24/11/2025 12:00:00
- Referencia Doc: CONSUMO-TARJ-1000000001
- Saldo Acumulado: 8910
```

### ✅ Resultado Esperado:
- ✓ Tarjeta estudiantil emitida
- ✓ Saldo cargado: Gs. 50.000
- ✓ Consumo registrado: Gs. 8.910
- ✓ Saldo restante: Gs. 41.090
- ✓ Factura emitida
- ✓ Stock actualizado

---

## 💰 Escenario 3: Carga de Saldo a Tarjeta

### Flujo: Padre recarga saldo en tarjeta de hijo

#### **Paso 1: Crear Documento para Recarga**
```
URL: /admin/gestion/documentostributarios/add/

Datos:
- Nro documento: 001-001-0000003
- Tipo documento: Factura
- Condición venta: Contado
- Fecha emisión: 25/11/2025 09:00:00
```

#### **Paso 2: Crear Venta de Recarga**
```
URL: /admin/gestion/ventas/add/

Datos:
- ID Documento: 001-001-0000003
- ID Cliente: Carmen Rodríguez
- ID Hijo: Pedro Rodríguez
- ID Tipo Pago: CONTADO
- ID Empleado Cajero: María González
- Fecha: 25/11/2025 09:00:00
- Tipo Venta: Carga Saldo
- Monto Total: 100000
- Estado: Completada
```

#### **Paso 3: Registrar Carga de Saldo**
```
URL: /admin/gestion/cargassaldo/add/

Datos:
- Nro Tarjeta: 1000000001
- ID Cliente Origen: Carmen Rodríguez
- Fecha carga: 25/11/2025 09:00:00
- Monto cargado: 100000.00
- Referencia: Recarga - Venta #[ID]
```

#### **Paso 4: Registrar Pago**
```
URL: /admin/gestion/pagosventa/add/

Datos:
- ID Venta: [Venta de recarga]
- ID Medio Pago: EFECTIVO
- Monto: 100000
- Fecha hora: 25/11/2025 09:00:00
- Referencia transacción: (dejar vacío)
```

#### **Paso 5: Actualizar Saldo Tarjeta**
```
URL: /admin/gestion/tarjeta/[id]/change/

- Saldo Actual: 141090.00 (41090 + 100000)
```

### ✅ Resultado Esperado:
- ✓ Recarga procesada: Gs. 100.000
- ✓ Saldo nuevo: Gs. 141.090
- ✓ Factura de recarga emitida
- ✓ Pago en efectivo registrado

---

## 📦 Escenario 4: Compra a Proveedor

### Flujo Completo: Comprar productos a proveedor

#### **Paso 1: Registrar Proveedor**
```
URL: /admin/gestion/proveedor/add/

Datos:
- RUC: 80098765-4
- Razón Social: Distribuidora La Economía S.A.
- Contacto: Jorge Benítez
- Teléfono: 021-555-4444
- Email: ventas@laeconomia.com.py
- Ciudad: Asunción
- Dirección: Av. España 456
- Activo: Sí
```

#### **Paso 2: Crear Compra**
```
URL: /admin/gestion/compras/add/

Datos:
- ID Proveedor: Distribuidora La Economía
- Fecha: 24/11/2025 14:00:00
- Monto Total: 500000
- Nro Factura: 001-001-0012345
- Observaciones: Compra semanal - Bebidas y snacks
```

#### **Paso 3: Registrar Detalle de Compra**
```
URL: /admin/gestion/detallecompra/add/

Detalle 1:
- ID Compra: [Compra recién creada]
- ID Producto: Coca Cola 500ml
- Cantidad: 100.000
- Costo unitario neto: 3500
- Subtotal neto: 350000

Detalle 2:
- ID Compra: [Compra recién creada]
- ID Producto: Empanada de Carne
- Cantidad: 50.000
- Costo unitario neto: 3000
- Subtotal neto: 150000
```

#### **Paso 4: Registrar Costo Histórico**
```
URL: /admin/gestion/costoshistoricos/add/

Para Coca Cola:
- ID Producto: Coca Cola 500ml
- ID Compra: [Compra recién creada]
- Costo unitario neto: 3500
- Fecha compra: 24/11/2025 14:00:00

Para Empanada:
- ID Producto: Empanada de Carne
- ID Compra: [Compra recién creada]
- Costo unitario neto: 3000
- Fecha compra: 24/11/2025 14:00:00
```

#### **Paso 5: Registrar Movimientos de Stock**
```
URL: /admin/gestion/movimientosstock/add/

Movimiento 1 - Coca Cola:
- ID Producto: Coca Cola 500ml
- Tipo movimiento: Compra
- Cantidad: 100.000
- Fecha hora: 24/11/2025 14:00:00
- ID Empleado responsable: [Empleado encargado]
- Observaciones: Compra #[ID] - La Economía

Movimiento 2 - Empanada:
- ID Producto: Empanada de Carne
- Tipo movimiento: Compra
- Cantidad: 50.000
- Fecha hora: 24/11/2025 14:00:00
```

#### **Paso 6: Actualizar Stock**
```
URL: /admin/gestion/stockunico/[id]/change/

Stock Coca Cola:
- Stock actual: 199.000 (99 + 100)

Stock Empanada:
- Stock actual: 249.000 (199 + 50)
```

#### **Paso 7: Registrar en Cuenta Corriente Proveedor**
```
URL: /admin/gestion/ctacorrienteprov/add/

Datos:
- ID Proveedor: Distribuidora La Economía
- ID Compra: [Compra recién creada]
- Tipo Movimiento: Cargo
- Monto: 500000
- Fecha: 24/11/2025 14:00:00
- Saldo Acumulado: 500000
- Referencia Doc: FACT-001-001-0012345
```

### ✅ Resultado Esperado:
- ✓ Compra registrada: Gs. 500.000
- ✓ Stock actualizado (+100 Coca Cola, +50 Empanadas)
- ✓ Costos históricos registrados
- ✓ Deuda con proveedor: Gs. 500.000

---

## 🍽️ Escenario 5: Plan de Almuerzo Mensual

### Flujo Completo: Suscribir estudiante a plan de almuerzo

#### **Paso 1: Crear Plan de Almuerzo**
```
URL: /admin/gestion/planesalmuerzo/add/

Datos:
- Nombre Plan: Plan Completo - Almuerzo Diario
- Descripción: Incluye almuerzo de lunes a viernes
- Precio Mensual: 450000.00
- Días Semana Incluidos: Lunes,Martes,Miércoles,Jueves,Viernes
- Fecha Creación: 24/11/2025
- Activo: Sí
```

#### **Paso 2: Crear Suscripción**
```
URL: /admin/gestion/suscripcionesalmuerzo/add/

Datos:
- ID Hijo: Pedro Rodríguez
- ID Plan Almuerzo: Plan Completo
- Fecha Inicio: 01/12/2025
- Fecha Fin: 31/12/2025
- Estado: Activa
```

#### **Paso 3: Crear Documento para Pago Mensual**
```
URL: /admin/gestion/documentostributarios/add/

Datos:
- Nro documento: 001-001-0000004
- Tipo documento: Factura
- Condición venta: Contado
- Fecha emisión: 24/11/2025 16:00:00
```

#### **Paso 4: Registrar Venta de Plan**
```
URL: /admin/gestion/ventas/add/

Datos:
- ID Documento: 001-001-0000004
- ID Cliente: Carmen Rodríguez
- ID Hijo: Pedro Rodríguez
- ID Tipo Pago: CONTADO (o CREDITO si paga a fin de mes)
- ID Empleado Cajero: María González
- Fecha: 24/11/2025 16:00:00
- Tipo Venta: Pago Almuerzo
- Monto Total: 450000
- Estado: Completada
```

#### **Paso 5: Registrar Pago Mensual**
```
URL: /admin/gestion/pagosalmuerzomensual/add/

Datos:
- ID Suscripción: [Suscripción recién creada]
- Mes Pagado: 12 (Diciembre)
- Anio Pagado: 2025
- ID Venta: [Venta del plan]
- Monto Pagado: 450000.00
- Fecha Pago: 24/11/2025 16:00:00
- Estado Pago: Pagado
```

#### **Paso 6: Registrar Pago**
```
URL: /admin/gestion/pagosventa/add/

Datos:
- ID Venta: [Venta del plan]
- ID Medio Pago: EFECTIVO (o TRANSFERENCIA BANCARIA según el caso)
- Monto: 450000
- Fecha hora: 24/11/2025 16:00:00
- Referencia transacción: (si es transferencia, incluir comprobante)
```

#### **Paso 7: Registrar Consumo Diario** (por cada día)
```
URL: /admin/gestion/registroconsumoalmuerzo/add/

Ejemplo - Día 1:
- ID Suscripción: [Suscripción de Pedro]
- Fecha Consumo: 02/12/2025
- Hora Consumo: 12:30:00
- Consumido: Sí
- Observaciones: Menú del día: Milanesa con ensalada
```

### ✅ Resultado Esperado:
- ✓ Plan creado: Gs. 450.000/mes
- ✓ Suscripción activa diciembre 2025
- ✓ Pago mensual registrado
- ✓ Factura emitida
- ✓ Control diario de consumo habilitado

---

## 📝 Escenario 6: Nota de Crédito

### Flujo: Devolución de productos

#### **Paso 1: Identificar Venta Original**
```
Venta a devolver: #1 (Juan Pérez)
Monto original: Gs. 8.910
Motivo: Producto en mal estado (Coca Cola)
```

#### **Paso 2: Crear Documento Nota de Crédito**
```
URL: /admin/gestion/documentostributarios/add/

Datos:
- Nro documento: 001-001-0000005
- Tipo documento: Nota Crédito
- Condición venta: Contado
- Fecha emisión: 24/11/2025 17:00:00
```

#### **Paso 3: Crear Nota de Crédito**
```
URL: /admin/gestion/notascredito/add/

Datos:
- ID Documento: 001-001-0000005
- ID Venta Original: Venta #1
- Fecha Emisión: 24/11/2025 17:00:00
- Monto Total: 4950 (solo Coca Cola)
- Motivo: Producto en mal estado - devolución
```

#### **Paso 4: Registrar Detalle de Nota**
```
URL: /admin/gestion/detallenota/add/

Datos:
- ID Nota: [Nota recién creada]
- ID Producto: Coca Cola 500ml
- Cantidad Devuelta: 1.000
- Precio Unitario: 4950
- Subtotal: 4950
- Monto IVA: 450
```

#### **Paso 5: Ajustar Stock (devolución)**
```
URL: /admin/gestion/movimientosstock/add/

Datos:
- ID Producto: Coca Cola 500ml
- Tipo movimiento: Devolucion
- Cantidad: 1.000
- Fecha hora: 24/11/2025 17:00:00
- ID Empleado responsable: María González
- Observaciones: Nota Crédito #[ID] - Producto defectuoso
```

#### **Paso 6: Actualizar Stock**
```
URL: /admin/gestion/stockunico/[id]/change/

Stock Coca Cola:
- Stock actual: 200.000 (199 + 1)
```

#### **Paso 7: Registrar en Cuenta Corriente**
```
URL: /admin/gestion/ctacorriente/add/

Datos:
- ID Cliente: Juan Pérez
- ID Nota Crédito: [Nota recién creada]
- Tipo Movimiento: Abono
- Monto: 4950
- Fecha: 24/11/2025 17:00:00
- Referencia Doc: NC-001-001-0000005
- Saldo Acumulado: -4950 (favor del cliente)
```

### ✅ Resultado Esperado:
- ✓ Nota de crédito emitida: Gs. 4.950
- ✓ Stock ajustado (+1 Coca Cola)
- ✓ Cliente con saldo a favor: Gs. 4.950
- ✓ Documento fiscal correcto

---

## 🔍 Flujos de Validación

### Validación 1: Stock Bajo
```
URL: /admin/gestion/vistastockalerta/

Verificar:
- Productos con Stock_Actual <= Stock_Minimo
- Nivel de alerta (AGOTADO, CRÍTICO, BAJO)
- Tomar acción según sea necesario
```

### Validación 2: Saldos Clientes
```
URL: /admin/gestion/vistasaldoclientes/

Verificar:
- Clientes con saldo pendiente
- Saldo acumulado por cliente
- Última actualización
- Total de movimientos
```

### Validación 3: Cierre de Caja
```
URL: /admin/gestion/cierrescaja/[id]/change/

Al finalizar turno:
- Fecha hora cierre: 24/11/2025 18:00:00
- Monto contado físico: [contar efectivo]
- Diferencia efectivo: [calcular]
- Estado: Cerrada
```

### Validación 4: Alertas del Sistema
```
URL: /admin/gestion/alertassistema/

Revisar alertas:
- Stock Bajo
- Saldo Bajo (tarjetas)
- Timbrado Próximo a Vencer
- Otras alertas del sistema
```

### Validación 5: Cuenta Corriente Proveedores
```
URL: /admin/gestion/ctacorrienteprov/

Verificar:
- Deudas pendientes
- Próximos vencimientos
- Saldo acumulado por proveedor
```

### Validación 6: Conciliación de Pagos
```
URL: /admin/gestion/conciliacionpagos/

Para pagos con tarjeta:
- Verificar fecha acreditación
- Confirmar monto acreditado
- Actualizar estado a "Conciliado"
```

---

## 📊 Reportes Sugeridos

### Reporte Diario de Ventas
```sql
-- Ver todas las ventas del día
SELECT 
    v.ID_Venta,
    c.Nombres + ' ' + c.Apellidos AS Cliente,
    v.Monto_Total,
    v.Tipo_Venta,
    v.Estado
FROM ventas v
JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
WHERE DATE(v.Fecha) = '2025-11-24'
ORDER BY v.Fecha DESC;
```

### Reporte de Stock Actual
```sql
-- Stock de todos los productos
SELECT 
    p.Codigo,
    p.Descripcion,
    s.Stock_Actual,
    p.Stock_Minimo,
    CASE 
        WHEN s.Stock_Actual <= 0 THEN 'AGOTADO'
        WHEN s.Stock_Actual <= p.Stock_Minimo * 0.5 THEN 'CRÍTICO'
        WHEN s.Stock_Actual <= p.Stock_Minimo THEN 'BAJO'
        ELSE 'NORMAL'
    END AS Estado
FROM productos p
JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
ORDER BY Estado DESC, s.Stock_Actual ASC;
```

### Reporte de Saldos Tarjetas
```sql
-- Saldos de todas las tarjetas activas
SELECT 
    t.Nro_Tarjeta,
    h.Nombre + ' ' + h.Apellido AS Estudiante,
    c.Nombres + ' ' + c.Apellidos AS Responsable,
    t.Saldo_Actual,
    t.Estado
FROM tarjetas t
JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
WHERE t.Estado = 'Activa'
ORDER BY t.Saldo_Actual ASC;
```

---

## 💡 Tips y Buenas Prácticas

### ✅ Al Crear Ventas:
1. Siempre crear el documento tributario primero
2. Verificar que hay stock suficiente
3. Calcular correctamente el IVA (precio neto + IVA)
4. Registrar movimiento de stock inmediatamente
5. Actualizar el stock_unico después de cada venta

### ✅ Al Manejar Tarjetas:
1. Validar saldo antes de permitir consumo
2. Registrar todas las cargas de saldo
3. Mantener historial de movimientos
4. Alertar cuando saldo sea bajo (< Gs. 10.000)

### ✅ Al Comprar a Proveedores:
1. Registrar costo histórico para análisis de precio
2. Actualizar stock inmediatamente
3. Llevar control de cuenta corriente
4. Programar alertas de vencimiento de pagos

### ✅ Al Gestionar Planes de Almuerzo:
1. Controlar consumo diario
2. Emitir alertas si no hay consumo por varios días
3. Facturar al inicio del mes
4. Validar que suscripción esté activa

### ✅ Al Emitir Notas de Crédito:
1. Referenciar siempre la venta original
2. Devolver productos al stock si corresponde
3. Actualizar cuenta corriente del cliente
4. Mantener trazabilidad completa

---

## 🎯 Checklist de Validación Diaria

- [ ] Abrir caja con monto inicial
- [ ] Verificar stock bajo (Vista Stock Alerta)
- [ ] Revisar alertas del sistema
- [ ] Procesar ventas del día
- [ ] Actualizar stock después de cada venta
- [ ] Registrar consumos de almuerzos
- [ ] Revisar saldos de tarjetas bajos
- [ ] Procesar recargas de tarjetas
- [ ] Cerrar caja al final del turno
- [ ] Verificar diferencia de caja
- [ ] Generar reporte de ventas del día
- [ ] Backup de datos (recomendado)

---

## ⚠️ Problemas Comunes y Soluciones

### Error 1: "Ya existe Stock con este Id producto"

**Causa:** La tabla `stock_unico` permite solo UN registro por producto (restricción UNIQUE).

**Solución RECOMENDADA - Editar el existente:**
```
1. Ve a: http://localhost:8000/admin/gestion/stockunico/
2. Busca el producto (ej: COC500 - Coca Cola 500ml)
3. Click en el registro existente para editarlo
4. Modifica Stock actual y Fecha última actualización
5. Guarda los cambios
```

**Alternativa - Eliminar y crear nuevo:**
```
1. Ve a: http://localhost:8000/admin/gestion/stockunico/
2. Busca y marca el checkbox del producto
3. En "Acción": Selecciona "Eliminar"
4. Confirma la eliminación
5. Ahora puedes crear uno nuevo en /add/
```

---

### Error 2: Documento Tributario - Campo "Nro secuencial"

**Error:** "Ingresa un número entero" o "Este campo es obligatorio"

**Causa:** El campo `nro_secuencial` es de tipo INTEGER, no acepta texto.

**❌ Valores INCORRECTOS:**
- "001-001-0000001" (formato completo)
- "001-001-" (formato incompleto)
- "0000001" (con ceros a la izquierda)

**✅ Valor CORRECTO:**
- `1` (solo el número entero)
- `2` (para el segundo documento)
- `3` (para el tercero), etc.

**Explicación:** 
El sistema combina automáticamente:
- Establecimiento del timbrado: 001
- Punto expedición del timbrado: 001
- Número secuencial que ingresas: 1
- Resultado final: 001-001-0000001

---

### Error 3: Documento Tributario - Campos de montos vacíos

**Error:** "Este campo es obligatorio" en Monto total

**Causa:** El campo `monto_total` es obligatorio y no puede estar vacío.

**Cálculo correcto para venta de ejemplo (Coca Cola + Empanada):**

```
Producto 1 - Coca Cola:
  Precio neto: 4,500 Gs.
  IVA 10%: 450 Gs.
  Total: 4,950 Gs.

Producto 2 - Empanada:
  Precio neto: 3,600 Gs.
  IVA 10%: 360 Gs.
  Total: 3,960 Gs.

DOCUMENTO TRIBUTARIO:
  Monto exento: 0 (dejar vacío o poner 0)
  Monto gravado 5: 0 (dejar vacío o poner 0)
  Monto iva 5: 0 (dejar vacío o poner 0)
  Monto gravado 10: 8,100 (4,500 + 3,600)
  Monto iva 10: 810 (450 + 360)
  Monto total: 8,910 (4,950 + 3,960)
```

**Fórmulas:**
- `Monto gravado 10 = Suma de precios netos (sin IVA)`
- `Monto iva 10 = Monto gravado 10 × 0.10`
- `Monto total = Monto gravado 10 + Monto iva 10`

---

### Error 4: "Datos truncados para la columna 'Tipo_Venta'"

**Error:** (1265, "Datos truncados para la columna 'Tipo_Venta' en la fila 1")

**Causa:** Campo `Tipo_Venta` en MySQL muy corto (solo 19 caracteres).

**Solución YA APLICADA en esta instalación:**
- Django model actualizado: max_length 19 → 20
- SQL ejecutado: `ALTER TABLE ventas MODIFY COLUMN Tipo_Venta VARCHAR(20)`

**Si el error persiste, ejecuta en MySQL:**
```sql
ALTER TABLE ventas 
MODIFY COLUMN Tipo_Venta VARCHAR(20) NOT NULL;
```

---

### Error 5: "Datos truncados para la columna 'Dias_Semana_Incluidos'"

**Error:** (1265, "Datos truncados para la columna 'Dias_Semana_Incluidos' en la fila 1")

**Causa:** Campo muy corto (52 caracteres) para días completos con acentos.

**Solución YA APLICADA en esta instalación:**
- Django model actualizado: max_length 52 → 60
- SQL ejecutado: `ALTER TABLE planes_almuerzo MODIFY COLUMN Dias_Semana_Incluidos VARCHAR(60)`

**Formato correcto para días de semana:**
```
✅ Correcto: Lunes,Martes,Miércoles,Jueves,Viernes
✅ Correcto: Lunes, Martes, Miércoles, Jueves, Viernes (con espacios)
✅ Correcto: Lunes,Martes,Miércoles,Jueves,Viernes,Sábado,Domingo
❌ Evitar: LUNES,MARTES (mayúsculas, aunque funciona)
```

---

### Error 6: "Se viola la restricción de comprobación 'impuestos_chk_2'"

**Error:** (3819, "Se viola la restricción de comprobación 'impuestos_chk_2'.")

**Causa:** Intentas crear impuesto "Exento" con Porcentaje=0, pero la restricción CHECK requiere `Porcentaje > 0`.

**Solución - Modificar restricción en MySQL:**
```sql
-- Eliminar restricción actual
ALTER TABLE impuestos DROP CHECK impuestos_chk_2;

-- Crear nueva restricción permitiendo 0%
ALTER TABLE impuestos 
ADD CONSTRAINT impuestos_chk_2 
CHECK (Porcentaje >= 0 AND Porcentaje <= 100);
```

**Después de ejecutar el SQL:**
- Podrás crear impuesto "Exento" con Porcentaje = 0.00
- También funcionarán IVA 5% y IVA 10%

---

### Error 7: Productos sin precio al crear venta

**Error:** "No se puede calcular el total" o precio aparece en 0

**Causa:** No hay precio asignado en `precios_por_lista` para el producto.

**Solución:**
```
1. Ve a: /admin/gestion/preciosporlista/add/
2. Completa:
   - ID Producto: [Selecciona tu producto]
   - ID Lista: Precio General
   - Precio unitario neto: [Precio SIN IVA]
   - Fecha vigencia: [Fecha actual o anterior]
3. Guarda
4. Ahora el producto tendrá precio en las ventas
```

**Verificación:**
```sql
SELECT 
    p.Codigo,
    p.Descripcion,
    pp.Precio_Unitario_Neto,
    pp.Fecha_Vigencia
FROM productos p
LEFT JOIN precios_por_lista pp ON p.ID_Producto = pp.ID_Producto
WHERE p.Codigo = 'COC500';
```

---

### Error 8: "No se puede eliminar o actualizar - violación de clave foránea"

**Error:** (1451, "Cannot delete or update a parent row: a foreign key constraint fails")

**Causa:** Intentas eliminar un registro que está siendo referenciado por otros registros.

**Ejemplo común:**
- No puedes eliminar un Cliente si tiene Ventas registradas
- No puedes eliminar un Producto si tiene Stock, Movimientos o Precios

**Solución:**
```
Opción 1 - Eliminar registros dependientes primero:
  1. Elimina las Ventas del cliente
  2. Elimina los Movimientos de stock
  3. Elimina el registro de Stock
  4. Ahora puedes eliminar el Producto

Opción 2 - Marcar como inactivo (RECOMENDADO):
  1. En lugar de eliminar, edita el registro
  2. Cambia el campo "Activo" a "No" o desmarca el checkbox
  3. El registro se mantiene para históricos pero no aparece en selecciones
```

---

### Error 9: Fecha/Hora con formato incorrecto

**Error:** "Ingresa una fecha/hora válida" o "Este campo es obligatorio"

**Formatos correctos:**

**Para campos de FECHA:**
```
✅ Correcto: 24/11/2025
✅ Correcto: 2025-11-24
❌ Incorrecto: 24-11-2025
❌ Incorrecto: 11/24/2025
```

**Para campos de FECHA Y HORA:**
```
✅ Correcto: 24/11/2025 10:30:00
✅ Correcto: 2025-11-24 10:30:00
❌ Incorrecto: 24/11/2025 10:30 (falta segundos)
❌ Incorrecto: 24/11/2025 10:30:00 AM (no usar AM/PM)
```

**Usar el selector del navegador:**
- Click en el ícono de calendario 📅
- Selecciona la fecha visualmente
- Click en el ícono de reloj 🕐 (si aplica)
- Selecciona hora y minutos

---

### Error 10: Caja cerrada al intentar crear venta

**Error:** "No hay caja abierta" o "La caja está cerrada"

**Causa:** No hay un registro de apertura de caja activo.

**Solución:**
```
1. Ve a: /admin/gestion/cierrescaja/add/
2. Completa:
   - ID Caja: [Selecciona tu caja]
   - ID Empleado: [Cajero responsable]
   - Fecha hora apertura: [Fecha y hora actual]
   - Monto inicial: [Efectivo con el que inicia, ej: 50000]
   - Estado: (dejar VACÍO = caja abierta)
   - Fecha hora cierre: (dejar VACÍO)
3. Guarda
4. Ahora puedes registrar ventas
```

**Al finalizar el turno:**
```
1. Ve a: /admin/gestion/cierrescaja/[id]/change/
2. Completa:
   - Fecha hora cierre: [Hora actual]
   - Monto final: [Total contado en caja]
   - Diferencia efectivo: [Se calcula automático]
   - Estado: Cerrada
3. Guarda
```

---

## 📞 Soporte

Para dudas sobre transacciones específicas:
- Revisar esta guía primero
- Consultar documentación de modelos en `gestion/models.py`
- Verificar admin panels en `gestion/admin.py`
- Usar las vistas SQL para reportes

---

**Fecha de creación:** 24/11/2025  
**Sistema:** Cantina Tita - Gestión Integral  
**Versión Django:** 5.2.8  
**Base de Datos:** MySQL 8.0.44 (cantinatitadb)

---

## 🔄 Actualizaciones de la Guía

**v1.2** - 24/11/2025 (Noche)
- ✅ Clarificada diferencia entre Tipo de Pago y Medio de Pago
- ✅ TIPO DE PAGO = Condición (CONTADO/CREDITO)
- ✅ MEDIO DE PAGO = Forma específica (EFECTIVO, TRANSFERENCIA, etc.)
- ✅ Actualizada configuración inicial con 6 medios de pago
- ✅ Agregada tabla comparativa de medios de pago
- ✅ Agregados 4 ejemplos prácticos de flujo completo
- ✅ Documentada configuración de comisiones por medio de pago
- ✅ Corregidos todos los escenarios con nomenclatura correcta

**v1.1** - 24/11/2025 (Tarde)
- ✅ Agregada sección "Problemas Comunes y Soluciones" (10 errores)
- ✅ Mejorado Paso 7: Documentos Tributarios con cálculos detallados
- ✅ Aclarado formato de Nro secuencial (solo número entero)
- ✅ Agregadas fórmulas de cálculo de IVA
- ✅ Documentados errores de stock, campos truncados, restricciones

**v1.0** - 24/11/2025
- Guía inicial con 6 escenarios completos
- Flujos de validación incluidos
- Reportes SQL básicos
- Checklist diario
