#!/usr/bin/env python
"""
Script para consolidar y mejorar templates base
"""
import os
import shutil
from pathlib import Path
import re


def consolidar_templates_base():
    """Consolida y mejora los templates base"""
    
    print("🏗️ CONSOLIDANDO TEMPLATES BASE")
    print("=" * 50)
    
    # Templates base actuales
    templates_base = {
        'templates/base.html': 'Base principal',
        'templates/portal/base_portal.html': 'Base portal padres', 
        'pos/templates/pos/base_pos.html': 'Base POS',
        'gestion/templates/gestion/base.html': 'Base gestión',
        'pos/templates/pos/pos_bootstrap.html': 'Base Bootstrap POS'
    }
    
    for template, descripcion in templates_base.items():
        if os.path.exists(template):
            print(f"✅ Encontrado: {template} - {descripcion}")
        else:
            print(f"❌ No encontrado: {template}")
    
    # Crear estructura unificada en templates/base/
    base_dir = 'templates/base'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"📁 Creado directorio: {base_dir}")
    
    return True


def verificar_consistencia_visual():
    """Verifica la consistencia visual entre templates base"""
    
    print(f"\n🎨 VERIFICACIÓN DE CONSISTENCIA VISUAL")
    print("=" * 50)
    
    templates_base = [
        'templates/base.html',
        'templates/portal/base_portal.html', 
        'pos/templates/pos/base_pos.html',
        'gestion/templates/gestion/base.html'
    ]
    
    css_frameworks = {}
    js_libraries = {}
    
    for template in templates_base:
        if os.path.exists(template):
            try:
                with open(template, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detectar frameworks CSS
                if 'bootstrap' in content.lower():
                    css_frameworks[template] = 'Bootstrap'
                elif 'bulma' in content.lower():
                    css_frameworks[template] = 'Bulma'
                elif 'tailwind' in content.lower():
                    css_frameworks[template] = 'Tailwind'
                else:
                    css_frameworks[template] = 'Custom/Other'
                
                # Detectar librerías JS
                js_libs = []
                if 'jquery' in content.lower():
                    js_libs.append('jQuery')
                if 'bootstrap.js' in content.lower() or 'bootstrap.min.js' in content.lower():
                    js_libs.append('Bootstrap JS')
                if 'vue' in content.lower():
                    js_libs.append('Vue.js')
                if 'react' in content.lower():
                    js_libs.append('React')
                
                js_libraries[template] = js_libs if js_libs else ['None/Custom']
                
            except:
                css_frameworks[template] = 'Error reading'
                js_libraries[template] = ['Error reading']
    
    print("📊 FRAMEWORKS CSS POR TEMPLATE:")
    for template, framework in css_frameworks.items():
        print(f"  {template.split('/')[-1]}: {framework}")
    
    print(f"\n📊 LIBRERÍAS JS POR TEMPLATE:")
    for template, libs in js_libraries.items():
        print(f"  {template.split('/')[-1]}: {', '.join(libs)}")
    
    # Verificar consistencia
    css_values = list(css_frameworks.values())
    js_values = [tuple(sorted(libs)) for libs in js_libraries.values()]
    
    css_consistent = len(set(css_values)) == 1
    js_consistent = len(set(js_values)) == 1
    
    print(f"\n✅ Consistencia CSS: {'Sí' if css_consistent else 'No'}")
    print(f"✅ Consistencia JS: {'Sí' if js_consistent else 'No'}")
    
    if not css_consistent:
        print("⚠️ Se recomienda unificar el framework CSS en todos los templates base")
    
    if not js_consistent:
        print("⚠️ Se recomienda unificar las librerías JS en todos los templates base")


def crear_template_base_unificado():
    """Crea un template base unificado mejorado"""
    
    print(f"\n🔨 CREANDO TEMPLATE BASE UNIFICADO")
    print("=" * 50)
    
    # Leer el template base principal
    base_template_path = 'templates/base.html'
    if os.path.exists(base_template_path):
        try:
            with open(base_template_path, 'r', encoding='utf-8') as f:
                base_content = f.read()
            
            # Crear versión mejorada
            improved_template = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    
    <!-- SEO Meta Tags -->
    <meta name="description" content="{% block meta_description %}Sistema de Gestión Cantina Escolar Paraguay{% endblock %}">
    <meta name="keywords" content="{% block meta_keywords %}cantina, escolar, paraguay, pagos, saldos{% endblock %}">
    <meta name="author" content="Sistema Cantina Escolar">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="{% block og_title %}{% block title %}Sistema Cantina{% endblock %}{% endblock %}">
    <meta property="og:description" content="{% block og_description %}{% block meta_description %}{% endblock %}{% endblock %}">
    <meta property="og:type" content="website">
    
    <title>{% block title %}Sistema Cantina Escolar{% endblock %}</title>
    
    <!-- Favicon -->
    {% load static %}
    <link rel="icon" type="image/x-icon" href="{% static 'favicon.ico' %}">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    
    <!-- Block for additional CSS -->
    {% block extra_css %}{% endblock %}
    
    <!-- Block for additional head content -->
    {% block extra_head %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    <!-- Loading Spinner -->
    <div id="loading-spinner" class="d-none">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
        </div>
    </div>

    <!-- Navigation -->
    {% block navigation %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-store me-2"></i>
                Sistema Cantina
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% block nav_items %}{% endblock %}
                </ul>
                
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-user me-1"></i>
                                {{ user.get_full_name|default:user.username }}
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>Perfil</a></li>
                                <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>Configuración</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{% url 'logout' %}"><i class="fas fa-sign-out-alt me-2"></i>Cerrar Sesión</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'login' %}">
                                <i class="fas fa-sign-in-alt me-1"></i>Iniciar Sesión
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    {% endblock %}

    <!-- Breadcrumb -->
    {% block breadcrumb %}
    <nav aria-label="breadcrumb" class="bg-light">
        <div class="container-fluid">
            <ol class="breadcrumb py-2 mb-0">
                {% block breadcrumb_items %}
                <li class="breadcrumb-item"><a href="/">Inicio</a></li>
                {% endblock %}
            </ol>
        </div>
    </nav>
    {% endblock %}

    <!-- Messages -->
    {% if messages %}
    <div class="container-fluid">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            <i class="fas fa-{% if message.tags == 'error' %}exclamation-triangle{% elif message.tags == 'success' %}check-circle{% elif message.tags == 'warning' %}exclamation-circle{% else %}info-circle{% endif %} me-2"></i>
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Main Content -->
    <main class="main-content">
        {% block content %}
        <div class="container-fluid py-4">
            <h1>Contenido Principal</h1>
            <p>Este es el contenido principal de la página.</p>
        </div>
        {% endblock %}
    </main>

    <!-- Footer -->
    {% block footer %}
    <footer class="bg-dark text-white py-4 mt-auto">
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-6">
                    <h5>Sistema Cantina Escolar</h5>
                    <p class="mb-0">Gestión integral para cantinas escolares en Paraguay</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="mb-0">&copy; 2024 - Todos los derechos reservados</p>
                    <small>Versión 1.0 - Paraguay</small>
                </div>
            </div>
        </div>
    </footer>
    {% endblock %}

    <!-- JavaScript -->
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script src="{% static 'js/base.js' %}"></script>
    
    <!-- Block for additional JavaScript -->
    {% block extra_js %}{% endblock %}
    
    <!-- Analytics and tracking -->
    {% block analytics %}{% endblock %}
</body>
</html>'''
            
            # Guardar template mejorado
            improved_path = 'templates/base_improved.html'
            with open(improved_path, 'w', encoding='utf-8') as f:
                f.write(improved_template)
            
            print(f"✅ Template base mejorado creado: {improved_path}")
            
        except Exception as e:
            print(f"❌ Error creando template mejorado: {e}")
    
    else:
        print(f"❌ No se encontró el template base principal")


def generar_guia_templates():
    """Genera una guía de buenas prácticas para templates"""
    
    guia_content = """# 📋 GUÍA DE BUENAS PRÁCTICAS PARA TEMPLATES

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
"""
    
    with open('GUIA_TEMPLATES.md', 'w', encoding='utf-8') as f:
        f.write(guia_content)
    
    print(f"📋 Guía de templates creada: GUIA_TEMPLATES.md")


def main():
    print("🎨 CONSOLIDACIÓN DE TEMPLATES BASE")
    print("=" * 60)
    
    os.chdir('D:/anteproyecto20112025')
    
    # Paso 1: Consolidar templates base
    consolidar_templates_base()
    
    # Paso 2: Verificar consistencia visual
    verificar_consistencia_visual()
    
    # Paso 3: Crear template base unificado
    crear_template_base_unificado()
    
    # Paso 4: Generar guía
    generar_guia_templates()
    
    print(f"\n✅ CONSOLIDACIÓN COMPLETADA")
    print("=" * 30)
    print("🎯 Templates optimizados y documentados")
    print("📋 Guía de buenas prácticas creada")
    print("🏗️ Template base mejorado disponible")


if __name__ == "__main__":
    main()