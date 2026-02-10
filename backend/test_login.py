"""
Test de autenticación del admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

print("=" * 80)
print("🔐 TEST DE AUTENTICACIÓN")
print("=" * 80)

# Mostrar usuarios disponibles
print("\n📋 USUARIOS EN EL SISTEMA:")
for user in User.objects.all():
    print(f"\n   Usuario: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - ID: {user.id}")
    print(f"   - is_staff: {user.is_staff}")
    print(f"   - is_active: {user.is_active}")
    print(f"   - is_superuser: {user.is_superuser}")
    print(f"   - has_usable_password: {user.has_usable_password()}")
    
    # Intentar autenticar con diferentes contraseñas comunes
    common_passwords = ['admin', '123', 'admin123', 'password']
    print(f"\n   🔑 Tests de contraseña:")
    for pwd in common_passwords:
        auth_user = authenticate(username=user.username, password=pwd)
        if auth_user:
            print(f"      ✅ '{pwd}' - FUNCIONA")
            print(f"         → Puede acceder al admin: {auth_user.is_staff}")
            break
        else:
            print(f"      ❌ '{pwd}' - no funciona")
    else:
        print(f"      ⚠️  Ninguna contraseña común funcionó")
        print(f"      💡 Necesitas resetear la contraseña")

print("\n" + "=" * 80)
print("✅ TEST COMPLETADO")
print("=" * 80)

# Mostrar cómo resetear contraseña
print("\n💡 PARA RESETEAR LA CONTRASEÑA DEL ADMIN:")
print("   python manage.py createsuperuser --username admin --email admin@cantinatita.com")
print("   (Te pedirá la nueva contraseña)")
print("\n   O usar este script rápido:")
print("   ---------------------------------------------")
print("   from django.contrib.auth import get_user_model")
print("   User = get_user_model()")
print(f"   u = User.objects.get(username='admin')")
print("   u.set_password('admin')  # Cambia 'admin' por la contraseña deseada")
print("   u.save()")
print("   print('Contraseña actualizada!')")
print("   ---------------------------------------------")
