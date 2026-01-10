#!/usr/bin/env python
"""
Script de Limpieza de Código Legacy
Identifica archivos y funciones que pueden ser eliminadas
"""
import os
from pathlib import Path

print("\n" + "="*80)
print("ANALISIS DE CODIGO LEGACY - QUE PUEDE ELIMINARSE")
print("="*80)

print("\n[1] ARCHIVOS QUE PUEDEN ELIMINARSE")
print("-" * 80)

legacy_files = [
    {
        'archivo': 'gestion/pos_views.py',
        'tamanio': '206 KB',
        'razon': 'Contiene funciones antiguas (buscar_productos, procesar_venta legacy)',
        'estado': 'REEMPLAZADO POR pos_general_views.py',
        'puede_eliminar': True
    },
    {
        'archivo': 'templates/pos/venta.html',
        'tamanio': '42 KB',
        'razon': 'Interfaz antigua HTML puro sin Bootstrap',
        'estado': 'REEMPLAZADO POR pos_bootstrap.html',
        'puede_eliminar': True
    }
]

for item in legacy_files:
    estado = '[SEGURO ELIMINAR]' if item['puede_eliminar'] else '[REVISAR PRIMERO]'
    print(f"\n{estado} {item['archivo']}")
    print(f"    Tamanio: {item['tamanio']}")
    print(f"    Razon: {item['razon']}")
    print(f"    Estado: {item['estado']}")

print("\n\n[2] RUTAS QUE PUEDEN ELIMINARSE (en pos_urls.py)")
print("-" * 80)

legacy_routes = [
    {
        'ruta': "path('buscar-productos/', pos_views.buscar_productos)",
        'razon': 'HTMX legacy - Función buscar_producto_api() reemplaza',
        'puede_eliminar': True
    },
    {
        'ruta': "path('productos-categoria/', pos_views.productos_por_categoria)",
        'razon': 'HTMX legacy - No usado en interfaz Bootstrap',
        'puede_eliminar': True
    },
    {
        'ruta': "path('procesar-venta-legacy/', pos_views.procesar_venta)",
        'razon': 'Legacy - Función procesar_venta_api() reemplaza',
        'puede_eliminar': True
    },
    {
        'ruta': "path('ticket-legacy/<int:venta_id>/', pos_views.ticket_view)",
        'razon': 'Legacy - Función imprimir_ticket_venta() reemplaza',
        'puede_eliminar': True
    }
]

for item in legacy_routes:
    print(f"\n[SEGURO ELIMINAR] {item['ruta']}")
    print(f"    Razon: {item['razon']}")

print("\n\n[3] RESUMEN DE LIMPIEZA")
print("-" * 80)

print(f"""
Archivos que pueden eliminarse: 2
  - gestion/pos_views.py (206 KB)
  - templates/pos/venta.html (42 KB)
  Total: ~248 KB

Rutas que pueden eliminarse: 4
  - buscar-productos
  - productos-categoria
  - procesar-venta-legacy
  - ticket-legacy

Beneficio de la limpieza:
  - Código mas simple y mantenible
  - Elimina confusión de multiples implementaciones
  - Reduces tamanio del proyecto
  - Fuente unica de verdad: pos_general_views.py

Riesgo: BAJO (todas las funciones estan reemplazadas en pos_general_views.py)

Recomendacion: REALIZAR LIMPIEZA AHORA
""")

print("\n[4] PASOS PARA LIMPIAR (MANUAL)")
print("-" * 80)

print("""
1. Backup de archivos (opcional):
   cp gestion/pos_views.py gestion/pos_views.py.bak
   cp templates/pos/venta.html templates/pos/venta.html.bak

2. Eliminar archivos legacy:
   del gestion/pos_views.py
   del templates/pos/venta.html

3. Actualizar gestion/pos_urls.py:
   - Eliminar linea: from gestion import pos_views
   - Eliminar 4 rutas legacy
   
4. Verificar que no haya imports a pos_views:
   grep -r "from gestion import pos_views" .
   grep -r "import pos_views" .
   grep -r "from . import pos_views" .

5. Ejecutar test:
   python manage.py test

6. Ejecutar test_endpoints_completos.py para validar todos endpoints

7. Commit a git:
   git add -A
   git commit -m "refactor: eliminar codigo legacy de pos_views.py"
""")

print("\n" + "="*80 + "\n")
