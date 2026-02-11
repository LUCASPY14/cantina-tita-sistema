#!/usr/bin/env python
"""
Script para configurar SMTP con Gmail (App Password) - Cantina Tita
"""
import os
import sys
import getpass

def configurar_gmail_smtp():
    """Configurar SMTP con Gmail usando App Password"""

    print("📧 CONFIGURACIÓN SMTP GMAIL - CANTINA TITA")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE:")
    print("   Gmail requiere una 'App Password' (no tu contraseña normal)")
    print("   Sigue estos pasos:")
    print("   1. Ve a: https://myaccount.google.com/apppasswords")
    print("   2. Inicia sesión con tu cuenta Gmail")
    print("   3. Nombre de la app: 'Cantina Tita Sistema'")
    print("   4. Copia la contraseña de 16 caracteres")
    print()

    # Solicitar datos
    email = input("Ingresa tu email de Gmail: ").strip()
    if not email or '@gmail.com' not in email:
        print("❌ Email inválido. Debe ser una cuenta @gmail.com")
        return

    app_password = getpass.getpass("Ingresa tu App Password (16 caracteres): ").strip()
    if not app_password or len(app_password.replace(' ', '')) != 16:
        print("❌ App Password inválida. Debe tener 16 caracteres")
        return

    # Actualizar archivo .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Actualizar configuraciones
        contenido = contenido.replace(
            'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend'
        )
        contenido = contenido.replace(
            'EMAIL_HOST_USER=tu_email@gmail.com',
            f'EMAIL_HOST_USER={email}'
        )
        contenido = contenido.replace(
            'EMAIL_HOST_PASSWORD=tu_app_password_de_16_caracteres',
            f'EMAIL_HOST_PASSWORD={app_password}'
        )

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(contenido)

        print("\n✅ CONFIGURACIÓN COMPLETADA")
        print(f"   Email: {email}")
        print("   App Password: Configurada")
        print("\n🧪 PRUEBA LA CONFIGURACIÓN:")
        print("   python probar_smtp.py")
        print("\n🔄 REINICIA EL SERVIDOR DJANGO para aplicar cambios")

    except FileNotFoundError:
        print("❌ Archivo .env no encontrado")
    except Exception as e:
        print(f"❌ Error al configurar: {e}")

def configurar_sendgrid():
    """Configurar SMTP con SendGrid"""

    print("📧 CONFIGURACIÓN SMTP SENDGRID - CANTINA TITA")
    print("=" * 60)
    print("\n📋 PASOS PARA SENDGRID:")
    print("   1. Ve a: https://sendgrid.com/")
    print("   2. Crea cuenta gratis")
    print("   3. Ve a Settings → API Keys")
    print("   4. Create API Key → Full Access")
    print("   5. Copia la API Key (empieza con 'SG.')")
    print()

    api_key = getpass.getpass("Ingresa tu SendGrid API Key: ").strip()
    if not api_key.startswith('SG.'):
        print("❌ API Key inválida. Debe empezar con 'SG.'")
        return

    # Actualizar archivo .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Cambiar a configuración SendGrid
        contenido = contenido.replace(
            'EMAIL_HOST=smtp.gmail.com',
            'EMAIL_HOST=smtp.sendgrid.net'
        )
        contenido = contenido.replace(
            'EMAIL_HOST_USER=tu_email@gmail.com',
            'EMAIL_HOST_USER=apikey'
        )
        contenido = contenido.replace(
            'EMAIL_HOST_PASSWORD=tu_app_password_de_16_caracteres',
            f'EMAIL_HOST_PASSWORD={api_key}'
        )

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(contenido)

        print("\n✅ CONFIGURACIÓN SENDGRID COMPLETADA")
        print("   Host: smtp.sendgrid.net")
        print("   User: apikey")
        print("   API Key: Configurada")
        print("\n🧪 PRUEBA LA CONFIGURACIÓN:")
        print("   python probar_smtp.py")

    except FileNotFoundError:
        print("❌ Archivo .env no encontrado")
    except Exception as e:
        print(f"❌ Error al configurar: {e}")

if __name__ == '__main__':
    print("Selecciona una opción:")
    print("1. Configurar Gmail (App Password)")
    print("2. Configurar SendGrid")
    print("3. Usar Console Backend (desarrollo)")

    opcion = input("\nOpción (1-3): ").strip()

    if opcion == '1':
        configurar_gmail_smtp()
    elif opcion == '2':
        configurar_sendgrid()
    elif opcion == '3':
        os.system('python probar_smtp.py --desarrollo')
    else:
        print("❌ Opción inválida")