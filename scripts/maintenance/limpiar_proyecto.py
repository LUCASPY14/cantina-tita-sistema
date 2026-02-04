import os
import shutil

# Definir las carpetas de destino
folders = {
    'documentacion': ['.md', '.txt', '.pdf', '.png', '.yml'],
    'scripts_db': ['.sql'],
    'scripts_mantenimiento': ['actualizar_', 'aplicar_', 'corregir_', 'fix_', 'verificar_', 'analizar_', 'check_', 'crear_'],
    'tests': ['test_'],
    'entorno': ['.env', '.env.example', '.env.production', '.env.whatsapp']
}

for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Mover archivos
for file in os.listdir('.'):
    if file in ['manage.py', 'requirements.txt', 'README.md', 'limpiar_proyecto.py', '.gitignore', '.git']:
        continue
    
    moved = False
    # 1. Por extensión
    name, ext = os.path.splitext(file)
    for folder, rules in folders.items():
        if ext in rules:
            shutil.move(file, os.path.join(folder, file))
            moved = True
            break
    
    # 2. Por prefijo (scripts y tests)
    if not moved:
        for folder, rules in folders.items():
            for prefix in rules:
                if file.startswith(prefix):
                    shutil.move(file, os.path.join(folder, file))
                    moved = True
                    break
            if moved: break

print("¡Proyecto organizado! Revisa las nuevas carpetas.")