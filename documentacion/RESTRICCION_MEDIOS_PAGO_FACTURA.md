# 🏦 Restricción: Métodos de Pago para Facturación Electrónica

## ⚠️ Importante

**NO todos los métodos de pago generan factura electrónica** según normativa paraguaya (SET/SIFEN).

## ✅ Métodos que PERMITEN Facturación Electrónica

```
1. EFECTIVO
2. TRANSFERENCIA BANCARIA
3. GIROS TIGO
4. TARJETA DEBITO /QR
5. TARJETA CREDITO / QR
```

Estos métodos generarán **factura electrónica** (XML, CDC, KUDE).

## 🎫 Métodos que SOLO Generan TICKET (Sin Factura)

```
1. TARJETA ESTUDIANTIL ← ⚠️ La factura ya se emitió en la RECARGA
```

**¿Por qué?**
- Cuando se recarga dinero a la tarjeta del estudiante → Se emite una factura
- Cuando el estudiante compra con esa tarjeta → NO se emite otra factura (evitar doble facturación)
- Solo se genera un **TICKET** de compra

## ❌ Métodos que NO PERMITEN Facturación Electrónica

Métodos en BD que no figuran en los listados anteriores:
- Tarjeta de Crédito (genérica)
- Tarjeta de Débito (genérica)
- Otros métodos no regulados

Estos cambiarán automáticamente a **factura FÍSICA** (si se solicita).

## 🔄 Comportamiento del Sistema

### Caso 1: EFECTIVO
```
Usuario selecciona: EFECTIVO + Marcar "Emitir Factura Electrónica"
↓
Sistema valida: "EFECTIVO" ∈ MEDIOS_CON_FACTURA_ELECTRONICA
↓
Se emite FACTURA ELECTRÓNICA ✅ (XML, CDC, KUDE)
```

### Caso 2: TARJETA ESTUDIANTIL
```
Usuario selecciona: TARJETA ESTUDIANTIL + Marcar "Emitir Factura Electrónica"
↓
Sistema valida: "TARJETA ESTUDIANTIL" ∈ MEDIOS_SIN_FACTURA
↓
Se RECHAZA emisión de factura ❌
Se emite solo TICKET 🎫
Mensaje: "✓ Método no genera factura (solo ticket). La factura se emitió en la recarga."
```

### Caso 3: TARJETA DE CRÉDITO (genérica)
```
Usuario selecciona: TARJETA DE CRÉDITO + Marcar "Emitir Factura Electrónica"
↓
Sistema valida: "TARJETA DE CRÉDITO" ∉ MEDIOS_CON_FACTURA_ELECTRONICA
             Y "TARJETA DE CRÉDITO" ∉ MEDIOS_SIN_FACTURA
↓
Se cambia automáticamente a FACTURA FÍSICA 📄
Mensaje: "Método no permite factura electrónica - Emitiendo factura física."
```

## 📋 Configuración en Base de Datos

Medios de pago en tabla `medios_pago`:

| ID | Descripción | Permite Factura Electrónica | Acción |
|----|-------------|----------------------------|---------|
| 1 | EFECTIVO | ✅ SÍ | Emite factura electrónica |
| 2 | TRANSFERENCIA BANCARIA | ✅ SÍ | Emite factura electrónica |
| 3 | TARJETA DEBITO /QR | ✅ SÍ | Emite factura electrónica |
| 4 | TARJETA CREDITO / QR | ✅ SÍ | Emite factura electrónica |
| 5 | GIROS TIGO | ✅ SÍ | Emite factura electrónica |
| **6** | **TARJETA ESTUDIANTIL** | **❌ NO** | **Solo ticket (sin factura)** |
| 7 | Tarjeta de Crédito | ❌ NO | Cambia a factura física |
| 8 | Tarjeta de Débito | ❌ NO | Cambia a factura física |

## 🔧 Código de Validación

En `gestion/pos_facturacion_integracion.py`:

```python
# Métodos que permiten factura electrónica
MEDIOS_PAGO_CON_FACTURA_ELECTRONICA = [
    'EFECTIVO',
    'TRANSFERENCIA BANCARIA',
    'GIROS TIGO',
    'TARJETA DEBITO /QR',
    'TARJETA CREDITO / QR',
]

# Métodos que NO permiten factura (solo ticket)
# Ya tienen factura desde la recarga
MEDIOS_PAGO_SIN_FACTURA = [
    'TARJETA ESTUDIANTIL',
]

# Validación
def puede_facturar_electronico(self, id_medio_pago: int) -> Tuple[bool, str]:
    medio = MediosPago.objects.get(id_medio_pago=id_medio_pago)
    descripcion = medio.descripcion.strip().upper()
    
    # ¿Es método sin factura?
    if descripcion == 'TARJETA ESTUDIANTIL':
        return False, 'La factura se emitió en la recarga'
    
    # ¿Es método con factura?
    if descripcion in ['EFECTIVO', 'TRANSFERENCIA BANCARIA', ...]:
        return True, ''
    
    # Otro método
    return False, 'No permite facturación electrónica'
```

## 📊 Flujo Completo de Venta

```
Venta iniciada
    ↓
¿Marcar "Emitir Factura Electrónica"? → NO → Solo TICKET
    ↓ SÍ
¿Método de pago?
    ├─ TARJETA ESTUDIANTIL → NO facturar (ya existe) → TICKET 🎫
    ├─ EFECTIVO, TRANSFERENCIA, etc. → FACTURA ELECTRÓNICA ✅
    └─ Otros métodos → FACTURA FÍSICA 📄
    ↓
Guardar venta
    ↓
Imprimir ticket/factura
```

## 🎯 Ejemplos de Escenarios

### Escenario 1: Compra con Efectivo
```
Estudiante: PEDRO PERÉZ
Productos: Coca Cola (5,000) + Pan (2,000) = 7,000
Método: EFECTIVO
Facturación: ✓ Emitir Factura

RESULTADO:
✅ Factura Electrónica emitida
CDC: ABC123...
KUDE: [código QR]
Ticket impreso
```

### Escenario 2: Compra con Tarjeta Estudiantil
```
Estudiante: LUIS LOPEZ
Productos: Agua (1,000) + Galletitas (1,500) = 2,500
Método: TARJETA ESTUDIANTIL
Facturación: ✓ Emitir Factura

RESULTADO:
🎫 Ticket impreso (sin factura)
Mensaje: "✓ Método no genera factura (solo ticket). 
          La factura se emitió en la recarga."
Saldo tarjeta: 47,500 (fue: 50,000)
```

### Escenario 3: Compra con Tarjeta Genérica
```
Papá/Mamá compra
Productos: Snacks (10,000)
Método: Tarjeta de Crédito
Facturación: ✓ Emitir Factura

RESULTADO:
📄 Factura FÍSICA emitida
(No es electrónica porque el método no está permitido)
Mensaje: "Método no permite factura electrónica 
          - Emitiendo factura física."
```

## 🔍 Testing

Para probar estas restricciones:

```bash
# Crear venta con EFECTIVO → Factura electrónica
python prueba_venta_con_metodo.py --metodo=1

# Crear venta con TARJETA ESTUDIANTIL → Solo ticket
python prueba_venta_con_metodo.py --metodo=6

# Crear venta con TARJETA DE CRÉDITO genérica → Factura física
python prueba_venta_con_metodo.py --metodo=7
```

## 📞 Preguntas Frecuentes

**P: ¿Por qué TARJETA ESTUDIANTIL no emite factura?**
R: Porque la factura ya se emitió cuando se hizo la recarga. Evitamos doble facturación.

**P: ¿Puedo agregar más métodos sin factura?**
R: Sí, agrégalos a `MEDIOS_PAGO_SIN_FACTURA` en `pos_facturacion_integracion.py`.

**P: ¿Las facturas físicas son válidas legalmente?**
R: Sí, son válidas. Solo que no pasan por SIFEN/SET.

**P: ¿El usuario ve un error o una advertencia?**
R: Se muestra un mensaje informativo, no un error. El sistema sigue adelante con la venta.

**P: ¿Se imprime algo diferente?**
R: Para TARJETA ESTUDIANTIL se imprime solo el TICKET (comprobante de compra).
   Para otros métodos se imprime el ticket + factura (si es electrónica) o ticket + comprobante (si es física).

---

**Implementado en**: `gestion/pos_facturacion_integracion.py`  
**Última actualización**: 09/01/2026 20:42  
**Estado**: ✅ Activo - Corregido para TARJETA ESTUDIANTIL
