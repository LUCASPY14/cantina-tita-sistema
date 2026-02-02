# 📋 GUÍA DE BUENAS PRÁCTICAS PARA TEMPLATES

## 🏗️ Estructura de Templates

### Jerarquía Recomendada
```
templates/
├── base/                    # Templates base
│   ├── base.html           # Template base principal
│   ├── base_admin.html     # Base para administración
│   └── base_portal.html    # Base para portal de padres
├── shared/                 # Componentes compartidos
│   ├── components/         # Componentes reutilizables
│   │   ├── pagination.html
│   │   ├── search_form.html
│   │   └── table_actions.html
│   └── emails/            # Templates de email
├── pos/                   # Templates específicos de POS
├── gestion/               # Templates de gestión
├── portal/                # Portal de padres
├── dashboard/             # Dashboards generales
└── auth/                  # Autenticación
```

## 📝 Convenciones de Nomenclatura

### Archivos de Template
- `lista.html` para listados
- `detalle.html` para vistas de detalle
- `form.html` para formularios
- `dashboard.html` para dashboards
- `modal_*.html` para modales
- `partial_*.html` para parciales

### Blocks de Django
- `{% block title %}` - Título de la página
- `{% block meta_description %}` - Descripción meta
- `{% block extra_css %}` - CSS adicional
- `{% block content %}` - Contenido principal
- `{% block extra_js %}` - JavaScript adicional

## 🎨 Consistencia Visual

### Framework CSS
- Usar Bootstrap 5.3+ en todos los templates
- Mantener clases consistentes
- Usar variables CSS para colores y espaciado

### Iconografía
- Font Awesome 6.0+ para iconos
- Mantener consistencia en iconos similares
- Usar prefijos semánticos (fa-edit, fa-delete, etc.)

## 🔧 Optimización

### Performance
- Minimizar uso de JavaScript inline
- Usar lazy loading para imágenes
- Comprimir CSS y JS en producción

### SEO
- Incluir meta tags apropiados
- Usar estructura HTML semántica
- Incluir breadcrumbs

### Accesibilidad
- Usar roles ARIA apropiados
- Incluir alt text en imágenes
- Mantener contraste adecuado

## 📱 Responsive Design

### Breakpoints
- xs: <576px (móviles)
- sm: ≥576px (móviles grandes)
- md: ≥768px (tablets)
- lg: ≥992px (desktop)
- xl: ≥1200px (desktop grande)

### Componentes Responsive
```html
<div class="row">
    <div class="col-12 col-md-8 col-lg-6">
        <!-- Contenido adaptable -->
    </div>
</div>
```

## 🚀 Mejores Prácticas

### Templates Base
1. Un solo template base principal
2. Templates base específicos heredan del principal
3. Blocks bien definidos y documentados
4. CSS y JS organizados por secciones

### Herencia
1. Usar `{% extends %}` al inicio del template
2. Sobrescribir solo los blocks necesarios
3. Usar `{{ block.super }}` cuando sea apropiado
4. Mantener jerarquía clara

### Seguridad
1. Siempre escapar variables: `{{ variable|escape }}`
2. Usar `{% csrf_token %}` en formularios
3. Validar permisos en templates: `{% if perms.app.permission %}`
4. No incluir información sensible en HTML

### Mantenibilidad
1. Comentar secciones complejas
2. Usar includes para código repetitivo
3. Separar lógica de presentación
4. Documentar blocks personalizados

## 🔍 Herramientas de Desarrollo

### Debugging
- Django Debug Toolbar
- `{% debug %}` para variables de contexto
- Browser DevTools para CSS/JS

### Testing
- Usar `django.test.Client` para testing
- Validar HTML con herramientas apropiadas
- Testing de accesibilidad

---
*Última actualización: $(date)*
