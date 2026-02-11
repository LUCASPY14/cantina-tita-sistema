"""
Script de Análisis de Performance de Queries
=============================================

Analiza las vistas existentes y sugiere optimizaciones.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Sum
from django.test.utils import override_settings

from gestion.models import Ventas, Compras


def analyze_query_performance():
    """Analizar performance de queries comunes"""
    print("="*70)
    print("📊 ANÁLISIS DE PERFORMANCE DE QUERIES")
    print("="*70)
    
    # Reset queries
    connection.queries_log.clear()
    
    # Test 1: Ventas pendientes sin optimizar
    print("\n🔍 TEST 1: Ventas pendientes SIN select_related")
    queries_before = len(connection.queries)
    
    ventas = Ventas.objects.filter(estado_pago__in=['PENDIENTE', 'PARCIAL'])[:10]
    for venta in ventas:
        _ = venta.id_cliente.nombres
        _ = venta.id_empleado_cajero.nombre
    
    queries_after = len(connection.queries)
    queries_count = queries_after - queries_before
    
    print(f"   Queries ejecutadas: {queries_count}")
    if queries_count > 5:
        print("   ⚠️ PROBLEMA N+1 detectado")
        print("   💡 Solución: Usar select_related('id_cliente', 'id_empleado_cajero')")
    else:
        print("   ✅ Query optimizado")
    
    # Test 2: Ventas pendientes optimizado
    print("\n🔍 TEST 2: Ventas pendientes CON select_related")
    connection.queries_log.clear()
    queries_before = len(connection.queries)
    
    ventas = Ventas.objects.filter(
        estado_pago__in=['PENDIENTE', 'PARCIAL']
    ).select_related('id_cliente', 'id_empleado_cajero')[:10]
    
    for venta in ventas:
        _ = venta.id_cliente.nombres
        _ = venta.id_empleado_cajero.nombre
    
    queries_after = len(connection.queries)
    queries_count = queries_after - queries_before
    
    print(f"   Queries ejecutadas: {queries_count}")
    if queries_count <= 3:
        print("   ✅ Query optimizado correctamente")
    
    # Test 3: Agregaciones
    print("\n🔍 TEST 3: Agregación de deuda por cliente")
    connection.queries_log.clear()
    queries_before = len(connection.queries)
    
    deudas = Ventas.objects.filter(
        estado_pago__in=['PENDIENTE', 'PARCIAL']
    ).values(
        'id_cliente__nombres'
    ).annotate(
        total=Sum('saldo_pendiente'),
        cantidad=Count('id_venta')
    )[:5]
    
    list(deudas)  # Ejecutar query
    
    queries_after = len(connection.queries)
    queries_count = queries_after - queries_before
    
    print(f"   Queries ejecutadas: {queries_count}")
    if queries_count <= 2:
        print("   ✅ Agregación eficiente")
    
    # Recomendaciones
    print("\n" + "="*70)
    print("💡 RECOMENDACIONES DE OPTIMIZACIÓN")
    print("="*70)
    
    print("\n1. Usar select_related() para ForeignKeys:")
    print("   ✅ .select_related('id_cliente', 'id_empleado_cajero')")
    
    print("\n2. Usar prefetch_related() para relaciones inversas:")
    print("   ✅ .prefetch_related('ventas_set')")
    
    print("\n3. Usar only() para limitar campos:")
    print("   ✅ .only('id_venta', 'monto_total', 'estado_pago')")
    
    print("\n4. Usar exists() en lugar de count() > 0:")
    print("   ✅ .exists() en lugar de .count() > 0")
    
    print("\n5. Usar iterator() para grandes resultados:")
    print("   ✅ .iterator(chunk_size=100)")
    
    print("\n" + "="*70)
    print("🎯 PRÓXIMOS PASOS")
    print("="*70)
    
    print("\n1. Revisar pos_views.py y agregar select_related()")
    print("2. Ejecutar tests de performance:")
    print("   python manage.py test gestion.tests_performance")
    print("3. Verificar mejoras con este script")


def find_optimization_opportunities():
    """Buscar oportunidades de optimización en el código"""
    print("\n" + "="*70)
    print("🔍 BUSCANDO OPORTUNIDADES DE OPTIMIZACIÓN")
    print("="*70)
    
    import re
    from pathlib import Path
    
    # Buscar archivos Python
    gestion_path = Path('gestion')
    python_files = list(gestion_path.glob('**/*.py'))
    
    issues = []
    
    for file in python_files:
        if 'migrations' in str(file) or 'tests' in str(file):
            continue
        
        try:
            content = file.read_text(encoding='utf-8')
            
            # Buscar .filter() sin select_related
            if re.search(r'\.filter\([^)]+\)(?!\.select_related)', content):
                issues.append({
                    'file': file,
                    'type': 'Posible N+1',
                    'suggestion': 'Considerar agregar select_related()'
                })
            
            # Buscar .count() > 0
            if '.count() > 0' in content:
                issues.append({
                    'file': file,
                    'type': 'Performance',
                    'suggestion': 'Usar .exists() en lugar de .count() > 0'
                })
        except:
            pass
    
    if issues:
        print(f"\n⚠️ Encontradas {len(issues)} posibles optimizaciones:\n")
        for i, issue in enumerate(issues[:10], 1):
            print(f"{i}. {issue['file'].name}")
            print(f"   Tipo: {issue['type']}")
            print(f"   💡 {issue['suggestion']}\n")
    else:
        print("\n✅ No se encontraron problemas obvios de performance")


def main():
    """Ejecutar análisis"""
    analyze_query_performance()
    find_optimization_opportunities()
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
