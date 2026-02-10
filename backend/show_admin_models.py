"""
Muestra exactamente qué debería verse en el admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("📋 LO QUE DEBERÍAS VER EN EL ADMIN")
print("=" * 80)

# Simular la vista del admin
registered = site._registry

# Agrupar por app
by_app = {}
for model, admin_class in registered.items():
    app_label = model._meta.app_label
    verbose_name = model._meta.verbose_name_plural
    
    if app_label not in by_app:
        by_app[app_label] = []
    
    by_app[app_label].append({
        'name': model.__name__,
        'verbose_name': verbose_name,
        'model': model
    })

# Mostrar como se vería en el admin
for app_label in sorted(by_app.keys()):
    app_name = app_label.upper()
    print(f"\n{'='*80}")
    print(f"📦 {app_name}")
    print(f"{'='*80}")
    
    for model_info in sorted(by_app[app_label], key=lambda x: x['verbose_name']):
        print(f"\n   ✓ {model_info['verbose_name']}")
        print(f"     Modelo: {model_info['name']}")
        print(f"     App: {app_label}")
        
        # Contar registros
        try:
            count = model_info['model'].objects.count()
            print(f"     Registros: {count}")
        except:
            print(f"     Registros: (no se puede contar)")

print("\n" + "=" * 80)
print("🔍 BUSCANDO NOTIFICACIONES...")
print("=" * 80)

# Búsqueda específica de notificaciones
notif_models = [m for m in registered.keys() if 'notificacion' in m.__name__.lower()]
print(f"\nModelos con 'notificacion' en el nombre: {len(notif_models)}")
for model in notif_models:
    print(f"   ✓ {model._meta.app_label}.{model.__name__}")
    print(f"     → Nombre en admin: {model._meta.verbose_name_plural}")
    
print("\n" + "=" * 80)
print("💡 IMPORTANTE:")
print("=" * 80)
print("\nEn el panel de admin deberías ver EXACTAMENTE estos modelos agrupados por app.")
print("Si NO ves 'Notificaciones' en la sección GESTION, hay un problema.")
print("\nLos modelos NotificacionSistema y ConfiguracionNotificacionesSistema")
print("deberían aparecer como:")
print("   - Notificaciones")
print("   - Configuraciones de Notificaciones")
print("\n" + "=" * 80)
