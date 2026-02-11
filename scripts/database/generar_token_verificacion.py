"""
Script para generar y mostrar token de verificación de email
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import UsuarioPortal, TokenVerificacion
from gestion.portal_views import enviar_email_verificacion
import secrets
from datetime import timedelta
from django.utils import timezone

def generar_y_mostrar_token():
    """Genera token y muestra enlace de verificación"""
    
    print("\n" + "="*80)
    print("📧 GENERADOR DE TOKEN DE VERIFICACIÓN DE EMAIL")
    print("="*80 + "\n")
    
    # Buscar usuarios NO verificados
    usuarios = UsuarioPortal.objects.filter(email_verificado=False)
    
    if not usuarios.exists():
        print("❌ No hay usuarios sin verificar.\n")
        return
    
    print("Usuarios disponibles:\n")
    for idx, usuario in enumerate(usuarios, 1):
        print(f"{idx}. {usuario.email} - {usuario.cliente.nombres} {usuario.cliente.apellidos}")
    
    # Seleccionar usuario
    try:
        seleccion = int(input("\n¿Para qué usuario generar token? (número): ")) - 1
        usuario = list(usuarios)[seleccion]
    except (ValueError, IndexError):
        print("\n❌ Selección inválida.\n")
        return
    
    print(f"\n📝 Generando token para: {usuario.email}\n")
    
    # Eliminar tokens anteriores del usuario
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
    
    # Mostrar información
    print("="*80)
    print("✅ TOKEN GENERADO EXITOSAMENTE")
    print("="*80)
    print(f"\n📧 Email: {usuario.email}")
    print(f"👤 Cliente: {usuario.cliente.nombres} {usuario.cliente.apellidos}")
    print(f"🔑 Token: {token_str}")
    print(f"⏰ Expira: {token_obj.expira_en.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)
    print("🔗 ENLACE DE VERIFICACIÓN:")
    print("="*80)
    
    enlace = f"http://127.0.0.1:8000/portal/verificar-email/{token_str}/"
    print(f"\n{enlace}")
    
    print("\n" + "="*80)
    print("📋 INSTRUCCIONES:")
    print("="*80)
    print("\n1. Copia el enlace completo de arriba")
    print("2. Pégalo en tu navegador")
    print("3. Presiona Enter")
    print("4. Deberías ver: 'Email verificado correctamente'")
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    generar_y_mostrar_token()
