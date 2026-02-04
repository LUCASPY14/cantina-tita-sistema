# 🔍 AUDITORÍA: portal/recargar_tarjeta.html

**Fecha:** 3 de febrero de 2026  
**Template:** `frontend/templates/portal/recargar_tarjeta.html`  
**Tipo:** Proceso de recarga de saldo (flujo multi-paso)  
**Puntuación Actual:** 7.5/10

---

## 📋 INFORMACIÓN GENERAL

### Propósito
Proceso guiado de 3 pasos para recargar saldo en tarjetas de estudiantes: seleccionar hijo → elegir monto → método de pago.

### Contexto Técnico
- **Extiende:** `base.html`
- **Componente Alpine.js:** `recargarTarjeta()`
- **APIs utilizadas:**
  - `/api/portal/hijos/`
  - `/api/portal/recargas/procesar/`
- **Funcionalidad principal:** Wizard de recarga con validación por pasos

### Usuarios Objetivo
- Padres recargando saldo de sus hijos
- Proceso crítico (involucra dinero)
- Requiere máxima claridad y confirmación

---

## ✅ FORTALEZAS IDENTIFICADAS

### 1. Wizard Multi-Paso Bien Implementado
```javascript
function recargarTarjeta() {
    return {
        pasoActual: 1,
        hijoSeleccionado: null,
        recarga: { monto: 0, metodo_pago: '' },
        
        puedeAvanzar() {
            switch(this.pasoActual) {
                case 1: return this.hijoSeleccionado !== null;
                case 2: return this.recarga.monto >= 1000;
                case 3: return this.recarga.metodo_pago !== '';
            }
        }
    }
}
```
- ✅ Validación por paso
- ✅ Navegación adelante/atrás
- ✅ Estado centralizado

### 2. Indicadores Visuales de Progreso
```html
<div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
     :class="{ 'opacity-50': pasoActual > 1 }">
    <h2 class="text-2xl font-bold">
        <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white mr-2">1</span>
        Seleccionar Hijo
    </h2>
</div>
```
- ✅ Pasos numerados (1, 2, 3)
- ✅ Opacity reducida en pasos completados
- ✅ Botón "Cambiar" para editar pasos previos

### 3. Resumen Final Detallado
```html
<div class="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg space-y-3">
    <h3 class="font-bold text-lg mb-3">Resumen de Recarga</h3>
    
    <div class="flex justify-between">
        <span>Estudiante:</span>
        <span class="font-semibold" x-text="hijoSeleccionado?.nombre"></span>
    </div>
    
    <div class="flex justify-between">
        <span>Monto:</span>
        <span class="font-semibold text-primary text-xl" x-text="formatearPrecio(recarga.monto)"></span>
    </div>
</div>
```
- ✅ Confirmación visual antes de procesar
- ✅ Todos los datos en un solo lugar
- ✅ Previene errores de recarga

### 4. Montos Sugeridos UX
```html
<div class="grid grid-cols-3 md:grid-cols-5 gap-3">
    <template x-for="monto in montosSugeridos" :key="monto">
        <button type="button"
                @click="seleccionarMonto(monto)"
                class="btn"
                :class="recarga.monto === monto ? 'btn-primary' : 'btn-outline'">
            <span x-text="formatearPrecio(monto)"></span>
        </button>
    </template>
</div>
```
- ✅ Shortcuts para montos comunes (5k, 10k, 20k, 50k, 100k)
- ✅ Reduce fricción en el proceso
- ✅ Estado activo visual claro

### 5. Nuevo Saldo Estimado
```html
<template x-if="recarga.monto > 0">
    <div class="bg-gradient-to-br from-success/10 to-primary/10 p-4 rounded-lg">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Nuevo saldo después de la recarga:</p>
        <p class="text-3xl font-bold text-success" 
           x-text="formatearPrecio((hijoSeleccionado?.saldo || 0) + recarga.monto)"></p>
    </div>
</template>
```
- ✅ Cálculo en tiempo real
- ✅ Feedback visual inmediato
- ✅ Reduce errores (usuario ve resultado antes de confirmar)

### 6. Métodos de Pago con Info Adicional
```html
<template x-if="recarga.metodo_pago === 'transferencia'">
    <div class="alert alert-info">
        <i class="fas fa-info-circle"></i>
        <div class="text-sm">
            <p class="font-semibold mb-1">Datos para transferencia:</p>
            <p>Banco: Banco XYZ</p>
            <p>Cuenta: 1234567890</p>
        </div>
    </div>
</template>
```
- ✅ Información contextual según método seleccionado
- ✅ Instrucciones claras para cada opción
- ✅ Reducción de consultas de soporte

### 7. Pre-selección de Hijo desde URL
```javascript
async init() {
    await this.cargarHijos();
    
    // Si hay un hijo pre-seleccionado en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const hijoId = urlParams.get('hijo');
    if (hijoId) {
        const hijo = this.hijos.find(h => h.id == hijoId);
        if (hijo) {
            this.seleccionarHijo(hijo);
        }
    }
}
```
- ✅ Deep linking desde otras pantallas
- ✅ UX fluida (dashboard → recargar hijo específico)
- ✅ Reduce pasos del usuario

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 🔴 CRÍTICOS (Bloquean Accesibilidad)

#### 1. Sin ARIA Labels en Wizard Steps
**Ubicación:** Líneas 26-154  
**Problema:** Pasos sin estructura semántica

```html
<!-- ❌ INCORRECTO -->
<div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
    <h2 class="text-2xl font-bold">
        <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white mr-2">1</span>
        Seleccionar Hijo
    </h2>
</div>

<!-- ✅ CORRECTO -->
<section role="region" 
         aria-labelledby="paso1-titulo"
         :aria-current="pasoActual === 1 ? 'step' : false"
         class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
    <h2 id="paso1-titulo" class="text-2xl font-bold">
        <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white mr-2" aria-hidden="true">1</span>
        Seleccionar Hijo
    </h2>
</section>
```

#### 2. Cards de selección sin radio buttons
**Ubicación:** Líneas 44-76  
**Problema:** Selección de hijo con clicks, no con inputs

```html
<!-- ❌ INCORRECTO - Solo visual -->
<div class="cursor-pointer border-2 rounded-lg p-4"
     :class="hijoSeleccionado?.id === hijo.id ? 'border-primary' : 'border-gray-200'"
     @click="seleccionarHijo(hijo)">
    <!-- Contenido -->
</div>

<!-- ✅ CORRECTO - Con input real -->
<label :for="`hijo-${hijo.id}`" class="cursor-pointer border-2 rounded-lg p-4">
    <input type="radio" 
           :id="`hijo-${hijo.id}`"
           name="hijo-seleccionado"
           :value="hijo.id"
           x-model="hijoSeleccionado.id"
           @change="seleccionarHijo(hijo)"
           class="sr-only">
    <!-- Contenido visual -->
</label>
```

#### 3. Botones de navegación sin ARIA
**Ubicación:** Líneas 378-409  
**Problema:** Botones Anterior/Siguiente/Confirmar sin contexto

```html
<!-- ❌ INCORRECTO -->
<button type="button" @click="avanzar()" class="btn btn-primary flex-1">
    Siguiente
    <i class="fas fa-arrow-right ml-2"></i>
</button>

<!-- ✅ CORRECTO -->
<button type="button" 
        @click="avanzar()" 
        class="btn btn-primary flex-1"
        :disabled="!puedeAvanzar()"
        :aria-disabled="!puedeAvanzar() ? 'true' : 'false'"
        :aria-label="pasoActual === 1 ? 'Continuar al paso 2: Seleccionar monto' : 'Continuar al paso 3: Método de pago'">
    Siguiente
    <i class="fas fa-arrow-right ml-2" aria-hidden="true"></i>
</button>
```

#### 4. Iconos sin aria-hidden (15+ ocurrencias)
**Ubicación:** Líneas 12, 250, 256, 262, 269, 311, etc.  
**Problema:** Screen readers anuncian clases CSS

```html
<!-- ❌ INCORRECTO -->
<i class="fas fa-credit-card mr-3 text-primary"></i>

<!-- ✅ CORRECTO -->
<i class="fas fa-credit-card mr-3 text-primary" aria-hidden="true"></i>
```

#### 5. Sin confirmación modal antes de procesar
**Ubicación:** Función `procesarRecarga()`  
**Problema:** No hay último paso de confirmación

```javascript
// ❌ INCORRECTO - Procesa directo
async procesarRecarga() {
    this.procesando = true;
    const response = await fetch('/api/portal/recargas/procesar/', {...});
}

// ✅ CORRECTO - Con confirmación
async procesarRecarga() {
    // Mostrar modal de confirmación
    const confirmado = await this.confirmarRecarga();
    if (!confirmado) return;
    
    this.procesando = true;
    const response = await fetch('/api/portal/recargas/procesar/', {...});
}
```

### 🟡 MEDIOS (Afectan UX)

#### 6. Monto personalizado sin validación en vivo
**Ubicación:** Líneas 134-152  
**Problema:** Validación solo al submit

```html
<!-- ❌ INCORRECTO -->
<input type="number" 
       x-model.number="recarga.monto"
       min="1000"
       step="1000"
       required>

<!-- ✅ CORRECTO - Con validación en vivo -->
<input type="number" 
       x-model.number="recarga.monto"
       @input="validarMonto()"
       min="1000"
       step="1000"
       :aria-invalid="recarga.monto > 0 && recarga.monto < 1000 ? 'true' : 'false'"
       aria-describedby="monto-help monto-error"
       required>
<div id="monto-error" 
     x-show="recarga.monto > 0 && recarga.monto < 1000"
     role="alert"
     class="text-error text-sm mt-1">
    El monto mínimo es 1.000 Gs.
</div>
```

#### 7. Método de pago sin role="radiogroup"
**Ubicación:** Líneas 168-197  
**Problema:** Grupo de opciones sin estructura semántica

```html
<!-- ❌ INCORRECTO -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="cursor-pointer border-2 rounded-lg p-6"
         @click="recarga.metodo_pago = 'transferencia'">
        <!-- Opción -->
    </div>
</div>

<!-- ✅ CORRECTO -->
<div role="radiogroup" 
     aria-labelledby="metodo-pago-label"
     class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <span id="metodo-pago-label" class="sr-only">Seleccionar método de pago</span>
    
    <label class="cursor-pointer border-2 rounded-lg p-6">
        <input type="radio" 
               name="metodo-pago"
               value="transferencia"
               x-model="recarga.metodo_pago"
               class="sr-only"
               aria-label="Transferencia bancaria - Inmediato">
        <!-- Contenido visual -->
    </label>
</div>
```

#### 8. Sin loading state al cargar hijos
**Ubicación:** Función `init()`  
**Problema:** No hay feedback mientras carga lista de hijos

```javascript
// ❌ INCORRECTO
async init() {
    await this.cargarHijos();
}

// ✅ CORRECTO
async init() {
    this.cargandoHijos = true;
    await this.cargarHijos();
    this.cargandoHijos = false;
}
```

```html
<!-- Agregar skeleton -->
<template x-if="cargandoHijos">
    <div role="status" aria-live="polite">
        <div class="skeleton h-24 w-full"></div>
        <span class="sr-only">Cargando lista de hijos...</span>
    </div>
</template>
```

#### 9. Botón "Confirmar Recarga" sin resumen final
**Ubicación:** Líneas 389-409  
**Problema:** El botón está lejos del resumen (scroll)

```html
<!-- ✅ MEJORA SUGERIDA - Modal de confirmación -->
<button type="button"
        @click="mostrarModalConfirmacion()"
        x-show="pasoActual === 3"
        class="btn btn-primary flex-1"
        aria-label="Revisar y confirmar recarga">
    <i class="fas fa-check-circle mr-2" aria-hidden="true"></i>
    Confirmar Recarga
</button>

<!-- Modal con resumen completo -->
<div x-show="modalConfirmacion" role="dialog" aria-modal="true">
    <h3>¿Confirmar esta recarga?</h3>
    <p>Estudiante: <strong x-text="hijoSeleccionado?.nombre"></strong></p>
    <p>Monto: <strong x-text="formatearPrecio(recarga.monto)"></strong></p>
    <p>Método: <strong x-text="recarga.metodo_pago"></strong></p>
    <button @click="procesarRecarga()">Confirmar</button>
</div>
```

### 🟢 MENORES (Mejoras Opcionales)

#### 10. Sin opción "Recordar método de pago"
**Ubicación:** Paso 3  
**Sugerencia:** Guardar preferencia en localStorage

```javascript
// ✅ MEJORA SUGERIDA
seleccionarMetodoPago(metodo) {
    this.recarga.metodo_pago = metodo;
    
    // Guardar preferencia
    if (this.recordarMetodo) {
        localStorage.setItem('metodo_pago_preferido', metodo);
    }
}

async init() {
    await this.cargarHijos();
    
    // Pre-seleccionar método preferido
    const metodoPreferido = localStorage.getItem('metodo_pago_preferido');
    if (metodoPreferido) {
        this.recarga.metodo_pago = metodoPreferido;
    }
}
```

#### 11. Sin historial de recargas previas
**Ubicación:** N/A  
**Sugerencia:** Mostrar últimas 3 recargas del hijo seleccionado

```html
<!-- ✅ MEJORA SUGERIDA -->
<template x-if="hijoSeleccionado && pasoActual >= 2">
    <div class="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg mt-4">
        <h4 class="font-semibold mb-2">Últimas recargas de <span x-text="hijoSeleccionado.nombre"></span>:</h4>
        <ul class="space-y-1 text-sm">
            <template x-for="recarga in hijoSeleccionado.ultimas_recargas" :key="recarga.id">
                <li><span x-text="recarga.fecha"></span> - <span x-text="formatearPrecio(recarga.monto)"></span></li>
            </template>
        </ul>
    </div>
</template>
```

#### 12. Sin recibo/comprobante descargable
**Ubicación:** Después de `procesarRecarga()` exitoso  
**Sugerencia:** Generar PDF o permitir imprimir

```javascript
// ✅ MEJORA SUGERIDA
async procesarRecarga() {
    // ... procesar
    if (data.success) {
        this.showNotification('Recarga procesada exitosamente', 'success');
        
        // Ofrecer descarga de comprobante
        this.comprobanteId = data.comprobante_id;
        this.mostrarModalComprobante = true;
    }
}
```

---

## 📊 MATRIZ DE EVALUACIÓN

| Criterio | Puntuación | Observaciones |
|----------|-----------|---------------|
| **ARIA Labels** | 0/10 | Sin implementación |
| **Wizard/Stepper** | 8/10 | Buen flujo pero sin ARIA |
| **Validación** | 7/10 | Por paso pero mejorable |
| **Confirmación** | 5/10 | Sin modal final de confirmación |
| **Formularios** | 6/10 | Funcionales pero sin radio buttons reales |
| **Loading States** | 4/10 | Solo en submit, no en carga inicial |
| **Screen Reader** | 2/10 | Muy pobre soporte |
| **UX Visual** | 9/10 | Excelente diseño wizard |
| **Responsive** | 9/10 | Bien adaptado |
| **Manejo Errores** | 7/10 | Console + notification |

**PUNTUACIÓN TOTAL:** 7.5/10

---

## 🎯 PLAN DE MEJORAS

### Prioridad 1 (CRÍTICA) - 2.5 horas
1. ✅ Agregar roles semánticos a wizard steps (role="region", aria-current) (30 min)
2. ✅ Implementar radio buttons reales para selección hijo/método pago (45 min)
3. ✅ Agregar ARIA labels a todos los botones (20 min)
4. ✅ Agregar `aria-hidden="true"` a 15+ iconos (15 min)
5. ✅ Implementar modal de confirmación final antes de procesar (40 min)
6. ✅ Loading state al cargar hijos (20 min)

### Prioridad 2 (MEDIA) - 1.5 horas
7. ✅ Validación en vivo de monto con `aria-invalid` (30 min)
8. ✅ role="radiogroup" en método de pago (20 min)
9. ✅ Mejorar estados disabled con aria-disabled (15 min)
10. ✅ Agregar textos SR en botones de acción (15 min)
11. ✅ Historial de recargas previas (30 min)

### Prioridad 3 (BAJA) - 1 hora
12. ✅ Opción "Recordar método de pago" (20 min)
13. ✅ Comprobante descargable/imprimible (30 min)
14. ✅ Validación anti-doble-click en submit (10 min)

**TIEMPO TOTAL ESTIMADO:** 5 horas

---

## 🔧 ELEMENTOS A MODIFICAR

### HTML
- [ ] 3 secciones de wizard → `role="region"`, `aria-current="step"`
- [ ] 15+ iconos → `aria-hidden="true"`
- [ ] Selección de hijos → convertir a radio buttons
- [ ] Métodos de pago → `role="radiogroup"` con radios
- [ ] 5 botones → ARIA labels descriptivos
- [ ] Input monto → `aria-invalid`, `aria-describedby`
- [ ] Agregar modal de confirmación final
- [ ] Loading skeleton al inicio

### JavaScript
- [ ] Agregar `cargandoHijos: false`
- [ ] Agregar `modalConfirmacion: false`
- [ ] Función `validarMonto()`
- [ ] Función `confirmarRecarga()`
- [ ] Cargar `ultimas_recargas` en API
- [ ] localStorage para método preferido
- [ ] Generar comprobante PDF

---

## 📝 NOTAS ADICIONALES

### Puntos Positivos
- **Wizard multi-paso**: Excelente UX para proceso complejo
- **Resumen final**: Muy útil para prevenir errores
- **Montos sugeridos**: Reduce fricción significativamente
- **Deep linking**: Pre-selección desde URL es smart

### Consideraciones Críticas
- **Involucra dinero**: Requiere máxima confirmación
- **Padres no técnicos**: Debe ser extremadamente claro
- **Métodos de pago variados**: Cada uno necesita instrucciones
- **Errores costosos**: Un error = pérdida de confianza

### Riesgos
- Sin confirmación modal = riesgo de recargas accidentales
- Sin radio buttons = inaccesible para navegación por teclado
- Sin validación en vivo = errores al final del proceso
- Sin comprobante = difícil probar la transacción

### Mejoras Futuras
- Integración con pasarelas de pago (Stripe, PayPal)
- Recargas programadas/automáticas
- Alertas de saldo bajo con recarga rápida
- Historial completo de transacciones

---

**Auditor:** GitHub Copilot  
**Próximo paso:** Implementar mejoras en los 3 templates auditados
