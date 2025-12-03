"""
🧪 TEST POST-MIGRACIÓN CUENTA CORRIENTE
========================================

Verifica específicamente los cambios realizados en:
- Campos en minúsculas (estado_pago, saldo_pendiente)
- Vistas corregidas
- Reportes actualizados
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.db.models import Sum, Count, Q, F
from gestion.models import Ventas, Compras, Cliente, Proveedor

print("=" * 80)
print("🧪 TEST POST-MIGRACIÓN - CUENTA CORRIENTE")
print("=" * 80)

errores = []
warnings = []
exitos = []

# ============================================================================
# TEST 1: Verificar campos en minúsculas - Ventas
# ============================================================================
print("\n📋 TEST 1: Campos en Minúsculas - Modelo Ventas")
print("-" * 80)

try:
    venta = Ventas.objects.first()
    if venta:
        # Test saldo_pendiente
        try:
            saldo = venta.saldo_pendiente
            if isinstance(saldo, (int, float)):
                print(f"✅ saldo_pendiente → Tipo: {type(saldo).__name__}, Valor: {saldo}")
                exitos.append("Ventas.saldo_pendiente existe y funciona")
            else:
                errores.append("Ventas.saldo_pendiente tipo incorrecto")
                print(f"❌ saldo_pendiente → Tipo incorrecto: {type(saldo)}")
        except AttributeError as e:
            errores.append(f"Ventas.saldo_pendiente no existe: {e}")
            print(f"❌ saldo_pendiente → No existe: {e}")
        
        # Test estado_pago
        try:
            estado = venta.estado_pago
            if estado in ['Pagado', 'Pendiente', 'Parcial', 'Anulado']:
                print(f"✅ estado_pago → Valor válido: '{estado}'")
                exitos.append("Ventas.estado_pago existe y tiene valor válido")
            else:
                warnings.append(f"Ventas.estado_pago valor inusual: {estado}")
                print(f"⚠️  estado_pago → Valor inusual: '{estado}'")
        except AttributeError as e:
            errores.append(f"Ventas.estado_pago no existe: {e}")
            print(f"❌ estado_pago → No existe: {e}")
    else:
        warnings.append("No hay ventas para verificar")
        print("⚠️  No hay ventas en la base de datos")
        
except Exception as e:
    errores.append(f"Error en TEST 1: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 2: Verificar campos en minúsculas - Compras
# ============================================================================
print("\n📋 TEST 2: Campos en Minúsculas - Modelo Compras")
print("-" * 80)

try:
    compra = Compras.objects.first()
    if compra:
        # Test saldo_pendiente
        try:
            saldo = compra.saldo_pendiente
            if isinstance(saldo, (int, float)):
                print(f"✅ saldo_pendiente → Tipo: {type(saldo).__name__}, Valor: {saldo}")
                exitos.append("Compras.saldo_pendiente existe y funciona")
            else:
                errores.append("Compras.saldo_pendiente tipo incorrecto")
                print(f"❌ saldo_pendiente → Tipo incorrecto: {type(saldo)}")
        except AttributeError as e:
            errores.append(f"Compras.saldo_pendiente no existe: {e}")
            print(f"❌ saldo_pendiente → No existe: {e}")
        
        # Test estado_pago
        try:
            estado = compra.estado_pago
            if estado in ['Pagado', 'Pendiente', 'Parcial', 'Anulado']:
                print(f"✅ estado_pago → Valor válido: '{estado}'")
                exitos.append("Compras.estado_pago existe y tiene valor válido")
            else:
                warnings.append(f"Compras.estado_pago valor inusual: {estado}")
                print(f"⚠️  estado_pago → Valor inusual: '{estado}'")
        except AttributeError as e:
            errores.append(f"Compras.estado_pago no existe: {e}")
            print(f"❌ estado_pago → No existe: {e}")
    else:
        warnings.append("No hay compras para verificar")
        print("⚠️  No hay compras en la base de datos")
        
except Exception as e:
    errores.append(f"Error en TEST 2: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 3: Query estado_pago con minúsculas - Ventas
# ============================================================================
print("\n🔍 TEST 3: Queries con Minúsculas - Ventas")
print("-" * 80)

try:
    # Query 1: estado_pago = 'Pendiente'
    pendientes = Ventas.objects.filter(estado_pago='Pendiente').count()
    print(f"✅ estado_pago='Pendiente' → {pendientes} ventas")
    exitos.append(f"Query estado_pago='Pendiente': {pendientes} resultados")
    
    # Query 2: estado_pago IN ['Pendiente', 'Parcial']
    no_pagadas = Ventas.objects.filter(
        estado_pago__in=['Pendiente', 'Parcial']
    ).count()
    print(f"✅ estado_pago__in=['Pendiente', 'Parcial'] → {no_pagadas} ventas")
    exitos.append(f"Query estado_pago__in: {no_pagadas} resultados")
    
    # Query 3: saldo_pendiente > 0
    con_saldo = Ventas.objects.filter(saldo_pendiente__gt=0).count()
    print(f"✅ saldo_pendiente__gt=0 → {con_saldo} ventas")
    exitos.append(f"Query saldo_pendiente__gt: {con_saldo} resultados")
    
    # Query 4: Combinado (como en compras_dashboard_view)
    total_deuda = Ventas.objects.filter(
        Q(estado_pago='Pendiente') | Q(estado_pago='Parcial'),
        saldo_pendiente__gt=0
    ).aggregate(total=Sum('saldo_pendiente'))['total'] or 0
    print(f"✅ Query combinado → Total deuda: Gs. {total_deuda:,.0f}")
    exitos.append(f"Query combinado: Gs. {total_deuda:,.0f}")
    
except Exception as e:
    errores.append(f"Error en queries Ventas: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 4: Query estado_pago con minúsculas - Compras
# ============================================================================
print("\n🔍 TEST 4: Queries con Minúsculas - Compras")
print("-" * 80)

try:
    # Query 1: estado_pago = 'Pendiente'
    pendientes = Compras.objects.filter(estado_pago='Pendiente').count()
    print(f"✅ estado_pago='Pendiente' → {pendientes} compras")
    exitos.append(f"Query estado_pago='Pendiente': {pendientes} resultados")
    
    # Query 2: estado_pago IN ['Pendiente', 'Parcial']
    no_pagadas = Compras.objects.filter(
        estado_pago__in=['Pendiente', 'Parcial']
    ).count()
    print(f"✅ estado_pago__in=['Pendiente', 'Parcial'] → {no_pagadas} compras")
    exitos.append(f"Query estado_pago__in: {no_pagadas} resultados")
    
    # Query 3: saldo_pendiente > 0
    con_saldo = Compras.objects.filter(saldo_pendiente__gt=0).count()
    print(f"✅ saldo_pendiente__gt=0 → {con_saldo} compras")
    exitos.append(f"Query saldo_pendiente__gt: {con_saldo} resultados")
    
    # Query 4: Como en deuda_proveedores_view (CORREGIDO HOY)
    deuda_proveedores = Compras.objects.filter(
        Q(estado_pago='Pendiente') | Q(estado_pago='Parcial'),
        saldo_pendiente__gt=0
    ).values(
        'id_proveedor__id_proveedor',
        'id_proveedor__razon_social'
    ).annotate(
        saldo=Sum('saldo_pendiente'),
        cantidad_compras=Count('id_compra')
    ).order_by('-saldo')
    
    total_deuda = deuda_proveedores.aggregate(total=Sum('saldo'))['total'] or 0
    print(f"✅ Query deuda_proveedores → {deuda_proveedores.count()} proveedores")
    print(f"✅ Total deuda proveedores → Gs. {total_deuda:,.0f}")
    exitos.append(f"Query deuda_proveedores: {deuda_proveedores.count()} proveedores")
    
except Exception as e:
    errores.append(f"Error en queries Compras: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 5: Verificar vistas corregidas
# ============================================================================
print("\n🎭 TEST 5: Vistas Corregidas")
print("-" * 80)

from gestion import pos_views

vistas = [
    ('cuenta_corriente_view', pos_views.cuenta_corriente_view),
    ('cc_detalle_view', pos_views.cc_detalle_view),
    ('compras_dashboard_view', pos_views.compras_dashboard_view),
    ('deuda_proveedores_view', pos_views.deuda_proveedores_view),
]

for nombre, vista in vistas:
    try:
        # Verificar que la vista existe
        if callable(vista):
            print(f"✅ {nombre:30} → Importada OK")
            exitos.append(f"Vista {nombre} existe")
        else:
            errores.append(f"Vista {nombre} no es callable")
            print(f"❌ {nombre:30} → No es callable")
    except Exception as e:
        errores.append(f"Error importando {nombre}: {e}")
        print(f"❌ {nombre:30} → Error: {e}")

# ============================================================================
# TEST 6: Verificar funciones de reportes
# ============================================================================
print("\n📊 TEST 6: Funciones de Reportes")
print("-" * 80)

from gestion import reportes

funciones = [
    'reporte_cta_corriente_cliente_pdf',
    'reporte_cta_corriente_cliente_excel',
    'reporte_cta_corriente_proveedor_pdf',
    'reporte_cta_corriente_proveedor_excel',
]

for nombre_funcion in funciones:
    try:
        funcion = getattr(reportes, nombre_funcion)
        if callable(funcion):
            print(f"✅ {nombre_funcion:45} → OK")
            exitos.append(f"Función {nombre_funcion} existe")
        else:
            errores.append(f"Función {nombre_funcion} no es callable")
            print(f"❌ {nombre_funcion:45} → No callable")
    except AttributeError:
        errores.append(f"Función {nombre_funcion} no existe")
        print(f"❌ {nombre_funcion:45} → No existe")

# ============================================================================
# TEST 7: Integridad de datos
# ============================================================================
print("\n🔐 TEST 7: Integridad de Datos")
print("-" * 80)

try:
    # Ventas con saldo negativo
    ventas_negativas = Ventas.objects.filter(saldo_pendiente__lt=0).count()
    if ventas_negativas == 0:
        print("✅ Ventas: Sin saldos negativos")
        exitos.append("Ventas: Sin saldos negativos")
    else:
        warnings.append(f"Ventas: {ventas_negativas} con saldo negativo")
        print(f"⚠️  Ventas: {ventas_negativas} con saldo negativo")
    
    # Compras con saldo negativo
    compras_negativas = Compras.objects.filter(saldo_pendiente__lt=0).count()
    if compras_negativas == 0:
        print("✅ Compras: Sin saldos negativos")
        exitos.append("Compras: Sin saldos negativos")
    else:
        warnings.append(f"Compras: {compras_negativas} con saldo negativo")
        print(f"⚠️  Compras: {compras_negativas} con saldo negativo")
    
    # Ventas pagadas con saldo > 0
    ventas_pagadas_con_saldo = Ventas.objects.filter(
        estado_pago='Pagado',
        saldo_pendiente__gt=0
    ).count()
    if ventas_pagadas_con_saldo == 0:
        print("✅ Ventas: 'Pagado' sin saldo pendiente")
        exitos.append("Ventas 'Pagado' sin saldo")
    else:
        warnings.append(f"Ventas: {ventas_pagadas_con_saldo} 'Pagado' con saldo > 0")
        print(f"⚠️  Ventas: {ventas_pagadas_con_saldo} 'Pagado' con saldo > 0")
    
    # Saldo no puede exceder total
    ventas_saldo_mayor = Ventas.objects.filter(
        saldo_pendiente__gt=F('total')
    ).count()
    if ventas_saldo_mayor == 0:
        print("✅ Ventas: saldo_pendiente <= total")
        exitos.append("Ventas: saldo <= total")
    else:
        errores.append(f"Ventas: {ventas_saldo_mayor} con saldo > total")
        print(f"❌ Ventas: {ventas_saldo_mayor} con saldo > total")
    
except Exception as e:
    errores.append(f"Error en integridad: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 8: Django check
# ============================================================================
print("\n⚙️  TEST 8: Django System Check")
print("-" * 80)

from django.core.management import call_command
from io import StringIO

try:
    output = StringIO()
    call_command('check', stdout=output, stderr=output)
    result = output.getvalue()
    
    if "no issues" in result.lower() or "0 silenced" in result:
        print("✅ Django check: Sin errores")
        exitos.append("Django check: OK")
    else:
        warnings.append("Django check: Revisar output")
        print(f"⚠️  Django check:\n{result}")
        
except Exception as e:
    errores.append(f"Error en Django check: {e}")
    print(f"❌ Error: {e}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN DE TESTS")
print("=" * 80)

print(f"\n✅ ÉXITOS: {len(exitos)}")
for exito in exitos:
    print(f"   • {exito}")

if warnings:
    print(f"\n⚠️  ADVERTENCIAS: {len(warnings)}")
    for warning in warnings:
        print(f"   • {warning}")

if errores:
    print(f"\n❌ ERRORES: {len(errores)}")
    for error in errores:
        print(f"   • {error}")

print("\n" + "=" * 80)

# Resultado final
total_tests = len(exitos) + len(warnings) + len(errores)
porcentaje = (len(exitos) / total_tests * 100) if total_tests > 0 else 0

if len(errores) == 0:
    print("🎉 RESULTADO: TODOS LOS TESTS PASARON")
    print(f"   {len(exitos)} éxitos, {len(warnings)} advertencias")
    print("\n✅ Sistema completamente funcional después de la migración")
elif len(errores) <= 2:
    print("⚠️  RESULTADO: TESTS MAYORMENTE EXITOSOS")
    print(f"   {len(exitos)} éxitos, {len(warnings)} advertencias, {len(errores)} errores")
    print("\n⚠️  Sistema funcional con errores menores")
else:
    print("❌ RESULTADO: TESTS FALLIDOS")
    print(f"   {len(exitos)} éxitos, {len(warnings)} advertencias, {len(errores)} errores")
    print("\n❌ Sistema requiere correcciones")

print(f"\nÉXITO: {porcentaje:.1f}%")
print("=" * 80)
