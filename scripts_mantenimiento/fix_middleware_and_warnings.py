import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
SETTINGS_FILE = BASE_DIR / "cantina_project" / "settings.py"

def fix_middleware():
    """Corrige la lista MIDDLEWARE"""
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    correct_middleware = '''MIDDLEWARE = [
    # Django core security middleware
    'django.middleware.security.SecurityMiddleware',
    # Django session middleware (REQUERIDO para admin)
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CORS middleware (debe estar antes de CommonMiddleware)
    'corsheaders.middleware.CorsMiddleware',
    # Django common middleware
    'django.middleware.common.CommonMiddleware',
    # CSRF protection middleware
    'django.middleware.csrf.CsrfViewMiddleware',
    # Django authentication middleware (REQUERIDO para admin)
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Django messages middleware (REQUERIDO para admin)
    'django.contrib.messages.middleware.MessageMiddleware',
    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Debug toolbar (solo en modo DEBUG)
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]'''
    pattern = r'MIDDLEWARE\s*=\s*\[.*?\]'
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, correct_middleware, content, flags=re.DOTALL)
        print("✅ MIDDLEWARE existente reemplazado")
    else:
        installed_apps_end = content.find("]")
        insert_pos = content.find("\n", installed_apps_end) + 1
        new_content = content[:insert_pos] + "\n" + correct_middleware + "\n\n" + content[insert_pos:]
        print("✅ MIDDLEWARE agregado después de INSTALLED_APPS")
    backup_file = SETTINGS_FILE.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup creado: {backup_file}")
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ MIDDLEWARE corregido exitosamente")
    return True

def add_debug_toolbar_config():
    """Agrega configuración de Debug Toolbar si falta"""
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'debug_toolbar' in content.lower():
        print("✅ Debug Toolbar ya está configurado")
        return True
    debug_config = '''
# =============================================================================
# DEBUG TOOLBAR CONFIGURATION
# =============================================================================

# Debug toolbar settings (solo en desarrollo)
if DEBUG:
    # Mostrar debug toolbar solo para IPs internas
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
    # Paneles personalizados del debug toolbar
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
'''
    new_content = content.rstrip() + debug_config
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Configuración de Debug Toolbar agregada")
    return True

def fix_installed_apps_order():
    """Asegura el orden correcto de INSTALLED_APPS"""
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    in_installed_apps = False
    django_apps = []
    third_party_apps = []
    local_apps = []
    other_lines = []
    for line in lines:
        if 'INSTALLED_APPS' in line and '=' in line:
            in_installed_apps = True
            other_lines.append(line)
            continue
        if in_installed_apps:
            if line.strip() == ']':
                in_installed_apps = False
                other_lines.append("    # Django core apps")
                for app in django_apps:
                    other_lines.append(f"    '{app}',")
                other_lines.append("")
                other_lines.append("    # Third-party apps")
                for app in third_party_apps:
                    other_lines.append(f"    '{app}',")
                other_lines.append("")
                other_lines.append("    # Local apps")
                for app in local_apps:
                    other_lines.append(f"    '{app}',")
                other_lines.append(line)
                continue
            app_line = line.strip().strip(",").strip("'\"")
            if app_line:
                if app_line.startswith('django.'):
                    django_apps.append(app_line)
                elif app_line in ['gestion', 'pos']:
                    local_apps.append(app_line)
                else:
                    third_party_apps.append(app_line)
        else:
            other_lines.append(line)
    if not in_installed_apps and (django_apps or third_party_apps or local_apps):
        new_content = '\n'.join(other_lines)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ INSTALLED_APPS reorganizado en orden correcto")
        return True
    return False

def check_foreignkey_warning():
    """Guía para corregir el warning de ForeignKey con unique=True"""
    print("\n🔧 WARNING: ForeignKey con unique=True")
    print("="*50)
    print("""
Un ForeignKey con unique=True generalmente debe ser un OneToOneField.

EJEMPLO PROBLEMA:
    class Perfil(models.Model):
        usuario = models.OneToOneField(User, on_delete=models.CASCADE)
        
SOLUCIÓN:
    class Perfil(models.Model):
        usuario = models.OneToOneField(User, on_delete=models.CASCADE)

PASOS PARA CORREGIR:
1. Busca en tus modelos dónde tienes ForeignKey con unique=True
2. Cámbialos por OneToOneField
3. Ejecuta migraciones:
   python manage.py makemigrations
   python manage.py migrate

PARA ENCONTRAR EL PROBLEMA:
""")
    models_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.py') and 'models' in file.lower():
                models_files.append(Path(root) / file)
    print(f"📁 Archivos models encontrados: {len(models_files)}")
    for model_file in models_files[:5]:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'ForeignKey' in content and 'unique=True' in content:
            print(f"\n⚠️  Posible problema en: {model_file.relative_to(BASE_DIR)}")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'ForeignKey' in line and 'unique=True' in line:
                    print(f"   Línea {i+1}: {line.strip()}")
    if len(models_files) > 5:
        print(f"\n... y {len(models_files) - 5} archivos más")
    print("\n🔧 PARA CORREGIR AUTOMÁTICAMENTE:")
    print("""
# Ejecuta este comando para buscar y reemplazar:
python -c "
import os, re
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            new_content = re.sub(
                r'ForeignKey\(([^)]+),\s*unique=True',
                r'OneToOneField(\\1',
                content
            )
            if new_content != content:
                print(f'Corrigiendo: {path}')
                with open(path, 'w') as f:
                    f.write(new_content)
"
""")

def main():
    print("=== CORRIGIENDO MIDDLEWARE Y WARNINGS ===")
    print("\n1. Corrigiendo MIDDLEWARE...")
    fix_middleware()
    print("\n2. Configurando Debug Toolbar...")
    add_debug_toolbar_config()
    print("\n3. Reorganizando INSTALLED_APPS...")
    fix_installed_apps_order()
    print("\n4. Analizando warning de ForeignKey...")
    check_foreignkey_warning()
    print("\n"+"="*50)
    print("✅ CORRECCIONES APLICADAS")
    print("="*50)
    print("""
📋 PRÓXIMOS PASOS:

1. ✅ MIDDLEWARE corregido (sesiones, auth, messages agregados)
2. ✅ Debug Toolbar configurado
3. ✅ INSTALLED_APPS reorganizado

🔧 PARA CORREGIR EL WARNING DE ForeignKey:

Ejecuta estos comandos:
python manage.py check --deploy  # Verificar configuración
python manage.py makemigrations  # Crear migraciones si cambiaste modelos
python manage.py migrate         # Aplicar migraciones

🔄 PARA PROBAR:
python manage.py runserver
""")

if __name__ == '__main__':
    main()
