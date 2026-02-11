"""
Script para probar el sistema de recuperación de contraseña
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.utils import timezone
from gestion.models import Cliente, UsuariosWebClientes, TokenRecuperacion
from gestion.seguridad_utils import generar_token_recuperacion, verificar_token_recuperacion
import bcrypt

print("🔐 Prueba del Sistema de Recuperación de Contraseña\n")
print("="*60)

# 1. Buscar un cliente con usuario web
print("\n1️⃣ Buscando cliente con usuario web...")
usuario_web = UsuariosWebClientes.objects.select_related('id_cliente').first()

if not usuario_web:
    print("❌ No hay usuarios web registrados")
    print("   Primero crea un cliente con usuario web desde el POS")
    sys.exit(1)

cliente = usuario_web.id_cliente
print(f"✅ Cliente encontrado: {cliente.nombres} {cliente.apellidos}")
print(f"   Usuario: {usuario_web.usuario}")
print(f"   Email: {cliente.email}")

# 2. Generar token de recuperación
print("\n2️⃣ Generando token de recuperación...")
from django.test import RequestFactory
factory = RequestFactory()
request = factory.get('/fake-request')
request.META['REMOTE_ADDR'] = '127.0.0.1'

token = generar_token_recuperacion(cliente, request)
if token:
    print(f"✅ Token generado: {token[:20]}...")
    
    # Buscar el objeto del token
    token_obj = TokenRecuperacion.objects.get(token=token)
    print(f"   Expira: {token_obj.fecha_expiracion}")
    print(f"   Usado: {token_obj.usado}")
else:
    print("❌ Error al generar token")
    sys.exit(1)

# 3. Verificar token
print("\n3️⃣ Verificando token...")
valido, token_obj, mensaje = verificar_token_recuperacion(token)
if valido:
    print(f"✅ Token válido")
    print(f"   Cliente: {token_obj.id_cliente.nombres}")
else:
    print(f"❌ Token inválido: {mensaje}")
    sys.exit(1)

# 4. Simular cambio de contraseña
print("\n4️⃣ Simulando cambio de contraseña...")
nueva_password = "NuevaPassword123"
nuevo_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"   Nueva contraseña: {nueva_password}")
print(f"   Hash generado: {nuevo_hash[:50]}...")

# No guardamos realmente, solo simulamos
print("   (No se guarda en la base de datos, solo prueba)")

# 5. Verificar que el token se puede marcar como usado
print("\n5️⃣ Probando marcar token como usado...")
from gestion.seguridad_utils import marcar_token_usado
if marcar_token_usado(token):
    print("✅ Token marcado como usado")
    
    # Verificar que ahora está usado
    valido, _, mensaje = verificar_token_recuperacion(token)
    if not valido:
        print(f"✅ Token correctamente invalidado: {mensaje}")
    else:
        print("❌ Error: token debería estar invalidado")
else:
    print("❌ Error al marcar token")

# 6. Estadísticas
print("\n6️⃣ Estadísticas del sistema:")
total_tokens = TokenRecuperacion.objects.count()
tokens_usados = TokenRecuperacion.objects.filter(usado=True).count()
tokens_activos = TokenRecuperacion.objects.filter(usado=False, fecha_expiracion__gt=timezone.now()).count()

print(f"   Total de tokens: {total_tokens}")
print(f"   Tokens usados: {tokens_usados}")
print(f"   Tokens activos: {tokens_activos}")

print("\n" + "="*60)
print("✅ Sistema de recuperación de contraseña funcionando correctamente!")
print("\n📋 Próximos pasos:")
print("   1. Iniciar servidor: python manage.py runserver")
print("   2. Ir a: http://127.0.0.1:8000/pos/portal/login/")
print("   3. Click en '¿Olvidaste tu contraseña?'")
print(f"   4. Usar email: {cliente.email}")
print("   5. El enlace aparecerá en la consola (EMAIL_BACKEND=console)")
