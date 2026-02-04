"""
Verificación Rápida de Validaciones (Pre-commit)
=================================================

Versión simplificada sin emojis para compatibilidad con Windows.
"""

import os
import sys

# Añadir el directorio backend al path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.core.exceptions import ValidationError
from gestion.models import Ventas


def test_validaciones():
    """Test rápido de validaciones"""
    errores = 0
    
    # Test 1: Saldo mayor a total
    try:
        venta = Ventas(monto_total=50000, saldo_pendiente=60000, estado_pago='PENDIENTE')
        venta.clean()
        print("ERROR: Validacion saldo > total no funciono")
        errores += 1
    except ValidationError:
        pass  # OK
    
    # Test 2: PAGADA con saldo
    try:
        venta = Ventas(monto_total=50000, saldo_pendiente=10000, estado_pago='PAGADA')
        venta.clean()
        print("ERROR: Validacion PAGADA con saldo no funciono")
        errores += 1
    except ValidationError:
        pass  # OK
    
    # Test 3: Venta válida
    try:
        venta = Ventas(monto_total=50000, saldo_pendiente=50000, estado_pago='PENDIENTE')
        venta.clean()
        # OK
    except ValidationError:
        print("ERROR: Venta valida rechazada")
        errores += 1
    
    if errores > 0:
        print(f"\n{errores} validaciones fallaron")
        return 1
    
    print("OK: Todas las validaciones pasaron")
    return 0


def main():
    """Ejecutar verificación"""
    return test_validaciones()


if __name__ == '__main__':
    sys.exit(main())
