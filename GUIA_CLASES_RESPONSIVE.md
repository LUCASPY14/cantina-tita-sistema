# 📱 Guía Rápida: Clases Responsive MetrePay

## 🎯 Breakpoints del Sistema

```
xs:   375px   - Smartphones pequeños (iPhone SE)
sm:   640px   - Smartphones (iPhone 12/13/14)
md:   768px   - Tablets pequeños (iPad Mini)
lg:   1024px  - Tablets grandes (iPad)
xl:   1280px  - Laptops
2xl:  1536px  - Monitores grandes
```

---

## 📐 Grid Responsive

### Pattern Común: Mobile → Tablet → Desktop
```html
<!-- 1 columna móvil, 2 en tablet, 4 en desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- contenido -->
</div>

<!-- 2 columnas móvil (xs), 3 en tablet, 4 en desktop -->
<div class="grid grid-cols-2 xs:grid-cols-3 md:grid-cols-4 gap-3 md:gap-6">
    <!-- contenido -->
</div>
```

### Grids Automáticos Responsivos
```html
<!-- Mínimo 160px por item, crece hasta 220px -->
<div class="grid-auto-mobile">
    <!-- Auto-fill items -->
</div>
```

---

## 📏 Spacing Responsive

### Padding
```html
<!-- Padding pequeño en móvil, grande en desktop -->
<div class="p-4 md:p-6 lg:p-8">
    
<!-- Padding horizontal adaptativo -->
<div class="px-4 md:px-8 lg:px-12">
    
<!-- Padding bottom para bottom nav -->
<div class="pb-24 md:pb-8">
    <!-- pb-24 (96px) en móvil para espacio del bottom nav -->
</div>
```

### Gap
```html
<!-- Gaps responsive en grids -->
<div class="grid gap-3 md:gap-4 lg:gap-6">
```

---

## 📝 Texto Responsive

### Tamaño de Fuente
```html
<!-- Título adaptativo -->
<h1 class="text-2xl md:text-4xl lg:text-5xl">
    Título Grande
</h1>

<!-- Párrafo -->
<p class="text-sm md:text-base lg:text-lg">
    Texto del párrafo
</p>

<!-- Caption -->
<span class="text-xs md:text-sm">
    Texto pequeño
</span>
```

### Texto Condicional
```html
<!-- Texto completo en desktop, corto en móvil -->
<span class="hidden sm:inline">Texto Completo Largo</span>
<span class="sm:hidden">Corto</span>

<!-- Ejemplo real -->
<h1>
    <span class="hidden sm:inline">Dashboard Administrativo</span>
    <span class="sm:hidden">Admin</span>
</h1>
```

---

## 🖼️ Visibilidad Responsive

### Mostrar/Ocultar por Breakpoint
```html
<!-- Oculto en móvil, visible en tablet+ -->
<div class="hidden md:block">
    Contenido solo desktop
</div>

<!-- Visible solo en móvil -->
<div class="md:hidden">
    Contenido solo móvil
</div>

<!-- Visible en tablet y desktop, oculto en móvil -->
<div class="hidden sm:block">
    Tablet y desktop
</div>

<!-- Oculto en pantallas extra pequeñas -->
<div class="hidden xs:block">
    Oculto solo en < 375px
</div>
```

### Clases Utilitarias Personalizadas
```html
<!-- Del archivo mobile-responsive.css -->
<div class="hide-on-mobile">
    <!-- Oculto en pantallas < 768px -->
</div>

<div class="show-on-mobile">
    <!-- Visible solo en < 768px -->
</div>
```

---

## 🔘 Botones Responsive

### Tamaños
```html
<!-- Botón pequeño en móvil, normal en desktop -->
<button class="btn btn-sm md:btn-md lg:btn-lg">
    Botón
</button>

<!-- Label oculto en móvil -->
<button class="btn btn-primary">
    <i class="fas fa-save"></i>
    <span class="hidden sm:inline ml-2">Guardar</span>
</button>
```

### Botones de Acción
```html
<!-- Botones full-width en móvil, auto en desktop -->
<div class="flex flex-col xs:flex-row gap-2">
    <button class="btn btn-primary flex-1 xs:flex-none">
        Primario
    </button>
    <button class="btn btn-ghost flex-1 xs:flex-none">
        Secundario
    </button>
</div>
```

---

## 📊 Tablas Responsive

### Tabla con Mobile Stack
```html
<table class="table table-zebra w-full table-mobile-stack">
    <thead data-mobile="hide">
        <tr class="bg-base-200">
            <th>Columna 1</th>
            <th>Columna 2</th>
            <th>Columna 3</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td data-label="Columna 1">Valor 1</td>
            <td data-label="Columna 2">Valor 2</td>
            <td data-label="Columna 3">Valor 3</td>
        </tr>
    </tbody>
</table>
```

**Resultado:**
- **Desktop**: Tabla normal horizontal
- **Móvil**: Cada fila se apila verticalmente con labels

---

## 🎴 Cards Responsive

### Card con Altura Mínima
```html
<div class="bg-white rounded-xl p-4 md:p-6 min-h-[120px] md:min-h-[140px]">
    <!-- Contenido -->
</div>
```

### Stats Card Responsive
```html
<div class="stat-card">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-xs md:text-sm opacity-90">Label</p>
            <p class="text-2xl md:text-3xl lg:text-4xl font-bold">
                Valor
            </p>
        </div>
        <i class="fas fa-icon text-3xl md:text-4xl lg:text-5xl"></i>
    </div>
</div>
```

---

## 🎛️ Flexbox Responsive

### Dirección
```html
<!-- Vertical en móvil, horizontal en tablet+ -->
<div class="flex flex-col md:flex-row gap-4">
    <div>Item 1</div>
    <div>Item 2</div>
</div>
```

### Alineación
```html
<!-- Stack en móvil, space-between en desktop -->
<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>Izquierda</div>
    <div>Derecha</div>
</div>
```

---

## 📐 Height & Width Responsive

### Altura
```html
<!-- Altura fija en móvil, auto en desktop -->
<div class="h-24 md:h-32 lg:h-40">

<!-- Altura mínima adaptativa -->
<div class="min-h-[100px] md:min-h-[150px]">

<!-- Altura completa solo en desktop -->
<div class="h-auto md:h-screen">
```

### Ancho
```html
<!-- Full width en móvil, auto en desktop -->
<div class="w-full md:w-auto">

<!-- Max width responsive -->
<input class="w-full md:max-w-md lg:max-w-lg">
```

---

## 🎨 Íconos Responsive

### Tamaños
```html
<!-- Ícono pequeño en móvil, grande en desktop -->
<i class="fas fa-home text-lg md:text-2xl lg:text-3xl"></i>

<!-- Con margen adaptativo -->
<i class="fas fa-icon mr-2 md:mr-3"></i>
```

---

## 📱 Componentes Móviles Especiales

### Bottom Navigation
```django
{% include "components/mobile-bottom-nav.html" with active_page="dashboard" %}
```
- Visible solo en `< 768px` (md:hidden)
- Auto-hide on scroll
- Safe area compatible (iOS)

### Mobile Header
```django
{% include "components/mobile-header.html" with 
    title="Mi Título"
    subtitle="Subtítulo"
    show_search=True
    show_notifications=True
%}
```

### Floating Action Button
```html
<div class="fab-mobile md:hidden">
    <button class="btn btn-circle btn-lg">
        <i class="fas fa-plus"></i>
    </button>
</div>
```
- Fixed bottom right
- Respeta bottom nav (bottom: 80px)
- Oculto en desktop

---

## 🍎 iOS Safe Areas

### Clases Disponibles
```html
<!-- Padding top para notch -->
<header class="safe-area-top">

<!-- Padding bottom para home indicator -->
<footer class="safe-area-bottom">

<!-- Bottom nav con safe area -->
<nav class="bottom-nav">
    <!-- Padding automático para iOS -->
</nav>
```

---

## 📑 Patterns Comunes

### Dashboard Stats Grid
```html
<div class="grid grid-cols-1 xs:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
    <div class="stat-card min-h-[120px] md:min-h-[140px]">
        <!-- Stat content -->
    </div>
</div>
```

### Header de Página
```html
<div class="bg-white rounded-2xl shadow-lg p-4 md:p-6 mb-6">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="flex-1">
            <h1 class="text-2xl md:text-4xl font-bold">
                Título
            </h1>
            <p class="text-sm md:text-base text-gray-600 mt-2">
                Descripción
            </p>
        </div>
        <div class="hidden md:block">
            <!-- Acciones solo desktop -->
        </div>
    </div>
</div>
```

### Acciones Rápidas
```html
<div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
    <button class="btn flex-col h-24 md:h-32">
        <i class="fas fa-icon text-2xl mb-2"></i>
        <span class="text-xs md:text-sm">Label</span>
    </button>
</div>
```

### Toolbar con Búsqueda
```html
<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
    <!-- Título -->
    <h2 class="text-lg md:text-xl font-bold">
        Mi Sección
    </h2>
    
    <!-- Búsqueda -->
    <input type="text" 
           class="input input-bordered w-full md:max-w-md"
           placeholder="Buscar...">
    
    <!-- Botones -->
    <div class="flex flex-wrap gap-2">
        <button class="btn btn-sm md:btn-md">
            <i class="fas fa-icon"></i>
            <span class="hidden sm:inline ml-2">Acción</span>
        </button>
    </div>
</div>
```

---

## 🚀 Tips de Performance

### 1. Mobile First
Siempre escribe primero para móvil, luego usa `md:` y `lg:` para desktop.

```html
<!-- ✅ BIEN: Mobile first -->
<div class="text-sm md:text-base lg:text-lg">

<!-- ❌ MAL: Desktop first -->
<div class="text-lg md:text-base sm:text-sm">
```

### 2. Evita Clases Redundantes
```html
<!-- ❌ MAL: Redundante -->
<div class="w-full md:w-full lg:w-96">

<!-- ✅ BIEN: Solo lo necesario -->
<div class="w-full lg:w-96">
```

### 3. Usa Utility Classes
```html
<!-- ✅ BIEN: Usa clases predefinidas -->
<div class="hide-on-mobile">

<!-- ❌ MAL: Media queries inline -->
<div style="@media (max-width: 768px) { display: none; }">
```

---

## 📱 Testing Quick Check

```bash
# Breakpoints para testing manual
375px  - iPhone SE (pequeño)
390px  - iPhone 12/13/14 (estándar)
430px  - iPhone 14 Pro Max (grande)
768px  - iPad Mini (tablet)
1024px - iPad Pro / Desktop
```

### Chrome DevTools
1. F12 → Toggle Device Toolbar (Ctrl+Shift+M)
2. Seleccionar "Responsive"
3. Probar: 375px, 640px, 768px, 1024px

---

## ✅ Checklist Template Responsive

Antes de marcar un template como "responsive-ready":

- [ ] Grid responsive en stats/cards (1→2→4 columnas)
- [ ] Texto adaptativo (text-sm→text-base→text-lg)
- [ ] Padding/margin responsive (p-4→p-6→p-8)
- [ ] Botones con labels ocultos en móvil
- [ ] Tablas con `.table-mobile-stack` o scroll horizontal
- [ ] Bottom navigation incluido
- [ ] Container con `pb-24 md:pb-8`
- [ ] Íconos/logos grandes ocultos en xs
- [ ] Formularios 1 columna→2 columnas
- [ ] Touch targets mínimo 44px
- [ ] Probado en 375px, 768px, 1024px

---

## 📚 Referencia Rápida

| Necesidad | Clase | Ejemplo |
|-----------|-------|---------|
| Ocultar en móvil | `hidden md:block` | Logos grandes |
| Texto condicional | `hidden sm:inline` + `sm:hidden` | Títulos largos |
| Grid responsive | `grid-cols-1 md:grid-cols-4` | Stats dashboard |
| Padding móvil | `p-4 md:p-6` | Cards |
| Stack vertical | `flex flex-col md:flex-row` | Headers |
| Bottom space | `pb-24 md:pb-8` | Main container |
| Tabla móvil | `table-mobile-stack` | Listados |
| FAB | `fab-mobile md:hidden` | Botón flotante |
| Gap responsive | `gap-3 md:gap-6` | Grids |
| Altura mínima | `min-h-[120px] md:min-h-[140px]` | Cards stats |

---

## 🎓 Aprende Más

- Ver: `EJEMPLO_TEMPLATE_RESPONSIVE.html` para template completo
- Ver: `mobile-responsive.css` para clases disponibles
- Ver: `DASHBOARD_MOBILE_COMPLETADO.md` para documentación completa

---

**Creado por:** MetrePay Development Team  
**Versión:** 1.0  
**Última actualización:** 2025
