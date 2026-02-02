"""
Auditoría de Seguridad - Cantina Tita
Verifica configuraciones de seguridad Django y mejores prácticas
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.conf import settings
from colorama import init, Fore, Style
import json
from datetime import datetime

init()

class AuditoriaSeguridad:
    """Audita configuraciones de seguridad"""
    
    def __init__(self):
        self.problemas_criticos = []
        self.warnings = []
        self.ok = []
    
    def print_header(self, texto):
        # Limpiar emojis Unicode para evitar problemas en Windows
        texto_limpio = texto.encode('ascii', 'ignore').decode('ascii')
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.WHITE}{texto_limpio}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    
    def verificar(self, nombre, condicion, mensaje_ok, mensaje_error, critico=False):
        """Verifica una condición de seguridad"""
        if condicion:
            print(f"{Fore.GREEN}[OK] {nombre}{Style.RESET_ALL}")
            print(f"   {mensaje_ok}")
            self.ok.append({'nombre': nombre, 'detalle': mensaje_ok})
        else:
            nivel = Fore.RED if critico else Fore.YELLOW
            icono = "[ERROR]" if critico else "[WARN]"
            print(f"{nivel}{icono} {nombre}{Style.RESET_ALL}")
            print(f"   {mensaje_error}")
            
            if critico:
                self.problemas_criticos.append({'nombre': nombre, 'detalle': mensaje_error})
            else:
                self.warnings.append({'nombre': nombre, 'detalle': mensaje_error})
        print()
    
    def auditoria_debug(self):
        """Audita configuración de DEBUG"""
        self.print_header("🔍 VERIFICACIÓN: DEBUG MODE")
        
        self.verificar(
            "DEBUG desactivado en producción",
            not settings.DEBUG,
            "DEBUG=False - Correcto para producción",
            "DEBUG=True - PELIGRO: Nunca usar en producción. Expone información sensible.",
            critico=True
        )
    
    def auditoria_secret_key(self):
        """Audita SECRET_KEY"""
        self.print_header("🔐 VERIFICACIÓN: SECRET_KEY")
        
        # Verificar que SECRET_KEY no esté vacía
        self.verificar(
            "SECRET_KEY configurada",
            bool(settings.SECRET_KEY),
            "SECRET_KEY está configurada",
            "SECRET_KEY vacía o no configurada",
            critico=True
        )
        
        # Verificar longitud
        self.verificar(
            "SECRET_KEY longitud adecuada",
            len(settings.SECRET_KEY) >= 50,
            f"Longitud: {len(settings.SECRET_KEY)} caracteres (recomendado: 50+)",
            f"Longitud insuficiente: {len(settings.SECRET_KEY)} caracteres. Recomendado: 50+",
            critico=False
        )
        
        # Verificar que no sea la clave por defecto de Django
        claves_inseguras = [
            'django-insecure-',
            'changeme',
            'secret',
            '1234567890'
        ]
        
        clave_segura = not any(unsafe in settings.SECRET_KEY.lower() for unsafe in claves_inseguras)
        
        self.verificar(
            "SECRET_KEY es única y segura",
            clave_segura,
            "SECRET_KEY no contiene valores comunes inseguros",
            "SECRET_KEY contiene valores inseguros o por defecto",
            critico=True
        )
    
    def auditoria_allowed_hosts(self):
        """Audita ALLOWED_HOSTS"""
        self.print_header("🌐 VERIFICACIÓN: ALLOWED_HOSTS")
        
        self.verificar(
            "ALLOWED_HOSTS configurado",
            len(settings.ALLOWED_HOSTS) > 0 and settings.ALLOWED_HOSTS != ['*'],
            f"Hosts permitidos: {', '.join(settings.ALLOWED_HOSTS)}",
            "ALLOWED_HOSTS vacío o con wildcard '*' (inseguro en producción)",
            critico=False
        )
        
        # Verificar si tiene wildcard
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            print(f"{Fore.RED}   ⚠️  PELIGRO: Wildcard '*' permite cualquier host{Style.RESET_ALL}\n")
    
    def auditoria_https(self):
        """Audita configuraciones HTTPS"""
        self.print_header("🔒 VERIFICACIÓN: HTTPS/SSL")
        
        # SECURE_SSL_REDIRECT
        self.verificar(
            "SECURE_SSL_REDIRECT",
            getattr(settings, 'SECURE_SSL_REDIRECT', False),
            "Redirige HTTP a HTTPS automáticamente",
            "No redirige a HTTPS. Recomendado: SECURE_SSL_REDIRECT=True en producción",
            critico=False
        )
        
        # SESSION_COOKIE_SECURE
        self.verificar(
            "SESSION_COOKIE_SECURE",
            getattr(settings, 'SESSION_COOKIE_SECURE', False),
            "Cookies de sesión solo por HTTPS",
            "Cookies de sesión pueden enviarse por HTTP. Recomendado: SESSION_COOKIE_SECURE=True",
            critico=False
        )
        
        # CSRF_COOKIE_SECURE
        self.verificar(
            "CSRF_COOKIE_SECURE",
            getattr(settings, 'CSRF_COOKIE_SECURE', False),
            "Cookies CSRF solo por HTTPS",
            "Cookies CSRF pueden enviarse por HTTP. Recomendado: CSRF_COOKIE_SECURE=True",
            critico=False
        )
        
        # SECURE_HSTS_SECONDS
        hsts_seconds = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
        self.verificar(
            "SECURE_HSTS_SECONDS",
            hsts_seconds >= 31536000,  # 1 año
            f"HSTS configurado: {hsts_seconds} segundos",
            f"HSTS no configurado o muy corto ({hsts_seconds}s). Recomendado: 31536000 (1 año)",
            critico=False
        )
        
        # SECURE_HSTS_INCLUDE_SUBDOMAINS
        self.verificar(
            "SECURE_HSTS_INCLUDE_SUBDOMAINS",
            getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', False),
            "HSTS incluye subdominios",
            "HSTS no incluye subdominios. Recomendado: True",
            critico=False
        )
    
    def auditoria_database(self):
        """Audita configuración de base de datos"""
        self.print_header("🗄️  VERIFICACIÓN: BASE DE DATOS")
        
        db_config = settings.DATABASES['default']
        
        # Verificar que use MySQL en producción
        self.verificar(
            "Motor de base de datos",
            'mysql' in db_config['ENGINE'].lower(),
            f"Usando: {db_config['ENGINE']} (MySQL configurado correctamente)",
            "Se requiere MySQL como motor de base de datos",
            critico=False
        )
        
        # Verificar que no tenga credenciales por defecto
        password = db_config.get('PASSWORD', '')
        password_inseguro = password in ['', 'password', 'root', '1234', 'admin']
        
        self.verificar(
            "Contraseña de BD segura",
            not password_inseguro,
            "Contraseña de base de datos configurada",
            "Contraseña de BD vacía o insegura",
            critico=True
        )
    
    def auditoria_middleware(self):
        """Audita MIDDLEWARE de seguridad"""
        self.print_header("🛡️  VERIFICACIÓN: MIDDLEWARE DE SEGURIDAD")
        
        middleware_requeridos = {
            'django.middleware.security.SecurityMiddleware': 'Middleware de seguridad general',
            'django.middleware.csrf.CsrfViewMiddleware': 'Protección CSRF',
            'django.contrib.sessions.middleware.SessionMiddleware': 'Gestión de sesiones',
            'django.contrib.auth.middleware.AuthenticationMiddleware': 'Autenticación',
        }
        
        for middleware, descripcion in middleware_requeridos.items():
            self.verificar(
                descripcion,
                middleware in settings.MIDDLEWARE,
                f"✓ {middleware}",
                f"✗ Falta {middleware}",
                critico=True
            )
    
    def auditoria_csrf(self):
        """Audita protección CSRF"""
        self.print_header("🔰 VERIFICACIÓN: PROTECCIÓN CSRF")
        
        # CSRF_TRUSTED_ORIGINS
        csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        self.verificar(
            "CSRF_TRUSTED_ORIGINS configurado",
            len(csrf_origins) > 0 if not settings.DEBUG else True,
            f"Orígenes confiables: {', '.join(csrf_origins)}",
            "CSRF_TRUSTED_ORIGINS vacío. Necesario para POST desde frontend",
            critico=False
        )
    
    def auditoria_xss(self):
        """Audita protección XSS"""
        self.print_header("🚫 VERIFICACIÓN: PROTECCIÓN XSS")
        
        # SECURE_BROWSER_XSS_FILTER
        self.verificar(
            "SECURE_BROWSER_XSS_FILTER",
            getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
            "Filtro XSS del navegador activado",
            "Filtro XSS desactivado. Recomendado: True",
            critico=False
        )
        
        # SECURE_CONTENT_TYPE_NOSNIFF
        self.verificar(
            "SECURE_CONTENT_TYPE_NOSNIFF",
            getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
            "Protección Content-Type sniffing activada",
            "Content-Type sniffing no protegido. Recomendado: True",
            critico=False
        )
        
        # X_FRAME_OPTIONS
        self.verificar(
            "X_FRAME_OPTIONS",
            getattr(settings, 'X_FRAME_OPTIONS', None) in ['DENY', 'SAMEORIGIN'],
            f"Clickjacking protegido: {getattr(settings, 'X_FRAME_OPTIONS', 'DENY')}",
            "X_FRAME_OPTIONS no configurado. Recomendado: 'DENY' o 'SAMEORIGIN'",
            critico=False
        )
    
    def auditoria_password_validators(self):
        """Audita validadores de contraseña"""
        self.print_header("🔑 VERIFICACIÓN: VALIDACIÓN DE CONTRASEÑAS")
        
        validators = settings.AUTH_PASSWORD_VALIDATORS
        
        self.verificar(
            "Validadores de contraseña",
            len(validators) >= 3,
            f"Configurados {len(validators)} validadores",
            f"Solo {len(validators)} validadores. Recomendado: al menos 3",
            critico=False
        )
        
        validadores_recomendados = [
            'UserAttributeSimilarityValidator',
            'MinimumLengthValidator',
            'CommonPasswordValidator',
            'NumericPasswordValidator'
        ]
        
        for validador in validadores_recomendados:
            presente = any(validador in v['NAME'] for v in validators)
            nombre_corto = validador.replace('Validator', '')
            
            self.verificar(
                f"Validador: {nombre_corto}",
                presente,
                f"✓ {validador}",
                f"✗ Falta {validador}",
                critico=False
            )
    
    def auditoria_static_media(self):
        """Audita configuración de archivos estáticos"""
        self.print_header("📁 VERIFICACIÓN: ARCHIVOS ESTÁTICOS Y MEDIA")
        
        # STATIC_ROOT configurado
        self.verificar(
            "STATIC_ROOT configurado",
            hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT,
            f"STATIC_ROOT: {settings.STATIC_ROOT}",
            "STATIC_ROOT no configurado. Necesario para collectstatic",
            critico=False
        )
        
        # MEDIA_ROOT configurado
        self.verificar(
            "MEDIA_ROOT configurado",
            hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT,
            f"MEDIA_ROOT: {settings.MEDIA_ROOT}",
            "MEDIA_ROOT no configurado",
            critico=False
        )
    
    def generar_reporte(self):
        """Genera reporte final"""
        self.print_header("📊 REPORTE FINAL DE SEGURIDAD")
        
        total = len(self.ok) + len(self.warnings) + len(self.problemas_criticos)
        
        print(f"{Fore.WHITE}Total verificaciones: {total}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Correctas: {len(self.ok)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Warnings: {len(self.warnings)}{Style.RESET_ALL}")
        print(f"{Fore.RED}Críticos: {len(self.problemas_criticos)}{Style.RESET_ALL}")
        print()
        
        if self.problemas_criticos:
            print(f"{Fore.RED}[CRITICOS]:{Style.RESET_ALL}\n")
            for problema in self.problemas_criticos:
                print(f"   - {problema['nombre']}")
                print(f"     {problema['detalle']}")
                print()
        
        if self.warnings:
            print(f"{Fore.YELLOW}[WARNINGS]:{Style.RESET_ALL}\n")
            for warning in self.warnings:
                print(f"   - {warning['nombre']}")
                print(f"     {warning['detalle']}")
                print()
        
        # Guardar reporte
        reporte = {
            'fecha': datetime.now().isoformat(),
            'total': total,
            'correctas': len(self.ok),
            'warnings': len(self.warnings),
            'criticos': len(self.problemas_criticos),
            'ok_detalle': self.ok,
            'warnings_detalle': self.warnings,
            'criticos_detalle': self.problemas_criticos
        }
        
        ruta = f"logs/auditoria_seguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('logs', exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"{Fore.CYAN}💾 Reporte guardado: {ruta}{Style.RESET_ALL}")
        
        # Recomendaciones
        if self.problemas_criticos or self.warnings:
            print(f"\n{Fore.YELLOW}[RECOMENDACIONES PARA PRODUCCION]:{Style.RESET_ALL}\n")
            print("   1. DEBUG=False")
            print("   2. SECRET_KEY única y segura (50+ caracteres)")
            print("   3. ALLOWED_HOSTS con dominios específicos")
            print("   4. SECURE_SSL_REDIRECT=True")
            print("   5. SESSION_COOKIE_SECURE=True")
            print("   6. CSRF_COOKIE_SECURE=True")
            print("   7. SECURE_HSTS_SECONDS=31536000")
            print("   8. Contraseña de BD fuerte")
            print("   9. Todos los middleware de seguridad activados")
            print("   10. Validadores de contraseña configurados")
            print()


def main():
    """Ejecuta auditoría completa"""
    try:
        auditoria = AuditoriaSeguridad()
        
        # Ejecutar todas las verificaciones
        auditoria.auditoria_debug()
        auditoria.auditoria_secret_key()
        auditoria.auditoria_allowed_hosts()
        auditoria.auditoria_https()
        auditoria.auditoria_database()
        auditoria.auditoria_middleware()
        auditoria.auditoria_csrf()
        auditoria.auditoria_xss()
        auditoria.auditoria_password_validators()
        auditoria.auditoria_static_media()
        
        # Generar reporte
        auditoria.generar_reporte()
        
        # Retornar código de salida según resultados
        if auditoria.problemas_criticos:
            print(f"{Fore.RED}[ALERTA] Hay problemas criticos que deben resolverse antes de produccion{Style.RESET_ALL}\n")
            sys.exit(1)
        elif auditoria.warnings:
            print(f"{Fore.YELLOW}[INFO] Hay warnings que deberian resolverse para maxima seguridad{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            print(f"{Fore.GREEN}[OK] Todas las verificaciones de seguridad pasaron{Style.RESET_ALL}\n")
            sys.exit(0)
            
    except Exception as e:
        print(f"{Fore.RED}[ERROR FATAL]: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
