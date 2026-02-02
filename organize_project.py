# organize_project.py
import os
import shutil
import re
from pathlib import Path

class ProjectOrganizer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.moved_files = []
        self.errors = []
        # ...existing code...

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Organizar proyecto Django')
    parser.add_argument('--path', default='.', help='Ruta del proyecto a organizar')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar cambios sin ejecutar')
    args = parser.parse_args()
    organizer = ProjectOrganizer(args.path)
    if args.dry_run:
        print("🔍 MODO SIMULACIÓN (dry-run)")
        print("\n📁 Estructura que se creará:")
        for folder in organizer.folders_to_create:
            print(f"  - {folder}/")
        print("\n📦 Archivos encontrados (ejemplo de organización):")
        sample_files = list(Path(args.path).glob("*"))
        for file in sample_files[:10]:  # Mostrar primeros 10
            if file.is_file():
                dest = organizer.get_destination(file.name)
                print(f"  - {file.name} → {dest}")
    else:
        confirm = input("¿Estás seguro de reorganizar el proyecto? (s/n): ")
        if confirm.lower() == 's':
            organizer.run()
        else:
            print("❌ Operación cancelada")
