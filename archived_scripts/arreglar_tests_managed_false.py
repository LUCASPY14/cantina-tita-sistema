"""
Script para arreglar el problema de managed=False en los tests
Solución: Cambiar temporalmente managed=True solo para tests

PROBLEMA:
- Django no crea tablas para modelos con managed=False en la base de datos de test
- Los tests fallan porque las tablas no existen

SOLUCIÓN:
- Detectar si estamos en modo test (settings.TESTING = True)
- Cambiar managed=True automáticamente para tests
- Mantener managed=False para producción
"""

import os
import sys
import re

def arreglar_models_para_tests():
    """Modificar gestion/models.py para que funcione en tests"""
    
    models_path = 'gestion/models.py'
    
    print("📝 ARREGLANDO MODELS.PY PARA TESTS...")
    print(f"   Archivo: {models_path}")
    
    # Leer archivo
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene la solución
    if 'import sys' in content and "'test' in sys.argv" in content:
        print("✅ El archivo ya tiene la solución aplicada")
        return
    
    # Encontrar los imports
    import_section = content.split('\n\n')[0]
    
    # Agregar import sys si no existe
    if 'import sys' not in import_section:
        lines = content.split('\n')
        # Encontrar última línea de imports
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                last_import_idx = i
        
        # Insertar import sys
        lines.insert(last_import_idx + 1, 'import sys')
        content = '\n'.join(lines)
    
    # Reemplazar todas las instancias de managed = False
    # con lógica condicional
    
    # Patrón para encontrar class Meta: ... managed = False
    pattern = r'(class Meta:\s*\n\s+db_table\s*=\s*[\'"][^\'"]+[\'"])\s*\n\s+managed\s*=\s*False'
    
    # Reemplazo con lógica condicional
    replacement = r"\1\n        managed = 'test' not in sys.argv"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print("⚠️  No se encontró el patrón esperado")
        print("   Aplicando solución alternativa...")
        
        # Solución alternativa: reemplazar directamente managed = False
        new_content = content.replace(
            'managed = False',
            "managed = 'test' not in sys.argv  # True para tests, False para producción"
        )
    
    # Guardar backup
    backup_path = 'gestion/models.py.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup creado: {backup_path}")
    
    # Guardar nuevo contenido
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Archivo modificado exitosamente")
    print("\n📋 CAMBIOS REALIZADOS:")
    print("   - Agregado: import sys")
    print("   - Cambiado: managed = False")
    print("   - Por: managed = 'test' not in sys.argv")
    print("\n🧪 AHORA PUEDES EJECUTAR:")
    print("   python manage.py test")
    
    return True


def crear_settings_test():
    """Crear configuración específica para tests"""
    
    settings_test_content = '''"""
Configuración específica para tests
"""
from .settings import *

# Indicar que estamos en modo test
TESTING = True

# Base de datos en memoria para tests rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_cantinatitadb',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Desactivar cache para tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Desactivar migraciones para tests más rápidos
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password hashers simples para tests rápidos
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desactivar debug para tests
DEBUG = False

# Email backend de consola para tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
'''
    
    settings_path = 'cantina_project/settings_test.py'
    
    if os.path.exists(settings_path):
        print(f"⚠️  {settings_path} ya existe, no se sobrescribirá")
        return
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(settings_test_content)
    
    print(f"✅ Creado: {settings_path}")
    print("\n🧪 Para usar esta configuración en tests:")
    print("   python manage.py test --settings=cantina_project.settings_test")


def crear_script_ejecutar_tests():
    """Crear script conveniente para ejecutar tests"""
    
    script_content = '''#!/usr/bin/env python
"""
Script para ejecutar tests con la configuración correcta
"""
import os
import sys
import subprocess

# Activar virtual environment si existe
venv_activate = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'activate')
if os.path.exists(venv_activate):
    print("🔧 Activando virtual environment...")

print("🧪 EJECUTANDO TESTS - CANTINA TITA")
print("=" * 60)

# Ejecutar tests
cmd = [
    sys.executable,
    'manage.py',
    'test',
    '--parallel=1',
    '--keepdb',  # Mantener DB de test entre ejecuciones (más rápido)
    '--no-input',
    '--verbosity=2'
]

# Agregar app específica si se pasó como argumento
if len(sys.argv) > 1:
    cmd.append(sys.argv[1])

print(f"📋 Comando: {' '.join(cmd)}")
print()

# Ejecutar
result = subprocess.run(cmd)

sys.exit(result.returncode)
'''
    
    script_path = 'ejecutar_tests.py'
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Creado: {script_path}")
    print("\n🧪 Para ejecutar tests:")
    print("   python ejecutar_tests.py")
    print("   python ejecutar_tests.py gestion.tests_portal_api")


if __name__ == '__main__':
    print("🔧 ARREGLANDO PROBLEMA DE TESTS CON managed=False")
    print("=" * 70)
    print()
    
    try:
        # 1. Arreglar models.py
        arreglar_models_para_tests()
        print()
        
        # 2. Crear settings de test
        print("\n" + "=" * 70)
        print("📝 CREANDO CONFIGURACIÓN DE TEST...")
        crear_settings_test()
        print()
        
        # 3. Crear script de tests
        print("\n" + "=" * 70)
        print("📝 CREANDO SCRIPT DE EJECUCIÓN...")
        crear_script_ejecutar_tests()
        print()
        
        print("\n" + "=" * 70)
        print("✅ TODO LISTO!")
        print()
        print("🔄 PRÓXIMOS PASOS:")
        print("   1. Revisar los cambios en gestion/models.py")
        print("   2. Ejecutar: python manage.py makemigrations")
        print("   3. Ejecutar: python manage.py migrate")
        print("   4. Ejecutar: python ejecutar_tests.py")
        print()
        print("⚠️  NOTA: Si algo sale mal, hay un backup en gestion/models.py.backup")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
