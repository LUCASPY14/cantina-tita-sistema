import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from gestion.models import Empleado

# Prueba de autenticación
print("\n=== PROBANDO AUTENTICACIÓN ===\n")

test_users = [
    ('IDA_CAJA', 'IDA_CAJA'),
    ('TITA', 'TITA'),
    ('IDA_CAJA', 'contraseña_incorrecta'),
]

for username, password in test_users:
    print(f"Intentando: usuario={username}, contraseña={password}")
    user = authenticate(username=username, password=password)
    
    if user is not None:
        print(f"  ✅ Autenticación exitosa!")
        print(f"     - User ID: {user.id}")
        print(f"     - Nombre: {user.first_name} {user.last_name}")
        print(f"     - Email: {user.email}")
        print(f"     - is_staff: {user.is_staff}")
        print(f"     - is_superuser: {user.is_superuser}")
        
        # Obtener empleado asociado
        try:
            emp = Empleado.objects.get(usuario=username)
            print(f"     - Rol empleado: {emp.id_rol.descripcion}")
        except:
            pass
    else:
        print(f"  ❌ Autenticación fallida")
    print()

# Verificar usuarios Django creados
print("\n=== USUARIOS DJANGO EXISTENTES ===\n")
users = User.objects.all()
for u in users:
    print(f"- {u.username} (staff: {u.is_staff}, superuser: {u.is_superuser})")
