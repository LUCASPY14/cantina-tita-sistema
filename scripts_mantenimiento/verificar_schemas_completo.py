import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, r'D:\anteproyecto20112025')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')

import django
django.setup()

from django.db import connection

def describir_tabla(nombre_tabla):
    """Muestra la estructura de una tabla"""
    cursor = connection.cursor()
    cursor.execute(f"DESCRIBE {nombre_tabla}")
    columnas = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"TABLA: {nombre_tabla}")
    print(f"{'='*80}")
    print(f"{'Campo':<30} {'Tipo':<25} {'Null':<8} {'Key':<8} {'Default':<15}")
    print(f"{'-'*80}")
    
    for col in columnas:
        campo, tipo, null, key, default, extra = col
        default_str = str(default) if default else 'NULL'
        print(f"{campo:<30} {tipo:<25} {null:<8} {key:<8} {default_str:<15}")
    
    cursor.close()
    return columnas

def verificar_todas():
    """Verifica las 5 tablas problemáticas"""
    tablas = [
        'clientes',
        'alertas_sistema',
        'conciliacion_pagos',
        'tarifas_comision',
        'impuestos'
    ]
    
    resultados = {}
    for tabla in tablas:
        try:
            cols = describir_tabla(tabla)
            resultados[tabla] = [col[0] for col in cols]  # Solo nombres de columnas
        except Exception as e:
            print(f"\n[ERROR] {tabla}: {e}")
            resultados[tabla] = None
    
    # Resumen de columnas críticas
    print(f"\n\n{'='*80}")
    print("RESUMEN DE COLUMNAS CRÍTICAS")
    print(f"{'='*80}")
    
    print("\n1. CLIENTES - Campos de nombre:")
    if resultados.get('clientes'):
        campos_nombre = [c for c in resultados['clientes'] if 'nombre' in c.lower() or 'razon' in c.lower()]
        for campo in campos_nombre:
            print(f"   ✓ {campo}")
    
    print("\n2. ALERTAS_SISTEMA - Todos los campos:")
    if resultados.get('alertas_sistema'):
        for campo in resultados['alertas_sistema']:
            print(f"   ✓ {campo}")
    
    print("\n3. CONCILIACION_PAGOS - Todos los campos:")
    if resultados.get('conciliacion_pagos'):
        for campo in resultados['conciliacion_pagos']:
            print(f"   ✓ {campo}")
    
    print("\n4. TARIFAS_COMISION - Todos los campos:")
    if resultados.get('tarifas_comision'):
        for campo in resultados['tarifas_comision']:
            print(f"   ✓ {campo}")
    
    print("\n5. IMPUESTOS - Todos los campos:")
    if resultados.get('impuestos'):
        for campo in resultados['impuestos']:
            print(f"   ✓ {campo}")

if __name__ == '__main__':
    verificar_todas()
