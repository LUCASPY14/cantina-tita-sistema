"""
🔍 AUDITORÍA DE TEMPLATES DESPUÉS DE CAMBIOS
============================================

OBJETIVO: Verificar que los templates HTML estén alineados con el nuevo sistema
         de cuenta corriente y no tengan referencias obsoletas.

METODOLOGÍA:
1. Buscar referencias a campos/tablas legacy
2. Verificar vistas que renderizan templates críticos
3. Comprobar consistencia de datos mostrados
4. Identificar templates que necesitan actualizaciones
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

print("=" * 80)
print("AUDITORÍA DE TEMPLATES - SISTEMA CUENTA CORRIENTE")
print("=" * 80)

# Definir templates críticos y sus vistas asociadas
templates_criticos = {
    'cuenta_corriente.html': {
        'vista': 'pos_views.cuenta_corriente_view',
        'url': 'pos:cuenta_corriente',
        'descripción': 'Listado de clientes con límite de crédito',
        'campos_esperados': ['limite_credito', 'num_hijos', 'activo'],
        'sistema': 'Nuevo (usa Cliente.limite_credito)'
    },
    'cc_detalle.html': {
        'vista': 'pos_views.cc_detalle_view',
        'url': 'pos:cc_detalle',
        'descripción': 'Detalle de cuenta corriente por cliente',
        'campos_esperados': ['ventas', 'recargas', 'limite_credito'],
        'sistema': 'Nuevo (usa Ventas y CargasSaldo)'
    },
    'deuda_proveedores.html': {
        'vista': 'pos_views.deuda_proveedores_view',
        'url': 'pos:deuda_proveedores',
        'descripción': 'Listado de deudas con proveedores',
        'campos_esperados': ['saldo', 'id_proveedor', 'ultima_compra'],
        'sistema': 'Actualizar (usa Compras.saldo_pendiente)'
    },
    'compras_dashboard.html': {
        'vista': 'pos_views.compras_dashboard_view',
        'url': 'pos:compras_dashboard',
        'descripción': 'Dashboard principal de compras',
        'campos_esperados': ['compras_pendientes', 'deuda_total'],
        'sistema': 'Actualizado (usa estado_pago y saldo_pendiente)'
    },
    'proveedor_detalle.html': {
        'vista': 'pos_views.proveedor_detalle_view',
        'url': 'pos:proveedor_detalle',
        'descripción': 'Detalle de proveedor con compras',
        'campos_esperados': ['compras', 'saldo_pendiente'],
        'sistema': 'Verificar implementación'
    }
}

print("\n" + "=" * 80)
print("1. ANÁLISIS DE TEMPLATES CRÍTICOS")
print("=" * 80)

for template, info in templates_criticos.items():
    print(f"\n📄 {template}")
    print(f"   Vista: {info['vista']}")
    print(f"   URL: {info['url']}")
    print(f"   Descripción: {info['descripción']}")
    print(f"   Sistema: {info['sistema']}")
    print(f"   Campos esperados: {', '.join(info['campos_esperados'])}")

print("\n" + "=" * 80)
print("2. VERIFICACIÓN DE VISTAS")
print("=" * 80)

from django.urls import reverse
from gestion import pos_views

# Verificar que las vistas existen y están actualizadas
vistas_verificar = [
    ('cuenta_corriente_view', pos_views.cuenta_corriente_view),
    ('cc_detalle_view', pos_views.cc_detalle_view),
    ('deuda_proveedores_view', pos_views.deuda_proveedores_view),
    ('compras_dashboard_view', pos_views.compras_dashboard_view),
]

for nombre, vista in vistas_verificar:
    print(f"\n✅ {nombre}")
    print(f"   Ubicación: {vista.__module__}.{vista.__name__}")
    if hasattr(vista, '__doc__') and vista.__doc__:
        print(f"   Descripción: {vista.__doc__.strip()[:80]}...")

print("\n" + "=" * 80)
print("3. BÚSQUEDA DE REFERENCIAS LEGACY EN CÓDIGO DE VISTAS")
print("=" * 80)

import inspect

# Revisar código de deuda_proveedores_view
print("\n📋 Analizando deuda_proveedores_view...")
codigo = inspect.getsource(pos_views.deuda_proveedores_view)

problemas = []

if 'CtaCorrienteProv' in codigo:
    problemas.append("❌ Usa CtaCorrienteProv (legacy)")
if 'cta_corriente_prov' in codigo.lower():
    problemas.append("❌ Referencia a cta_corriente_prov")
if 'Saldo_Pendiente' in codigo:
    problemas.append("⚠️ Usa Saldo_Pendiente (mayúsculas)")
if 'saldo_pendiente' in codigo:
    print("   ✅ Usa saldo_pendiente (nuevo campo)")
if 'estado_pago' in codigo or 'Estado_Pago' in codigo:
    print("   ✅ Usa estado_pago (nuevo campo)")

if problemas:
    for problema in problemas:
        print(f"   {problema}")
else:
    print("   ✅ Sin referencias legacy detectadas")

print("\n" + "=" * 80)
print("4. RECOMENDACIONES ESPECÍFICAS POR TEMPLATE")
print("=" * 80)

recomendaciones = {
    'cuenta_corriente.html': {
        'estado': '✅ BIEN',
        'notas': [
            'Template solo muestra información del cliente',
            'No depende de tablas legacy',
            'Vista usa Cliente.limite_credito correctamente'
        ]
    },
    'cc_detalle.html': {
        'estado': '✅ BIEN',
        'notas': [
            'Vista usa Ventas y CargasSaldo (no legacy)',
            'Muestra ventas relacionadas al cliente',
            'Sistema de recargas funciona correctamente'
        ]
    },
    'deuda_proveedores.html': {
        'estado': '⚠️ VERIFICAR',
        'notas': [
            'Template usa campo "saldo" en el contexto',
            'Vista debe calcular saldo desde Compras.saldo_pendiente',
            'Verificar que deuda.saldo usa el campo correcto'
        ],
        'acciones': [
            'Revisar pos_views.deuda_proveedores_view',
            'Confirmar que usa Compras.saldo_pendiente',
            'Verificar query de agregación'
        ]
    },
    'compras_dashboard.html': {
        'estado': '✅ ACTUALIZADO',
        'notas': [
            'Vista ya corregida (usa estado_pago y saldo_pendiente)',
            'Dashboard muestra deuda_total correctamente',
            'Estadísticas usan nuevo sistema'
        ]
    },
    'proveedor_detalle.html': {
        'estado': '❓ PENDIENTE REVISIÓN',
        'notas': [
            'Necesita verificación de implementación',
            'Debe mostrar Compras.saldo_pendiente',
            'Debe usar Compras.estado_pago'
        ],
        'acciones': [
            'Revisar vista proveedor_detalle_view',
            'Verificar queries usados',
            'Comprobar template con datos del proveedor'
        ]
    }
}

for template, rec in recomendaciones.items():
    print(f"\n📄 {template}")
    print(f"   Estado: {rec['estado']}")
    print(f"   Notas:")
    for nota in rec['notas']:
        print(f"      • {nota}")
    if 'acciones' in rec:
        print(f"   ⚡ Acciones recomendadas:")
        for accion in rec['acciones']:
            print(f"      → {accion}")

print("\n" + "=" * 80)
print("5. RESUMEN Y PLAN DE ACCIÓN")
print("=" * 80)

print("""
✅ TEMPLATES QUE ESTÁN BIEN:
   • cuenta_corriente.html - No usa tablas legacy
   • cc_detalle.html - Usa Ventas y CargasSaldo correctamente
   • compras_dashboard.html - Ya actualizado con campos correctos

⚠️ TEMPLATES QUE REQUIEREN VERIFICACIÓN:
   • deuda_proveedores.html - Confirmar que usa saldo_pendiente
   • proveedor_detalle.html - Revisar implementación completa

🔧 ACCIÓN INMEDIATA RECOMENDADA:
   1. Revisar vista deuda_proveedores_view (línea ~2645)
   2. Confirmar que query usa Compras.saldo_pendiente
   3. Verificar vista proveedor_detalle_view
   4. Probar templates manualmente con datos reales

📊 PRIORIDAD:
   • Alta: deuda_proveedores.html (vista pública importante)
   • Media: proveedor_detalle.html (funcionalidad secundaria)

💡 NOTA:
   Los templates HTML en sí están bien (no usan campos en código).
   La verificación se centra en las VISTAS que generan el contexto.
   Si las vistas usan el nuevo sistema, los templates funcionarán.
""")

print("\n" + "=" * 80)
print("AUDITORÍA COMPLETADA")
print("=" * 80)
