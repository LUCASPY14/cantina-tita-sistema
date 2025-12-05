# 🍽️ MÓDULO POS ALMUERZO - GUÍA DE USO

## ✅ SISTEMA IMPLEMENTADO Y FUNCIONANDO

### 📋 Resumen del Módulo

El sistema de almuerzos está completamente separado del módulo de tarjeta prepaga:
- **Tarjeta**: Solo identifica al estudiante (NO descuenta saldo)
- **Registro**: Automático al pasar el código de barras
- **Cobro**: Independiente (contado anticipado o crédito mensual)
- **Reportes**: Separados (almuerzos vs uso de tarjeta)

---

## 🚀 CÓMO USAR EL POS DE ALMUERZO

### 1. Acceso al Sistema

**URL**: http://localhost:8000/pos/almuerzo/

El servidor está corriendo en: http://127.0.0.1:8000/

### 2. Operación del POS

#### Paso a paso:
1. Abrir el navegador en `/pos/almuerzo/`
2. El cursor ya está en el campo de código de barras (autofocus)
3. **Pasar la tarjeta del estudiante** por el lector
4. El sistema automáticamente:
   - Lee el código de barras (Nro_Tarjeta)
   - Verifica que la tarjeta esté activa
   - Valida que no tenga almuerzo registrado hoy
   - **Registra el almuerzo** (SIN tocar el saldo)
   - Muestra confirmación visual
5. El input se limpia automáticamente para el siguiente estudiante

#### Importante:
- ✅ **No requiere confirmación manual**
- ✅ **No descuenta saldo de la tarjeta**
- ✅ **Solo 1 almuerzo por día** por estudiante
- ✅ **Registro instantáneo**

---

## 🧪 TARJETAS DE PRUEBA

Puedes probar con estas tarjetas activas:

| Código | Estudiante | Saldo Actual |
|--------|-----------|--------------|
| `00203` | ROMINA MONGELOS RODRIGUEZ | Gs. 1,000 |
| `00414` | LUIS LOPEZ | Gs. 26,000 |
| `01024` | PEDRO PERÉZ | Gs. 14,000 |
| `10000` | SANTIAGO JOSÉ GONZÁLEZ LÓPEZ | Gs. 50,000 |
| `10001` | SANTIAGO JOSÉ GONZÁLEZ LÓPEZ | Gs. 29,500 |

**Nota**: El saldo que ves aquí es para compras en CANTINA, NO para almuerzos.

---

## 📱 SIMULANDO UN LECTOR DE CÓDIGO DE BARRAS

Si no tienes lector físico, puedes simular:

1. **En el navegador**: 
   - Tipea el código manualmente (ej: `01024`)
   - Presiona ENTER

2. **Comportamiento del lector real**:
   - El lector escribe el código automáticamente
   - Envía ENTER al finalizar
   - Todo sucede en milisegundos

---

## 📊 FLUJO COMPLETO DEL SISTEMA

### A. Registro Diario (POS)
```
Estudiante pasa tarjeta
    ↓
Sistema lee código de barras (Nro_Tarjeta)
    ↓
Verifica tarjeta ACTIVA
    ↓
Valida NO tenga almuerzo HOY
    ↓
Registra en: registro_consumo_almuerzo
    - ID_Hijo
    - Nro_Tarjeta
    - ID_Tipo_Almuerzo (Almuerzo Completo)
    - Costo_Almuerzo: Gs. 30,000
    - Fecha_Consumo: HOY
    - Marcado_En_Cuenta: FALSE
    ↓
✅ Almuerzo registrado
❌ Saldo tarjeta NO SE MODIFICA
```

### B. Generación Cuenta Mensual (Fin de mes)
```
Administrador ejecuta: /almuerzo/cuentas/generar/
    ↓
Sistema agrupa consumos del mes por hijo
    ↓
Crea registro en: cuentas_almuerzo_mensual
    - Cantidad_Almuerzos: X días
    - Monto_Total: Gs. X * 30,000
    - Forma_Cobro: CREDITO_MENSUAL o CONTADO_ANTICIPADO
    - Estado: PENDIENTE
    ↓
Marca consumos como facturados (Marcado_En_Cuenta = TRUE)
```

### C. Registro de Pagos
```
Padre/Responsable paga
    ↓
Cajero registra: /almuerzo/cuentas/pagar/
    ↓
Crea registro en: pagos_cuentas_almuerzo
    - Monto pagado
    - Medio_Pago: EFECTIVO, DEBITO, CREDITO, etc.
    ↓
Actualiza cuenta:
    - Monto_Pagado += pago
    - Estado: PAGADO / PARCIAL / PENDIENTE
```

---

## 🔍 DIFERENCIAS CLAVE: ALMUERZO vs TARJETA

### Módulo ALMUERZO
- **Propósito**: Control diario de almuerzos
- **Registro**: Automático al pasar tarjeta
- **Cobro**: Mensual (contado o crédito)
- **Tabla**: `registro_consumo_almuerzo`
- **NO afecta**: Saldo de tarjeta

### Módulo TARJETA (Cantina)
- **Propósito**: Compras en cantina (snacks, jugos, etc.)
- **Registro**: Manual desde POS de venta
- **Cobro**: Inmediato (descuenta saldo)
- **Tabla**: `consumos_tarjeta`
- **SÍ afecta**: Saldo de tarjeta

---

## 📈 REPORTES DISPONIBLES

### 1. Reporte Diario
**URL**: `/almuerzo/reportes/diario/`
- Almuerzos del día o rango de fechas
- Cantidad total
- Monto total

### 2. Reporte Mensual Separado
**URL**: `/almuerzo/reportes/mensual/`
- **Columna Almuerzos**: Cantidad y costo total del mes
- **Columna Tarjeta**: Consumos y cargas de saldo
- Completamente independientes

### 3. Cuentas Mensuales
**URL**: `/almuerzo/cuentas/`
- Estado de cuentas por hijo
- Filtros: año, mes, estado
- Saldo pendiente

---

## 🎯 TIPOS DE ALMUERZO CONFIGURADOS

| ID | Nombre | Precio | Estado |
|----|--------|--------|--------|
| 1 | Almuerzo Completo | Gs. 30,000 | ✅ Activo |
| 2 | Almuerzo Básico | Gs. 20,000 | ✅ Activo |
| 3 | Almuerzo Vegetariano | Gs. 28,000 | ✅ Activo |
| 4 | Almuerzo Especial | Gs. 35,000 | ✅ Activo |

**Actual**: El POS usa el primer tipo activo (Almuerzo Completo - Gs. 30,000)

---

## ⚙️ CONFIGURACIÓN ADICIONAL

### Cambiar Tipo de Almuerzo Predeterminado
```sql
-- Desactivar todos
UPDATE tipos_almuerzo SET activo = 0;

-- Activar el deseado (ej: Básico)
UPDATE tipos_almuerzo SET activo = 1 WHERE ID_Tipo_Almuerzo = 2;
```

### Agregar Nuevo Tipo
```sql
INSERT INTO tipos_almuerzo (Nombre, Descripcion, Precio_Unitario, Activo)
VALUES ('Almuerzo Light', 'Opción saludable', 25000.00, 1);
```

---

## 🔐 SEGURIDAD Y VALIDACIONES

### El sistema valida:
- ✅ Tarjeta debe existir en BD
- ✅ Tarjeta debe estar ACTIVA
- ✅ Estudiante solo puede tener 1 almuerzo por día
- ✅ Debe haber tipo de almuerzo configurado

### Mensajes de error:
- ❌ "Tarjeta no encontrada o inactiva"
- ⚠️ "Ya tiene almuerzo registrado hoy"
- ❌ "No hay tipo de almuerzo configurado"

---

## 🛠️ FUNCIONES ADMINISTRATIVAS

### Anular Último Registro
- Solo el último registro del día
- Botón "Anular" en panel lateral
- Requiere confirmación

### Generar Cuentas Mensuales
```bash
POST /almuerzo/cuentas/generar/
Parámetros:
- anio: 2025
- mes: 12
- forma_cobro: CREDITO_MENSUAL | CONTADO_ANTICIPADO
```

### Registrar Pago
```bash
POST /almuerzo/cuentas/pagar/
Parámetros:
- cuenta_id: ID de cuenta
- monto: Monto pagado
- medio_pago: EFECTIVO | DEBITO | CREDITO | TRANSFERENCIA
- referencia: Nro. comprobante (opcional)
```

---

## 📞 SOPORTE

### Base de Datos: `cantinatitadb`

### Tablas Principales:
- `tipos_almuerzo` - Catálogo de menús
- `registro_consumo_almuerzo` - Registros diarios
- `cuentas_almuerzo_mensual` - Cuentas mensuales
- `pagos_cuentas_almuerzo` - Pagos realizados

### Vistas SQL:
- `v_almuerzos_diarios` - Registros con detalles
- `v_cuentas_almuerzo_detallado` - Cuentas con info completa
- `v_reporte_mensual_separado` - Reporte separado almuerzos/tarjeta

---

## ✅ PRUEBA RÁPIDA

1. Abre: http://localhost:8000/pos/almuerzo/
2. Tipea: `01024` (tarjeta de PEDRO PERÉZ)
3. Presiona ENTER
4. Deberías ver: ✅ "Almuerzo Registrado"
5. El saldo de la tarjeta NO cambia (sigue en Gs. 14,000)
6. Si vuelves a escanear la misma tarjeta HOY: ⚠️ "Ya tiene almuerzo registrado hoy"

---

## 🎉 SISTEMA LISTO PARA PRODUCCIÓN

El módulo está completamente funcional y listo para usar en el comedor escolar.
