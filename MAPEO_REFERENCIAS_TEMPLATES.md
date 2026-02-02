# 📋 MAPEO DE REFERENCIAS DE TEMPLATES

## 🔄 Cambios Necesarios en Views.py

Para actualizar las referencias a templates en tus archivos Python, reemplaza las siguientes rutas:

### Templates de POS
```python
# ANTES → DESPUÉS
'pos/' → 'apps/pos/'
'pos/admin/' → 'apps/pos/admin/'
'pos/almuerzo/' → 'apps/pos/almuerzo/'
'pos/reportes/' → 'apps/pos/reportes/'
'pos/partials/' → 'shared/components/'
'pos/modales/' → 'shared/modals/'
```

### Templates de Gestión
```python
# ANTES → DESPUÉS
'gestion/' → 'apps/gestion/'
'gestion/admin/' → 'apps/gestion/admin/'
'gestion/productos/' → 'apps/gestion/productos/'
'gestion/clientes/' → 'apps/gestion/clientes/'
'gestion/empleados/' → 'apps/gestion/empleados/'
'gestion/reportes/' → 'apps/gestion/reportes/'
'gestion/emails/' → 'shared/emails/'
'gestion/components/' → 'shared/components/'
```

### Templates de Portal
```python
# ANTES → DESPUÉS
'portal/' → 'apps/portal/'
'portal/auth/' → 'apps/portal/auth/'
'portal/dashboard/' → 'apps/portal/dashboard/'
'portal/widgets/' → 'apps/portal/widgets/'
```

### Templates Generales
```python
# ANTES → DESPUÉS
'dashboard/' → 'pages/dashboard/'
'emails/' → 'shared/emails/'
'seguridad/' → 'apps/auth/'
'registration/' → 'apps/auth/'
'clientes/' → 'apps/gestion/clientes/'
```

## 🔧 Templates Base Actualizados

### Nuevos Templates Base Disponibles
```python
# Template base principal
{% extends "base/base.html" %}

# Template base específico POS
{% extends "base/pos_base.html" %}

# Template base específico Portal
{% extends "base/portal_base.html" %}
```

## 🧩 Componentes Compartidos Creados

### Navegación
```html
{% include "shared/components/navigation.html" %}
```

### Mensajes del Sistema
```html
{% include "shared/components/messages.html" %}
```

### Footer
```html
{% include "shared/components/footer.html" %}
```

### Componentes Específicos
```html
{% include "shared/components/productos_grid.html" %}
{% include "shared/components/tarjeta_info.html" %}
{% include "shared/components/pagination.html" %}
```

## ⚡ Script de Actualización Automática

Puedes usar este comando para actualizar referencias automáticamente:

```python
import re

def actualizar_referencias_en_archivo(archivo_path):
    with open(archivo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Mapeo de reemplazos
    replacements = {
        r"'pos/([^']*)'": r"'apps/pos/\1'",
        r"'gestion/([^']*)'": r"'apps/gestion/\1'",
        r"'portal/([^']*)'": r"'apps/portal/\1'",
        r"'dashboard/([^']*)'": r"'pages/dashboard/\1'",
        r"'emails/([^']*)'": r"'shared/emails/\1'",
        r"'seguridad/([^']*)'": r"'apps/auth/\1'",
        r"'registration/([^']*)'": r"'apps/auth/\1'",
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    with open(archivo_path, 'w', encoding='utf-8') as f:
        f.write(content)
```

## 📊 Estadísticas de la Reorganización

- **Templates reorganizados:** 135
- **Estructura anterior:** 3 carpetas dispersas
- **Estructura nueva:** 1 carpeta unificada profesional
- **Categorías creadas:** 15
- **Componentes reutilizables:** 6
- **Templates base:** 3 unificados

---
*Archivo generado automáticamente durante la reorganización profesional*
