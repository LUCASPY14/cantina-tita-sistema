"""
Script de Cobertura de Código - Sistema de Cuenta Corriente
============================================================

Script para ejecutar tests con cobertura y generar reportes.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*70}")
    print(f"🔄 {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=False,
        text=True
    )
    
    return result.returncode == 0


def main():
    """Ejecutar suite de cobertura completa"""
    print("="*70)
    print("📊 COBERTURA DE CÓDIGO - Sistema de Cuenta Corriente")
    print("="*70)
    
    # 1. Instalar coverage si no está instalado
    print("\n🔍 Verificando coverage...")
    subprocess.run("pip install coverage", shell=True, capture_output=True)
    
    # 2. Limpiar cobertura anterior
    if run_command("coverage erase", "Limpiando datos de cobertura anterior"):
        print("✅ Limpieza exitosa")
    
    # 3. Ejecutar tests con cobertura
    success = run_command(
        "coverage run --source='gestion' manage.py test gestion --verbosity=2",
        "Ejecutando tests con cobertura"
    )
    
    if not success:
        print("\n❌ Error al ejecutar tests")
        return 1
    
    print("\n✅ Tests ejecutados exitosamente")
    
    # 4. Generar reporte en consola
    run_command(
        "coverage report -m",
        "Generando reporte de cobertura"
    )
    
    # 5. Generar reporte HTML
    if run_command("coverage html", "Generando reporte HTML"):
        print("\n✅ Reporte HTML generado en: htmlcov/index.html")
    
    # 6. Generar reporte XML (para CI/CD)
    if run_command("coverage xml", "Generando reporte XML"):
        print("✅ Reporte XML generado: coverage.xml")
    
    # 7. Verificar cobertura mínima
    print("\n" + "="*70)
    print("📊 VERIFICACIÓN DE COBERTURA MÍNIMA")
    print("="*70 + "\n")
    
    result = subprocess.run(
        "coverage report --fail-under=70",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Cobertura cumple con el mínimo requerido (70%)")
    else:
        print("⚠️ Cobertura por debajo del mínimo requerido (70%)")
        print("   Considera agregar más tests")
    
    # 8. Mostrar resumen
    print("\n" + "="*70)
    print("📋 RESUMEN DE ARCHIVOS")
    print("="*70 + "\n")
    
    print("Archivos generados:")
    print("  • htmlcov/index.html  - Reporte HTML interactivo")
    print("  • coverage.xml        - Reporte XML para CI/CD")
    print("  • .coverage           - Datos de cobertura")
    
    print("\nComandos útiles:")
    print("  coverage report       - Ver reporte en consola")
    print("  coverage html         - Regenerar HTML")
    print("  coverage erase        - Limpiar datos")
    
    print("\n" + "="*70)
    print("🎉 PROCESO COMPLETADO")
    print("="*70 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
