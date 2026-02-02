import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

def find_and_fix_foreignkey():
    """Busca y corrige ForeignKey con unique=True"""
    print("🔍 Buscando ForeignKey con unique=True...")
    changes_made = False
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in ['venv', '.venv', '__pycache__', '.git', 'static', 'media']]
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                pattern = r'(\b)ForeignKey\(([^)]*),\s*unique\s*=\s*True([^)]*)\)'
                def replace_foreignkey(match):
                    before = match.group(1)
                    args = match.group(2)
                    after = match.group(3)
                    return f'{before}OneToOneField({args}{after})'
                new_content = re.sub(pattern, replace_foreignkey, content, flags=re.IGNORECASE)
                if new_content != content:
                    backup_file = filepath.with_suffix(filepath.suffix + '.backup')
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    relative_path = filepath.relative_to(BASE_DIR)
                    print(f"✅ Corregido: {relative_path}")
                    changes_made = True
    return changes_made

def main():
    print("=== CORRIGIENDO WARNING DE ForeignKey ===")
    if find_and_fix_foreignkey():
        print("\n✅ Cambios realizados. Ahora ejecuta:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
    else:
        print("\n✅ No se encontraron ForeignKey con unique=True")
        print("   El warning puede venir de una app de terceros")
    print("\n📋 Para verificar todos los warnings:")
    print("   python manage.py check --deploy")

if __name__ == '__main__':
    main()
