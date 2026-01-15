"""
Script para eliminar BOM (Byte Order Mark) de archivos Python
"""
import os

files_to_fix = [
    'gestion/admin.py',
    'gestion/models.py'
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Escribir sin BOM
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ {file_path} - BOM eliminado")
    else:
        print(f"✗ {file_path} - No encontrado")

print("\n✅ Archivos corregidos")
