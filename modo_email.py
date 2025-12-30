#!/usr/bin/env python
"""
Script para alternar entre modo desarrollo y producción para emails
"""
import os
import sys

def cambiar_a_desarrollo():
    """Cambiar a backend de consola (desarrollo)"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        if 'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend' in contenido:
            print("ℹ️  Ya está en modo DESARROLLO")
            return

        contenido = contenido.replace(
            'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend'
        )

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(contenido)

        print("✅ Cambiado a modo DESARROLLO")
        print("   Los emails aparecerán en la consola")
        print("   Reinicia el servidor Django")

    except Exception as e:
        print(f"❌ Error: {e}")

def cambiar_a_produccion():
    """Cambiar a backend SMTP (producción)"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        if 'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend' in contenido:
            print("ℹ️  Ya está en modo PRODUCCIÓN")
            return

        contenido = contenido.replace(
            'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend',
            'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend'
        )

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(contenido)

        print("✅ Cambiado a modo PRODUCCIÓN")
        print("   Los emails se enviarán realmente")
        print("   Asegúrate de configurar credenciales SMTP")
        print("   Reinicia el servidor Django")

    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_estado():
    """Mostrar estado actual"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        if 'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend' in contenido:
            print("🔧 MODO ACTUAL: DESARROLLO (Console)")
            print("   Los emails aparecen en la consola")
        elif 'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend' in contenido:
            print("🚀 MODO ACTUAL: PRODUCCIÓN (SMTP)")
            print("   Los emails se envían realmente")
        else:
            print("❓ MODO ACTUAL: DESCONOCIDO")

    except Exception as e:
        print(f"❌ Error al leer configuración: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python modo_email.py [desarrollo|produccion|estado]")
        print()
        mostrar_estado()
        sys.exit(1)

    comando = sys.argv[1].lower()

    if comando == 'desarrollo':
        cambiar_a_desarrollo()
    elif comando == 'produccion':
        cambiar_a_produccion()
    elif comando == 'estado':
        mostrar_estado()
    else:
        print("❌ Comando inválido. Use: desarrollo, produccion, o estado")