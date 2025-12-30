#!/usr/bin/env python
"""
Script para probar la configuración SMTP de Cantina Tita
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.core.mail import send_mail, get_connection
from django.conf import settings

def probar_configuracion_smtp():
    """Probar la configuración SMTP actual"""

    print("📧 PRUEBA DE CONFIGURACIÓN SMTP - CANTINA TITA")
    print("=" * 60)

    # Mostrar configuración actual
    print("\n🔧 CONFIGURACIÓN ACTUAL:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   User: {settings.EMAIL_HOST_USER}")
    print(f"   Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'No configurado'}")

    # Verificar si está usando console backend
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("\n⚠️  ATENCIÓN: Estás usando el backend de CONSOLE")
        print("   Los emails aparecerán en la terminal/consola, no se enviarán realmente.")
        print("   Para enviar emails reales, configura EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
        return

    # Verificar configuración básica
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: Credenciales SMTP no configuradas")
        print("   Configura EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en tu archivo .env")
        return

    print("\n🧪 PROBANDO CONEXIÓN SMTP...")

    try:
        # Probar conexión
        connection = get_connection()
        connection.open()
        connection.close()

        print("✅ Conexión SMTP exitosa")

        # Enviar email de prueba
        print("\n📤 ENVIANDO EMAIL DE PRUEBA...")

        resultado = send_mail(
            subject='🧪 Prueba SMTP - Cantina Tita',
            message=f'''Hola,

Esta es una prueba de configuración SMTP del sistema Cantina Tita.

Configuración utilizada:
- Host: {settings.EMAIL_HOST}
- Puerto: {settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- Usuario: {settings.EMAIL_HOST_USER}

Si recibes este email, ¡la configuración SMTP funciona correctamente! 🎉

Saludos,
Sistema Cantina Tita
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Enviar a la misma cuenta
            fail_silently=False,
        )

        if resultado == 1:
            print("✅ Email enviado exitosamente")
            print(f"   Destinatario: {settings.EMAIL_HOST_USER}")
        else:
            print("❌ Error al enviar email")

    except Exception as e:
        print(f"❌ Error de conexión SMTP: {e}")
        print("\n🔍 POSIBLES SOLUCIONES:")
        print("   1. Verifica que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD sean correctos")
        print("   2. Para Gmail: Asegúrate de usar una App Password (no tu contraseña normal)")
        print("   3. Verifica que tu cuenta no tenga restricciones de seguridad")
        print("   4. Para desarrollo: Cambia EMAIL_BACKEND a 'django.core.mail.backends.console.EmailBackend'")

def configurar_para_desarrollo():
    """Configurar para usar backend de consola (desarrollo)"""

    print("\n🔧 CONFIGURANDO PARA DESARROLLO (CONSOLE BACKEND)...")

    # Leer archivo .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Cambiar backend a console
        if 'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend' in contenido:
            contenido = contenido.replace(
                'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend'
            )

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(contenido)

            print("✅ Configurado para desarrollo (console backend)")
            print("   Los emails aparecerán en la consola/terminal")
            print("   Reinicia el servidor Django para aplicar cambios")
        else:
            print("ℹ️  Ya está configurado para desarrollo")

    except Exception as e:
        print(f"❌ Error al configurar: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--desarrollo':
        configurar_para_desarrollo()
    else:
        probar_configuracion_smtp()

        print("\n💡 PARA DESARROLLO:")
        print("   Ejecuta: python probar_smtp.py --desarrollo")
        print("   Esto cambiará EMAIL_BACKEND a console.EmailBackend")