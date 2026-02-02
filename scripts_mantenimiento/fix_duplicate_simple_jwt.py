import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
SETTINGS_FILE = BASE_DIR / "cantina_project" / "settings.py"

def fix_duplicate_simple_jwt():
    """Elimina la definición duplicada y mal cerrada de SIMPLE_JWT"""
    
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Hacer backup
    backup_file = SETTINGS_FILE.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✓ Backup creado: {backup_file}")
    
    # Encontrar la primera definición (línea 94 aproximadamente)
    first_start = None
    first_end = None
    
    for i, line in enumerate(lines):
        # Primera definición (alrededor de línea 94)
        if 'SIMPLE_JWT = {' in line and i < 150:
            first_start = i
            print(f"✓ Primera definición SIMPLE_JWT encontrada en línea {i+1}")
            break
    
    if first_start is None:
        print("✗ No se encontró la primera definición de SIMPLE_JWT")
        return False
    
    # Buscar el cierre erróneo con las líneas extra
    for i in range(first_start, min(first_start + 40, len(lines))):
        if lines[i].strip() == ']' and i > first_start + 25:
            first_end = i
            print(f"✓ Fin de primera definición (con error) en línea {i+1}")
            break
    
    if first_end is None:
        print("⚠ No se encontró el fin de la primera definición")
        return False
    
    # Encontrar la segunda definición (correcta)
    second_start = None
    for i in range(first_end, len(lines)):
        if 'SIMPLE_JWT = {' in lines[i] and i > first_end:
            second_start = i
            print(f"✓ Segunda definición SIMPLE_JWT encontrada en línea {i+1}")
            break
    
    # Eliminar la primera definición (con el error)
    print(f"\n❌ Eliminando líneas {first_start+1} a {first_end+1} (primera definición con error)")
    
    # Mantener la segunda definición (que está bien)
    new_lines = lines[:first_start] + lines[first_end+1:]
    
    # Guardar
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✓ Primera definición duplicada eliminada")
    print("✓ Segunda definición (correcta) mantenida")
    
    return True

def verify_fix():
    """Verifica que la corrección sea correcta"""
    
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Contar cuántas veces aparece SIMPLE_JWT
    count = content.count('SIMPLE_JWT = {')
    
    if count == 1:
        print("✅ CORRECTO: Solo hay UNA definición de SIMPLE_JWT")
        return True
    elif count == 0:
        print("⚠ ADVERTENCIA: No hay definiciones de SIMPLE_JWT")
        return False
    else:
        print(f"❌ ERROR: Aún hay {count} definiciones de SIMPLE_JWT")
        return False

def main():
    print("=== CORRIGIENDO DEFINICIÓN DUPLICADA DE SIMPLE_JWT ===")
    
    # 1. Corregir
    if fix_duplicate_simple_jwt():
        # 2. Verificar
        print("\n📋 Verificando corrección...")
        if verify_fix():
            print("\n✅ Corrección exitosa")
            print("\n🔧 Prueba ahora con:")
            print("   python manage.py check")
            print("   python -m py_compile cantina_project/settings.py")
        else:
            print("\n⚠ La verificación falló. Revisa manualmente.")
    else:
        print("\n❌ No se pudo corregir automáticamente")

if __name__ == '__main__':
    main()
