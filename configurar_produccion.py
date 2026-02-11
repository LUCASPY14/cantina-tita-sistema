#!/usr/bin/env python3
"""
Asistente Interactivo para Configurar .env.production
======================================================

Este script te guiará paso a paso para completar todas las variables
necesarias para producción.
"""

import os
import sys
from pathlib import Path

# Colores
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{END}")
    print(f"{BOLD}{BLUE}{text:^70}{END}")
    print(f"{BOLD}{BLUE}{'='*70}{END}\n")

def print_step(num, text):
    print(f"\n{BOLD}{GREEN}[PASO {num}] {text}{END}")
    print("-" * 70)

def ask_question(prompt, default=""):
    if default:
        user_input = input(f"{YELLOW}{prompt} [{default}]: {END}").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{YELLOW}{prompt}: {END}").strip()
            if user_input:
                return user_input
            print(f"{YELLOW}⚠️  Este campo es obligatorio. Por favor ingresa un valor.{END}")

def ask_yes_no(prompt, default="s"):
    while True:
        response = input(f"{YELLOW}{prompt} (s/n) [{default}]: {END}").strip().lower()
        if not response:
            response = default
        if response in ['s', 'n', 'si', 'no']:
            return response in ['s', 'si']
        print(f"{YELLOW}Por favor responde 's' o 'n'{END}")

def main():
    print_header("CONFIGURACIÓN DE .env.production")
    
    print(f"{BOLD}Este asistente te ayudará a configurar todas las variables necesarias")
    print(f"para desplegar tu sistema a producción.{END}\n")
    
    config = {}
    
    # =========================================================================
    # PASO 1: ALLOWED_HOSTS
    # =========================================================================
    print_step(1, "Configurar ALLOWED_HOSTS")
    print("¿Qué tipo de hosting usarás?")
    print("1. Railway")
    print("2. Render")
    print("3. VPS con dominio propio")
    print("4. Servidor local con IP")
    
    hosting_choice = ask_question("Selecciona opción (1-4)", "1")
    
    if hosting_choice == "1":
        config['ALLOWED_HOSTS'] = ".railway.app"
        domain = input(f"{YELLOW}¿Tienes dominio personalizado? (déjalo vacío si no): {END}").strip()
        if domain:
            config['ALLOWED_HOSTS'] = f".railway.app,{domain},www.{domain}"
    elif hosting_choice == "2":
        config['ALLOWED_HOSTS'] = ".onrender.com"
        domain = input(f"{YELLOW}¿Tienes dominio personalizado? (déjalo vacío si no): {END}").strip()
        if domain:
            config['ALLOWED_HOSTS'] = f".onrender.com,{domain},www.{domain}"
    elif hosting_choice == "3":
        domain = ask_question("Ingresa tu dominio (ej: cantitatita.com)")
        ip = ask_question("Ingresa la IP de tu servidor", "")
        config['ALLOWED_HOSTS'] = f"{domain},www.{domain},{ip}" if ip else f"{domain},www.{domain}"
    else:
        ip = ask_question("Ingresa la IP local de tu servidor (ej: 192.168.1.100)")
        config['ALLOWED_HOSTS'] = f"{ip},localhost,127.0.0.1"
    
    print(f"{GREEN}✓ ALLOWED_HOSTS configurado: {config['ALLOWED_HOSTS']}{END}")
    
    # =========================================================================
    # PASO 2: BASE DE DATOS
    # =========================================================================
    print_step(2, "Configurar Base de Datos MySQL")
    
    if hosting_choice in ["1", "2"]:
        print(f"{BLUE}ℹ️  Railway/Render crean la base de datos automáticamente.{END}")
        print(f"{BLUE}   Usa las credenciales que te proporcionan en su Dashboard.{END}\n")
        
        config['DB_NAME'] = ask_question("DB_NAME", "railway" if hosting_choice == "1" else "render")
        config['DB_USER'] = ask_question("DB_USER", "root")
        config['DB_PASSWORD'] = ask_question("DB_PASSWORD (proporcionado por Railway/Render)")
        config['DB_HOST'] = ask_question("DB_HOST (proporcionado por Railway/Render)")
        config['DB_PORT'] = ask_question("DB_PORT", "3306")
    else:
        config['DB_NAME'] = ask_question("DB_NAME", "cantitatitadb")
        config['DB_USER'] = ask_question("DB_USER", "cantina_user")
        
        print(f"\n{YELLOW}⚠️  IMPORTANTE: Usa un password seguro (20+ caracteres){END}")
        print(f"{YELLOW}   Combina: mayúsculas + minúsculas + números + símbolos{END}")
        config['DB_PASSWORD'] = ask_question("DB_PASSWORD")
        
        config['DB_HOST'] = ask_question("DB_HOST", "localhost")
        config['DB_PORT'] = ask_question("DB_PORT", "3306")
    
    print(f"{GREEN}✓ Base de datos configurada{END}")
    
    # =========================================================================
    # PASO 3: EMAIL (SMTP)
    # =========================================================================
    print_step(3, "Configurar Email (SMTP)")
    
    print("¿Qué servicio de email usarás?")
    print("1. Gmail (recomendado)")
    print("2. SendGrid")
    print("3. Otro")
    
    email_choice = ask_question("Selecciona opción (1-3)", "1")
    
    if email_choice == "1":
        config['EMAIL_HOST'] = "smtp.gmail.com"
        config['EMAIL_PORT'] = "587"
        config['EMAIL_USE_TLS'] = "True"
        config['EMAIL_HOST_USER'] = ask_question("Email de Gmail")
        
        print(f"\n{BLUE}📋 Para obtener App Password:{END}")
        print(f"{BLUE}1. Ve a: https://myaccount.google.com/apppasswords{END}")
        print(f"{BLUE}2. Crea 'App Password' con nombre 'Cantina Tita'{END}")
        print(f"{BLUE}3. Copia la contraseña de 16 caracteres (sin espacios){END}\n")
        
        config['EMAIL_HOST_PASSWORD'] = ask_question("App Password de Gmail (16 caracteres)")
    elif email_choice == "2":
        config['EMAIL_HOST'] = "smtp.sendgrid.net"
        config['EMAIL_PORT'] = "587"
        config['EMAIL_USE_TLS'] = "True"
        config['EMAIL_HOST_USER'] = "apikey"
        
        print(f"\n{BLUE}📋 Para obtener SendGrid API Key:{END}")
        print(f"{BLUE}1. Regístrate en: https://sendgrid.com{END}")
        print(f"{BLUE}2. Ve a Settings > API Keys{END}")
        print(f"{BLUE}3. Crea nueva API Key (Full Access){END}\n")
        
        config['EMAIL_HOST_PASSWORD'] = ask_question("SendGrid API Key (empieza con SG.)")
    else:
        config['EMAIL_HOST'] = ask_question("SMTP Host")
        config['EMAIL_PORT'] = ask_question("SMTP Port", "587")
        config['EMAIL_USE_TLS'] = "True" if ask_yes_no("¿Usar TLS?") else "False"
        config['EMAIL_HOST_USER'] = ask_question("Email usuario")
        config['EMAIL_HOST_PASSWORD'] = ask_question("Email password")
    
    print(f"{GREEN}✓ Email configurado{END}")
    
    # =========================================================================
    # PASO 4: reCAPTCHA
    # =========================================================================
    print_step(4, "Configurar Google reCAPTCHA")
    
    if ask_yes_no("¿Ya tienes claves de reCAPTCHA?", "n"):
        config['RECAPTCHA_PUBLIC_KEY'] = ask_question("reCAPTCHA Site Key (pública)")
        config['RECAPTCHA_PRIVATE_KEY'] = ask_question("reCAPTCHA Secret Key (privada)")
    else:
        print(f"\n{BLUE}📋 Para obtener claves de reCAPTCHA:{END}")
        print(f"{BLUE}1. Ve a: https://www.google.com/recaptcha/admin/create{END}")
        print(f"{BLUE}2. Tipo: reCAPTCHA v2 > 'No soy un robot'{END}")
        print(f"{BLUE}3. Dominio: {config.get('ALLOWED_HOSTS', 'tu-dominio.com').split(',')[0]}{END}")
        print(f"{BLUE}4. Copia ambas claves{END}\n")
        
        if ask_yes_no("¿Abrir el link en el navegador ahora?"):
            import webbrowser
            webbrowser.open("https://www.google.com/recaptcha/admin/create")
        
        print(f"\n{YELLOW}Presiona Enter cuando hayas obtenido las claves...{END}")
        input()
        
        config['RECAPTCHA_PUBLIC_KEY'] = ask_question("reCAPTCHA Site Key")
        config['RECAPTCHA_PRIVATE_KEY'] = ask_question("reCAPTCHA Secret Key")
    
    print(f"{GREEN}✓ reCAPTCHA configurado{END}")
    
    # =========================================================================
    # PASO 5: SSL/HTTPS
    # =========================================================================
    print_step(5, "Configurar SSL/HTTPS")
    
    if hosting_choice in ["1", "2"]:
        print(f"{BLUE}ℹ️  Railway/Render configuran SSL automáticamente.{END}")
        config['SECURE_SSL_REDIRECT'] = "True"
        config['SESSION_COOKIE_SECURE'] = "True"
        config['CSRF_COOKIE_SECURE'] = "True"
        config['SECURE_HSTS_SECONDS'] = "31536000"
        print(f"{GREEN}✓ SSL configurado (automático){END}")
    else:
        if ask_yes_no("¿Ya tienes certificado SSL instalado?", "n"):
            config['SECURE_SSL_REDIRECT'] = "True"
            config['SESSION_COOKIE_SECURE'] = "True"
            config['CSRF_COOKIE_SECURE'] = "True"
            config['SECURE_HSTS_SECONDS'] = "31536000"
            print(f"{GREEN}✓ SSL activado{END}")
        else:
            config['SECURE_SSL_REDIRECT'] = "False"
            config['SESSION_COOKIE_SECURE'] = "False"
            config['CSRF_COOKIE_SECURE'] = "False"
            config['SECURE_HSTS_SECONDS'] = "0"
            print(f"{YELLOW}⚠️  SSL desactivado (activar después de instalar certificado){END}")
            print(f"{YELLOW}   Ver: docs/SSL_SETUP.md para instrucciones{END}")
    
    # =========================================================================
    # GENERAR ARCHIVO
    # =========================================================================
    print_step(6, "Generar archivo .env.production")
    
    env_path = Path(__file__).parent / 'entorno' / '.env.production'
    
    print(f"\n{BOLD}Resumen de configuración:{END}")
    print("-" * 70)
    for key, value in config.items():
        # Ocultar passwords
        if 'PASSWORD' in key or 'SECRET' in key or 'KEY' in key:
            display_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
        else:
            display_value = value
        print(f"{key:30} = {display_value}")
    print("-" * 70)
    
    if ask_yes_no("\n¿Guardar esta configuración?"):
        # Leer archivo actual
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Actualizar valores
            new_lines = []
            for line in lines:
                written = False
                for key, value in config.items():
                    if line.strip().startswith(f"{key}="):
                        new_lines.append(f"{key}={value}\n")
                        written = True
                        break
                if not written:
                    new_lines.append(line)
            
            # Escribir archivo
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"\n{GREEN}✅ Archivo .env.production actualizado exitosamente!{END}")
            print(f"{GREEN}   Ubicación: {env_path}{END}")
            
            # Verificar
            print(f"\n{BOLD}Próximo paso:{END}")
            print(f"python verificar_produccion.py")
        else:
            print(f"{YELLOW}⚠️  Archivo .env.production no encontrado en: {env_path}{END}")
    else:
        print(f"\n{YELLOW}Configuración no guardada. Copia estos valores manualmente:{END}\n")
        for key, value in config.items():
            print(f"{key}={value}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Configuración cancelada{END}")
        sys.exit(0)
