"""
Script para crear un cliente con usuario web de prueba
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Cliente, UsuariosWebClientes
import bcrypt

print("👤 Creando Cliente con Usuario Web de Prueba\n")
print("="*60)

# Verificar si ya existe
usuario_existente = UsuariosWebClientes.objects.filter(usuario='cliente_prueba').first()
if usuario_existente:
    print("ℹ️ Ya existe un usuario web de prueba")
    cliente = usuario_existente.id_cliente
    print(f"   Cliente: {cliente.nombres} {cliente.apellidos}")
    print(f"   Usuario: {usuario_existente.usuario}")
    print(f"   Email: {cliente.email}")
    print("\n✅ Puedes usar este usuario para las pruebas")
    sys.exit(0)

# Buscar un cliente sin usuario web o crear uno nuevo
cliente = Cliente.objects.filter(
    id_cliente__in=UsuariosWebClientes.objects.values('id_cliente')
).first()

if not cliente:
    # Buscar cualquier cliente
    cliente = Cliente.objects.first()
    
    if not cliente:
        print("❌ No hay clientes en el sistema")
        print("   Crea un cliente desde el POS primero")
        sys.exit(1)

print(f"📋 Cliente seleccionado:")
print(f"   ID: {cliente.id_cliente}")
print(f"   Nombre: {cliente.nombres} {cliente.apellidos}")
print(f"   Email: {cliente.email or '(sin email)'}")

# Crear usuario web
usuario = "cliente_prueba"
password = "Prueba123"  # Cumple requisitos: 8 chars, mayúscula, minúscula, número

print(f"\n🔐 Creando usuario web:")
print(f"   Usuario: {usuario}")
print(f"   Contraseña: {password}")

# Generar hash bcrypt
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Crear usuario web
usuario_web = UsuariosWebClientes.objects.create(
    id_cliente=cliente,
    usuario=usuario,
    contrasena_hash=password_hash
)

print(f"\n✅ Usuario web creado exitosamente!")
print(f"   ID: {usuario_web.id_cliente.id_cliente}")
print(f"   Usuario: {usuario_web.usuario}")

print("\n" + "="*60)
print("🎉 ¡Listo! Ahora puedes probar el sistema de seguridad:\n")
print("1️⃣ Portal de Login:")
print("   URL: http://127.0.0.1:8000/pos/portal/login/")
print(f"   Usuario: {usuario}")
print(f"   Contraseña: {password}")
print()
print("2️⃣ Recuperación de Contraseña:")
print("   URL: http://127.0.0.1:8000/pos/portal/recuperar-password/")
print(f"   Email: {cliente.email or '(actualiza el email del cliente primero)'}")
print()
print("3️⃣ Cambio de Contraseña:")
print("   Desde el dashboard, ir a 'Cambiar Contraseña'")
print()
print("4️⃣ Ejecutar pruebas:")
print("   python probar_recuperacion_password.py")
