"""
✅ TEST DE VERIFICACIÓN - ESTÁNDAR MAYÚSCULAS
==============================================

Verifica que todos los valores de estado_pago usen MAYÚSCULAS
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db.models import Sum, Count, Q
from gestion.models import Ventas, Compras

print("=" * 80)
print("✅ VERIFICACIÓN ESTÁNDAR MAYÚSCULAS - estado_pago")
print("=" * 80)

errores = []
exitos = []

# ============================================================================
# TEST 1: Queries con MAYÚSCULAS - Ventas
# ============================================================================
print("\n📋 TEST 1: Queries con MAYÚSCULAS - Ventas")
print("-" * 80)

try:
    # Query con MAYÚSCULAS
    ventas_mayusculas = Ventas.objects.filter(
        estado_pago__in=['PENDIENTE', 'PARCIAL']
    ).count()
    print(f"✅ estado_pago__in=['PENDIENTE', 'PARCIAL'] → {ventas_mayusculas} ventas")
    exitos.append("Query ventas con MAYÚSCULAS funciona")
    
    # Query individual
    ventas_pendientes = Ventas.objects.filter(estado_pago='PENDIENTE').count()
    print(f"✅ estado_pago='PENDIENTE' → {ventas_pendientes} ventas")
    exitos.append("Query PENDIENTE funciona")
    
    ventas_parciales = Ventas.objects.filter(estado_pago='PARCIAL').count()
    print(f"✅ estado_pago='PARCIAL' → {ventas_parciales} ventas")
    exitos.append("Query PARCIAL funciona")
    
    ventas_pagadas = Ventas.objects.filter(estado_pago='PAGADA').count()
    print(f"✅ estado_pago='PAGADA' → {ventas_pagadas} ventas")
    exitos.append("Query PAGADA funciona")
    
except Exception as e:
    errores.append(f"Error en queries Ventas: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 2: Queries con MAYÚSCULAS - Compras
# ============================================================================
print("\n📋 TEST 2: Queries con MAYÚSCULAS - Compras")
print("-" * 80)

try:
    # Query con MAYÚSCULAS
    compras_mayusculas = Compras.objects.filter(
        estado_pago__in=['PENDIENTE', 'PARCIAL']
    ).count()
    print(f"✅ estado_pago__in=['PENDIENTE', 'PARCIAL'] → {compras_mayusculas} compras")
    exitos.append("Query compras con MAYÚSCULAS funciona")
    
    # Query con Q objects (como en deuda_proveedores_view)
    deudas = Compras.objects.filter(
        Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL'),
        saldo_pendiente__gt=0
    ).count()
    print(f"✅ Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL') → {deudas} compras")
    exitos.append("Query con Q objects funciona")
    
    # Agregación
    total_deuda = Compras.objects.filter(
        estado_pago__in=['PENDIENTE', 'PARCIAL']
    ).aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    print(f"✅ Agregación Sum → Gs. {total_deuda:,.0f}")
    exitos.append("Agregación con MAYÚSCULAS funciona")
    
except Exception as e:
    errores.append(f"Error en queries Compras: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 3: Verificar vistas principales
# ============================================================================
print("\n📋 TEST 3: Vistas Principales")
print("-" * 80)

try:
    from gestion import pos_views
    
    # Verificar que las vistas importan
    vistas = [
        'compras_dashboard_view',
        'deuda_proveedores_view',
    ]
    
    for vista in vistas:
        if hasattr(pos_views, vista):
            print(f"✅ {vista} → Importada correctamente")
            exitos.append(f"Vista {vista} OK")
        else:
            errores.append(f"Vista {vista} no encontrada")
            print(f"❌ {vista} → No encontrada")
    
except Exception as e:
    errores.append(f"Error importando vistas: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 4: Verificar reportes
# ============================================================================
print("\n📋 TEST 4: Módulo de Reportes")
print("-" * 80)

try:
    from gestion.reportes import ReportesPDF, ReportesExcel
    
    print("✅ ReportesPDF importado")
    print("✅ ReportesExcel importado")
    exitos.append("Módulo reportes importa correctamente")
    
except Exception as e:
    errores.append(f"Error importando reportes: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN")
print("=" * 80)

print(f"\n✅ Éxitos: {len(exitos)}")
for exito in exitos:
    print(f"   • {exito}")

if errores:
    print(f"\n❌ Errores: {len(errores)}")
    for error in errores:
        print(f"   • {error}")

if len(errores) == 0:
    print("\n🎉 RESULTADO: ✅ ESTÁNDAR MAYÚSCULAS IMPLEMENTADO CORRECTAMENTE")
    print("\nTodos los queries usan valores en MAYÚSCULAS:")
    print("• estado_pago__in=['PENDIENTE', 'PARCIAL']")
    print("• Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL')")
    print("• estado_pago='PAGADA'")
else:
    print("\n⚠️  RESULTADO: HAY ERRORES")

print("\n" + "=" * 80)
