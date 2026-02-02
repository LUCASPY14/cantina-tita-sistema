"""
Script para verificar roles y empleados en el sistema
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import TipoRolGeneral, Empleado

print("=" * 60)
print("ROLES DISPONIBLES EN EL SISTEMA")
print("=" * 60)
roles = TipoRolGeneral.objects.all()
for rol in roles:
    print(f"{rol.id_rol} | {rol.nombre_rol:20} | {rol.descripcion or 'Sin descripción'}")

print("\n" + "=" * 60)
print("EMPLEADOS Y SUS ROLES")
print("=" * 60)
empleados = Empleado.objects.select_related('id_rol').filter(activo=True)
for emp in empleados:
    print(f"{emp.usuario:15} | {emp.nombre_completo:30} | {emp.id_rol.nombre_rol}")
