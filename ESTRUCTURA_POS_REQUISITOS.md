# 📋 ESTRUCTURA DEL POS DE VENTA - Requisitos Mínimos

## Basado en Análisis del Anterior POS (`pos_views.py`)

El anterior sistema de POS manejaba correctamente la siguiente estructura. El nuevo POS Bootstrap debe implementar lo mismo.

---

## 1️⃣ INFORMACIÓN DE TARJETA ESTUDIANTE

### Datos que debe mostrar:

```javascript
{
  "id_hijo": 11,                          // ID del hijo
  "nombre": "ROMINA MONGELLOS RODRIGUEZ", // Nombre completo
  "saldo": 1000,                          // Saldo actual en Gs.
  "grado": "5to Grado",                   // Grado escolar
  "cliente": "CARMEN RODRIGUEZ",          // Nombre responsable
  "nro_tarjeta": "00203",                 // Número de tarjeta
  "foto_perfil": "hijos/foto_123.jpg",    // URL foto del hijo
  "restricciones": [                      // Restricciones alimentarias
    {
      "tipo_restriccion": "Intolerancia a la lactosa",
      "descripcion": "Dificultad para digerir lácteos",
      "severidad": "Moderada"
    }
  ]
}
```

### Flujo:
1. Usuario escanea/escribe número de tarjeta
2. API consulta: `GET /pos/buscar-tarjeta/` (POST con JSON)
3. Sistema verifica:
   - Tarjeta existe
   - Estado = "Activa"
   - Obtiene datos de Hijo
   - Obtiene datos de Cliente responsable
   - Obtiene restricciones
4. UI muestra información sin errores

---

## 2️⃣ CARRITO DE COMPRAS

### Debe gestionar:

```javascript
carrito = [
  {
    "id": 5,                    // ID del producto
    "nombre": "Coca Cola 500ml",
    "precio": 5000,             // Precio unitario
    "cantidad": 2,              // Cantidad en carrito
    "subtotal": 10000           // precio * cantidad
  },
  {
    "id": 12,
    "nombre": "Sándwich de jamón",
    "precio": 15000,
    "cantidad": 1,
    "subtotal": 15000
  }
]
```

### Operaciones:
- ✅ Agregar producto
- ✅ Eliminar producto
- ✅ Modificar cantidad
- ✅ Calcular subtotal automático
- ✅ Mostrar total

---

## 3️⃣ CÁLCULO DE TOTALES

```javascript
{
  "subtotal": 25000,           // Suma de todos los subtotales
  "descuento": 0,              // Descuento especial (si aplica)
  "total_final": 25000,        // subtotal - descuento
  "cantidad_items": 2          // Cantidad total de items
}
```

---

## 4️⃣ VALIDACIONES EN TIEMPO REAL

### Antes de procesar venta:

1. **Verificación de Tarjeta**
   - Tarjeta activa ✅
   - Saldo suficiente para pago con tarjeta
   - Sin restricciones bloqueantes

2. **Verificación de Productos**
   - Stock disponible
   - Producto activo
   - Precio válido

3. **Verificación de Restricciones**
   - El producto NO contiene alérgenos que el hijo tiene
   - Si contiene, mostrar advertencia roja
   - Permitir venta pero con confirmación

4. **Validación de Pago**
   - Si pago con tarjeta: validar saldo
   - Si pago mixto: validar combinación
   - Verificar medios de pago permitidos

---

## 5️⃣ MEDIOS DE PAGO PERMITIDOS

### El anterior POS soportaba:

```
Medios de Pago Válidos:
├── EFECTIVO
├── TRANSFERENCIA
├── DÉBITO/QR
├── CRÉDITO/QR
└── GIROS TIGO

Especial:
└── TARJETA ESTUDIANTIL (descuento de saldo, NO genera factura)
```

### Lógica:
- Usuario selecciona medio de pago
- Si es TARJETA ESTUDIANTIL:
  - Restar del saldo
  - Generar solo TICKET (no factura)
- Si es otro:
  - Generar FACTURA ELECTRÓNICA (si checkbox marcado)

---

## 6️⃣ FACTURA ELECTRÓNICA

### Checkbox "¿Emitir Factura Electrónica?"

- ✅ Solo para ciertos medios de pago
- ✅ Requiere tarjeta seleccionada
- ✅ Genera XML y timbrado
- ✅ Envía a SET/Ekuatia

### Estructura de Factura:
```
FACTURA ELECTRÓNICA
═══════════════════
Timbrado: 12345678
RUC: XXX
Número: 00069

Cliente: CARMEN RODRIGUEZ
Hijo: ROMINA MONGELLOS RODRIGUEZ
RUC/Cédula Cliente: XXXXX
Fecha: 09/01/2026

─────────────────────────
Descripción      Cant  Precio
─────────────────────────
Coca Cola 500ml   2    5,000
Sándwich         1    15,000
─────────────────────────
SUBTOTAL:         25,000
IVA 10%:           2,500
─────────────────────────
TOTAL:           27,500
═══════════════════════════
```

---

## 7️⃣ TICKET DE VENTA

### Registro rápido (impreso)

```
TICKET VENTA
═══════════════════════
Hora: 21:25
Venta #91

Cliente: PEDRO PERÉZ
─────────────────────────
Coca Cola 500ml  2 × 5,000
Sándwich         1 × 15,000
─────────────────────────
TOTAL:              25,000
PAGO:          EFECTIVO
═══════════════════════
```

---

## 8️⃣ BASE DE DATOS - TABLAS CLAVE

### Tarjeta
```sql
SELECT * FROM tarjetas
WHERE Nro_Tarjeta = '00203'
  AND Estado = 'Activa'
  
Resultado:
├── Nro_Tarjeta: '00203'
├── ID_Hijo: 11
├── Saldo_Actual: 1000
├── Estado: 'Activa'
└── Fecha_Vencimiento: '2027-01-09'
```

### Hijo
```sql
SELECT * FROM hijos
WHERE ID_Hijo = 11
  
Resultado:
├── ID_Hijo: 11
├── ID_Cliente_Responsable: 5
├── Nombre: 'ROMINA'
├── Apellido: 'MONGELLOS RODRIGUEZ'
├── Grado: NULL
└── Restricciones (relación): [...]
```

### Restricciones
```sql
SELECT * FROM restricciones_hijos
WHERE ID_Hijo = 11 AND Activo = 1
  
Resultado:
├── ID_Restriccion: 1
├── ID_Hijo: 11
├── Tipo_Restriccion: 'Intolerancia a la lactosa'
├── Descripcion: 'Dificultad para digerir lácteos'
└── Severidad: 'Moderada'
```

### Ventas
```sql
INSERT INTO ventas (
  ID_Cliente, ID_Hijo, Monto_Total, Fecha_Venta, 
  Tipo_Pago, Generar_Factura_Legal
)
VALUES (
  5, 11, 27500, NOW(), 'EFECTIVO', TRUE
)
```

---

## 9️⃣ FLUJO COMPLETO DE UNA VENTA

```
1. ESCANEAR TARJETA
   ├─ Número: 00203
   └─ API buscar-tarjeta/ 
      └─ Retorna: Datos estudiante + restricciones

2. SELECCIONAR PRODUCTOS
   ├─ Coca Cola 500ml → Cantidad: 2
   ├─ Sándwich de jamón → Cantidad: 1
   └─ Carrito se actualiza automáticamente

3. REVISAR RESTRICCIONES
   ├─ Verificar cada producto contra restricciones
   ├─ Si tiene alérgeno: mostrar ⚠️ ALERTA
   └─ Permitir procesal con confirmación

4. SELECCIONAR MEDIO DE PAGO
   ├─ Opciones: Efectivo, Transferencia, Tarjeta, etc.
   └─ Si Tarjeta Estudiantil:
      ├─ Validar saldo (1000 < 25000 → NO CUBRE)
      └─ Mostrar error

5. MARCAR FACTURA ELECTRÓNICA (opcional)
   ├─ Checkbox: ¿Emitir factura?
   └─ Si es tarjeta estudiante → NO PERMITIR

6. PROCESAR VENTA
   ├─ Guardar en BD (tabla ventas)
   ├─ Registrar detalles (tabla detalle_venta)
   ├─ Actualizar saldo si es tarjeta
   ├─ Generar factura electrónica (si aplica)
   └─ Mostrar confirmación

7. IMPRIMIR
   ├─ Ticket de venta
   └─ Factura electrónica (si se generó)

8. FINALIZAR
   ├─ Limpiar carrito
   ├─ Resetear tarjeta
   └─ Listo para próxima venta
```

---

## 🔟 COMPONENTES UI NECESARIOS

### Estructura básica:

```html
┌────────────────────────────────────────┐
│         NAVBAR (Cantina Tita POS)      │
├────────────────────────────────┬───────┤
│                                │       │
│   PRODUCTOS                    │CARRITO│
│   ┌──────┐┌──────┐┌────────┐  │       │
│   │ Coca ││Sandwich│Galleta │  │ Item1 │
│   │5,000 ││15,000  │8,000  │  │ Item2 │
│   └──────┘└──────┘└────────┘  │       │
│                                │ TOTAL │
│   [Buscador de productos]      │27,500 │
│                                │       │
│   ┌──────┐┌──────┐┌────────┐  ├───────┤
│   │ Jugo ││Café  │Agua     │  │Tarjeta│
│   │7,000 ││6,000 │3,000    │  │Proc.V.│
│   └──────┘└──────┘└────────┘  │Limpiar│
└────────────────────────────────┴───────┘
```

---

## ✅ CHECKLIST IMPLEMENTACIÓN

- [x] API tarjeta: `/pos/buscar-tarjeta/`
- [x] API productos: `/pos/buscar-producto/`
- [x] Carrito en JavaScript
- [x] Cálculo de totales
- [x] UI Bootstrap 5
- [ ] Validación de restricciones
- [ ] API procesar venta: `/pos/procesar-venta/`
- [ ] Generación de factura
- [ ] Impresión de ticket
- [ ] Manejo de pagos mixtos
- [ ] Historial de ventas

---

**Fecha**: 09 Enero 2026
**Status**: Análisis Completo
**Próximo**: Implementar validación de restricciones
