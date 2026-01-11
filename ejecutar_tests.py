#!/usr/bin/env python
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
