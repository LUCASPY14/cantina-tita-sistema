"""
🔧 TEST SIMPLIFICADO - VERIFICACIÓN RÁPIDA
==========================================

Verifica solo lo esencial:
1. Campos existen
2. Queries funcionan
3. Vistas importan
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db.models import Sum, Count, Q
from gestion.models import Ventas, Compras

print("=" * 80)
print("🔧 VERIFICACIÓN RÁPIDA POST-MIGRACIÓN")
print("=" * 80)

# TEST 1: Queries básicos
print("\n✅ TEST 1: Queries Básicos")
print("-" * 80)

try:
    # Ventas
    ventas_count = Ventas.objects.count()
    ventas_pendientes = Ventas.objects.filter(
        Q(estado_pago='Pendiente') | Q(estado_pago='Parcial') |
        Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL')
    ).count()
    print(f"✅ Ventas totales: {ventas_count}")
    print(f"✅ Ventas pendientes: {ventas_pendientes}")
    
    # Compras
    compras_count = Compras.objects.count()
    compras_pendientes = Compras.objects.filter(
        Q(estado_pago='Pendiente') | Q(estado_pago='Parcial') |
        Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL')
    ).count()
    print(f"✅ Compras totales: {compras_count}")
    print(f"✅ Compras pendientes: {compras_pendientes}")
    
    # Deuda total proveedores
    deuda_total = Compras.objects.filter(
        Q(estado_pago__icontains='Pendiente') | Q(estado_pago__icontains='Parcial'),
        saldo_pendiente__gt=0
    ).aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    print(f"✅ Deuda total proveedores: Gs. {deuda_total:,.0f}")
    
except Exception as e:
    print(f"❌ Error en queries: {e}")

# TEST 2: Vistas
print("\n✅ TEST 2: Vistas Principales")
print("-" * 80)

try:
    from gestion import pos_views
    
    vistas = [
        'cuenta_corriente_view',
        'cc_detalle_view',
        'compras_dashboard_view',
        'deuda_proveedores_view',
    ]
    
    for vista in vistas:
        if hasattr(pos_views, vista):
            print(f"✅ {vista}")
        else:
            print(f"❌ {vista} - No encontrada")
            
except Exception as e:
    print(f"❌ Error importando vistas: {e}")

# TEST 3: Reportes
print("\n✅ TEST 3: Módulo de Reportes")
print("-" * 80)

try:
    from gestion import reportes
    
    # Listar todas las funciones que contienen "reporte_cta_corriente"
    funciones = [attr for attr in dir(reportes) if 'reporte_cta_corriente' in attr.lower()]
    
    print(f"Funciones encontradas: {len(funciones)}")
    for func in funciones:
        print(f"✅ {func}")
        
except Exception as e:
    print(f"❌ Error con reportes: {e}")

# TEST 4: Django check
print("\n✅ TEST 4: Django Check")
print("-" * 80)

from django.core.management import call_command
from io import StringIO

try:
    output = StringIO()
    call_command('check', stdout=output, stderr=output)
    result = output.getvalue()
    
    if "no issues" in result.lower() or "0 silenced" in result:
        print("✅ Sin errores detectados")
    else:
        print(f"⚠️  {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
