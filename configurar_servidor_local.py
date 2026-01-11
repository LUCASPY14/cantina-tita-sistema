#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de configuración para servidor local
Configura Gmail SMTP, IP local, firewall y configuraciones de seguridad

Autor: Sistema Cantina Tita
Fecha: 10 de Enero de 2026
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

# Agregar el directorio del proyecto al path de Python
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
import django
django.setup()

def print_header(text):
    """Imprime un encabezado destacado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"[OK] {text}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"[ERROR] {text}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"[WARNING] {text}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"[INFO] {text}")

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        # Crear socket para obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No detectada"

def check_firewall_rule(port):
    """Verifica si existe regla de firewall para el puerto"""
    try:
        # Ejecutar netsh para verificar reglas
        cmd = f'netsh advfirewall firewall show rule name="Django Server Port {port}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return "No rules match" not in result.stdout
    except Exception:
        return False

def create_firewall_rule(port):
    """Crea regla de firewall para el puerto especificado"""
    try:
        # Eliminar regla si existe
        cmd_delete = f'netsh advfirewall firewall delete rule name="Django Server Port {port}"'
        subprocess.run(cmd_delete, shell=True, capture_output=True)
        
        # Crear nueva regla
        cmd_add = (
            f'netsh advfirewall firewall add rule '
            f'name="Django Server Port {port}" '
            f'dir=in action=allow protocol=TCP localport={port}'
        )
        result = subprocess.run(cmd_add, shell=True, capture_output=True, text=True)
        
        return result.returncode == 0
    except Exception as e:
        print_error(f"Error al crear regla de firewall: {e}")
        return False

def update_env_file(updates):
    """Actualiza variables en el archivo .env"""
    env_path = BASE_DIR / '.env'
    
    try:
        # Leer archivo actual
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Actualizar líneas
        updated_lines = []
        for line in lines:
            updated = False
            for key, value in updates.items():
                if line.strip().startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    updated = True
                    print_success(f"Actualizado: {key}")
                    break
            if not updated:
                updated_lines.append(line)
        
        # Escribir archivo actualizado
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        return True
    except Exception as e:
        print_error(f"Error al actualizar .env: {e}")
        return False

def update_settings_file(updates):
    """Actualiza configuraciones en settings.py"""
    settings_path = BASE_DIR / 'cantina_project' / 'settings.py'
    
    try:
        # Leer archivo actual
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar actualizaciones
        for old_text, new_text in updates.items():
            if old_text in content:
                content = content.replace(old_text, new_text)
                print_success(f"Actualizado settings.py")
        
        # Escribir archivo actualizado
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print_error(f"Error al actualizar settings.py: {e}")
        return False

def configure_gmail_smtp():
    """Configura Gmail SMTP interactivamente"""
    print_header("CONFIGURACIÓN DE GMAIL SMTP")
    
    print("Para enviar emails desde el sistema necesitas:")
    print("1. Una cuenta de Gmail")
    print("2. Una 'Contraseña de Aplicación' (App Password)")
    print("\nPASOS:")
    print("  a) Ve a: https://myaccount.google.com/apppasswords")
    print("  b) Inicia sesión con tu Gmail")
    print("  c) Nombre de la app: 'Cantina Tita'")
    print("  d) Copia la contraseña de 16 caracteres\n")
    
    configurar = input("¿Deseas configurar Gmail SMTP ahora? (s/n): ").strip().lower()
    
    if configurar == 's':
        email = input("\nIngresa tu email de Gmail: ").strip()
        
        print("\nIngresa la contraseña de aplicación (16 caracteres):")
        print("Formato: xxxx xxxx xxxx xxxx (con o sin espacios)")
        password = input("App Password: ").strip().replace(" ", "")
        
        if len(password) != 16:
            print_warning(f"La contraseña tiene {len(password)} caracteres, debería tener 16")
            confirmar = input("¿Continuar de todas formas? (s/n): ").strip().lower()
            if confirmar != 's':
                print_info("Configuración de SMTP cancelada")
                return False
        
        # Actualizar .env
        updates = {
            'EMAIL_HOST_USER': email,
            'EMAIL_HOST_PASSWORD': password
        }
        
        if update_env_file(updates):
            print_success("Configuración de Gmail SMTP completada")
            print_info(f"Email configurado: {email}")
            return True
        else:
            print_error("No se pudo actualizar la configuración")
            return False
    else:
        print_info("Configuración de SMTP omitida - puedes hacerlo después editando .env")
        return False

def configure_allowed_hosts():
    """Configura ALLOWED_HOSTS con la IP local"""
    print_header("CONFIGURACIÓN DE ALLOWED_HOSTS")
    
    # Detectar IP local
    local_ip = get_local_ip()
    print_info(f"IP local detectada: {local_ip}")
    
    # Solicitar IP adicional si es necesaria
    print("\n¿Deseas agregar IPs adicionales? (separadas por comas)")
    print("Ejemplo: 192.168.1.100,192.168.1.200")
    additional = input("IPs adicionales (Enter para omitir): ").strip()
    
    # Construir lista de hosts permitidos
    allowed = ['localhost', '127.0.0.1', 'testserver']
    
    if local_ip != "No detectada":
        allowed.append(local_ip)
    
    if additional:
        allowed.extend([ip.strip() for ip in additional.split(',')])
    
    # Actualizar settings.py
    allowed_hosts_str = str(allowed)
    
    updates = {
        "ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']": 
        f"ALLOWED_HOSTS = {allowed_hosts_str}"
    }
    
    if update_settings_file(updates):
        print_success("ALLOWED_HOSTS actualizado")
        print_info(f"Hosts permitidos: {', '.join(allowed)}")
        return True
    else:
        print_error("No se pudo actualizar ALLOWED_HOSTS")
        return False

def configure_firewall():
    """Configura reglas de firewall"""
    print_header("CONFIGURACIÓN DE FIREWALL DE WINDOWS")
    
    print("Para acceder al servidor desde otras PCs en la red local,")
    print("necesitas abrir puertos en el firewall de Windows.\n")
    
    print("Puertos necesarios:")
    print("  - 8000: Django development server (runserver)")
    print("  - 80: HTTP (producción con nginx/Apache)")
    print("  - 443: HTTPS (producción con SSL)\n")
    
    configurar = input("¿Configurar firewall ahora? (s/n): ").strip().lower()
    
    if configurar == 's':
        ports = [8000]
        
        agregar_prod = input("¿Agregar puertos 80 y 443 para producción? (s/n): ").strip().lower()
        if agregar_prod == 's':
            ports.extend([80, 443])
        
        print("\n[INFO] Configurando firewall (requiere privilegios de administrador)...\n")
        
        success_count = 0
        for port in ports:
            if check_firewall_rule(port):
                print_info(f"Puerto {port} ya está abierto")
                success_count += 1
            else:
                print_info(f"Abriendo puerto {port}...")
                if create_firewall_rule(port):
                    print_success(f"Puerto {port} abierto exitosamente")
                    success_count += 1
                else:
                    print_error(f"No se pudo abrir puerto {port}")
                    print_warning("Ejecuta este script como Administrador")
        
        if success_count == len(ports):
            print_success(f"\nTodos los puertos configurados ({success_count}/{len(ports)})")
            return True
        else:
            print_warning(f"\nAlgunos puertos no se configuraron ({success_count}/{len(ports)})")
            return False
    else:
        print_info("Configuración de firewall omitida")
        print_warning("Deberás abrir puertos manualmente si tienes problemas de conexión")
        return False

def activate_https_settings():
    """Activa configuraciones HTTPS en settings.py (para SSL local)"""
    print_header("CONFIGURACIÓN DE HTTPS/SSL")
    
    print("Las configuraciones HTTPS están comentadas en settings.py")
    print("Para pruebas locales, puedes:")
    print("  1. Usar HTTP (no seguro pero funcional)")
    print("  2. Configurar certificado autofirmado (mkcert)")
    print("  3. Esperar hasta tener SSL real (Let's Encrypt)\n")
    
    activar = input("¿Activar configuraciones HTTPS ahora? (s/n): ").strip().lower()
    
    if activar == 's':
        # Descomentariar líneas en settings.py
        updates = {
            "# SECURE_SSL_REDIRECT = True": "SECURE_SSL_REDIRECT = True",
            "# SESSION_COOKIE_SECURE = True": "SESSION_COOKIE_SECURE = True",
            "# CSRF_COOKIE_SECURE = True": "CSRF_COOKIE_SECURE = True",
            "# SECURE_HSTS_SECONDS = 31536000": "SECURE_HSTS_SECONDS = 31536000",
            "# SECURE_HSTS_INCLUDE_SUBDOMAINS = True": "SECURE_HSTS_INCLUDE_SUBDOMAINS = True",
            "# SECURE_BROWSER_XSS_FILTER = True": "SECURE_BROWSER_XSS_FILTER = True"
        }
        
        if update_settings_file(updates):
            print_success("Configuraciones HTTPS activadas")
            print_warning("IMPORTANTE: Necesitarás certificado SSL para que funcione")
            print_info("Para certificado autofirmado local: instala mkcert")
            return True
        else:
            print_error("No se pudieron activar configuraciones HTTPS")
            return False
    else:
        print_info("Configuraciones HTTPS no activadas (recomendado para pruebas)")
        print_info("El sistema funcionará con HTTP en http://IP:8000")
        return False

def test_email_configuration():
    """Prueba el envío de un email de prueba"""
    print_header("PRUEBA DE CONFIGURACIÓN DE EMAIL")
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Verificar configuración
        if not settings.EMAIL_HOST_USER or settings.EMAIL_HOST_USER == 'tu_email@gmail.com':
            print_warning("Email no configurado todavía")
            return False
        
        probar = input(f"¿Enviar email de prueba desde {settings.EMAIL_HOST_USER}? (s/n): ").strip().lower()
        
        if probar == 's':
            destinatario = input("Email destinatario: ").strip()
            
            print("\n[INFO] Enviando email de prueba...")
            
            send_mail(
                subject='Prueba - Sistema Cantina Tita',
                message='Este es un email de prueba del Sistema de Gestión de Cantina Escolar "Tita".\n\n'
                        'Si recibiste este mensaje, la configuración SMTP está funcionando correctamente.\n\n'
                        'Fecha: 10 de Enero de 2026\n'
                        'Sistema: Cantina Tita v1.0',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[destinatario],
                fail_silently=False,
            )
            
            print_success("Email enviado exitosamente")
            print_info(f"Revisa la bandeja de entrada de {destinatario}")
            return True
        else:
            print_info("Prueba de email omitida")
            return False
            
    except Exception as e:
        print_error(f"Error al enviar email: {e}")
        print_warning("Verifica:")
        print("  - Que el email y contraseña sean correctos")
        print("  - Que tengas conexión a internet")
        print("  - Que la cuenta de Gmail permita apps menos seguras")
        return False

def show_server_info():
    """Muestra información para iniciar el servidor"""
    print_header("INFORMACIÓN DEL SERVIDOR")
    
    local_ip = get_local_ip()
    
    print("El servidor está configurado. Para iniciarlo:\n")
    print("1. DESARROLLO (con runserver):")
    print(f"   python manage.py runserver 0.0.0.0:8000")
    print(f"\n   Accede desde:")
    print(f"   - Esta PC: http://127.0.0.1:8000")
    print(f"   - Otras PCs: http://{local_ip}:8000\n")
    
    print("2. PRODUCCIÓN (con Gunicorn + nginx):")
    print("   - Instalar Gunicorn: pip install gunicorn")
    print("   - Ejecutar: gunicorn cantina_project.wsgi:application --bind 0.0.0.0:8000")
    print("   - Configurar nginx como proxy reverso\n")
    
    print("3. VERIFICAR SEGURIDAD:")
    print("   python auditoria_seguridad.py\n")
    
    print("4. DESDE OTRA PC:")
    print(f"   http://{local_ip}:8000/admin")
    print(f"   http://{local_ip}:8000/portal\n")

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("  CONFIGURACIÓN DE SERVIDOR LOCAL - SISTEMA CANTINA TITA")
    print("  Fecha: 10 de Enero de 2026")
    print("=" * 70)
    
    print("\nEste script configurará:")
    print("  [1] Gmail SMTP para envío de emails")
    print("  [2] ALLOWED_HOSTS con IP local")
    print("  [3] Firewall de Windows (puertos 8000, 80, 443)")
    print("  [4] Configuraciones HTTPS/SSL (opcional)")
    print("  [5] Prueba de envío de email")
    
    print("\n¿Deseas continuar? (s/n): ", end='')
    continuar = input().strip().lower()
    
    if continuar != 's':
        print("\n[INFO] Configuración cancelada por el usuario")
        return
    
    # Ejecutar configuraciones
    resultados = {}
    
    # 1. Gmail SMTP
    resultados['gmail'] = configure_gmail_smtp()
    
    # 2. ALLOWED_HOSTS
    resultados['allowed_hosts'] = configure_allowed_hosts()
    
    # 3. Firewall
    resultados['firewall'] = configure_firewall()
    
    # 4. HTTPS
    resultados['https'] = activate_https_settings()
    
    # 5. Prueba de email
    if resultados['gmail']:
        resultados['test_email'] = test_email_configuration()
    else:
        resultados['test_email'] = False
    
    # Resumen
    print_header("RESUMEN DE CONFIGURACIÓN")
    
    print(f"Gmail SMTP:        {'[OK]' if resultados['gmail'] else '[OMITIDO]'}")
    print(f"ALLOWED_HOSTS:     {'[OK]' if resultados['allowed_hosts'] else '[ERROR]'}")
    print(f"Firewall:          {'[OK]' if resultados['firewall'] else '[OMITIDO]'}")
    print(f"HTTPS:             {'[OK]' if resultados['https'] else '[OMITIDO]'}")
    print(f"Test Email:        {'[OK]' if resultados['test_email'] else '[OMITIDO]'}")
    
    # Mostrar información del servidor
    show_server_info()
    
    # Guardar configuración
    config_file = BASE_DIR / 'CONFIGURACION_SERVIDOR_LOCAL.txt'
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write("CONFIGURACIÓN DE SERVIDOR LOCAL\n")
        f.write("================================\n")
        f.write(f"Fecha: 10 de Enero de 2026\n\n")
        f.write(f"IP Local: {get_local_ip()}\n")
        f.write(f"Gmail SMTP: {'Configurado' if resultados['gmail'] else 'No configurado'}\n")
        f.write(f"HTTPS: {'Activado' if resultados['https'] else 'No activado'}\n")
        f.write(f"\nPara iniciar servidor:\n")
        f.write(f"python manage.py runserver 0.0.0.0:8000\n")
    
    print_success(f"\nConfiguración guardada en: {config_file}")
    print("\n[INFO] Configuración completada. ¡El servidor está listo para usar!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Configuración interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
