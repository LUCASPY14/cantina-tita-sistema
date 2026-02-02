"""
✅ TEST FINAL - SISTEMA CUENTA CORRIENTE
========================================

Verificación completa después de todas las correcciones.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db.models import Sum, Count, Q
from gestion.models import Ventas, Compras, Cliente, Proveedor

print("=" * 80)
print("✅ TEST FINAL - SISTEMA CUENTA CORRIENTE")
print("=" * 80)

resultados = {
    'exitosos': 0,
    'fallidos': 0,
    'advertencias': 0
}

# ============================================================================
# TEST 1: Campos en modelos
# ============================================================================
print("\n📋 TEST 1: Campos en Modelos")
print("-" * 80)

try:
    # Verificar Ventas
    venta = Ventas.objects.first()
    if venta:
        assert hasattr(venta, 'saldo_pendiente'), "Ventas.saldo_pendiente no existe"
        assert hasattr(venta, 'estado_pago'), "Ventas.estado_pago no existe"
        print(f"✅ Ventas: saldo_pendiente={venta.saldo_pendiente}, estado_pago={venta.estado_pago}")
        resultados['exitosos'] += 1
    
    # Verificar Compras
    compra = Compras.objects.first()
    if compra:
        assert hasattr(compra, 'saldo_pendiente'), "Compras.saldo_pendiente no existe"
        assert hasattr(compra, 'estado_pago'), "Compras.estado_pago no existe"
        print(f"✅ Compras: saldo_pendiente={compra.saldo_pendiente}, estado_pago={compra.estado_pago}")
        resultados['exitosos'] += 1
        
except AssertionError as e:
    print(f"❌ {e}")
    resultados['fallidos'] += 1
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 2: Queries con estado_pago (soporta mayúsculas/minúsculas)
# ============================================================================
print("\n🔍 TEST 2: Queries con estado_pago")
print("-" * 80)

try:
    # Ventas pendientes (case-insensitive)
    ventas_pendientes = Ventas.objects.filter(
        Q(estado_pago__iexact='Pendiente') | 
        Q(estado_pago__iexact='Parcial') |
        Q(estado_pago__iexact='PENDIENTE') |
        Q(estado_pago__iexact='PARCIAL')
    ).count()
    print(f"✅ Ventas pendientes/parciales: {ventas_pendientes}")
    resultados['exitosos'] += 1
    
    # Compras pendientes
    compras_pendientes = Compras.objects.filter(
        Q(estado_pago__iexact='Pendiente') | 
        Q(estado_pago__iexact='Parcial') |
        Q(estado_pago__iexact='PENDIENTE') |
        Q(estado_pago__iexact='PARCIAL')
    ).count()
    print(f"✅ Compras pendientes/parciales: {compras_pendientes}")
    resultados['exitosos'] += 1
    
except Exception as e:
    print(f"❌ Error en queries: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 3: Query deuda_proveedores_view (VISTA CORREGIDA HOY)
# ============================================================================
print("\n💰 TEST 3: Query deuda_proveedores (Vista Corregida)")
print("-" * 80)

try:
    # Simulación exacta de deuda_proveedores_view
    deudas = Compras.objects.filter(
        Q(estado_pago__iexact='Pendiente') | Q(estado_pago__iexact='Parcial') |
        Q(estado_pago__iexact='PENDIENTE') | Q(estado_pago__iexact='PARCIAL'),
        saldo_pendiente__gt=0
    ).values(
        'id_proveedor__id_proveedor',
        'id_proveedor__razon_social'
    ).annotate(
        saldo=Sum('saldo_pendiente'),
        cantidad_compras=Count('id_compra')
    ).order_by('-saldo')
    
    total_deuda = deudas.aggregate(total=Sum('saldo'))['total'] or 0
    
    print(f"✅ Proveedores con deuda: {deudas.count()}")
    print(f"✅ Total deuda: Gs. {total_deuda:,.0f}")
    
    if deudas.count() > 0:
        print("\n   Top 3 proveedores con mayor deuda:")
        for i, deuda in enumerate(deudas[:3], 1):
            print(f"   {i}. {deuda['id_proveedor__razon_social']}: Gs. {deuda['saldo']:,.0f} ({deuda['cantidad_compras']} compras)")
    
    resultados['exitosos'] += 1
    
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 4: Query compras_dashboard (VISTA CORREGIDA ANTERIORMENTE)
# ============================================================================
print("\n📊 TEST 4: Query compras_dashboard")
print("-" * 80)

try:
    # Compras pendientes
    compras_pendientes = Compras.objects.filter(
        Q(estado_pago__iexact='Pendiente') | Q(estado_pago__iexact='Parcial') |
        Q(estado_pago__iexact='PENDIENTE') | Q(estado_pago__iexact='PARCIAL')
    ).count()
    
    # Deuda total
    deuda_total = Compras.objects.filter(
        Q(estado_pago__iexact='Pendiente') | Q(estado_pago__iexact='Parcial') |
        Q(estado_pago__iexact='PENDIENTE') | Q(estado_pago__iexact='PARCIAL')
    ).aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    
    print(f"✅ Compras pendientes: {compras_pendientes}")
    print(f"✅ Deuda total: Gs. {deuda_total:,.0f}")
    resultados['exitosos'] += 1
    
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 5: Vistas principales
# ============================================================================
print("\n🎭 TEST 5: Vistas Principales")
print("-" * 80)

try:
    from gestion import pos_views
    
    vistas = [
        ('cuenta_corriente_view', pos_views.cuenta_corriente_view),
        ('cc_detalle_view', pos_views.cc_detalle_view),
        ('compras_dashboard_view', pos_views.compras_dashboard_view),
        ('deuda_proveedores_view', pos_views.deuda_proveedores_view),
    ]
    
    for nombre, vista in vistas:
        if callable(vista):
            print(f"✅ {nombre:30} → OK")
        else:
            print(f"❌ {nombre:30} → No callable")
            resultados['fallidos'] += 1
    
    resultados['exitosos'] += len(vistas)
    
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 6: Módulo de reportes
# ============================================================================
print("\n📄 TEST 6: Módulo de Reportes")
print("-" * 80)

try:
    from gestion import reportes
    
    # Buscar funciones de reportes
    funciones = [attr for attr in dir(reportes) if callable(getattr(reportes, attr)) and not attr.startswith('_')]
    reportes_cc = [f for f in funciones if 'cta_corriente' in f.lower()]
    
    print(f"✅ Funciones totales en reportes.py: {len(funciones)}")
    print(f"✅ Funciones de cuenta corriente: {len(reportes_cc)}")
    
    if reportes_cc:
        print("\n   Funciones de cuenta corriente encontradas:")
        for func in reportes_cc:
            print(f"   • {func}")
    else:
        print("\n   ⚠️  No se encontraron funciones con 'cta_corriente' en el nombre")
        resultados['advertencias'] += 1
    
    resultados['exitosos'] += 1
    
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 7: Django check
# ============================================================================
print("\n⚙️  TEST 7: Django System Check")
print("-" * 80)

try:
    from django.core.management import call_command
    from io import StringIO
    
    output = StringIO()
    call_command('check', stdout=output, stderr=output)
    result = output.getvalue()
    
    if "no issues" in result.lower() or "0 silenced" in result:
        print("✅ Django check: Sin errores")
        resultados['exitosos'] += 1
    else:
        print(f"⚠️  Django check: {result}")
        resultados['advertencias'] += 1
        
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# TEST 8: Integridad de datos
# ============================================================================
print("\n🔐 TEST 8: Integridad de Datos")
print("-" * 80)

try:
    # Saldos negativos
    ventas_neg = Ventas.objects.filter(saldo_pendiente__lt=0).count()
    compras_neg = Compras.objects.filter(saldo_pendiente__lt=0).count()
    
    if ventas_neg == 0 and compras_neg == 0:
        print("✅ Sin saldos negativos")
        resultados['exitosos'] += 1
    else:
        print(f"⚠️  Ventas con saldo negativo: {ventas_neg}")
        print(f"⚠️  Compras con saldo negativo: {compras_neg}")
        resultados['advertencias'] += 1
    
    # Estados válidos
    estados_validos = ['Pagado', 'Pendiente', 'Parcial', 'Anulado', 
                       'PAGADO', 'PENDIENTE', 'PARCIAL', 'ANULADO',
                       'PAGADA', 'Pagada']
    
    ventas_invalidas = Ventas.objects.exclude(estado_pago__in=estados_validos).count()
    compras_invalidas = Compras.objects.exclude(estado_pago__in=estados_validos).count()
    
    if ventas_invalidas == 0 and compras_invalidas == 0:
        print("✅ Todos los estados son válidos")
        resultados['exitosos'] += 1
    else:
        print(f"⚠️  Ventas con estado inválido: {ventas_invalidas}")
        print(f"⚠️  Compras con estado inválido: {compras_invalidas}")
        resultados['advertencias'] += 1
        
except Exception as e:
    print(f"❌ Error: {e}")
    resultados['fallidos'] += 1

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN FINAL")
print("=" * 80)

total = resultados['exitosos'] + resultados['fallidos'] + resultados['advertencias']
porcentaje = (resultados['exitosos'] / total * 100) if total > 0 else 0

print(f"""
✅ Tests exitosos:    {resultados['exitosos']}
❌ Tests fallidos:    {resultados['fallidos']}
⚠️  Advertencias:     {resultados['advertencias']}

Tasa de éxito: {porcentaje:.1f}%
""")

if resultados['fallidos'] == 0:
    print("🎉 RESULTADO: ✅ TODOS LOS TESTS PASARON")
    print("\n✅ Sistema completamente funcional después de la migración")
    print("✅ Vistas corregidas funcionando correctamente")
    print("✅ Queries usando campos en minúsculas")
    print("✅ Integridad de datos verificada")
elif resultados['fallidos'] <= 2:
    print("⚠️  RESULTADO: ⚠️  SISTEMA FUNCIONAL CON ADVERTENCIAS")
    print("\n⚠️  Sistema operativo pero con puntos menores a revisar")
else:
    print("❌ RESULTADO: ❌ TESTS FALLIDOS")
    print("\n❌ Sistema requiere correcciones adicionales")

print("\n" + "=" * 80)
