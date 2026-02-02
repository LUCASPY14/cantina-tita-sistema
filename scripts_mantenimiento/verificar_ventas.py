#!/usr/bin/env python
"""
Script de Verificación: Estado de Ventas y Facturación
======================================================
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.insert(0, 'd:/anteproyecto20112025')
django.setup()

from gestion.models import Ventas, DatosFacturacionElect

print("\n" + "="*80)
print("VERIFICACIÓN: ESTADO DE VENTAS Y FACTURACIÓN")
print("="*80)

# Obtener últimas ventas
ventas_recientes = Ventas.objects.all().order_by('-id_venta')[:5]

print(f"\n📊 ÚLTIMAS 5 VENTAS:")
print("-" * 80)

for venta in ventas_recientes:
    print(f"\nVenta #{venta.id_venta}")
    print(f"  Cliente: {venta.id_cliente}")
    print(f"  Estudiante: {venta.id_hijo or 'N/A'}")
    print(f"  Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}")
    print(f"  Monto: ₲{venta.monto_total:,.0f}")
    print(f"  Productos: {venta.detalles.count()}")
    print(f"  Estado: {venta.estado}")
    
    # Buscar factura asociada
    try:
        factura = DatosFacturacionElect.objects.filter(id_venta=venta).first()
        if factura:
            print(f"  ✓ Factura Electrónica:")
            print(f"    - CDC: {factura.cdc[:30]}..." if factura.cdc else "    - CDC: Pendiente")
            print(f"    - Estado: {factura.estado_sifen}")
            print(f"    - Emitida: {factura.fecha_envio.strftime('%d/%m/%Y %H:%M') if factura.fecha_envio else 'Pendiente'}")
        else:
            print(f"  ⚠ Sin factura electrónica")
    except Exception as e:
        print(f"  ⚠ Error verificando factura: {str(e)[:50]}")

# Estadísticas
print("\n" + "="*80)
print("📈 ESTADÍSTICAS")
print("="*80)

total_ventas = Ventas.objects.count()
total_facturadas = DatosFacturacionElect.objects.count()
monto_total = sum(v.monto_total for v in Ventas.objects.all())

print(f"\nTotal de ventas: {total_ventas}")
print(f"Ventas facturadas: {total_facturadas}")
print(f"Monto total: ₲{monto_total:,.0f}")
print(f"Porcentaje facturado: {(total_facturadas/total_ventas*100):.1f}%" if total_ventas > 0 else "Porcentaje facturado: N/A")

print("\n" + "="*80)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*80)
print("\nPróximos pasos:")
print("1. Abre http://localhost:8000/reportes/facturacion/dashboard/ en tu navegador")
print("2. Deberías ver la venta #88 (y posiblemente otras)")
print("3. Usa el admin para asignar un timbrado a la venta para completar la factura")
print("4. Crea más ventas para ver estadísticas\n")
