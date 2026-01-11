# Script para corregir referencias a modelos en migraciones
# Problema: Django usa nombres de clases, no nombres de tablas

import re
import os

# Mapeo de referencias incorrectas a correctas
CORRECCIONES = {
    "to='gestion.ventas'": "to='gestion.Ventas'",
    "to='gestion.compras'": "to='gestion.Compras'",  
    "to='gestion.producto'": "to='gestion.Producto'",
    "to='gestion.productos'": "to='gestion.Producto'",
    "to='gestion.categoria'": "to='gestion.Categoria'",
    "to='gestion.categorias'": "to='gestion.Categoria'",
    "to='gestion.cliente'": "to='gestion.Cliente'",
    "to='gestion.clientes'": "to='gestion.Cliente'",
    "to='gestion.proveedor'": "to='gestion.Proveedor'",
    "to='gestion.proveedores'": "to='gestion.Proveedor'",
}

# Archivo a corregir
archivo = r"D:\anteproyecto20112025\gestion\migrations\0001_initial.py"

print(f"Corrigiendo {archivo}...")

with open(archivo, 'r', encoding='utf-8') as f:
    contenido = f.read()

cambios = 0
for incorrecto, correcto in CORRECCIONES.items():
    if incorrecto in contenido:
        count = contenido.count(incorrecto)
        contenido = contenido.replace(incorrecto, correcto)
        print(f"  ✓ {incorrecto} → {correcto} ({count} veces)")
        cambios += count

if cambios > 0:
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"\n✅ {cambios} correcciones aplicadas")
else:
    print("\n⊘ No se encontraron referencias para corregir")
