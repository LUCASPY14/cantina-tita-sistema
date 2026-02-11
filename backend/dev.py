#!/usr/bin/env python
"""Script de desarrollo para backend."""
import os
import sys
import subprocess

def main():
    """Ejecutar comandos de desarrollo."""
    if len(sys.argv) < 2:
        print("Uso: python dev.py [comando]")
        print("Comandos disponibles:")
        print("  runserver  - Ejecutar servidor de desarrollo")
        print("  migrate    - Ejecutar migraciones")
        print("  shell      - Abrir shell de Django")
        print("  test       - Ejecutar tests")
        print("  makemigrations - Crear migraciones")
        return
    
    comando = sys.argv[1]
    
    if comando == "runserver":
        subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8000"])
    elif comando == "migrate":
        subprocess.run(["python", "manage.py", "migrate"])
    elif comando == "shell":
        subprocess.run(["python", "manage.py", "shell"])
    elif comando == "test":
        subprocess.run(["python", "manage.py", "test"])
    elif comando == "makemigrations":
        subprocess.run(["python", "manage.py", "makemigrations"])
    else:
        print(f"Comando desconocido: {comando}")

if __name__ == "__main__":
    main()