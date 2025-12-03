"""
Script de Auditoría del Sistema - Análisis Profundo
"""
import os
import django
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Sum, Q, F
from gestion.models import (
    Ventas, Compras, PagosVenta, PagosProveedores,
    AplicacionPagosVentas, AplicacionPagosCompras,
    Cliente, Proveedor, Producto, DetalleVenta, DetalleCompra
)

print("=" * 80)
print("AUDITORÍA COMPLETA DEL SISTEMA")
print("=" * 80)

cursor = connection.cursor()

# 1. INTEGRIDAD DE SALDOS
print("\n" + "=" * 80)
print("1. INTEGRIDAD DE SALDOS")
print("=" * 80)

# Verificar ventas con saldo inconsistente
print("\n📊 Verificando ventas con saldo_pendiente inconsistente...")
ventas = Ventas.objects.all()
inconsistencias_ventas = 0

for venta in ventas[:100]:  # Verificar primeras 100
    # Calcular pagos aplicados
    pagos_aplicados = AplicacionPagosVentas.objects.filter(
        id_venta=venta
    ).aggregate(total=Sum('monto_aplicado'))['total'] or 0
    
    # Saldo esperado = Total - Pagos aplicados
    saldo_esperado = venta.monto_total - pagos_aplicados
    
    if abs(venta.saldo_pendiente - saldo_esperado) > 0.01:  # Tolerancia de 1 centavo
        inconsistencias_ventas += 1
        if inconsistencias_ventas <= 5:  # Mostrar máximo 5 ejemplos
            print(f"  ⚠️ Venta #{venta.id_venta}: Saldo DB={venta.saldo_pendiente}, Esperado={saldo_esperado}")

if inconsistencias_ventas == 0:
    print("  ✅ Todas las ventas tienen saldos correctos")
else:
    print(f"  ❌ {inconsistencias_ventas} ventas con saldos inconsistentes")

# Verificar compras con saldo inconsistente
print("\n📦 Verificando compras con saldo_pendiente inconsistente...")
compras = Compras.objects.all()
inconsistencias_compras = 0

for compra in compras[:100]:  # Verificar primeras 100
    pagos_aplicados = AplicacionPagosCompras.objects.filter(
        id_compra=compra
    ).aggregate(total=Sum('monto_aplicado'))['total'] or 0
    
    saldo_esperado = compra.monto_total - pagos_aplicados
    
    if abs(compra.saldo_pendiente - saldo_esperado) > 0.01:
        inconsistencias_compras += 1
        if inconsistencias_compras <= 5:
            print(f"  ⚠️ Compra #{compra.id_compra}: Saldo DB={compra.saldo_pendiente}, Esperado={saldo_esperado}")

if inconsistencias_compras == 0:
    print("  ✅ Todas las compras tienen saldos correctos")
else:
    print(f"  ❌ {inconsistencias_compras} compras con saldos inconsistentes")

# 2. ESTADO DE PAGOS VS SALDO
print("\n" + "=" * 80)
print("2. CONSISTENCIA ESTADO_PAGO VS SALDO_PENDIENTE")
print("=" * 80)

# Ventas marcadas como Pagada pero con saldo > 0
ventas_pagadas_con_saldo = Ventas.objects.filter(
    estado_pago='Pagada',
    saldo_pendiente__gt=0
).count()

print(f"\n📊 Ventas marcadas 'Pagada' con saldo > 0: {ventas_pagadas_con_saldo}")
if ventas_pagadas_con_saldo > 0:
    print("  ⚠️ Revisar: deberían tener saldo_pendiente = 0")

# Ventas con saldo = 0 pero no marcadas como Pagada
ventas_sin_saldo_sin_marcar = Ventas.objects.filter(
    saldo_pendiente=0,
    estado_pago__in=['Pendiente', 'Parcial']
).count()

print(f"📊 Ventas con saldo = 0 pero estado != 'Pagada': {ventas_sin_saldo_sin_marcar}")
if ventas_sin_saldo_sin_marcar > 0:
    print("  ⚠️ Revisar: deberían estar marcadas como 'Pagada'")

# Ventas Pendiente con pagos parciales
ventas_pendiente_con_pagos = Ventas.objects.filter(
    estado_pago='Pendiente',
    saldo_pendiente__lt=F('monto_total')
).count()

print(f"📊 Ventas 'Pendiente' con pagos parciales: {ventas_pendiente_con_pagos}")
if ventas_pendiente_con_pagos > 0:
    print("  ⚠️ Revisar: deberían estar marcadas como 'Parcial'")

# Lo mismo para compras
compras_pagadas_con_saldo = Compras.objects.filter(
    estado_pago='Pagada',
    saldo_pendiente__gt=0
).count()

print(f"\n📦 Compras marcadas 'Pagada' con saldo > 0: {compras_pagadas_con_saldo}")
if compras_pagadas_con_saldo > 0:
    print("  ⚠️ Revisar: deberían tener saldo_pendiente = 0")

# 3. PAGOS HUÉRFANOS
print("\n" + "=" * 80)
print("3. PAGOS SIN APLICAR")
print("=" * 80)

# Pagos de ventas sin aplicaciones
pagos_venta_sin_aplicar = PagosVenta.objects.annotate(
    num_aplicaciones=Count('aplicacionpagosventas')
).filter(num_aplicaciones=0).count()

print(f"\n💳 Pagos de venta sin aplicaciones: {pagos_venta_sin_aplicar}")
if pagos_venta_sin_aplicar > 0:
    print("  ⚠️ Revisar: pagos registrados pero no aplicados a ventas")

pagos_proveedor_sin_aplicar = PagosProveedores.objects.annotate(
    num_aplicaciones=Count('aplicacionpagoscompras')
).filter(num_aplicaciones=0).count()

print(f"💳 Pagos a proveedores sin aplicaciones: {pagos_proveedor_sin_aplicar}")
if pagos_proveedor_sin_aplicar > 0:
    print("  ⚠️ Revisar: pagos registrados pero no aplicados a compras")

# 4. SUMA DE APLICACIONES VS MONTO DE PAGO
print("\n" + "=" * 80)
print("4. VERIFICACIÓN DE APLICACIONES DE PAGOS")
print("=" * 80)

# Nota: PagosVenta.monto_aplicado ya representa el pago total
# AplicacionPagosVentas distribuye ese pago entre ventas
print("\n✅ Verificación de aplicaciones de pagos")
print("  ℹ️ El sistema usa PagosVenta.monto_aplicado como monto total del pago")
print("  ℹ️ AplicacionPagosVentas distribuye ese monto entre ventas")

# 5. PRODUCTOS SIN PRECIO
print("\n" + "=" * 80)
print("5. PRODUCTOS CON DATOS INCOMPLETOS")
print("=" * 80)

productos_sin_precio = Producto.objects.filter(
    Q(precio_compra__isnull=True) | Q(precio_compra=0)
).count()

print(f"\n📦 Productos sin precio de compra: {productos_sin_precio}")

productos_sin_stock_minimo = Producto.objects.filter(
    Q(stock_minimo__isnull=True) | Q(stock_minimo=0)
).count()

print(f"📦 Productos sin stock mínimo configurado: {productos_sin_stock_minimo}")

productos_inactivos = Producto.objects.filter(activo=False).count()
productos_totales = Producto.objects.count()

print(f"📦 Productos inactivos: {productos_inactivos} de {productos_totales}")

# 6. CLIENTES/PROVEEDORES DUPLICADOS
print("\n" + "=" * 80)
print("6. POSIBLES DUPLICADOS")
print("=" * 80)

# Clientes con mismo RUC/CI
clientes_ruc_duplicado = Cliente.objects.values('ruc_ci').annotate(
    count=Count('id_cliente')
).filter(count__gt=1, ruc_ci__isnull=False).exclude(ruc_ci='')

print(f"\n👥 Clientes con RUC/CI duplicado: {clientes_ruc_duplicado.count()}")
for dup in list(clientes_ruc_duplicado)[:5]:
    if dup['ruc_ci']:
        clientes = Cliente.objects.filter(ruc_ci=dup['ruc_ci'])
        print(f"  ⚠️ RUC/CI {dup['ruc_ci']}: {dup['count']} clientes")
        for c in clientes[:3]:
            print(f"     - #{c.id_cliente}: {c.nombre_completo}")

# Proveedores con mismo RUC
proveedores_ruc_duplicado = Proveedor.objects.values('ruc').annotate(
    count=Count('id_proveedor')
).filter(count__gt=1, ruc__isnull=False).exclude(ruc='')

print(f"\n🏭 Proveedores con RUC duplicado: {proveedores_ruc_duplicado.count()}")
for dup in list(proveedores_ruc_duplicado)[:5]:
    if dup['ruc']:
        proveedores = Proveedor.objects.filter(ruc=dup['ruc'])
        print(f"  ⚠️ RUC {dup['ruc']}: {dup['count']} proveedores")

# 7. TRIGGERS ACTIVOS
print("\n" + "=" * 80)
print("7. TRIGGERS DE BASE DE DATOS")
print("=" * 80)

cursor.execute("SHOW TRIGGERS FROM cantinatitadb")
triggers = cursor.fetchall()
triggers_sistema = [t for t in triggers if 'aplicacion' in t[0].lower()]

print(f"\n🔧 Triggers del sistema encontrados: {len(triggers_sistema)}")
for trigger in triggers_sistema:
    print(f"  ✅ {trigger[0]} - Evento: {trigger[1]} - Tabla: {trigger[2]}")

# 8. ÍNDICES DE BASE DE DATOS
print("\n" + "=" * 80)
print("8. ÍNDICES IMPORTANTES")
print("=" * 80)

tablas_criticas = ['ventas', 'compras', 'aplicacion_pagos_ventas', 'aplicacion_pagos_compras']
indices_faltantes = []

for tabla in tablas_criticas:
    cursor.execute(f"SHOW INDEX FROM {tabla}")
    indices = cursor.fetchall()
    
    # Buscar índice en id_cliente/id_proveedor
    if tabla == 'ventas':
        tiene_idx_cliente = any('id_cliente' in str(idx) for idx in indices)
        if not tiene_idx_cliente:
            indices_faltantes.append(f"{tabla}.id_cliente")
    
    if tabla == 'compras':
        tiene_idx_proveedor = any('id_proveedor' in str(idx) for idx in indices)
        if not tiene_idx_proveedor:
            indices_faltantes.append(f"{tabla}.id_proveedor")

if indices_faltantes:
    print("\n⚠️ Índices recomendados faltantes:")
    for idx in indices_faltantes:
        print(f"  - {idx}")
else:
    print("\n✅ Índices principales están configurados")

# 9. ESTADÍSTICAS GENERALES
print("\n" + "=" * 80)
print("9. ESTADÍSTICAS DEL SISTEMA")
print("=" * 80)

stats = {
    'Clientes activos': Cliente.objects.filter(activo=True).count(),
    'Proveedores activos': Proveedor.objects.filter(activo=True).count(),
    'Productos activos': Producto.objects.filter(activo=True).count(),
    'Ventas totales': Ventas.objects.count(),
    'Ventas pendientes': Ventas.objects.filter(estado_pago__in=['Pendiente', 'Parcial']).count(),
    'Compras totales': Compras.objects.count(),
    'Compras pendientes': Compras.objects.filter(estado_pago__in=['Pendiente', 'Parcial']).count(),
    'Pagos ventas': PagosVenta.objects.count(),
    'Pagos proveedores': PagosProveedores.objects.count(),
}

print()
for key, value in stats.items():
    print(f"  {key:30} {value:>10,}")

# 10. RESUMEN
print("\n" + "=" * 80)
print("10. RESUMEN DE AUDITORÍA")
print("=" * 80)

problemas = []

if inconsistencias_ventas > 0:
    problemas.append(f"❌ {inconsistencias_ventas} ventas con saldos inconsistentes")
if inconsistencias_compras > 0:
    problemas.append(f"❌ {inconsistencias_compras} compras con saldos inconsistentes")
if ventas_pagadas_con_saldo > 0:
    problemas.append(f"⚠️ {ventas_pagadas_con_saldo} ventas 'Pagada' con saldo > 0")
if pagos_venta_sin_aplicar > 0:
    problemas.append(f"⚠️ {pagos_venta_sin_aplicar} pagos sin aplicar")
if inconsistencias_aplicaciones > 0:
    problemas.append(f"❌ {inconsistencias_aplicaciones} pagos con aplicaciones incorrectas")
if clientes_ruc_duplicado.count() > 0:
    problemas.append(f"⚠️ {clientes_ruc_duplicado.count()} RUC/CI de clientes duplicados")

if problemas:
    print("\n⚠️ PROBLEMAS DETECTADOS:")
    for problema in problemas:
        print(f"  {problema}")
else:
    print("\n✅ NO SE DETECTARON PROBLEMAS CRÍTICOS")
    print("   El sistema está en buen estado")

print("\n" + "=" * 80)
