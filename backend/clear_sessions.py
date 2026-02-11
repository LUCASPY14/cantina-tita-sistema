import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.utils import timezone

print("🧹 Limpiando todas las sesiones...")
print("=" * 60)

# Contar sesiones antes de eliminar
total_sessions = Session.objects.count()
print(f"📊 Sesiones activas antes: {total_sessions}")

# Eliminar TODAS las sesiones (fuerza cierre de sesión de todos los usuarios)
deleted_count, _ = Session.objects.all().delete()

print(f"🗑️  Sesiones eliminadas: {deleted_count}")
print("\n✅ ¡Todas las sesiones han sido limpiadas!")
print("\n📌 Ahora DEBES:")
print("   1. Ir a http://localhost:8000/admin/")
print("   2. Iniciar sesión nuevamente")
print("   3. Usuario: admin")
print("   4. Contraseña: admin123")
print("\n" + "=" * 60)
