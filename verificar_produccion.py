#!/usr/bin/env python3
"""
Script de Verificación Pre-Deployment
======================================

Verifica que todas las configuraciones críticas estén listas antes de desplegar a producción.

Uso:
    python verificar_produccion.py
    python verificar_produccion.py --env entorno/.env.production
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def load_env_file(env_path: Path) -> Dict[str, str]:
    """Cargar variables del archivo .env"""
    env_vars = {}
    
    if not env_path.exists():
        print_error(f"Archivo no encontrado: {env_path}")
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('#'):
                continue
            
            # Parsear variable=valor
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def check_secret_key(value: str) -> Tuple[bool, str]:
    """Verificar SECRET_KEY"""
    if not value:
        return False, "SECRET_KEY no está configurada"
    
    if len(value) < 50:
        return False, f"SECRET_KEY muy corta ({len(value)} chars, mínimo 50)"
    
    if value.startswith('django-insecure-'):
        return False, "Usando SECRET_KEY insegura generada por Django"
    
    # Verificar variedad de caracteres
    unique_chars = len(set(value))
    if unique_chars < 20:
        return False, f"SECRET_KEY con poca variedad ({unique_chars} chars únicos)"
    
    return True, f"SECRET_KEY segura ({len(value)} chars, {unique_chars} únicos)"

def check_debug(value: str) -> Tuple[bool, str]:
    """Verificar DEBUG"""
    if value.lower() in ['false', '0', 'no']:
        return True, "DEBUG=False (correcto para producción)"
    
    return False, f"DEBUG={value} (DEBE ser False en producción)"

def check_allowed_hosts(value: str) -> Tuple[bool, str]:
    """Verificar ALLOWED_HOSTS"""
    if not value:
        return False, "ALLOWED_HOSTS vacío"
    
    hosts = [h.strip() for h in value.split(',')]
    
    # Verificar que no sean solo localhost
    if all(h in ['localhost', '127.0.0.1', 'testserver'] for h in hosts):
        return False, "ALLOWED_HOSTS solo tiene valores de desarrollo (localhost, 127.0.0.1)"
    
    # Verificar que haya al menos un dominio o IP real
    has_real_host = any(
        h not in ['localhost', '127.0.0.1', 'testserver'] and h 
        for h in hosts
    )
    
    if not has_real_host:
        return False, "No hay dominios/IPs de producción en ALLOWED_HOSTS"
    
    return True, f"ALLOWED_HOSTS configurado con {len(hosts)} host(s): {', '.join(hosts[:3])}"

def check_ssl_config(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Verificar configuración SSL"""
    ssl_redirect = env_vars.get('SECURE_SSL_REDIRECT', 'False')
    session_secure = env_vars.get('SESSION_COOKIE_SECURE', 'False')
    csrf_secure = env_vars.get('CSRF_COOKIE_SECURE', 'False')
    hsts = env_vars.get('SECURE_HSTS_SECONDS', '0')
    
    ssl_enabled = ssl_redirect.lower() in ['true', '1', 'yes']
    
    if not ssl_enabled:
        return False, "SSL/HTTPS desactivado (activar cuando tengas certificado)"
    
    issues = []
    if session_secure.lower() not in ['true', '1', 'yes']:
        issues.append("SESSION_COOKIE_SECURE=False")
    if csrf_secure.lower() not in ['true', '1', 'yes']:
        issues.append("CSRF_COOKIE_SECURE=False")
    if int(hsts) < 31536000:
        issues.append(f"SECURE_HSTS_SECONDS={hsts} (debería ser 31536000)")
    
    if issues:
        return False, f"SSL parcialmente configurado: {', '.join(issues)}"
    
    return True, "SSL completamente configurado"

def check_database(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Verificar configuración de base de datos"""
    db_password = env_vars.get('DB_PASSWORD', '')
    db_user = env_vars.get('DB_USER', '')
    
    issues = []
    
    if not db_password:
        issues.append("DB_PASSWORD vacío")
    elif 'TU_PASSWORD' in db_password or 'AQUI' in db_password:
        issues.append("DB_PASSWORD es un placeholder")
    elif len(db_password) < 12:
        issues.append(f"DB_PASSWORD débil ({len(db_password)} chars)")
    
    if db_user == 'root':
        issues.append("Usando usuario 'root' (crear usuario específico)")
    
    if issues:
        return False, '; '.join(issues)
    
    return True, f"Base de datos configurada (usuario: {db_user})"

def check_email(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Verificar configuración de email"""
    email_password = env_vars.get('EMAIL_HOST_PASSWORD', '')
    email_user = env_vars.get('EMAIL_HOST_USER', '')
    
    if not email_user:
        return False, "EMAIL_HOST_USER no configurado"
    
    if not email_password:
        return False, "EMAIL_HOST_PASSWORD no configurado"
    
    if 'tu_app_password' in email_password.lower() or 'aqui' in email_password.lower():
        return False, "EMAIL_HOST_PASSWORD es un placeholder"
    
    # Verificar que sea App Password de Gmail (16 chars) o API key de SendGrid
    if len(email_password) < 16:
        return False, f"EMAIL_HOST_PASSWORD muy corto ({len(email_password)} chars)"
    
    return True, f"Email configurado ({email_user})"

def check_recaptcha(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Verificar reCAPTCHA"""
    public_key = env_vars.get('RECAPTCHA_PUBLIC_KEY', '')
    private_key = env_vars.get('RECAPTCHA_PRIVATE_KEY', '')
    
    # Claves de prueba de Google (solo funcionan en localhost)
    test_keys = ['6LeIxAcTAAAAAA', 'tu_clave', 'aqui']
    
    issues = []
    
    if not public_key:
        issues.append("RECAPTCHA_PUBLIC_KEY vacía")
    elif any(test in public_key for test in test_keys):
        issues.append("Usando claves de TEST (solo funcionan en localhost)")
    
    if not private_key:
        issues.append("RECAPTCHA_PRIVATE_KEY vacía")
    
    if issues:
        return False, '; '.join(issues)
    
    return True, "reCAPTCHA configurado con claves de producción"

def check_file_structure() -> Tuple[bool, List[str]]:
    """Verificar estructura de archivos necesarios"""
    base_dir = Path(__file__).resolve().parent
    
    required_files = [
        'backend/manage.py',
        'backend/cantina_project/settings.py',
        'backend/cantina_project/wsgi.py',
        'gunicorn_config.py',
        'backend/requirements.txt',
    ]
    
    missing = []
    for file_path in required_files:
        if not (base_dir / file_path).exists():
            missing.append(file_path)
    
    return len(missing) == 0, missing

def main():
    print_header("VERIFICACIÓN PRE-DEPLOYMENT - CANTINA TITA")
    
    # Determinar ruta del .env
    if len(sys.argv) > 2 and sys.argv[1] == '--env':
        env_path = Path(sys.argv[2])
    else:
        env_path = Path(__file__).parent / 'entorno' / '.env.production'
    
    print(f"📄 Verificando: {env_path}\n")
    
    # Cargar variables
    env_vars = load_env_file(env_path)
    
    if not env_vars:
        print_error("No se pudieron cargar variables del archivo .env")
        sys.exit(1)
    
    # Contadores
    total_checks = 0
    passed_checks = 0
    critical_failures = 0
    warnings = 0
    
    # Verificaciones
    checks = [
        ("SECRET_KEY", lambda: check_secret_key(env_vars.get('SECRET_KEY', '')), True),
        ("DEBUG", lambda: check_debug(env_vars.get('DEBUG', 'True')), True),
        ("ALLOWED_HOSTS", lambda: check_allowed_hosts(env_vars.get('ALLOWED_HOSTS', '')), True),
        ("Base de Datos", lambda: check_database(env_vars), True),
        ("Email/SMTP", lambda: check_email(env_vars), True),
        ("reCAPTCHA", lambda: check_recaptcha(env_vars), False),  # No crítico
        ("SSL/HTTPS", lambda: check_ssl_config(env_vars), False),  # No crítico si no tienes certificado
    ]
    
    for name, check_func, is_critical in checks:
        total_checks += 1
        success, message = check_func()
        
        if success:
            print_success(f"{name}: {message}")
            passed_checks += 1
        else:
            if is_critical:
                print_error(f"{name}: {message}")
                critical_failures += 1
            else:
                print_warning(f"{name}: {message}")
                warnings += 1
    
    # Verificar estructura de archivos
    print("\n" + "─" * 70)
    structure_ok, missing_files = check_file_structure()
    if structure_ok:
        print_success(f"Estructura de archivos: Todos los archivos necesarios presentes")
        passed_checks += 1
    else:
        print_error(f"Estructura de archivos: Faltan {len(missing_files)} archivo(s)")
        for f in missing_files:
            print(f"  - {f}")
        critical_failures += 1
    total_checks += 1
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    print(f"Total de verificaciones: {total_checks}")
    print(f"{Colors.GREEN}✓ Exitosas: {passed_checks}{Colors.END}")
    
    if critical_failures > 0:
        print(f"{Colors.RED}✗ Críticas fallidas: {critical_failures}{Colors.END}")
    
    if warnings > 0:
        print(f"{Colors.YELLOW}⚠ Advertencias: {warnings}{Colors.END}")
    
    print("\n" + "─" * 70 + "\n")
    
    # Veredicto final
    if critical_failures > 0:
        print_error("❌ NO LISTO PARA PRODUCCIÓN")
        print(f"\n{Colors.BOLD}Acción requerida:{Colors.END}")
        print("  1. Corregir las verificaciones críticas fallidas")
        print("  2. Ejecutar este script nuevamente")
        print("  3. Cuando todas las verificaciones pasen, proceder con deployment\n")
        sys.exit(1)
    elif warnings > 0:
        print_warning("⚠️  LISTO CON ADVERTENCIAS")
        print(f"\n{Colors.BOLD}Recomendaciones:{Colors.END}")
        print("  - Las advertencias no bloquean el deployment")
        print("  - SSL se puede activar después de instalar certificado")
        print("  - reCAPTCHA se puede configurar después del deploy inicial\n")
        sys.exit(0)
    else:
        print_success("✅ LISTO PARA PRODUCCIÓN")
        print(f"\n{Colors.BOLD}Siguiente paso:{Colors.END}")
        print("  → Ejecutar deployment según tu método elegido")
        print("  → Ver: docs/DEPLOYMENT_GUIDE.md\n")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verificación cancelada por usuario{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
