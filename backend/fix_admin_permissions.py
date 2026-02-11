import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth.models import User

print("🔍 Verificando permisos del usuario 'admin'...")
print("=" * 60)

try:
    admin_user = User.objects.get(username='admin')
    
    print(f"✅ Usuario 'admin' encontrado")
    print(f"   - ID: {admin_user.id}")
    print(f"   - Email: {admin_user.email}")
    print(f"   - Es staff: {admin_user.is_staff}")
    print(f"   - Es superusuario: {admin_user.is_superuser}")
    print(f"   - Está activo: {admin_user.is_active}")
    print(f"   - Último login: {admin_user.last_login}")
    
    if not admin_user.is_superuser or not admin_user.is_staff:
        print("\n⚠️  El usuario 'admin' no tiene permisos completos")
        print("🔧 Actualizando permisos...")
        
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        
        print("✅ Permisos actualizados:")
        print(f"   - is_staff: {admin_user.is_staff}")
        print(f"   - is_superuser: {admin_user.is_superuser}")
        print(f"   - is_active: {admin_user.is_active}")
    else:
        print("\n✅ El usuario 'admin' ya tiene todos los permisos necesarios")
    
    # Mostrar todos los permisos
    print("\n📋 Permisos del usuario:")
    permisos = admin_user.user_permissions.all()
    if permisos:
        for perm in permisos:
            print(f"   - {perm.codename}: {perm.name}")
    else:
        print("   (Ninguno - es superusuario, tiene todos los permisos)")
    
    # Mostrar grupos
    print("\n👥 Grupos del usuario:")
    grupos = admin_user.groups.all()
    if grupos:
        for grupo in grupos:
            print(f"   - {grupo.name}")
    else:
        print("   (Ninguno)")
    
except User.DoesNotExist:
    print("❌ El usuario 'admin' no existe")
    print("\n🔧 Creando usuario 'admin'...")
    
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@cantinatita.com',
        password='admin123',  # Cambiar en producción
        first_name='Administrador',
        last_name='Sistema'
    )
    
    print("✅ Usuario 'admin' creado exitosamente:")
    print(f"   - Username: admin")
    print(f"   - Password: admin123")
    print(f"   - Email: {admin_user.email}")
    print(f"   ⚠️  IMPORTANTE: Cambiar la contraseña en producción")

print("\n" + "=" * 60)
print("🎉 ¡Configuración completada!")
print("\n📌 Ahora puedes:")
print("   1. Ir a http://localhost:8000/admin/")
print("   2. Iniciar sesión con usuario 'admin'")
print("   3. Acceder a todos los modelos del sistema")
