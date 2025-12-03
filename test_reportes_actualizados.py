"""
Script para probar que los reportes actualizados funcionan correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from datetime import date, timedelta
from gestion.reportes import ReportesPDF, ReportesExcel
from gestion.models import Cliente, Proveedor, Ventas, Compras

print("=" * 70)
print("TEST DE REPORTES ACTUALIZADOS")
print("=" * 70)

# Fechas para pruebas
fecha_inicio = date.today() - timedelta(days=30)
fecha_fin = date.today()

print(f"\nPeríodo de prueba: {fecha_inicio} a {fecha_fin}")

# 1. Test Reporte PDF Cliente
print("\n" + "=" * 70)
print("1. TEST: Reporte PDF Cuenta Corriente Cliente")
print("=" * 70)

try:
    response = ReportesPDF.reporte_cta_corriente_cliente(
        id_cliente=None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    print(f"✅ Reporte PDF Cliente generado exitosamente")
    print(f"   - Content-Type: {response['Content-Type']}")
    print(f"   - Content-Disposition: {response['Content-Disposition']}")
    print(f"   - Tamaño: {len(response.content)} bytes")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# 2. Test Reporte Excel Cliente
print("\n" + "=" * 70)
print("2. TEST: Reporte Excel Cuenta Corriente Cliente")
print("=" * 70)

try:
    response = ReportesExcel.reporte_cta_corriente_cliente(
        id_cliente=None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    print(f"✅ Reporte Excel Cliente generado exitosamente")
    print(f"   - Content-Type: {response['Content-Type']}")
    print(f"   - Content-Disposition: {response['Content-Disposition']}")
    print(f"   - Tamaño: {len(response.content)} bytes")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# 3. Test Reporte PDF Proveedor
print("\n" + "=" * 70)
print("3. TEST: Reporte PDF Cuenta Corriente Proveedor")
print("=" * 70)

try:
    response = ReportesPDF.reporte_cta_corriente_proveedor(
        id_proveedor=None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    print(f"✅ Reporte PDF Proveedor generado exitosamente")
    print(f"   - Content-Type: {response['Content-Type']}")
    print(f"   - Content-Disposition: {response['Content-Disposition']}")
    print(f"   - Tamaño: {len(response.content)} bytes")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# 4. Test Reporte Excel Proveedor
print("\n" + "=" * 70)
print("4. TEST: Reporte Excel Cuenta Corriente Proveedor")
print("=" * 70)

try:
    response = ReportesExcel.reporte_cta_corriente_proveedor(
        id_proveedor=None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    print(f"✅ Reporte Excel Proveedor generado exitosamente")
    print(f"   - Content-Type: {response['Content-Type']}")
    print(f"   - Content-Disposition: {response['Content-Disposition']}")
    print(f"   - Tamaño: {len(response.content)} bytes")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# 5. Verificar datos que se mostrarían
print("\n" + "=" * 70)
print("5. DATOS QUE APARECERÍAN EN LOS REPORTES")
print("=" * 70)

# Ventas pendientes
ventas_pendientes = Ventas.objects.filter(
    estado_pago__in=['Pendiente', 'Parcial']
).count()

ventas_con_fecha = Ventas.objects.filter(
    estado_pago__in=['Pendiente', 'Parcial'],
    fecha__date__gte=fecha_inicio,
    fecha__date__lte=fecha_fin
).count()

print(f"\n📊 Ventas pendientes:")
print(f"   - Total: {ventas_pendientes}")
print(f"   - En período seleccionado: {ventas_con_fecha}")

# Compras pendientes
compras_pendientes = Compras.objects.filter(
    estado_pago__in=['Pendiente', 'Parcial']
).count()

compras_con_fecha = Compras.objects.filter(
    estado_pago__in=['Pendiente', 'Parcial'],
    fecha__date__gte=fecha_inicio,
    fecha__date__lte=fecha_fin
).count()

print(f"\n📦 Compras pendientes:")
print(f"   - Total: {compras_pendientes}")
print(f"   - En período seleccionado: {compras_con_fecha}")

# 6. Test con cliente/proveedor específico
print("\n" + "=" * 70)
print("6. TEST CON CLIENTE/PROVEEDOR ESPECÍFICO")
print("=" * 70)

# Buscar un cliente con ventas pendientes
venta_pendiente = Ventas.objects.filter(
    estado_pago__in=['Pendiente', 'Parcial']
).select_related('id_cliente').first()

if venta_pendiente:
    print(f"\n✅ Cliente encontrado: {venta_pendiente.id_cliente.nombre_completo}")
    try:
        response = ReportesPDF.reporte_cta_corriente_cliente(
            id_cliente=venta_pendiente.id_cliente.id_cliente
        )
        print(f"   ✅ Reporte PDF específico generado: {len(response.content)} bytes")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
else:
    print("\nℹ️ No hay ventas pendientes para probar reporte específico")

# Buscar un proveedor con compras pendientes
compra_pendiente = Compras.objects.filter(
    estado_pago__in=['Pendiente', 'Parcial']
).select_related('id_proveedor').first()

if compra_pendiente:
    print(f"\n✅ Proveedor encontrado: {compra_pendiente.id_proveedor.razon_social}")
    try:
        response = ReportesPDF.reporte_cta_corriente_proveedor(
            id_proveedor=compra_pendiente.id_proveedor.id_proveedor
        )
        print(f"   ✅ Reporte PDF específico generado: {len(response.content)} bytes")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
else:
    print("\nℹ️ No hay compras pendientes para probar reporte específico")

print("\n" + "=" * 70)
print("✅ TESTS COMPLETADOS")
print("=" * 70)
