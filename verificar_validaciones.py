"""
Verificación de Validaciones del Sistema
=========================================

Este script verifica que las validaciones estén implementadas correctamente.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from decimal import Decimal
from django.core.exceptions import ValidationError
from gestion.models import Ventas, Compras


def test_validacion_saldo_mayor_a_total():
    """Test: Saldo no puede ser mayor al total"""
    print("\n📋 TEST 1: Validación saldo > total")
    
    # Crear instancia sin guardar
    venta = Ventas(
        monto_total=50000,
        saldo_pendiente=60000,  # ❌ Mayor al total
        estado_pago='PENDIENTE'
    )
    
    try:
        venta.clean()
        print("❌ FALLÓ: No lanzó ValidationError")
        return False
    except ValidationError as e:
        print(f"✅ PASÓ: Validación funcionó correctamente")
        print(f"   Mensaje: {e.message_dict.get('saldo_pendiente', [None])[0]}")
        return True


def test_validacion_pagada_con_saldo():
    """Test: PAGADA no puede tener saldo > 0"""
    print("\n📋 TEST 2: Validación PAGADA con saldo > 0")
    
    venta = Ventas(
        monto_total=50000,
        saldo_pendiente=10000,  # ❌ PAGADA con saldo
        estado_pago='PAGADA'
    )
    
    try:
        venta.clean()
        print("❌ FALLÓ: No lanzó ValidationError")
        return False
    except ValidationError as e:
        print(f"✅ PASÓ: Validación funcionó correctamente")
        print(f"   Mensaje: {e.message_dict.get('estado_pago', [None])[0]}")
        return True


def test_validacion_pendiente_saldo_diferente():
    """Test: PENDIENTE debe tener saldo == total"""
    print("\n📋 TEST 3: Validación PENDIENTE con saldo diferente al total")
    
    venta = Ventas(
        monto_total=50000,
        saldo_pendiente=30000,  # ❌ PENDIENTE pero saldo < total
        estado_pago='PENDIENTE'
    )
    
    try:
        venta.clean()
        print("❌ FALLÓ: No lanzó ValidationError")
        return False
    except ValidationError as e:
        print(f"✅ PASÓ: Validación funcionó correctamente")
        print(f"   Mensaje: {e.message_dict.get('estado_pago', [None])[0]}")
        return True


def test_venta_valida():
    """Test: Venta válida no debe lanzar error"""
    print("\n📋 TEST 4: Venta válida")
    
    venta = Ventas(
        monto_total=50000,
        saldo_pendiente=50000,  # ✅ Igual al total
        estado_pago='PENDIENTE'
    )
    
    try:
        venta.clean()
        print("✅ PASÓ: Venta válida aceptada")
        return True
    except ValidationError as e:
        print(f"❌ FALLÓ: Lanzó error inesperado: {e}")
        return False


def test_venta_pagada_valida():
    """Test: Venta PAGADA válida"""
    print("\n📋 TEST 5: Venta PAGADA válida (saldo = 0)")
    
    venta = Ventas(
        monto_total=50000,
        saldo_pendiente=0,  # ✅ PAGADA con saldo 0
        estado_pago='PAGADA'
    )
    
    try:
        venta.clean()
        print("✅ PASÓ: Venta PAGADA válida aceptada")
        return True
    except ValidationError as e:
        print(f"❌ FALLÓ: Lanzó error inesperado: {e}")
        return False


def verificar_metodo_clean_existe():
    """Verificar que el método clean() existe"""
    print("\n🔍 VERIFICACIÓN: Método clean() en modelo Ventas")
    
    if hasattr(Ventas, 'clean'):
        print("✅ Método clean() existe en Ventas")
        return True
    else:
        print("❌ Método clean() NO existe en Ventas")
        return False


def main():
    """Ejecutar todas las verificaciones"""
    print("="*60)
    print("🧪 VERIFICACIÓN DE VALIDACIONES - Sistema Cuenta Corriente")
    print("="*60)
    
    resultados = []
    
    # Verificar que el método existe
    resultados.append(verificar_metodo_clean_existe())
    
    # Ejecutar tests
    resultados.append(test_validacion_saldo_mayor_a_total())
    resultados.append(test_validacion_pagada_con_saldo())
    resultados.append(test_validacion_pendiente_saldo_diferente())
    resultados.append(test_venta_valida())
    resultados.append(test_venta_pagada_valida())
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    print(f"\n✅ Tests exitosos: {exitosos}/{total}")
    print(f"❌ Tests fallidos: {total - exitosos}/{total}")
    
    if exitosos == total:
        print("\n🎉 RESULTADO: ✅ TODAS LAS VALIDACIONES FUNCIONAN CORRECTAMENTE")
        return 0
    else:
        print("\n⚠️ RESULTADO: ❌ ALGUNAS VALIDACIONES FALLARON")
        return 1


if __name__ == '__main__':
    sys.exit(main())
