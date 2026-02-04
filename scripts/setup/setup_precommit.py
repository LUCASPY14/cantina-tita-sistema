"""
Script de Instalación de Pre-commit Hooks
==========================================

Instala y configura pre-commit hooks para el proyecto.
"""

import subprocess
import sys


def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}...")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {description} - OK")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - ERROR")
        if result.stderr:
            print(result.stderr)
        return False


def main():
    """Instalar pre-commit hooks"""
    print("="*70)
    print("🔧 INSTALACIÓN DE PRE-COMMIT HOOKS")
    print("="*70)
    
    # 1. Instalar pre-commit
    if not run_command("pip install pre-commit", "Instalando pre-commit"):
        print("\n⚠️ Error al instalar pre-commit")
        return 1
    
    # 2. Instalar hooks
    if not run_command("pre-commit install", "Instalando hooks de git"):
        print("\n⚠️ Error al instalar hooks")
        return 1
    
    # 3. Ejecutar primera vez (opcional)
    print("\n" + "="*70)
    print("🧪 EJECUTANDO VALIDACIONES INICIALES")
    print("="*70)
    
    run_command("pre-commit run --all-files", "Ejecutando todos los hooks")
    
    # Resumen
    print("\n" + "="*70)
    print("✅ PRE-COMMIT CONFIGURADO")
    print("="*70)
    
    print("\nAhora los hooks se ejecutarán automáticamente antes de cada commit.")
    print("\nComandos útiles:")
    print("  pre-commit run --all-files  # Ejecutar manualmente")
    print("  pre-commit run <hook-id>    # Ejecutar hook específico")
    print("  git commit --no-verify       # Saltar hooks (no recomendado)")
    
    print("\n🎉 INSTALACIÓN COMPLETADA")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
