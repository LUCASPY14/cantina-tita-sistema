"""
Script para crear superusuario de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth.models import User

# Crear superusuario si no existe
username = 'admin'
email = 'admin@cantitatita.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superusuario '{username}' creado exitosamente")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
else:
    print(f"⚠️  El usuario '{username}' ya existe")
