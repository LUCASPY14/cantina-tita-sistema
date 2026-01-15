"""
Script de verificación completa del proyecto Cantina Tita
Verifica templates, vistas, URLs y configuración
"""
import os
import sys
import django
import re
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.urls import get_resolver
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.conf import settings

print("=" * 80)
print("VERIFICACIÓN COMPLETA DEL PROYECTO CANTINA TITA".center(80))
print("=" * 80 + "\n")

# ============================================================================
# 1. VERIFICAR CONFIGURACIÓN
# ============================================================================
print("📋 1. VERIFICANDO CONFIGURACIÓN")
print("-" * 80)

try:
    print(f"✓ DEBUG: {settings.DEBUG}")
    print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✓ DATABASES: {settings.DATABASES['default']['ENGINE']}")
    print(f"✓ TEMPLATES: {len(settings.TEMPLATES)} configuración(es)")
    print(f"✓ INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
    print()
except Exception as e:
    print(f"✗ Error en configuración: {e}\n")

# ============================================================================
# 2. VERIFICAR TEMPLATES
# ============================================================================
print("📄 2. VERIFICANDO TEMPLATES")
print("-" * 80)

templates_dir = Path('templates')
if templates_dir.exists():
    all_templates = list(templates_dir.rglob('*.html'))
    print(f"✓ Directorio de templates encontrado")
    print(f"✓ Total de templates: {len(all_templates)}")
    
    # Agrupar por directorio
    templates_by_dir = {}
    for tmpl in all_templates:
        dir_name = tmpl.parent.name
        if dir_name not in templates_by_dir:
            templates_by_dir[dir_name] = []
        templates_by_dir[dir_name].append(tmpl.name)
    
    for dir_name, files in sorted(templates_by_dir.items()):
        print(f"  📁 {dir_name}: {len(files)} templates")
else:
    print("✗ Directorio de templates no encontrado")

print()

# ============================================================================
# 3. VERIFICAR URLS
# ============================================================================
print("🔗 3. VERIFICANDO URLs")
print("-" * 80)

resolver = get_resolver()
url_patterns = []

def extract_patterns(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # Es un include
            new_prefix = prefix + str(pattern.pattern)
            extract_patterns(pattern.url_patterns, new_prefix)
        else:
            # Es una URL normal
            url_patterns.append({
                'pattern': prefix + str(pattern.pattern),
                'name': pattern.name if hasattr(pattern, 'name') else None,
                'view': str(pattern.callback) if hasattr(pattern, 'callback') else None
            })

extract_patterns(resolver.url_patterns)

print(f"✓ Total de URLs configuradas: {len(url_patterns)}")
print(f"✓ URLs con nombre: {sum(1 for p in url_patterns if p['name'])}")
print()

# Agrupar por prefijo
url_groups = {}
for url in url_patterns:
    prefix = url['pattern'].split('/')[0] if '/' in url['pattern'] else 'root'
    if prefix not in url_groups:
        url_groups[prefix] = []
    url_groups[prefix].append(url)

print("URLs por prefijo:")
for prefix, urls in sorted(url_groups.items()):
    if prefix and prefix != '^':
        print(f"  /{prefix}: {len(urls)} URLs")

print()

# ============================================================================
# 4. VERIFICAR VISTAS
# ============================================================================
print("👁️ 4. VERIFICANDO VISTAS")
print("-" * 80)

view_files = [
    'gestion/views.py',
    'gestion/pos_views.py',
    'gestion/cliente_views.py',
    'gestion/portal_views.py',
    'gestion/auth_views.py',
    'gestion/dashboard_views.py',
]

total_views = 0
for view_file in view_files:
    if os.path.exists(view_file):
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Contar funciones que parecen vistas
            views = re.findall(r'^def\s+(\w+)\s*\(request', content, re.MULTILINE)
            total_views += len(views)
            print(f"✓ {view_file}: {len(views)} vistas")
    else:
        print(f"✗ {view_file}: No encontrado")

print(f"\n✓ Total de vistas encontradas: {total_views}")
print()

# ============================================================================
# 5. VERIFICAR MODELOS
# ============================================================================
print("🗄️ 5. VERIFICANDO MODELOS")
print("-" * 80)

from django.apps import apps

models = apps.get_models()
print(f"✓ Total de modelos: {len(models)}")

# Agrupar por app
models_by_app = {}
for model in models:
    app_label = model._meta.app_label
    if app_label not in models_by_app:
        models_by_app[app_label] = []
    models_by_app[app_label].append(model.__name__)

for app, model_list in sorted(models_by_app.items()):
    print(f"  {app}: {len(model_list)} modelos")

print()

# ============================================================================
# 6. VERIFICAR TEMPLATES USADOS EN VISTAS
# ============================================================================
print("🔍 6. VERIFICANDO TEMPLATES REFERENCIADOS EN VISTAS")
print("-" * 80)

templates_found = set()
templates_missing = set()

template_errors = {}

for view_file in view_files:
    if os.path.exists(view_file):
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Buscar render() calls
            renders = re.findall(r"render\([^,]+,\s*['\"]([^'\"]+\.html)['\"]", content)
            for template_name in renders:
                try:
                    get_template(template_name)
                    templates_found.add(template_name)
                except TemplateDoesNotExist:
                    templates_missing.add(template_name)
                except Exception as e:
                    template_errors[template_name] = str(e)

print(f"✓ Templates encontrados: {len(templates_found)}")
if templates_missing:
    print(f"✗ Templates faltantes: {len(templates_missing)}")
    for tmpl in sorted(templates_missing)[:10]:  # Mostrar solo los primeros 10
        print(f"  - {tmpl}")
    if len(templates_missing) > 10:
        print(f"  ... y {len(templates_missing) - 10} más")
else:
    print("✓ Todos los templates referenciados existen")

if template_errors:
    print(f"\n⚠️  Templates con errores de sintaxis: {len(template_errors)}")
    for tmpl, error in list(template_errors.items())[:5]:
        print(f"  - {tmpl}: {error[:80]}")
    if len(template_errors) > 5:
        print(f"  ... y {len(template_errors) - 5} más")

print()

# ============================================================================
# 7. VERIFICAR MIGRACIONES
# ============================================================================
print("🔄 7. VERIFICANDO MIGRACIONES")
print("-" * 80)

from django.db.migrations.executor import MigrationExecutor
from django.db import connection

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

if plan:
    print(f"⚠️  Hay {len(plan)} migraciones pendientes")
    for migration, backwards in plan[:5]:
        print(f"  - {migration}")
    if len(plan) > 5:
        print(f"  ... y {len(plan) - 5} más")
else:
    print("✓ Todas las migraciones aplicadas")

print()

# ============================================================================
# 8. VERIFICAR ERRORES DE SINTAXIS
# ============================================================================
print("🐛 8. VERIFICANDO ERRORES DE SINTAXIS")
print("-" * 80)

python_files = []
for root, dirs, files in os.walk('gestion'):
    # Excluir directorios
    dirs[:] = [d for d in dirs if d not in ['__pycache__', 'migrations', '.git']]
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

syntax_errors = []
for py_file in python_files:
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            compile(f.read(), py_file, 'exec')
    except SyntaxError as e:
        syntax_errors.append((py_file, str(e)))

if syntax_errors:
    print(f"✗ Encontrados {len(syntax_errors)} errores de sintaxis:")
    for file, error in syntax_errors:
        print(f"  - {file}: {error}")
else:
    print(f"✓ No se encontraron errores de sintaxis en {len(python_files)} archivos")

print()

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("=" * 80)
print("RESUMEN FINAL".center(80))
print("=" * 80)

issues = []
if templates_missing:
    issues.append(f"❌ {len(templates_missing)} templates faltantes")
if template_errors:
    issues.append(f"⚠️  {len(template_errors)} templates con errores")
if plan:
    issues.append(f"⚠️  {len(plan)} migraciones pendientes")
if syntax_errors:
    issues.append(f"❌ {len(syntax_errors)} errores de sintaxis")

if issues:
    print("\n⚠️  PROBLEMAS ENCONTRADOS:\n")
    for issue in issues:
        print(f"  {issue}")
    print(f"\n⚠️  Total de problemas: {len(issues)}")
else:
    print("\n✅ ¡TODO ESTÁ BIEN! No se encontraron problemas críticos.")
    print(f"\n📊 Estadísticas:")
    print(f"  • {len(all_templates)} templates")
    print(f"  • {len(url_patterns)} URLs")
    print(f"  • {total_views} vistas")
    print(f"  • {len(models)} modelos")

print("\n" + "=" * 80)
