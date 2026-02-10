import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib import admin
from gestion.models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema

print("🔍 Verificando registro de modelos en Django Admin...")
print("=" * 60)

# Obtener todos los modelos registrados
registered_models = admin.site._registry

print(f"\n📋 Total de modelos registrados: {len(registered_models)}")
print("\n🔍 Buscando modelos de notificaciones...")

# Buscar NotificacionSistema
notif_found = False
config_found = False

for model, model_admin in registered_models.items():
    model_name = model.__name__
    app_label = model._meta.app_label
    
    if model_name == 'NotificacionSistema':
        notif_found = True
        print(f"\n✅ NotificacionSistema encontrado:")
        print(f"   - App: {app_label}")
        print(f"   - Model: {model_name}")
        print(f"   - Admin class: {model_admin.__class__.__name__}")
        print(f"   - Verbose name: {model._meta.verbose_name}")
        
    if model_name == 'ConfiguracionNotificacionesSistema':
        config_found = True
        print(f"\n✅ ConfiguracionNotificacionesSistema encontrado:")
        print(f"   - App: {app_label}")
        print(f"   - Model: {model_name}")
        print(f"   - Admin class: {model_admin.__class__.__name__}")
        print(f"   - Verbose name: {model._meta.verbose_name}")

if not notif_found:
    print("\n❌ NotificacionSistema NO está registrado en el admin")
    print("   Verificando si el modelo existe...")
    try:
        from gestion.models_notificaciones import NotificacionSistema
        print(f"   ✓ El modelo existe: {NotificacionSistema}")
        print("   ✗ Pero NO está registrado en admin.site")
    except ImportError as e:
        print(f"   ✗ Error al importar: {e}")

if not config_found:
    print("\n❌ ConfiguracionNotificacionesSistema NO está registrado en el admin")
    print("   Verificando si el modelo existe...")
    try:
        from gestion.models_notificaciones import ConfiguracionNotificacionesSistema
        print(f"   ✓ El modelo existe: {ConfiguracionNotificacionesSistema}")
        print("   ✗ Pero NO está registrado en admin.site")
    except ImportError as e:
        print(f"   ✗ Error al importar: {e}")

print("\n" + "=" * 60)
print("\n📋 Lista completa de modelos registrados:")
print("=" * 60)

# Agrupar por app
from collections import defaultdict
apps_models = defaultdict(list)

for model in registered_models.keys():
    app_label = model._meta.app_label
    apps_models[app_label].append(model._meta.verbose_name_plural)

for app, models in sorted(apps_models.items()):
    print(f"\n{app.upper()}:")
    for model_name in sorted(models):
        print(f"  - {model_name}")

print("\n" + "=" * 60)
if notif_found and config_found:
    print("✅ ¡Todos los modelos de notificaciones están registrados!")
else:
    print("⚠️  Faltan modelos por registrar en el admin")
