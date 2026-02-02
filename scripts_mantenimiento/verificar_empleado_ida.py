import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Empleado
from django.contrib.auth.models import User

# Verificar empleado IDA_CAJA
emp = Empleado.objects.filter(usuario='IDA_CAJA').first()

if emp:
    print(f"\n=== EMPLEADO IDA_CAJA ===")
    print(f"ID: {emp.id_empleado}")
    print(f"Nombre: {emp.nombre}")
    print(f"Usuario: {emp.usuario}")
    print(f"Contraseña (hash): {emp.contrasena_hash[:60] if emp.contrasena_hash else 'SIN CONTRASEÑA'}")
    print(f"Activo: {emp.activo}")
    print(f"Rol: {emp.id_rol_id}")
    print(f"Email: {emp.email if emp.email else 'N/A'}")
else:
    print("❌ Empleado IDA_CAJA NO encontrado")

# Verificar si existe un User de Django para este empleado
user = User.objects.filter(username='IDA_CAJA').first()
if user:
    print(f"\n=== USER DJANGO ===")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is active: {user.is_active}")
    print(f"Is staff: {user.is_staff}")
    print(f"Is superuser: {user.is_superuser}")
else:
    print("\n❌ Usuario Django para IDA_CAJA NO existe")
    print("   El sistema usa el modelo User de Django para autenticación.")
    print("   Necesitas crear un User o implementar un backend personalizado.")
