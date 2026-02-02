# 📋 Guía: Dónde Está el Checkbox de Facturación Electrónica

## ⚠️ El Checkbox NO es Visible Inicialmente

El checkbox "Emitir Factura Electrónica" **no aparece en la pantalla principal del POS**. 

Está en un **MODAL (ventana emergente)** que se abre cuando procesas el pago.

## 🎯 Ubicación Exacta

```
POS General
    ↓
Agregar productos al carrito
    ↓
Haz clic en "PROCESAR PAGO" (botón verde grande)
    ↓
Se abre MODAL de Pago
    ↓
Ahí verás el checkbox ✓ "Emitir Factura Electrónica"
```

## 📸 Pasos Visuales

### Paso 1: POS General Abierto
```
┌─────────────────────────────┐
│       POS GENERAL           │
├─────────────────────────────┤
│                             │
│  Buscar productos...        │
│  [Selecciona estudiante]    │
│                             │
│  Carrito:                   │
│  □ COCA COLA - ₲5,000       │
│  □ PULP - ₲5,000            │
│                             │
│  TOTAL: ₲10,000             │
│                             │
│  [PROCESAR PAGO] ← Click    │
│  [Limpiar Carrito]          │
└─────────────────────────────┘
```

### Paso 2: Modal de Pago se Abre
```
┌──────────────────────────────────┐
│    Procesar Pago (MODAL)         │
├──────────────────────────────────┤
│                                  │
│  Total a pagar: ₲10,000          │
│                                  │
│  Medios de Pago:                 │
│  [ 1 ] [ EFECTIVO ] [ 10,000 ]   │
│        [ Quitar ]                │
│  [ + Agregar Medio de Pago ]    │
│                                  │
│  Total a pagar: ₲10,000          │
│  Total recibido: ₲10,000         │
│  Cambio: ₲0                      │
│                                  │
│  ☑ Emitir Factura Electrónica  ← AQUÍ ESTÁ
│  Se generará automáticamente... │
│                                  │
│  [Cancelar] [PROCESAR PAGO]     │
└──────────────────────────────────┘
```

## ✅ Flujo Completo para Prueba

### 1. En el POS General
```
1. Ve a: http://localhost:8000/pos/general/
2. Busca un estudiante (escribe "PEDRO" o "00414")
3. Selecciona productos (haz clic en cada uno):
   - COCA COLA 250 ML
   - PULP NARANJA 250ML
4. Verás el carrito actualizado
5. Espera a que aparezca el botón "PROCESAR PAGO" (verde)
6. Haz clic en "PROCESAR PAGO"
```

### 2. En el Modal de Pago
```
7. Se abre una ventana emergente ("Modal")
8. Verás:
   - Total a pagar: ₲10,000
   - Medios de Pago: EFECTIVO ₲10,000
9. ⬇️ DESPLÁZATE HACIA ABAJO en el modal
10. Verás el checkbox: ☑ Emitir Factura Electrónica
11. Marca el checkbox ✓
12. Haz clic en "PROCESAR PAGO" (en el modal)
```

## 🔧 Solución si NO Ves el Checkbox

### Problema 1: No aparece el modal
**Solución**: Asegúrate de agregar productos al carrito antes.
```
Si carrito está vacío → El botón "PROCESAR PAGO" está deshabilitado
Debes:
1. Seleccionar un estudiante
2. Agregar 1+ productos
3. Luego podrás hacer clic en "PROCESAR PAGO"
```

### Problema 2: El modal aparece pero no ves el checkbox
**Solución**: Desplázate hacia abajo en el modal.
```
El checkbox está en la parte inferior del modal.
Si no lo ves:
1. Abre las DevTools (F12)
2. Verifica que modalPago: true en la consola
3. O, desplázate con el mouse/scroll en el modal
```

### Problema 3: El checkbox existe pero está oculto
**Solución**: Revisa que el modal tenga suficiente altura.
```
Si max-w-2xl es muy pequeño para mostrar todo:
En pos_general.html línea ~413:
<div class="modal-box max-w-2xl max-h-96"> ← Agregar max-h-96
```

## 📋 Estructura del Código

En `templates/gestion/pos_general.html`:

```html
<!-- Línea ~412: Modal de Pago -->
<div x-show="modalPago" class="modal modal-open">
    <div class="modal-box max-w-2xl">
        <!-- Contenido del modal -->
        
        <!-- Línea ~501: Checkbox de Facturación -->
        <div class="form-control mb-4">
            <label class="label cursor-pointer">
                <span class="label-text font-semibold">
                    Emitir Factura Electrónica
                </span>
                <input 
                    type="checkbox" 
                    x-model="emitirFactura"
                    class="checkbox checkbox-primary"
                >
            </label>
        </div>
        
        <!-- Botones Cancelar/Procesar -->
    </div>
</div>
```

## 🎯 Alpine.js Data

En la sección `<script>`:

```javascript
// Línea ~602
emitirFactura: false,  // ← Estado del checkbox
```

## 📊 Datos Enviados al Backend

Cuando haces clic en "PROCESAR PAGO" con el checkbox marcado:

```javascript
// Línea ~946 en pos_general.html
const request = {
    // ...otros datos...
    emitir_factura: this.emitirFactura  // ✓ true si está marcado
}

fetch('/gestion/pos/general/api/procesar-venta-factura/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(request)
})
```

## ✨ Resultado Esperado

Si todo está bien:

```
✅ Carrito no vacío
✅ Modal se abre al hacer clic en "PROCESAR PAGO"
✅ Ves el checkbox "Emitir Factura Electrónica"
✅ Puedes marcarlo/desmarcarlo
✅ Al procesar, se emite la factura (si el método lo permite)
```

## 🆘 Testing Rápido

```bash
# Abrir DevTools (F12) en Chrome y ejecutar:
# En la consola (Console):

// Verificar estado del modal
Alpine.$data(document.querySelector('[x-data]')).modalPago
// Output: true = está abierto

// Verificar estado del checkbox
Alpine.$data(document.querySelector('[x-data]')).emitirFactura
// Output: true/false = marcado o no

// Simular clic en "PROCESAR PAGO"
document.querySelector('[x-data]').dispatchEvent(new Event('modalPago'))
```

## 🔍 Checklist

- [ ] ¿Tienes productos en el carrito?
- [ ] ¿El botón "PROCESAR PAGO" está habilitado (no gris)?
- [ ] ¿Se abre el modal cuando haces clic?
- [ ] ¿Ves la sección "Medios de Pago" en el modal?
- [ ] ¿Desplazaste hacia abajo para ver el checkbox?
- [ ] ¿El checkbox dice "Emitir Factura Electrónica"?

Si todas las respuestas son SÍ, entonces está funcionando correctamente.

---

**Ubicación del código**: `templates/gestion/pos_general.html` líneas 412-530  
**Variable en Alpine.js**: `emitirFactura`  
**Enviado a**: `/gestion/pos/general/api/procesar-venta-factura/`  
**Estado**: ✅ Funcionando
