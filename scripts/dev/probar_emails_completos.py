#!/usr/bin/env python
"""
Script para probar todas las funcionalidades de email en Cantina Tita
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.test import RequestFactory
from django.core.mail import send_mail
from django.conf import settings
from gestion.models import Cliente, UsuariosWebClientes
from gestion.seguridad_utils import (
    generar_token_recuperacion,
    enviar_notificacion_seguridad,
    notificar_login_nueva_ip
)

def probar_email_recuperacion():
    """Probar envío de email de recuperación de contraseña"""

    print("🔐 PRUEBA: EMAIL DE RECUPERACIÓN DE CONTRASEÑA")
    print("-" * 50)

    # Buscar un cliente con usuario web
    usuario_web = UsuariosWebClientes.objects.select_related('id_cliente').first()

    if not usuario_web:
        print("❌ No hay usuarios web registrados para probar")
        print("   Crea un cliente con usuario web desde el POS primero")
        return False

    cliente = usuario_web.id_cliente
    print(f"✅ Cliente encontrado: {cliente.nombres} {cliente.apellidos}")
    print(f"   Email: {cliente.email}")
    print(f"   Usuario: {usuario_web.usuario}")

    # Crear request simulado
    factory = RequestFactory()
    request = factory.get('/fake-request')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.session = {'cliente_usuario': usuario_web.usuario, 'cliente_id': cliente.id_cliente}

    # Generar token
    token = generar_token_recuperacion(cliente, request)

    if token:
        print("✅ Token generado correctamente")

        # Simular envío de email (como en cliente_views.py)
        reset_url = f"http://localhost:8000/pos/portal/reset-password/{token}/"

        try:
            resultado = send_mail(
                subject='Recuperación de Contraseña - Cantina Tita',
                message=f'''Hola {cliente.nombres},

Has solicitado recuperar tu contraseña del portal de clientes.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{reset_url}

Este enlace expira en 24 horas.

Si no solicitaste este cambio, ignora este mensaje.

Saludos,
Sistema Cantina Tita
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cliente.email],
                fail_silently=False,
            )

            if resultado == 1:
                print("✅ Email de recuperación enviado correctamente")
                print(f"   URL de recuperación: {reset_url}")
                return True
            else:
                print("❌ Error al enviar email de recuperación")
                return False

        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False
    else:
        print("❌ Error al generar token")
        return False

def probar_notificacion_seguridad():
    """Probar envío de notificación de seguridad"""

    print("\n🛡️  PRUEBA: NOTIFICACIÓN DE SEGURIDAD")
    print("-" * 50)

    # Buscar un cliente con email
    cliente = Cliente.objects.filter(email__isnull=False).exclude(email='').first()

    if not cliente:
        print("❌ No hay clientes con email registrado")
        return False

    print(f"✅ Cliente encontrado: {cliente.nombres} {cliente.apellidos}")
    print(f"   Email: {cliente.email}")

    # Probar notificación de seguridad
    resultado = enviar_notificacion_seguridad(
        cliente=cliente,
        asunto='Prueba de Notificación de Seguridad',
        mensaje='Esta es una prueba del sistema de notificaciones de seguridad de Cantina Tita.',
        tipo='info'
    )

    if resultado:
        print("✅ Notificación de seguridad enviada correctamente")
        return True
    else:
        print("❌ Error al enviar notificación de seguridad")
        return False

def probar_notificacion_login_ip():
    """Probar notificación de login desde nueva IP"""

    print("\n🌐 PRUEBA: NOTIFICACIÓN DE LOGIN DESDE NUEVA IP")
    print("-" * 50)

    # Buscar un cliente con email
    cliente = Cliente.objects.filter(email__isnull=False).exclude(email='').first()

    if not cliente:
        print("❌ No hay clientes con email registrado")
        return False

    print(f"✅ Cliente encontrado: {cliente.nombres} {cliente.apellidos}")
    print(f"   Email: {cliente.email}")

    # Crear request simulado
    factory = RequestFactory()
    request = factory.get('/fake-request')
    request.META['REMOTE_ADDR'] = '192.168.1.100'  # IP de prueba

    # Probar notificación
    try:
        notificar_login_nueva_ip(cliente, request)
        print("✅ Notificación de nueva IP procesada")
        return True
    except Exception as e:
        print(f"❌ Error en notificación de nueva IP: {e}")
        return False

def main():
    """Función principal"""

    print("📧 PRUEBA COMPLETA DE FUNCIONALIDADES EMAIL - CANTINA TITA")
    print("=" * 70)
    print(f"Backend actual: {settings.EMAIL_BACKEND}")
    print()

    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("ℹ️  Usando backend de CONSOLA - Los emails aparecerán abajo:")
        print("-" * 70)
    else:
        print("📤 Usando backend SMTP - Los emails se enviarán realmente")
        print("-" * 70)

    resultados = []

    # Probar cada funcionalidad
    resultados.append(probar_email_recuperacion())
    resultados.append(probar_notificacion_seguridad())
    resultados.append(probar_notificacion_login_ip())

    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Recuperación de contraseña: {'✅ OK' if resultados[0] else '❌ Error'}")
    print(f"   Notificación de seguridad:  {'✅ OK' if resultados[1] else '❌ Error'}")
    print(f"   Notificación nueva IP:      {'✅ OK' if resultados[2] else '❌ Error'}")

    exitos = sum(resultados)
    print(f"\n🎯 RESULTADO: {exitos}/3 pruebas exitosas")

    if exitos == 3:
        print("🎉 ¡Todas las funcionalidades de email funcionan correctamente!")
    elif exitos > 0:
        print("⚠️  Algunas funcionalidades funcionan, revisa los errores arriba")
    else:
        print("❌ Ninguna funcionalidad de email funciona")

    print("\n💡 PARA CONFIGURAR SMTP REAL:")
    print("   python configurar_smtp.py")

if __name__ == '__main__':
    main()