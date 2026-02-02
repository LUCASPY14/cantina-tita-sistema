"""
Script para generar token de verificación y mostrar enlace
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import UsuarioPortal, TokenVerificacion
import secrets
from datetime import timedelta
from django.utils import timezone

# Buscar primer usuario NO verificado
usuario = UsuarioPortal.objects.filter(email_verificado=False).first()

if not usuario:
    print("\n❌ No hay usuarios sin verificar.\n")
    exit()

print("\n" + "="*80)
print("📧 GENERANDO TOKEN DE VERIFICACIÓN")
print("="*80)

# Eliminar tokens anteriores
TokenVerificacion.objects.filter(
    usuario_portal=usuario,
    tipo='email_verification'
).delete()

# Crear nuevo token
token_str = secrets.token_urlsafe(32)
token_obj = TokenVerificacion.objects.create(
    usuario_portal=usuario,
    token=token_str,
    tipo='email_verification',
    expira_en=timezone.now() + timedelta(hours=24)
)

print(f"\n📧 Usuario: {usuario.email}")
print(f"👤 Cliente: {usuario.cliente.nombres} {usuario.cliente.apellidos}")
print(f"⏰ Expira: {token_obj.expira_en.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "="*80)
print("🔗 COPIA ESTE ENLACE COMPLETO:")
print("="*80)

enlace = f"http://127.0.0.1:8000/portal/verificar-email/{token_str}/"
print(f"\n{enlace}\n")

print("="*80)
print("\n✅ Copia el enlace de arriba y ábrelo en tu navegador\n")
