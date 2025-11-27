# ANÁLISIS DE COBERTURA DE TESTS - CANTINA TITA
## Base de Datos: cantinatitadb (87 tablas)
## Fecha: 26 de Noviembre de 2025

---

## 📊 RESUMEN DE COBERTURA

**Total Tablas en BD:** 87 tablas  
**Tablas con Tests:** ~20 tablas  
**Tablas sin Tests:** ~67 tablas  
**Cobertura Estimada:** 23%

---

## ✅ MÓDULOS CON TESTS EXISTENTES

### 1. **VENTAS** ✅ COMPLETO
- **Test:** `test_modulo_ventas_directas.py` (5/5 - 100%)
- **Tablas cubiertas:**
  - `ventas`
  - `detalle_venta`
  - `pagos_venta`
  - `medios_pago`
  - `productos`
  - `clientes`
  - `hijos`

### 2. **DOCUMENTOS TRIBUTARIOS** ✅ COMPLETO
- **Test:** `test_modulo_documentos.py` (5/5 - 100%)
- **Tablas cubiertas:**
  - `documentos_tributarios`
  - `timbrados`
  - `ventas`

### 3. **CIERRES DE CAJA** ✅ COMPLETO
- **Test:** `test_modulo_cierres_caja.py` (5/5 - 100%)
- **Tablas cubiertas:**
  - `cierres_caja`
  - `cajas`
  - `empleados`
  - `ventas`
  - `cargas_saldo`

### 4. **ALMUERZOS/SUSCRIPCIONES** ✅ COMPLETO
- **Test:** `test_modulo_almuerzos.py` (5/5 - 100%)
- **Tablas cubiertas:**
  - `suscripciones_almuerzo`
  - `planes_almuerzo`
  - `pagos_almuerzo_mensual`
  - `registro_consumo_almuerzo`
  - `hijos`
  - `clientes`

### 5. **TARJETAS** ✅ PARCIAL
- **Tests:** `test_recarga_tarjeta.py`, `test_movimientos.py`
- **Tablas cubiertas:**
  - `tarjetas`
  - `cargas_saldo`
  - `consumos_tarjeta`
  - `hijos`

### 6. **CLIENTES** ✅ COMPLETO
- **Test:** `test_modulo_clientes.py` (6 tests)
- **Tablas cubiertas:**
  - `clientes`
  - `tipos_cliente`
  - `hijos`

### 7. **PROVEEDORES** ✅ COMPLETO
- **Test:** `test_modulo_gestion_proveedores.py` (5/5 - 100%)
- **Tablas cubiertas:**
  - `proveedores`
  - `cta_corriente_prov`

### 8. **COMPRAS** ✅ COMPLETO
- **Test:** `test_modulo_compras.py` (5 tests)
- **Tablas cubiertas:**
  - `compras`
  - `detalle_compra`
  - `proveedores`
  - `productos`

### 9. **CUENTA CORRIENTE CLIENTES** ✅ COMPLETO
- **Test:** `test_modulo_cta_cte_clientes.py` (6/6 - 100%)
- **Tablas cubiertas:**
  - `cta_corriente`
  - `clientes`
  - `ventas`
  - `notas_credito`

### 10. **CATEGORÍAS** ✅ COMPLETO
- **Test:** `test_modulo_categorias.py` (4/4 - 100%)
- **Tablas cubiertas:**
  - `categorias`
  - `productos`

### 11. **USUARIOS** ✅ COMPLETO
- **Test:** `test_modulo_usuarios.py` (6 tests)
- **Tablas cubiertas:**
  - `empleados`
  - `tipos_rol_general`

### 12. **TESTS FUNCIONALES/INTEGRALES**
- **Tests:** `test_funcional_sistema.py`, `test_integral_sistema.py`, `test_sistema_completo.py`
- **Cobertura:** Tests de integración que prueban triggers, vistas, y flujos completos

---

## ❌ MÓDULOS SIN TESTS (67 tablas)

### 🔴 **CRÍTICOS - Alta Prioridad**

#### 1. **STOCK E INVENTARIO** 🔥
- **Tablas sin tests:**
  - ❌ `stock_unico` - Control principal de inventario
  - ❌ `movimientos_stock` - Historial de movimientos
  - ❌ `ajustes_inventario` - Ajustes manuales
  - ❌ `detalle_ajuste` - Detalles de ajustes
  - ❌ `costos_historicos` - Historial de costos
- **Impacto:** MUY ALTO - Control de inventario es crítico
- **Tests sugeridos:**
  - Consulta de stock actual
  - Registro de movimientos (entradas/salidas)
  - Ajustes de inventario
  - Alertas de stock bajo
  - Historial de costos

#### 2. **PRECIOS Y LISTAS** 🔥
- **Tablas sin tests:**
  - ❌ `listas_precios` - Diferentes listas (mayorista, minorista, etc.)
  - ❌ `precios_por_lista` - Precios específicos por lista
  - ❌ `historico_precios` - Historial de cambios de precio
- **Impacto:** ALTO - Gestión de precios es fundamental
- **Tests sugeridos:**
  - Crear/editar listas de precios
  - Asignar productos a listas
  - Consultar precio según lista
  - Historial de cambios

#### 3. **NOTAS DE CRÉDITO** 🔥
- **Tablas sin tests:**
  - ❌ `notas_credito` - Solo se usa en CTA_CTE, falta test específico
  - ❌ `detalle_nota` - Detalles de notas de crédito
- **Impacto:** ALTO - Manejo de devoluciones/anulaciones
- **Tests sugeridos:**
  - Emisión de nota de crédito
  - Aplicación a cuenta corriente
  - Consulta de notas emitidas
  - Anulación de notas

#### 4. **COMISIONES** 🔥
- **Tablas sin tests:**
  - ❌ `tarifas_comision` - Configuración de comisiones
  - ❌ `detalle_comision_venta` - Comisiones por venta
  - ❌ `auditoria_comisiones` - Auditoría de comisiones
- **Impacto:** MEDIO-ALTO - Control de comisiones de vendedores
- **Tests sugeridos:**
  - Calcular comisión por venta
  - Consultar comisiones por empleado
  - Reportes de comisiones
  - Auditoría de cambios

### 🟡 **IMPORTANTES - Media Prioridad**

#### 5. **PUNTOS DE EXPEDICIÓN** ⚠️
- **Tablas sin tests:**
  - ❌ `puntos_expedicion` - Puntos de emisión de facturas
- **Impacto:** MEDIO - Importante para facturación
- **Tests sugeridos:**
  - Gestionar puntos de expedición
  - Asignar a empleados/cajas

#### 6. **IMPUESTOS** ⚠️
- **Tablas sin tests:**
  - ❌ `impuestos` - Configuración de IVA y otros impuestos
- **Impacto:** MEDIO - Configuración tributaria
- **Tests sugeridos:**
  - Gestionar tasas de impuestos
  - Aplicar a productos/ventas

#### 7. **UNIDADES DE MEDIDA** ⚠️
- **Tablas sin tests:**
  - ❌ `unidades_medida` - Kg, unidad, litros, etc.
- **Impacto:** MEDIO - Gestión de productos
- **Tests sugeridos:**
  - CRUD de unidades
  - Conversiones entre unidades

#### 8. **ALERTAS Y NOTIFICACIONES** ⚠️
- **Tablas sin tests:**
  - ❌ `alertas_sistema` - Alertas generales
  - ❌ `solicitudes_notificacion` - Sistema de notificaciones
- **Impacto:** MEDIO - Comunicación con usuarios
- **Tests sugeridos:**
  - Crear alertas
  - Enviar notificaciones
  - Marcar como leídas

#### 9. **CONCILIACIÓN DE PAGOS** ⚠️
- **Tablas sin tests:**
  - ❌ `conciliacion_pagos` - Conciliación bancaria
- **Impacto:** MEDIO - Control financiero
- **Tests sugeridos:**
  - Registrar conciliaciones
  - Consultar diferencias
  - Reportes de conciliación

#### 10. **AUDITORÍA** ⚠️
- **Tablas sin tests:**
  - ❌ `auditoria_empleados` - Cambios en empleados
  - ❌ `auditoria_usuarios_web` - Cambios en usuarios web
- **Impacto:** MEDIO - Trazabilidad
- **Tests sugeridos:**
  - Registrar cambios
  - Consultar historial
  - Reportes de auditoría

### 🟢 **OPCIONALES - Baja Prioridad**

#### 11. **CONFIGURACIÓN EMPRESA** 📝
- **Tablas sin tests:**
  - ❌ `datos_empresa` - Información de la empresa
  - ❌ `datos_facturacion_elect` - Configuración facturación electrónica
  - ❌ `datos_facturacion_fisica` - Configuración facturación física
- **Impacto:** BAJO - Configuración inicial, raramente cambia
- **Tests sugeridos:**
  - Consultar datos empresa
  - Actualizar configuración

#### 12. **USUARIOS WEB** 📝
- **Tablas sin tests:**
  - ❌ `usuarios_web_clientes` - Portal de clientes
- **Impacto:** BAJO - Depende si hay portal web
- **Tests sugeridos:**
  - Registro de usuarios
  - Login/logout
  - Consulta de cuenta

#### 13. **TABLAS DJANGO/GESTION (Apps legacy)** 📝
- **Tablas sin tests:**
  - ❌ `gestion_*` (9 tablas) - Tablas de apps Django legacy
  - ❌ `auth_*` (6 tablas) - Django auth (manejado por Django)
  - ❌ `django_*` (4 tablas) - Django internals
- **Impacto:** BAJO - Son tablas de Django o apps antiguas
- **Acción:** Determinar si están en uso o son legacy

### 📊 **VISTAS (13 vistas)** - Ya funcionan
- Todas las vistas empiezan con `v_*`
- Se prueban indirectamente en tests integrales
- No requieren tests unitarios específicos (son queries de solo lectura)

---

## 🎯 RECOMENDACIONES PRIORITARIAS

### **FASE 5 - STOCK E INVENTARIO** 🔥 (CRÍTICO)
**Estimación:** 2-3 horas  
**Tablas:** `stock_unico`, `movimientos_stock`, `ajustes_inventario`
```python
# test_modulo_inventario.py
- TEST 1: Consulta de stock actual por producto
- TEST 2: Registro de movimientos de stock
- TEST 3: Ajustes de inventario manual
- TEST 4: Alertas de stock bajo/crítico
- TEST 5: Reporte de movimientos por período
```

### **FASE 6 - PRECIOS Y LISTAS** 🔥 (CRÍTICO)
**Estimación:** 1.5-2 horas  
**Tablas:** `listas_precios`, `precios_por_lista`, `historico_precios`
```python
# test_modulo_precios.py
- TEST 1: Crear/editar listas de precios
- TEST 2: Asignar precios a productos por lista
- TEST 3: Consultar precio según lista de cliente
- TEST 4: Actualización masiva de precios
- TEST 5: Historial de cambios de precio
```

### **FASE 7 - NOTAS DE CRÉDITO** 🔥 (CRÍTICO)
**Estimación:** 1.5-2 horas  
**Tablas:** `notas_credito`, `detalle_nota`
```python
# test_modulo_notas_credito.py
- TEST 1: Emisión de nota de crédito desde venta
- TEST 2: Detalle de productos en nota
- TEST 3: Aplicación a cuenta corriente
- TEST 4: Consulta de notas por cliente
- TEST 5: Reportes y estadísticas
```

### **FASE 8 - COMISIONES** 🔥 (CRÍTICO)
**Estimación:** 1.5-2 horas  
**Tablas:** `tarifas_comision`, `detalle_comision_venta`, `auditoria_comisiones`
```python
# test_modulo_comisiones.py
- TEST 1: Configurar tarifas de comisión
- TEST 2: Calcular comisión en venta
- TEST 3: Consultar comisiones por empleado
- TEST 4: Reportes de comisiones por período
- TEST 5: Auditoría de cambios en comisiones
```

### **FASE 9 - PUNTOS DE EXPEDICIÓN** ⚠️ (IMPORTANTE)
**Estimación:** 1 hora  
**Tablas:** `puntos_expedicion`
```python
# test_modulo_puntos_expedicion.py
- TEST 1: Crear punto de expedición
- TEST 2: Asignar a caja/empleado
- TEST 3: Consultar puntos activos
- TEST 4: Activar/desactivar punto
```

### **FASE 10 - IMPUESTOS Y UNIDADES** ⚠️ (IMPORTANTE)
**Estimación:** 1 hora  
**Tablas:** `impuestos`, `unidades_medida`
```python
# test_modulo_configuraciones.py
- TEST 1: Gestionar tasas de impuestos
- TEST 2: Gestionar unidades de medida
- TEST 3: Aplicar impuestos a productos
- TEST 4: Conversiones entre unidades
```

---

## 📈 PROGRESO ACTUAL

```
COBERTURA DE TESTS POR CATEGORÍA:

Ventas y Facturación:    ████████████████████ 100% (5 módulos)
Clientes y Proveedores:  ████████████████████ 100% (3 módulos)
Caja y Pagos:            ████████████████████ 100% (2 módulos)
Productos y Categorías:  ████████████████████ 100% (2 módulos)
Almuerzos:               ████████████████████ 100% (1 módulo)
Tarjetas:                ███████████████░░░░░  75% (parcial)

Inventario:              ░░░░░░░░░░░░░░░░░░░░   0% ❌
Precios y Listas:        ░░░░░░░░░░░░░░░░░░░░   0% ❌
Notas de Crédito:        ░░░░░░░░░░░░░░░░░░░░   0% ❌
Comisiones:              ░░░░░░░░░░░░░░░░░░░░   0% ❌
Config. Facturación:     ░░░░░░░░░░░░░░░░░░░░   0% ❌
```

**COBERTURA TOTAL ESTIMADA:** 23% (20/87 tablas)

---

## 🎯 PLAN DE ACCIÓN SUGERIDO

### **Opción A: Completar Críticos** (6-9 horas)
Fases 5, 6, 7, 8 - Cubre 100% de funcionalidad crítica

### **Opción B: Completar Críticos + Importantes** (8-12 horas)
Fases 5-10 - Cobertura al ~50% de todas las tablas

### **Opción C: Mantener Status Quo**
Los 57 tests actuales cubren los flujos principales de negocio.
Las tablas sin tests son configuraciones o módulos secundarios.

---

## 💡 CONCLUSIÓN

**ESTADO ACTUAL:** ✅ Excelente cobertura de flujos principales  
- Ventas, compras, clientes, proveedores, caja, almuerzos: **100%**
- Total tests: **57 tests funcionando correctamente**

**GAPS CRÍTICOS:** 
1. **Inventario** - Sin tests de stock, movimientos, ajustes
2. **Precios** - Sin tests de listas de precios
3. **Notas de Crédito** - Sin tests específicos de emisión
4. **Comisiones** - Sin tests de cálculo/seguimiento

**RECOMENDACIÓN:**
- Si el sistema está en producción: **Implementar Fases 5-8** (críticas)
- Si es desarrollo: **Status quo es aceptable**, implementar bajo demanda
