#!/usr/bin/env python
"""
Script para listar usuarios del sistema
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth.models import User
from gestion.models import Empleado

def listar_usuarios():
    print("=" * 50)
    print("🔐 USUARIOS DEL SISTEMA CANTINA")
    print("=" * 50)
    
    # Usuarios Django
    users = User.objects.all()
    print(f"\n👥 USUARIOS DJANGO: {users.count()}")
    print("-" * 40)
    
    if users.count() == 0:
        print("❌ No hay usuarios registrados")
    else:
        for u in users:
            status = "✅ Activo" if u.is_active else "❌ Inactivo"
            tipo = []
            if u.is_superuser:
                tipo.append("🔑 Superuser")
            if u.is_staff:
                tipo.append("👨‍💼 Staff")
            if not tipo:
                tipo.append("👤 Usuario normal")
            
            print(f"ID: {u.id:2d} | {u.username:15} | {u.email:25} | {status} | {', '.join(tipo)}")
            if u.last_login:
                print(f"      Último login: {u.last_login.strftime('%d/%m/%Y %H:%M')}")
            else:
                print(f"      Último login: Nunca")
            print()
    
    # Empleados
    empleados = Empleado.objects.all()
    print(f"\n👨‍💼 EMPLEADOS: {empleados.count()}")
    print("-" * 40)
    
    if empleados.count() == 0:
        print("❌ No hay empleados registrados")
    else:
        for e in empleados[:10]:  # Solo primeros 10
            status = "✅ Activo" if e.activo else "❌ Inactivo"
            print(f"ID: {e.id:2d} | {e.nombre:20} | {e.cedula:15} | {e.email:25} | {status}")
            if hasattr(e, 'cargo'):
                print(f"      Cargo: {e.cargo}")
            print()
        
        if empleados.count() > 10:
            print(f"... y {empleados.count() - 10} empleados más")
    
    print("=" * 50)

if __name__ == "__main__":
    listar_usuarios()