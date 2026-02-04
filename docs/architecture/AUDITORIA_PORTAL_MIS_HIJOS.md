# 🔍 AUDITORÍA: portal/mis_hijos.html

**Fecha:** 3 de febrero de 2026  
**Template:** `frontend/templates/portal/mis_hijos.html`  
**Tipo:** Gestión de tarjetas de estudiantes  
**Puntuación Actual:** 7.0/10

---

## 📋 INFORMACIÓN GENERAL

### Propósito
Pantalla para gestionar las tarjetas de los hijos: ver saldos, historial, agregar nuevos hijos y realizar recargas directas.

### Contexto Técnico
- **Extiende:** `base.html`
- **Componente Alpine.js:** `misHijos()`
- **APIs utilizadas:** 
  - `/api/portal/hijos/`
  - `/api/tarjetas/verificar/{numero}/`
  - `/api/portal/hijos/agregar/`
  - `/api/portal/hijos/{id}/historial/`
- **Funcionalidad principal:** CRUD de relaciones padre-hijo con tarjetas

### Usuarios Objetivo
- Padres de familia gestionando múltiples hijos
- Tutores con varios estudiantes a cargo

---

## ✅ FORTALEZAS IDENTIFICADAS

### 1. Componente Alpine.js Completo
```javascript
function misHijos() {
    return {
        cargando: true,
        hijos: [],
        modalAbierto: false,
        modalHistorialAbierto: false,
        guardando: false,
        cargandoHistorial: false,
        tarjetaBuscada: false,
        tarjetaEncontrada: false,
        // ... más estados
    }
}
```
- ✅ Gestión de estados múltiples bien organizada
- ✅ Separación clara de modales (agregar/historial)
- ✅ Estados de carga independientes

### 2. Grid Cards Responsivo Atractivo
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <template x-for="hijo in hijos" :key="hijo.id">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-shadow">
            <!-- Card con gradiente -->
        </div>
    </template>
</div>
```
- ✅ Layout profesional en grid
- ✅ Transiciones suaves (hover effects)
- ✅ Diseño visual atractivo con gradientes

### 3. Validación de Tarjeta en Tiempo Real
```javascript
async buscarTarjeta() {
    if (this.formulario.numero_tarjeta.length < 5) {
        this.tarjetaBuscada = false;
        this.tarjetaEncontrada = false;
        return;
    }
    
    const response = await fetch(`/api/tarjetas/verificar/${this.formulario.numero_tarjeta}/`);
    // ... validación
}
```
- ✅ Búsqueda incremental
- ✅ Feedback inmediato al usuario
- ✅ Prevención de errores (tarjeta inválida)

### 4. Modales Bien Estructurados
```html
<!-- Modal agregar hijo -->
<div x-show="modalAbierto" @click.self="cerrarModal()" class="fixed inset-0 bg-black bg-opacity-50">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl">
        <!-- Formulario -->
    </div>
</div>

<!-- Modal historial -->
<div x-show="modalHistorialAbierto" @click.self="cerrarModalHistorial()">
    <!-- Lista de transacciones -->
</div>
```
- ✅ Dos modales independientes
- ✅ Cierre por click fuera del modal
- ✅ Sticky headers en modales

### 5. Estados Visuales Claros
```html
<!-- Badge de estado -->
<span class="badge" :class="hijo.tarjeta_activa ? 'badge-success' : 'badge-error'">
    <span x-text="hijo.tarjeta_activa ? 'Activa' : 'Bloqueada'"></span>
</span>

<!-- Alerta de saldo bajo -->
<p class="text-3xl font-bold" 
   :class="hijo.saldo < 5000 ? 'text-warning' : 'text-success'"
   x-text="formatearPrecio(hijo.saldo)"></p>
```
- ✅ Colores semánticos (success/error/warning)
- ✅ Indicadores visuales de estado
- ✅ Alertas contextuales

### 6. Empty State Bien Diseñado
```html
<template x-if="!cargando && hijos.length === 0">
    <div class="text-center py-20">
        <i class="fas fa-child text-8xl text-gray-300 dark:text-gray-600 mb-6"></i>
        <h2 class="text-2xl font-bold text-gray-600 dark:text-gray-400 mb-4">
            Aún no has agregado ningún hijo
        </h2>
        <button @click="abrirModalAgregar()" class="btn btn-primary btn-lg">
            <i class="fas fa-user-plus mr-2"></i>
            Agregar Mi Primer Hijo
        </button>
    </div>
</template>
```
- ✅ Mensaje claro cuando no hay datos
- ✅ CTA (Call To Action) prominente
- ✅ Diseño visual atractivo

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 🔴 CRÍTICOS (Bloquean Accesibilidad)

#### 1. Sin ARIA Labels (0% Implementación)
**Ubicación:** Todo el template  
**Problema:** Elementos interactivos sin descripciones para screen readers

```html
<!-- ❌ INCORRECTO - Botón sin contexto -->
<button @click="abrirModalAgregar()" class="btn btn-primary btn-lg">
    <i class="fas fa-user-plus mr-2"></i>
    Agregar Hijo
</button>

<!-- ✅ CORRECTO -->
<button @click="abrirModalAgregar()" 
        class="btn btn-primary btn-lg"
        aria-label="Abrir formulario para agregar nuevo hijo">
    <i class="fas fa-user-plus mr-2" aria-hidden="true"></i>
    Agregar Hijo
</button>
```

#### 2. Iconos sin aria-hidden (20+ ocurrencias)
**Ubicación:** Líneas 13, 42, 58, 64, 73, 97, 103, 133, 143, 162, 237, 271, etc.  
**Problema:** Screen readers leen "fas fa-child" en lugar de omitirlo

```html
<!-- ❌ INCORRECTO -->
<i class="fas fa-users mr-3 text-primary"></i>

<!-- ✅ CORRECTO -->
<i class="fas fa-users mr-3 text-primary" aria-hidden="true"></i>
```

#### 3. Modales sin role="dialog" y aria-modal
**Ubicación:** Líneas 149, 245  
**Problema:** Modales no se identifican como diálogos

```html
<!-- ❌ INCORRECTO -->
<div x-show="modalAbierto" 
     @click.self="cerrarModal()"
     class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">

<!-- ✅ CORRECTO -->
<div x-show="modalAbierto" 
     @click.self="cerrarModal()"
     role="dialog"
     aria-modal="true"
     aria-labelledby="modal-agregar-titulo"
     class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
```

#### 4. Formularios sin labels asociados
**Ubicación:** Líneas 169-179, 216-227  
**Problema:** Inputs sin asociación explícita label/input

```html
<!-- ❌ INCORRECTO -->
<label class="label">
    <span class="label-text">Número de Tarjeta *</span>
</label>
<input type="text" x-model="formulario.numero_tarjeta" required>

<!-- ✅ CORRECTO -->
<label for="numero-tarjeta" class="label">
    <span class="label-text">Número de Tarjeta *</span>
</label>
<input type="text" 
       id="numero-tarjeta"
       x-model="formulario.numero_tarjeta"
       aria-label="Número de tarjeta del estudiante"
       aria-describedby="tarjeta-help"
       required>
<span id="tarjeta-help" class="label-text-alt text-gray-500">
    Escanea el código de barras de la tarjeta
</span>
```

#### 5. Cards de hijos sin estructura semántica
**Ubicación:** Líneas 39-145  
**Problema:** Cards sin roles ARIA ni contexto

```html
<!-- ❌ INCORRECTO -->
<div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg">
    <div class="bg-gradient-to-br from-primary to-secondary p-6 text-white">
        <h3 class="text-xl font-bold text-center mb-1" x-text="hijo.nombre"></h3>
    </div>
</div>

<!-- ✅ CORRECTO -->
<article role="article" 
         :aria-label="`Tarjeta de ${hijo.nombre}`"
         class="bg-white dark:bg-gray-800 rounded-xl shadow-lg">
    <header class="bg-gradient-to-br from-primary to-secondary p-6 text-white">
        <h3 class="text-xl font-bold text-center mb-1" x-text="hijo.nombre"></h3>
    </header>
</article>
```

### 🟡 MEDIOS (Afectan UX)

#### 6. Sin debounce en buscarTarjeta()
**Ubicación:** Línea 170, función `buscarTarjeta()`  
**Problema:** Una petición API por cada tecla presionada

```javascript
// ❌ INCORRECTO
<input type="text" 
       x-model="formulario.numero_tarjeta"
       @input="buscarTarjeta()">

// ✅ CORRECTO - Con debounce
<input type="text" 
       x-model="formulario.numero_tarjeta"
       @input.debounce.500ms="buscarTarjeta()">
```

#### 7. Loading states sin texto para screen readers
**Ubicación:** Líneas 28-36, 260-265, 320-328  
**Problema:** Skeletons sin descripción

```html
<!-- ❌ INCORRECTO -->
<template x-if="cargando">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="skeleton h-32 w-full mb-4"></div>
    </div>
</template>

<!-- ✅ CORRECTO -->
<template x-if="cargando">
    <div role="status" aria-live="polite">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="skeleton h-32 w-full mb-4"></div>
        </div>
        <span class="sr-only">Cargando lista de hijos...</span>
    </div>
</template>
```

#### 8. Botones sin estados disabled/aria-disabled
**Ubicación:** Líneas 97-106, 227-241  
**Problema:** Botones no indican cuando están deshabilitados

```html
<!-- ❌ INCORRECTO -->
<button type="submit" 
        class="btn btn-primary flex-1"
        :disabled="!tarjetaEncontrada || guardando">
    Agregar
</button>

<!-- ✅ CORRECTO -->
<button type="submit" 
        class="btn btn-primary flex-1"
        :disabled="!tarjetaEncontrada || guardando"
        :aria-disabled="!tarjetaEncontrada || guardando ? 'true' : 'false'"
        aria-label="Agregar hijo a mi lista">
    <template x-if="!guardando">
        <span><i class="fas fa-save mr-2" aria-hidden="true"></i>Agregar</span>
    </template>
    <template x-if="guardando">
        <span role="status" aria-live="polite">
            <span class="loading loading-spinner loading-sm mr-2"></span>
            <span class="sr-only">Guardando información...</span>
            Guardando...
        </span>
    </template>
</button>
```

#### 9. Alertas de validación sin role="alert"
**Ubicación:** Líneas 188-201  
**Problema:** Feedback de validación no se anuncia

```html
<!-- ❌ INCORRECTO -->
<template x-if="tarjetaEncontrada">
    <div class="alert alert-success">
        <i class="fas fa-check-circle"></i>
        <p>Tarjeta encontrada</p>
    </div>
</template>

<!-- ✅ CORRECTO -->
<template x-if="tarjetaEncontrada">
    <div class="alert alert-success" role="alert" aria-live="polite">
        <i class="fas fa-check-circle" aria-hidden="true"></i>
        <div>
            <p class="font-semibold">Tarjeta encontrada</p>
            <p class="text-sm" x-text="`Estudiante: ${tarjetaInfo.nombre}`"></p>
        </div>
    </div>
</template>
```

#### 10. Sin filtro/búsqueda de hijos
**Ubicación:** N/A (Funcionalidad faltante)  
**Problema:** Si un padre tiene 10+ hijos, es difícil encontrar uno específico

```html
<!-- ✅ MEJORA SUGERIDA -->
<div class="mb-6">
    <input type="text" 
           x-model="filtroNombre"
           @input.debounce.300ms="filtrarHijos()"
           placeholder="Buscar hijo por nombre..."
           aria-label="Buscar hijo por nombre"
           class="input input-bordered w-full">
</div>
```

### 🟢 MENORES (Mejoras Opcionales)

#### 11. Sin confirmación antes de acciones críticas
**Ubicación:** Función `agregarHijo()`  
**Sugerencia:** Confirmación antes de agregar (evitar duplicados)

```javascript
// ✅ MEJORA SUGERIDA
async agregarHijo() {
    // Verificar si ya existe
    const yaExiste = this.hijos.some(h => h.numero_tarjeta === this.formulario.numero_tarjeta);
    
    if (yaExiste) {
        this.showNotification('Esta tarjeta ya está asociada a tu cuenta', 'warning');
        return;
    }
    
    this.guardando = true;
    // ... resto del código
}
```

#### 12. Historial sin paginación
**Ubicación:** Modal de historial (líneas 245-309)  
**Problema:** Si hay 100+ transacciones, carga lenta

```javascript
// ✅ MEJORA SUGERIDA
async verHistorial(hijo) {
    this.hijoSeleccionado = hijo;
    this.modalHistorialAbierto = true;
    this.cargandoHistorial = true;
    this.paginaActual = 1;
    
    // Cargar solo primeras 20
    const response = await fetch(`/api/portal/hijos/${hijo.id}/historial/?limit=20&offset=0`);
    // ...
}
```

#### 13. Sin opción para editar relación
**Ubicación:** Cards de hijos  
**Sugerencia:** Permitir cambiar relación (padre/madre/tutor)

```html
<!-- ✅ MEJORA SUGERIDA -->
<div class="border-t dark:border-gray-700 pt-4">
    <p class="text-xs text-gray-500">Relación: <span x-text="hijo.relacion"></span></p>
    <button @click="editarRelacion(hijo)" 
            class="btn btn-xs btn-ghost"
            aria-label="Editar relación con el estudiante">
        <i class="fas fa-edit" aria-hidden="true"></i>
        Editar
    </button>
</div>
```

---

## 📊 MATRIZ DE EVALUACIÓN

| Criterio | Puntuación | Observaciones |
|----------|-----------|---------------|
| **ARIA Labels** | 0/10 | Sin implementación |
| **Roles Semánticos** | 2/10 | Solo HTML básico |
| **Modales** | 6/10 | Funcionales pero sin ARIA |
| **Formularios** | 5/10 | Validación JS pero sin labels asociados |
| **Loading States** | 7/10 | Skeletons implementados |
| **Navegación por Teclado** | 6/10 | Funcional pero mejorable |
| **Screen Reader** | 2/10 | Muy pobre soporte |
| **Validación** | 8/10 | Búsqueda de tarjeta en tiempo real ✅ |
| **UX Visual** | 9/10 | Diseño atractivo y profesional |
| **Responsive** | 9/10 | Excelente adaptación |

**PUNTUACIÓN TOTAL:** 7.0/10

---

## 🎯 PLAN DE MEJORAS

### Prioridad 1 (CRÍTICA) - 2 horas
1. ✅ Agregar ARIA labels a todos los botones y links (30 min)
2. ✅ Agregar `aria-hidden="true"` a 20+ iconos (20 min)
3. ✅ Implementar `role="dialog"` y `aria-modal` en modales (30 min)
4. ✅ Asociar labels con inputs usando `for`/`id` (20 min)
5. ✅ Agregar roles semánticos a cards (article, header) (20 min)
6. ✅ Textos SR en loading states y spinners (20 min)

### Prioridad 2 (MEDIA) - 1.5 horas
7. ✅ Implementar debounce en búsqueda de tarjeta (15 min)
8. ✅ Agregar `role="alert"` en mensajes de validación (15 min)
9. ✅ Mejorar estados disabled con aria-disabled (20 min)
10. ✅ Agregar búsqueda/filtro de hijos (40 min)

### Prioridad 3 (BAJA) - 1 hora
11. ✅ Validación anti-duplicados antes de agregar (20 min)
12. ✅ Implementar paginación en historial (30 min)
13. ✅ Agregar opción para editar relación (10 min)

**TIEMPO TOTAL ESTIMADO:** 4.5 horas

---

## 🔧 ELEMENTOS A MODIFICAR

### HTML
- [ ] 20+ iconos → agregar `aria-hidden="true"`
- [ ] 1 botón "Agregar Hijo" → ARIA label
- [ ] 2 modales → `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- [ ] Cards de hijos → `role="article"`, ARIA labels
- [ ] 3 formularios → asociar labels con `for`/`id`
- [ ] 2 alertas de validación → `role="alert"`, `aria-live="polite"`
- [ ] 6 botones en cards → ARIA labels descriptivos
- [ ] 3 loading states → `role="status"`, textos SR
- [ ] Agregar input de búsqueda/filtro

### JavaScript
- [ ] `buscarTarjeta()` → cambiar a debounce en HTML
- [ ] Agregar función `filtrarHijos()`
- [ ] `agregarHijo()` → validación anti-duplicados
- [ ] `verHistorial()` → implementar paginación

---

## 📝 NOTAS ADICIONALES

### Puntos Positivos
- Validación de tarjeta en tiempo real es excelente UX
- Modales bien estructurados y separados
- Empty state muy bien diseñado
- Cards visualmente atractivas

### Consideraciones Especiales
- Padres pueden tener 1-10+ hijos (requiere búsqueda/filtro)
- Tarjetas deben escanearse (UX de input debe soportar scanner)
- Relación padre-hijo es sensible (privacidad)
- Historial puede tener muchas transacciones

### Riesgos
- Sin ARIA labels = padres con discapacidad visual no pueden usar
- Sin debounce = sobrecarga de servidor con búsquedas
- Sin validación de duplicados = puede agregar mismo hijo 2 veces

---

**Auditor:** GitHub Copilot  
**Próximo paso:** Auditar portal/recargar_tarjeta.html
