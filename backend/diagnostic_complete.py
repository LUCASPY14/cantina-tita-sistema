import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

print("🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA")
print("=" * 60)

# 1. Verificar usuario admin
print("\n1️⃣ VERIFICANDO USUARIO 'admin':")
try:
    admin = User.objects.get(username='admin')
    print(f"   ✅ Usuario existe")
    print(f"   - ID: {admin.id}")
    print(f"   - is_superuser: {admin.is_superuser}")
    print(f"   - is_staff: {admin.is_staff}")
    print(f"   - is_active: {admin.is_active}")
    
    if not admin.is_superuser or not admin.is_staff:
        print("\n   ⚠️  PROBLEMA ENCONTRADO: Usuario sin permisos completos")
        print("   🔧 Corrigiendo...")
        admin.is_superuser = True
        admin.is_staff = True
        admin.is_active = True
        admin.save()
        print("   ✅ Permisos actualizados")
    
except User.DoesNotExist:
    print("   ❌ Usuario 'admin' no existe")
    print("   🔧 Creando usuario...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@cantinatita.com',
        password='admin123'
    )
    print("   ✅ Usuario creado")

# 2. Eliminar TODAS las sesiones activas
print("\n2️⃣ ELIMINANDO SESIONES ACTIVAS:")
count = Session.objects.all().count()
print(f"   📊 Sesiones antes: {count}")
Session.objects.all().delete()
print(f"   🗑️  Todas las sesiones eliminadas")

# 3. Verificar permisos del usuario
print("\n3️⃣ VERIFICANDO PERMISOS:")
print(f"   - Tiene acceso al admin: {admin.has_perm('admin.view_logentry')}")
print(f"   - Es superusuario: {admin.is_superuser}")
print(f"   - Total de permisos: {admin.user_permissions.count()} (superuser tiene TODOS)")

# 4. Verificar modelos registrados en admin
print("\n4️⃣ MODELOS REGISTRADOS EN ADMIN:")
from django.contrib import admin
registered = admin.site._registry
print(f"   📋 Total modelos: {len(registered)}")

# Buscar notificaciones
notif_models = [m.__name__ for m in registered.keys() if 'Notificacion' in m.__name__]
print(f"   🔔 Modelos de notificaciones: {notif_models}")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("\n🎯 SOLUCIÓN DEFINITIVA:")
print("=" * 60)
print("\n1. En tu navegador, ve a la barra de direcciones")
print("2. Haz clic en el CANDADO 🔒 que aparece antes de 'localhost:8000'")
print("3. Click en 'Cookies' o 'Configuración del sitio'")
print("4. Click en 'Eliminar datos' o 'Borrar cookies'")
print("5. Cierra COMPLETAMENTE el navegador (todas las ventanas)")
print("6. Abre el navegador de nuevo")
print("7. Ve a: http://localhost:8000/admin/")
print("8. Inicia sesión:")
print("   Usuario: admin")
print("   Contraseña: admin123")
print("\n" + "=" * 60)
