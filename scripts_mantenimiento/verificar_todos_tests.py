#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar el estado de todos los tests del sistema"""

import subprocess
import sys
import re

tests = [
    'test_funcional_sistema.py',
    'test_modulo_compras.py',
    'test_modulo_clientes.py',
    'test_modulo_usuarios.py',
    'test_modulo_gestion_proveedores.py',
    'test_modulo_cta_cte_clientes.py',
    'test_modulo_categorias.py',
    'test_modulo_ventas_directas.py',
    'test_modulo_documentos.py',
    'test_modulo_cierres_caja.py',
    'test_modulo_almuerzos.py'
]

print("="*80)
print("VERIFICACION COMPLETA DE TESTS - CANTINA TITA".center(80))
print("="*80)

total_tests = 0
total_passed = 0
resultados = []

for test in tests:
    try:
        result = subprocess.run(
            [sys.executable, test],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        
        # Buscar patrón "Total: X/Y tests exitosos"
        match = re.search(r'Total:\s+(\d+)/(\d+)\s+tests?\s+exitosos?', output)
        
        if match:
            passed = int(match.group(1))
            total = int(match.group(2))
            total_passed += passed
            total_tests += total
            status = "OK " if passed == total else "FAIL"
            resultados.append((test, passed, total, status))
            print(f"{status} {test:45s} {passed:2d}/{total:2d} ({passed/total*100:5.1f}%)")
        else:
            resultados.append((test, 0, 0, "ERR"))
            print(f"ERR {test:45s}  Error de ejecucion")
            
    except subprocess.TimeoutExpired:
        resultados.append((test, 0, 0, "TIME"))
        print(f"TIME {test:45s}  Timeout")
    except Exception as e:
        resultados.append((test, 0, 0, "ERR"))
        print(f"ERR {test:45s}  {str(e)[:20]}")

print("="*80)
print(f"RESUMEN TOTAL: {total_passed}/{total_tests} tests pasaron ({total_passed/total_tests*100:.1f}%)".center(80))
print("="*80)

# Detalle por categoría
ok_tests = [r for r in resultados if r[3] == "OK "]
fail_tests = [r for r in resultados if r[3] == "FAIL"]
err_tests = [r for r in resultados if r[3] == "ERR"]

print(f"\nModulos 100% OK: {len(ok_tests)}")
if ok_tests:
    for t, p, tot, _ in ok_tests:
        print(f"  - {t}")

if fail_tests:
    print(f"\nModulos con fallas: {len(fail_tests)}")
    for t, p, tot, _ in fail_tests:
        print(f"  - {t}: {p}/{tot} tests")

if err_tests:
    print(f"\nModulos con errores: {len(err_tests)}")
    for t, _, _, _ in err_tests:
        print(f"  - {t}")
