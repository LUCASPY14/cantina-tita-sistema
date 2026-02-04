import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Empleado
import bcrypt

# Verificar todos los empleados
empleados = Empleado.objects.filter(activo=True)

print("\n=== EMPLEADOS Y SUS CONTRASEÑAS ===\n")
for emp in empleados:
    tiene_hash = "✅" if emp.contrasena_hash else "❌"
    print(f"{tiene_hash} {emp.usuario:15} - {emp.nombre:20} (Rol: {emp.id_rol_id})")
    if emp.contrasena_hash:
        print(f"   Hash: {emp.contrasena_hash[:60]}")
    else:
        print(f"   ⚠️  SIN CONTRASEÑA - Necesita establecer una")
    print()

# Establecer contraseñas para empleados que no tienen
print("\n=== ESTABLECIENDO CONTRASEÑAS FALTANTES ===\n")

empleados_sin_password = Empleado.objects.filter(activo=True, contrasena_hash__isnull=True) | \
                         Empleado.objects.filter(activo=True, contrasena_hash='')

for emp in empleados_sin_password:
    # Usar el usuario como contraseña por defecto
    password = emp.usuario
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    emp.contrasena_hash = password_hash
    emp.save()
    
    print(f"✅ Contraseña establecida para {emp.usuario}")
    print(f"   Usuario: {emp.usuario}")
    print(f"   Contraseña: {password}")
    print()
