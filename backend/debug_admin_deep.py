"""
Script de diagnóstico profundo del admin de Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.admin.sites import site
from django.apps import apps
from django.conf import settings

User = get_user_model()

print("=" * 80)
print("🔍 DIAGNÓSTICO PROFUNDO DE DJANGO ADMIN")
print("=" * 80)

# 1. Verificar usuario admin
print("\n1️⃣ VERIFICANDO USUARIO ADMIN:")
try:
    admin_user = User.objects.get(username='admin')
    print(f"   ✅ Usuario encontrado:")
    print(f"      - ID: {admin_user.id}")
    print(f"      - Username: {admin_user.username}")
    print(f"      - Email: {admin_user.email}")
    print(f"      - is_staff: {admin_user.is_staff}")
    print(f"      - is_active: {admin_user.is_active}")
    print(f"      - is_superuser: {admin_user.is_superuser}")
    print(f"      - has_usable_password: {admin_user.has_usable_password()}")
except User.DoesNotExist:
    print("   ❌ Usuario 'admin' NO existe")
    print("\n   Usuarios disponibles:")
    for user in User.objects.all():
        print(f"      - {user.username} (superuser={user.is_superuser})")

# 2. Verificar settings importantes
print("\n2️⃣ VERIFICANDO SETTINGS:")
print(f"   - DEBUG: {settings.DEBUG}")
print(f"   - INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
print(f"   - Admin instalado: {'django.contrib.admin' in settings.INSTALLED_APPS}")
print(f"   - Auth instalado: {'django.contrib.auth' in settings.INSTALLED_APPS}")

# 3. Verificar middleware
print("\n3️⃣ MIDDLEWARE:")
for mw in settings.MIDDLEWARE:
    print(f"   - {mw}")

# 4. Modelos registrados en admin
print("\n4️⃣ MODELOS REGISTRADOS EN ADMIN:")
registered = site._registry
print(f"   Total: {len(registered)} modelos")

by_app = {}
for model, admin_class in registered.items():
    app_label = model._meta.app_label
    if app_label not in by_app:
        by_app[app_label] = []
    by_app[app_label].append(model.__name__)

for app, models in sorted(by_app.items()):
    print(f"\n   📦 {app.upper()}:")
    for model_name in sorted(models):
        print(f"      ✓ {model_name}")

# 5. Verificar permisos de Django
print("\n5️⃣ VERIFICANDO PERMISOS DE DJANGO:")
from django.contrib.auth.models import Permission
total_perms = Permission.objects.count()
print(f"   Total permisos en BD: {total_perms}")

# Verificar permisos de notificaciones
notif_perms = Permission.objects.filter(content_type__app_label='gestion', 
                                       content_type__model__icontains='notificacion')
print(f"   Permisos de notificaciones: {notif_perms.count()}")
for perm in notif_perms:
    print(f"      - {perm.codename} ({perm.name})")

# 6. Verificar ContentTypes
print("\n6️⃣ VERIFICANDO CONTENT TYPES:")
from django.contrib.contenttypes.models import ContentType
notif_cts = ContentType.objects.filter(app_label='gestion', 
                                       model__icontains='notificacion')
print(f"   ContentTypes de notificaciones: {notif_cts.count()}")
for ct in notif_cts:
    print(f"      - {ct.app_label}.{ct.model}")

# 7. Verificar que los modelos existen
print("\n7️⃣ VERIFICANDO MODELOS EN GESTION:")
gestion_models = apps.get_app_config('gestion').get_models()
print(f"   Total modelos en gestion: {len(gestion_models)}")
for model in gestion_models:
    registered_icon = "✓" if model in registered else "✗"
    print(f"      {registered_icon} {model.__name__}")

# 8. Test de permiso directo
print("\n8️⃣ TEST DE PERMISOS DEL USUARIO ADMIN:")
try:
    admin_user = User.objects.get(username='admin')
    print(f"   - Puede acceder al admin: {admin_user.has_perm('admin.can_access')}")
    print(f"   - Tiene algún permiso: {admin_user.user_permissions.count()} permisos directos")
    print(f"   - En grupos: {admin_user.groups.count()} grupos")
    
    # Test específico de notificaciones
    print(f"\n   Permisos sobre NotificacionSistema:")
    print(f"      - add: {admin_user.has_perm('gestion.add_notificacionsistema')}")
    print(f"      - change: {admin_user.has_perm('gestion.change_notificacionsistema')}")
    print(f"      - delete: {admin_user.has_perm('gestion.delete_notificacionsistema')}")
    print(f"      - view: {admin_user.has_perm('gestion.view_notificacionsistema')}")
except User.DoesNotExist:
    print("   ❌ No se puede verificar, usuario no existe")

# 9. Verificar admin.py se está cargando
print("\n9️⃣ VERIFICANDO CARGA DE ADMIN.PY:")
try:
    import gestion.admin
    print("   ✅ gestion.admin se importó correctamente")
    
    # Ver qué está exportando
    admin_attrs = [attr for attr in dir(gestion.admin) if not attr.startswith('_')]
    print(f"   Atributos en gestion.admin: {len(admin_attrs)}")
    
    admin_classes = [attr for attr in admin_attrs if 'Admin' in attr]
    print(f"   Clases Admin encontradas: {admin_classes}")
except Exception as e:
    print(f"   ❌ Error importando gestion.admin: {e}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
