# 📖 MANUAL DE USUARIO - SISTEMA POS
## Cantina Tita - Punto de Venta

**Versión**: 1.0  
**Fecha**: Enero 2026  
**Audiencia**: Cajeros y Personal de Caja

---

## ÍNDICE

1. [Inicio de Sesión](#login)
2. [Pantalla Principal del POS](#pantalla-principal)
3. [Realizar una Venta](#realizar-venta)
4. [Venta con Tarjeta Estudiantil](#venta-tarjeta)
5. [Venta con Efectivo](#venta-efectivo)
6. [Pagos Mixtos](#pagos-mixtos)
7. [Restricciones Alimentarias](#restricciones)
8. [Promociones y Descuentos](#promociones)
9. [Anular/Cancelar Venta](#anular-venta)
10. [Cierre de Caja](#cierre-caja)
11. [Solución de Problemas](#troubleshooting)

---

<a name="login"></a>
## 1. 🔐 INICIO DE SESIÓN

### Acceso al Sistema
1. Abrir navegador web
2. Ir a: `http://localhost:8000/pos/` (o la dirección del servidor)
3. Ingresar credenciales:
   - **Usuario**: Tu usuario asignado
   - **Contraseña**: Tu contraseña personal
4. Click en "Iniciar Sesión"

### Primera Vez
Si es tu primera vez:
- Tu usuario será creado por el administrador
- Te darán una contraseña temporal
- **IMPORTANTE**: Cambiar la contraseña en el primer acceso

---

<a name="pantalla-principal"></a>
## 2. 🖥️ PANTALLA PRINCIPAL DEL POS

### Elementos de la Pantalla

```
┌─────────────────────────────────────────────────────┐
│  CANTINA TITA - POS          Usuario: Juan Pérez  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Buscar Producto] _______________ [🔍 Buscar]     │
│                                                     │
│  ┌─── PRODUCTOS DISPONIBLES ───┐  ┌─── CARRITO ───┐│
│  │ ☕ Café - Gs. 5,000         │  │ (vacío)       ││
│  │ 🍞 Pan - Gs. 3,000          │  │               ││
│  │ 🥤 Gaseosa - Gs. 6,000      │  │               ││
│  └─────────────────────────────┘  └───────────────┘│
│                                                     │
│  Tarjeta: [_______________] [Leer Tarjeta]         │
│                                                     │
│  TOTAL: Gs. 0                                       │
│                                                     │
│  [PROCESAR VENTA]  [LIMPIAR]  [SALIR]              │
└─────────────────────────────────────────────────────┘
```

### Componentes:
- **Buscador de productos**: Ingresar código de barras o nombre
- **Lista de productos**: Productos disponibles para vender
- **Carrito**: Productos seleccionados para la venta actual
- **Lector de tarjeta**: Escanear tarjeta estudiantil
- **Total**: Monto total de la compra

---

<a name="realizar-venta"></a>
## 3. 🛒 REALIZAR UNA VENTA

### Proceso Básico

#### Paso 1: Buscar Productos
**Opción A: Por código de barras**
1. Escanear código de barras con lector
2. El producto se agrega automáticamente al carrito

**Opción B: Por nombre**
1. Escribir nombre del producto
2. Click en "Buscar"
3. Seleccionar producto de la lista
4. Click en "Agregar al Carrito"

#### Paso 2: Ajustar Cantidad
- **Aumentar**: Click en `+`
- **Disminuir**: Click en `-`
- **Eliminar**: Click en `🗑️` (icono de basura)

#### Paso 3: Seleccionar Método de Pago
Ver secciones específicas:
- [Venta con Tarjeta](#venta-tarjeta)
- [Venta con Efectivo](#venta-efectivo)
- [Pagos Mixtos](#pagos-mixtos)

#### Paso 4: Procesar Venta
1. Verificar total
2. Click en **"PROCESAR VENTA"**
3. Confirmar en el diálogo
4. Esperar mensaje de éxito
5. Se imprime ticket automáticamente (si hay impresora)

---

<a name="venta-tarjeta"></a>
## 4. 💳 VENTA CON TARJETA ESTUDIANTIL

### Proceso

1. **Leer Tarjeta**
   - Colocar tarjeta en lector
   - O escribir número de tarjeta manualmente
   - Click en "Leer Tarjeta"

2. **Verificar Datos**
   ```
   ┌─── INFORMACIÓN DE TARJETA ───┐
   │ Tarjeta: 12345678            │
   │ Estudiante: María González   │
   │ Grado: 5to Básico            │
   │ Saldo: Gs. 50,000            │
   └──────────────────────────────┘
   ```

3. **Agregar Productos** (normal)

4. **Verificar Saldo**
   - El sistema verifica automáticamente
   - Si hay saldo: ✅ Continúa normal
   - Si NO hay saldo: ⚠️ Ver [Saldo Insuficiente](#saldo-insuficiente)

5. **Procesar Venta**
   - Click en "PROCESAR VENTA"
   - Se descuenta del saldo automáticamente
   - Se imprime ticket con saldo actualizado

### Ejemplo de Ticket
```
═══════════════════════════════
    CANTINA TITA
    Venta #12345
═══════════════════════════════
Fecha: 10/01/2026 14:30
Cajero: Juan Pérez

Tarjeta: 12345678
Estudiante: María González

PRODUCTOS:
─────────────────────────────────
Café              Gs.    5,000
Pan x2            Gs.    6,000
Gaseosa           Gs.    6,000
─────────────────────────────────
TOTAL             Gs.   17,000

SALDO ANTERIOR    Gs.   50,000
SALDO ACTUAL      Gs.   33,000

═══════════════════════════════
   ¡Gracias por tu compra!
═══════════════════════════════
```

<a name="saldo-insuficiente"></a>
### ⚠️ Saldo Insuficiente

Si el saldo no alcanza:

**Opción 1: Reducir Compra**
- Quitar productos del carrito
- Hasta que el total <= saldo

**Opción 2: Pago Mixto**
- Usar saldo de tarjeta + efectivo
- Ver [Pagos Mixtos](#pagos-mixtos)

**Opción 3: Autorización de Supervisor** (solo para emergencias)
1. Llamar a supervisor
2. Supervisor ingresa su clave
3. Se permite venta a crédito
4. Se genera factura

---

<a name="venta-efectivo"></a>
## 5. 💵 VENTA CON EFECTIVO

### Proceso

1. **Agregar Productos** (normal)

2. **Seleccionar Efectivo**
   - Click en "Efectivo" en Medios de Pago
   - Aparece calculadora de cambio:
   ```
   ┌─── PAGO EN EFECTIVO ───┐
   │ Total: Gs. 17,000      │
   │                        │
   │ Recibido: ____________ │
   │                        │
   │ Cambio: Gs. 0          │
   └────────────────────────┘
   ```

3. **Ingresar Monto Recibido**
   - Escribir cuánto pagó el cliente
   - El sistema calcula cambio automáticamente
   - Ejemplo:
     - Total: Gs. 17,000
     - Recibido: Gs. 20,000
     - **Cambio: Gs. 3,000** ← Entregar al cliente

4. **Procesar Venta**
   - Verificar cambio
   - Click en "PROCESAR VENTA"
   - Se genera factura legal
   - Se imprime ticket

---

<a name="pagos-mixtos"></a>
## 6. 💰 PAGOS MIXTOS

Cuando el cliente paga con **múltiples métodos** (ej: tarjeta + efectivo).

### Ejemplo Real

**Compra**: Gs. 25,000  
**Saldo en tarjeta**: Gs. 15,000  
**Faltante**: Gs. 10,000 → Pagar en efectivo

### Proceso

1. **Leer Tarjeta** (normal)

2. **Click en "Pago Mixto"**
   ```
   ┌─── PAGOS MIXTOS ───┐
   │ Total: Gs. 25,000  │
   │                    │
   │ ☑ Tarjeta Estudiantil │
   │   Monto: 15,000    │
   │                    │
   │ ☑ Efectivo         │
   │   Monto: 10,000    │
   │                    │
   │ Total Pagos: 25,000│
   └────────────────────┘
   ```

3. **Configurar Pagos**
   - Marcar cada medio de pago
   - Ingresar monto para cada uno
   - El sistema valida que sumen el total

4. **Procesar**
   - Click en "PROCESAR VENTA"
   - Se descuenta de tarjeta
   - Se registra efectivo
   - Ticket muestra desglose

### Medios de Pago Disponibles

| Medio | Ícono | Requiere Referencia | Comisión |
|-------|-------|---------------------|----------|
| Efectivo | 💵 | No | 0% |
| Tarjeta Estudiantil | 🎓 | No | 0% |
| Tarjeta Débito | 💳 | Sí | 3% |
| Tarjeta Crédito | 💳 | Sí | 5% |
| Giros Tigo | 📱 | Sí | 5% |
| Transferencia | 🏦 | Sí | 0% |
| QR Zimple | 📱 | Sí | 3% |

**Referencia** = Código de transacción o autorización

---

<a name="restricciones"></a>
## 7. ⚠️ RESTRICCIONES ALIMENTARIAS

### Qué son
Algunos estudiantes tienen restricciones médicas (alergias, diabetes, etc.) que limitan qué pueden comprar.

### Cuando Aparece la Alerta

Al leer una tarjeta con restricciones:
```
┌────────────────────────────────────┐
│  ⚠️  ALERTA: RESTRICCIONES        │
├────────────────────────────────────┤
│ Estudiante: Pedro Ramírez          │
│                                    │
│ RESTRICCIONES ACTIVAS:             │
│ • Alérgico a frutos secos          │
│ • No puede consumir azúcar         │
│                                    │
│ PRODUCTOS EN EL CARRITO:           │
│ ✓ Agua mineral - OK                │
│ ⚠️  Chocolate - CONTIENE AZÚCAR    │
│                                    │
│ Justificación (obligatoria):       │
│ ________________________________   │
│                                    │
│ [CANCELAR]  [PROCESAR DE TODAS FORMAS] │
└────────────────────────────────────┘
```

### Qué Hacer

**Opción 1: Cancelar** (Recomendado)
- Quitar productos prohibidos
- Sugerir alternativas
- Procesar venta normal

**Opción 2: Procesar de Todas Formas**
⚠️ **Solo en casos excepcionales**
1. Verificar con padre/responsable
2. Escribir justificación clara
3. Ejemplo: "Autorizado por su mamá vía teléfono"
4. Click en "PROCESAR DE TODAS FORMAS"
5. **Se registra en auditoría**

### IMPORTANTE
- ❌ **NO ignorar** restricciones sin autorización
- ✅ Siempre pedir justificación escrita
- 📞 En duda, contactar a padres o dirección
- 📝 Todas las excepciones quedan registradas

---

<a name="promociones"></a>
## 8. 🎉 PROMOCIONES Y DESCUENTOS

### Promociones Automáticas

El sistema aplica descuentos automáticamente:

```
┌─── PROMOCIÓN APLICADA ───┐
│ 🎉 COMBO DESAYUNO        │
│                          │
│ Café + Pan = Gs. 7,000   │
│ Precio normal: Gs. 8,000 │
│ AHORRAS: Gs. 1,000       │
└──────────────────────────┘
```

### Tipos de Promociones

1. **2x1** - Lleva 2, paga 1
2. **Combos** - Descuento por comprar productos juntos
3. **Descuento %** - Porcentaje sobre total
4. **Precio especial** - Precio fijo para producto

### Verificar Promoción
- Aparece automáticamente al agregar productos
- Se muestra en pantalla
- Descuento reflejado en total
- Impreso en ticket

---

<a name="anular-venta"></a>
## 9. ❌ ANULAR/CANCELAR VENTA

### Durante la Venta (antes de procesar)

**Limpiar Carrito**:
- Click en "LIMPIAR"
- Confirmar en diálogo
- Carrito queda vacío

**Quitar un Producto**:
- Click en 🗑️ junto al producto
- Se elimina del carrito

### Después de Procesar (venta ya hecha)

⚠️ **Requiere supervisor**

1. Llamar a supervisor
2. Ir a `/admin/ventas/`
3. Buscar venta por número
4. Click en "Anular Venta"
5. Ingresar motivo
6. Confirmar

**Efectos**:
- Si fue con tarjeta: Se devuelve saldo
- Si fue efectivo: Registrar devolución manual
- Se marca venta como "ANULADA"
- No se puede revertir

---

<a name="cierre-caja"></a>
## 10. 💼 CIERRE DE CAJA

### Al Final del Turno

1. **Contar Efectivo**
   - Contar dinero en caja
   - Separar por denominación

2. **Ir a Cierre de Caja**
   - Menú → "Cierre de Caja"
   - O `/pos/cierre-caja/`

3. **Ingresar Montos**
   ```
   ┌─── CIERRE DE CAJA ───┐
   │ Fecha: 10/01/2026    │
   │ Cajero: Juan Pérez   │
   │                      │
   │ Monto en Sistema:    │
   │   Efectivo: Gs. 150,000 │
   │   Tarjeta: Gs. 200,000  │
   │                      │
   │ Monto Físico:        │
   │   Efectivo: ______   │
   │                      │
   │ Diferencia: Gs. 0    │
   │                      │
   │ [CERRAR CAJA]        │
   └──────────────────────┘
   ```

4. **Verificar Diferencia**
   - ✅ Diferencia = 0 → Perfecto
   - ⚠️ Diferencia > 0 → Sobra dinero
   - ❌ Diferencia < 0 → Falta dinero

5. **Si hay Diferencia**
   - Recontar efectivo
   - Revisar ventas anuladas
   - Escribir observaciones
   - Avisar a supervisor si es grande

6. **Confirmar Cierre**
   - Click en "CERRAR CAJA"
   - Se genera reporte PDF
   - Imprimir y firmar
   - Entregar a supervisor

---

<a name="troubleshooting"></a>
## 11. 🔧 SOLUCIÓN DE PROBLEMAS

### Problema: Lector de Código de Barras No Funciona

**Solución**:
1. Verificar que esté conectado (USB)
2. Probar escanear en un notepad
3. Si no funciona: Ingresar código manualmente
4. Avisar a soporte técnico

---

### Problema: Impresora No Imprime

**Solución**:
1. Verificar que esté encendida
2. Verificar papel
3. Si falla: La venta se procesa igual
4. Reimprimir ticket desde historial
5. Avisar a soporte técnico

---

### Problema: Tarjeta No Se Lee

**Solución**:
1. Limpiar tarjeta
2. Intentar nuevamente
3. **Opción alternativa**: Ingresar número manualmente
   - Pedir número al estudiante
   - Escribir en campo "Tarjeta"
   - Click en "Buscar"
4. Avisar a padres que soliciten nueva tarjeta

---

### Problema: Sistema Lento

**Solución**:
1. Cerrar pestañas innecesarias del navegador
2. Refrescar página (F5)
3. Si persiste: Avisar a soporte

---

### Problema: Error al Procesar Venta

**Mensaje de error común**:
```
❌ Error: No se pudo procesar la venta
Código: 500
```

**Solución**:
1. **NO repetir** la operación inmediatamente
2. Verificar si la venta se procesó:
   - Ir a "Historial de Ventas"
   - Buscar última venta
3. Si NO se procesó:
   - Intentar nuevamente
   - Si falla: Anotar en cuaderno y avisar
4. Avisar a soporte técnico

---

## 📞 CONTACTO SOPORTE

**Problemas técnicos**:
- Email: soporte@cantinatita.com.py
- Teléfono: (021) XXX-XXXX
- WhatsApp: +595 XXX XXXXXX

**Horario de atención**:
- Lunes a Viernes: 7:00 - 18:00
- Sábados: 7:00 - 12:00

---

## ✅ CHECKLIST DIARIO

### Al Iniciar Turno
- [ ] Iniciar sesión
- [ ] Verificar impresora (papel, tinta)
- [ ] Verificar lector de código de barras
- [ ] Verificar conexión a internet
- [ ] Contar dinero inicial en caja

### Durante el Turno
- [ ] Procesar ventas normalmente
- [ ] Atender restricciones alimentarias
- [ ] Mantener orden y limpieza
- [ ] Registrar problemas o incidentes

### Al Finalizar Turno
- [ ] Contar efectivo
- [ ] Realizar cierre de caja
- [ ] Imprimir reporte
- [ ] Entregar efectivo y reporte a supervisor
- [ ] Cerrar sesión

---

**Versión**: 1.0  
**Última actualización**: Enero 2026  
**Autor**: Equipo Cantina Tita
