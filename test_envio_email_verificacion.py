"""
Script para probar el envío de email de verificación a usuarios portal
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import UsuarioPortal
from gestion.portal_views import enviar_email_verificacion

def test_envio_email():
    """Prueba el envío de email de verificación"""
    
    print("\n" + "="*70)
    print("📧 TEST DE ENVÍO DE EMAIL DE VERIFICACIÓN")
    print("="*70 + "\n")
    
    # Listar usuarios NO verificados
    usuarios_no_verificados = UsuarioPortal.objects.filter(email_verificado=False)
    
    if not usuarios_no_verificados.exists():
        print("✓ No hay usuarios sin verificar. Todos los emails ya están verificados.\n")
        return
    
    print(f"Usuarios sin verificar: {usuarios_no_verificados.count()}\n")
    
    for idx, usuario in enumerate(usuarios_no_verificados, 1):
        print(f"{idx}. {usuario.email} - Cliente: {usuario.cliente.nombres} {usuario.cliente.apellidos}")
    
    print("\n" + "-"*70)
    
    # Preguntar si desea enviar email
    opcion = input("\n¿Desea enviar email de verificación? (s/n o número específico): ").strip().lower()
    
    if opcion == 'n':
        print("\n❌ Operación cancelada.\n")
        return
    
    if opcion == 's':
        # Enviar a todos
        print("\n📤 Enviando emails a todos los usuarios...\n")
        
        for usuario in usuarios_no_verificados:
            try:
                if enviar_email_verificacion(usuario):
                    print(f"✓ Email enviado a: {usuario.email}")
                else:
                    print(f"✗ Error enviando a: {usuario.email}")
            except Exception as e:
                print(f"✗ Error con {usuario.email}: {e}")
    
    elif opcion.isdigit():
        # Enviar a uno específico
        idx = int(opcion) - 1
        usuario_list = list(usuarios_no_verificados)
        
        if 0 <= idx < len(usuario_list):
            usuario = usuario_list[idx]
            print(f"\n📤 Enviando email a: {usuario.email}...\n")
            
            try:
                if enviar_email_verificacion(usuario):
                    print(f"✓ Email enviado correctamente")
                    print(f"\n📧 Configuración actual:")
                    print(f"   - Backend: django.core.mail.backends.console.EmailBackend")
                    print(f"   - El email se muestra en la consola (no se envía realmente)")
                    print(f"   - Para producción, configurar SMTP en settings.py")
                else:
                    print(f"✗ Error al enviar email")
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print("\n❌ Número inválido.\n")
    else:
        print("\n❌ Opción inválida.\n")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    test_envio_email()
