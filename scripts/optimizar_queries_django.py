"""
Script de Optimización de Queries Django
Analiza y optimiza queries N+1 problemáticas
Fecha: 10 Enero 2026
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.db.models import Prefetch
from django.test.utils import override_settings
from gestion import models
import re

class QueryOptimizer:
    """Analizador y optimizador de queries Django"""
    
    def __init__(self):
        self.optimizations = []
        self.query_count_before = 0
        self.query_count_after = 0
    
    def analyze_file(self, filepath):
        """Analiza un archivo Python buscando queries problemáticas"""
        print(f"\n📁 Analizando: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrones de queries problemáticas
        patterns = {
            'filter_without_select': r'\.filter\([^)]+\)(?!\.select_related|\.prefetch_related)',
            'all_without_select': r'\.all\(\)(?!\.select_related|\.prefetch_related)',
            'get_without_select': r'\.get\([^)]+\)(?!\.select_related)',
            'foreign_key_access': r'for\s+\w+\s+in\s+\w+\.all\(\):.*?\.id_\w+\.',
        }
        
        issues = []
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                issues.append({
                    'pattern': pattern_name,
                    'count': len(matches),
                    'examples': matches[:3]  # Primeros 3 ejemplos
                })
        
        if issues:
            print(f"⚠️  Encontrados {len(issues)} tipos de problemas potenciales")
            for issue in issues:
                print(f"   - {issue['pattern']}: {issue['count']} ocurrencias")
        else:
            print(f"✅ No se encontraron problemas evidentes")
        
        return issues
    
    def optimize_ventas_query(self):
        """Optimiza query de ventas con detalles"""
        print("\n" + "="*80)
        print("OPTIMIZACIÓN 1: Ventas con Detalles")
        print("="*80)
        
        # ANTES: Query N+1 problemática
        print("\n❌ ANTES (Query N+1):")
        connection.queries_log.clear()
        
        ventas_bad = models.Ventas.objects.all()[:10]
        for venta in ventas_bad:
            cliente = venta.id_cliente.nombres if venta.id_cliente else "Sin cliente"
            detalles = venta.detalleventa_set.count()
            total = sum([d.total for d in venta.detalleventa_set.all()])
        
        queries_before = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_before}")
        
        # DESPUÉS: Query optimizada
        print("\n✅ DESPUÉS (Optimizado):")
        connection.queries_log.clear()
        
        ventas_good = models.Ventas.objects.select_related(
            'id_cliente',
            'id_empleado',
            'id_documento_tributario'
        ).prefetch_related(
            Prefetch(
                'detalleventa_set',
                queryset=models.DetalleVenta.objects.select_related('id_producto')
            )
        )[:10]
        
        for venta in ventas_good:
            cliente = venta.id_cliente.nombres if venta.id_cliente else "Sin cliente"
            detalles = venta.detalleventa_set.count()
            total = sum([d.total for d in venta.detalleventa_set.all()])
        
        queries_after = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_after}")
        print(f"   📊 Mejora: {queries_before - queries_after} queries menos ({int((1 - queries_after/queries_before)*100)}% reducción)")
        
        self.optimizations.append({
            'nombre': 'Ventas con Detalles',
            'antes': queries_before,
            'despues': queries_after,
            'mejora': queries_before - queries_after
        })
    
    def optimize_tarjetas_query(self):
        """Optimiza query de tarjetas con movimientos"""
        print("\n" + "="*80)
        print("OPTIMIZACIÓN 2: Tarjetas con Movimientos")
        print("="*80)
        
        # ANTES
        print("\n❌ ANTES (Query N+1):")
        connection.queries_log.clear()
        
        tarjetas_bad = models.Tarjeta.objects.all()[:10]
        for tarjeta in tarjetas_bad:
            cliente = tarjeta.id_cliente.nombres if tarjeta.id_cliente else "N/A"
            hijo = tarjeta.id_hijo.nombres if tarjeta.id_hijo else "N/A"
            recargas = tarjeta.cargassaldo_set.count()
            consumos = tarjeta.consumotarjeta_set.count()
        
        queries_before = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_before}")
        
        # DESPUÉS
        print("\n✅ DESPUÉS (Optimizado):")
        connection.queries_log.clear()
        
        tarjetas_good = models.Tarjeta.objects.select_related(
            'id_cliente',
            'id_hijo',
            'id_hijo__id_cliente_responsable'
        ).prefetch_related(
            'cargassaldo_set',
            'consumotarjeta_set'
        )[:10]
        
        for tarjeta in tarjetas_good:
            cliente = tarjeta.id_cliente.nombres if tarjeta.id_cliente else "N/A"
            hijo = tarjeta.id_hijo.nombres if tarjeta.id_hijo else "N/A"
            recargas = tarjeta.cargassaldo_set.count()
            consumos = tarjeta.consumotarjeta_set.count()
        
        queries_after = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_after}")
        print(f"   📊 Mejora: {queries_before - queries_after} queries menos ({int((1 - queries_after/queries_before)*100)}% reducción)")
        
        self.optimizations.append({
            'nombre': 'Tarjetas con Movimientos',
            'antes': queries_before,
            'despues': queries_after,
            'mejora': queries_before - queries_after
        })
    
    def optimize_productos_query(self):
        """Optimiza query de productos con stock y categoría"""
        print("\n" + "="*80)
        print("OPTIMIZACIÓN 3: Productos con Stock")
        print("="*80)
        
        # ANTES
        print("\n❌ ANTES (Query N+1):")
        connection.queries_log.clear()
        
        productos_bad = models.Producto.objects.filter(activo=True)[:20]
        for producto in productos_bad:
            categoria = producto.id_categoria.nombre if producto.id_categoria else "Sin categoría"
            try:
                stock = producto.stock.stock_actual
            except:
                stock = 0
        
        queries_before = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_before}")
        
        # DESPUÉS
        print("\n✅ DESPUÉS (Optimizado):")
        connection.queries_log.clear()
        
        productos_good = models.Producto.objects.filter(
            activo=True
        ).select_related(
            'id_categoria',
            'stock'
        )[:20]
        
        for producto in productos_good:
            categoria = producto.id_categoria.nombre if producto.id_categoria else "Sin categoría"
            try:
                stock = producto.stock.stock_actual
            except:
                stock = 0
        
        queries_after = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_after}")
        print(f"   📊 Mejora: {queries_before - queries_after} queries menos ({int((1 - queries_after/queries_before)*100)}% reducción)")
        
        self.optimizations.append({
            'nombre': 'Productos con Stock',
            'antes': queries_before,
            'despues': queries_after,
            'mejora': queries_before - queries_after
        })
    
    def optimize_clientes_query(self):
        """Optimiza query de clientes con hijos y tarjetas"""
        print("\n" + "="*80)
        print("OPTIMIZACIÓN 4: Clientes con Hijos y Tarjetas")
        print("="*80)
        
        # ANTES
        print("\n❌ ANTES (Query N+1):")
        connection.queries_log.clear()
        
        clientes_bad = models.Cliente.objects.all()[:10]
        for cliente in clientes_bad:
            tipo = cliente.id_tipo_cliente.nombre if cliente.id_tipo_cliente else "Normal"
            hijos = cliente.hijo_set.count()
            tarjetas = models.Tarjeta.objects.filter(id_cliente=cliente).count()
        
        queries_before = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_before}")
        
        # DESPUÉS
        print("\n✅ DESPUÉS (Optimizado):")
        connection.queries_log.clear()
        
        clientes_good = models.Cliente.objects.select_related(
            'id_tipo_cliente'
        ).prefetch_related(
            'hijo_set',
            'tarjeta_set'
        )[:10]
        
        for cliente in clientes_good:
            tipo = cliente.id_tipo_cliente.nombre if cliente.id_tipo_cliente else "Normal"
            hijos = cliente.hijo_set.count()
            tarjetas = cliente.tarjeta_set.count()
        
        queries_after = len(connection.queries)
        print(f"   Queries ejecutadas: {queries_after}")
        print(f"   📊 Mejora: {queries_before - queries_after} queries menos ({int((1 - queries_after/queries_before)*100)}% reducción)")
        
        self.optimizations.append({
            'nombre': 'Clientes con Hijos y Tarjetas',
            'antes': queries_before,
            'despues': queries_after,
            'mejora': queries_before - queries_after
        })
    
    def generate_recommendations(self):
        """Genera recomendaciones de código optimizado"""
        print("\n" + "="*80)
        print("📋 GUÍA DE OPTIMIZACIÓN - PATRONES RECOMENDADOS")
        print("="*80)
        
        recommendations = """
# =============================================================================
# PATRONES DE QUERIES OPTIMIZADAS PARA COPIAR/PEGAR
# =============================================================================

# 1. VENTAS CON DETALLES
# Usar en: pos_views.py, api_views.py, reportes.py
# ------------------------------------------------------------------------------
ventas = Ventas.objects.select_related(
    'id_cliente',
    'id_empleado',
    'id_documento_tributario'
).prefetch_related(
    Prefetch(
        'detalleventa_set',
        queryset=DetalleVenta.objects.select_related('id_producto')
    ),
    'pagosventa_set'
).filter(fecha__range=[fecha_desde, fecha_hasta])


# 2. PRODUCTOS CON STOCK Y CATEGORÍA
# Usar en: pos_views.py (búsqueda productos), api_views.py
# ------------------------------------------------------------------------------
productos = Producto.objects.filter(activo=True).select_related(
    'id_categoria',
    'stock'
).order_by('descripcion')


# 3. TARJETAS CON CLIENTE, HIJO Y MOVIMIENTOS
# Usar en: portal_api.py, pos_views.py (recargas)
# ------------------------------------------------------------------------------
tarjetas = Tarjeta.objects.select_related(
    'id_cliente',
    'id_hijo',
    'id_hijo__id_cliente_responsable'
).prefetch_related(
    Prefetch(
        'cargassaldo_set',
        queryset=CargasSaldo.objects.order_by('-fecha_carga')[:10]
    ),
    Prefetch(
        'consumotarjeta_set',
        queryset=ConsumoTarjeta.objects.order_by('-fecha_consumo')[:10]
    )
).filter(activo=True)


# 4. CLIENTES CON HIJOS Y TARJETAS
# Usar en: cliente_views.py, api_views.py
# ------------------------------------------------------------------------------
clientes = Cliente.objects.select_related(
    'id_tipo_cliente'
).prefetch_related(
    'hijo_set',
    'tarjeta_set'
).filter(activo=True)


# 5. MOVIMIENTOS DE STOCK (KARDEX)
# Usar en: pos_views.py (kardex)
# ------------------------------------------------------------------------------
movimientos = MovimientosStock.objects.select_related(
    'id_producto',
    'id_venta',
    'id_compra'
).filter(
    id_producto=producto,
    fecha_movimiento__range=[fecha_desde, fecha_hasta]
).order_by('-fecha_movimiento')


# 6. DOCUMENTOS TRIBUTARIOS (FACTURACIÓN)
# Usar en: facturacion_views.py
# ------------------------------------------------------------------------------
facturas = DocumentosTributarios.objects.select_related(
    'id_timbrado',
    'id_punto_expedicion'
).prefetch_related(
    Prefetch(
        'ventas_set',
        queryset=Ventas.objects.select_related('id_cliente')
    )
).filter(estado='aceptado')


# 7. ALMUERZOS CON TARJETA Y ESTUDIANTE
# Usar en: almuerzo_views.py
# ------------------------------------------------------------------------------
almuerzos = RegistroConsumoAlmuerzo.objects.select_related(
    'id_tarjeta',
    'id_tarjeta__id_hijo',
    'id_tipo_almuerzo'
).filter(fecha_consumo=hoy).order_by('id_tarjeta__id_hijo__apellidos')


# 8. CUENTA CORRIENTE CLIENTE (OPTIMIZADA)
# Usar en: pos_views.py (cuenta corriente)
# ------------------------------------------------------------------------------
from django.db.models import Sum, Q, F, Value, CharField
from django.db.models.functions import Coalesce

# Query única combinada en lugar de múltiples queries
movimientos = Ventas.objects.filter(
    id_cliente=cliente
).select_related(
    'id_cliente'
).annotate(
    tipo_movimiento=Value('venta', output_field=CharField()),
    debe=F('total'),
    haber=Value(0, output_field=models.DecimalField())
).values('fecha', 'tipo_movimiento', 'debe', 'haber', 'estado').union(
    PagosVenta.objects.filter(
        id_venta__id_cliente=cliente
    ).annotate(
        tipo_movimiento=Value('pago', output_field=CharField()),
        debe=Value(0, output_field=models.DecimalField()),
        haber=F('monto')
    ).values('fecha_pago', 'tipo_movimiento', 'debe', 'haber')
).order_by('-fecha')


# =============================================================================
# ANTIPATRONES A EVITAR
# =============================================================================

# ❌ MALO: Query N+1
for venta in Ventas.objects.all():
    print(venta.id_cliente.nombres)  # Query por cada venta
    for detalle in venta.detalleventa_set.all():  # Query por cada venta
        print(detalle.id_producto.descripcion)  # Query por cada detalle

# ✅ BUENO: Single query con select_related/prefetch_related
ventas = Ventas.objects.select_related('id_cliente').prefetch_related(
    Prefetch('detalleventa_set', queryset=DetalleVenta.objects.select_related('id_producto'))
)
for venta in ventas:
    print(venta.id_cliente.nombres)  # Sin query adicional
    for detalle in venta.detalleventa_set.all():  # Sin query adicional
        print(detalle.id_producto.descripcion)  # Sin query adicional


# ❌ MALO: Usar .count() múltiples veces
total_ventas = Ventas.objects.filter(fecha=hoy).count()
total_productos = Producto.objects.filter(activo=True).count()
total_clientes = Cliente.objects.filter(activo=True).count()

# ✅ BUENO: Aggregate en una sola query
from django.db.models import Count
stats = {
    'ventas': Ventas.objects.filter(fecha=hoy).count(),
    'productos': Producto.objects.filter(activo=True).count(),
    'clientes': Cliente.objects.filter(activo=True).count()
}
# O mejor aún, usar una sola query con subqueries si son del mismo modelo


# ❌ MALO: Loop con queries dentro
productos_bajo_stock = []
for producto in Producto.objects.all():
    if producto.stock.stock_actual < producto.stock_minimo:
        productos_bajo_stock.append(producto)

# ✅ BUENO: Filter con F() objects
from django.db.models import F
productos_bajo_stock = Producto.objects.filter(
    stock__stock_actual__lt=F('stock_minimo')
).select_related('stock')


# =============================================================================
# COMANDO PARA DEBUG DE QUERIES
# =============================================================================

# En settings.py (solo development):
if DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }

# Ver queries en una vista específica:
from django.db import connection
from django.db import reset_queries

reset_queries()
# ... tu código aquí ...
print(f"Queries ejecutadas: {len(connection.queries)}")
for query in connection.queries:
    print(f"{query['time']}s: {query['sql']}")
"""
        
        print(recommendations)
        
        # Guardar en archivo
        output_file = BASE_DIR / 'GUIA_OPTIMIZACION_QUERIES.py'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(recommendations)
        
        print(f"\n✅ Guía guardada en: {output_file}")
    
    def print_summary(self):
        """Imprime resumen de todas las optimizaciones"""
        print("\n" + "="*80)
        print("📊 RESUMEN DE OPTIMIZACIONES")
        print("="*80)
        
        total_before = sum(opt['antes'] for opt in self.optimizations)
        total_after = sum(opt['despues'] for opt in self.optimizations)
        total_saved = total_before - total_after
        
        print(f"\n{'Optimización':<40} {'Antes':>10} {'Después':>10} {'Mejora':>10}")
        print("-" * 80)
        
        for opt in self.optimizations:
            porcentaje = int((1 - opt['despues']/opt['antes'])*100) if opt['antes'] > 0 else 0
            print(f"{opt['nombre']:<40} {opt['antes']:>10} {opt['despues']:>10} {opt['mejora']:>9} (-{porcentaje}%)")
        
        print("-" * 80)
        print(f"{'TOTAL':<40} {total_before:>10} {total_after:>10} {total_saved:>10}")
        
        if total_before > 0:
            total_percentage = int((1 - total_after/total_before)*100)
            print(f"\n🎯 Reducción total: {total_percentage}% de queries")
            print(f"💾 Queries ahorradas: {total_saved}")


def main():
    """Función principal"""
    print("="*80)
    print("🔍 ANALIZADOR Y OPTIMIZADOR DE QUERIES DJANGO")
    print("="*80)
    
    optimizer = QueryOptimizer()
    
    # Analizar archivos críticos
    files_to_analyze = [
        BASE_DIR / 'gestion' / 'pos_views.py',
        BASE_DIR / 'gestion' / 'api_views.py',
        BASE_DIR / 'gestion' / 'portal_api.py',
        BASE_DIR / 'gestion' / 'dashboard_views.py',
    ]
    
    print("\n🔎 FASE 1: Análisis Estático de Código")
    for filepath in files_to_analyze:
        if filepath.exists():
            optimizer.analyze_file(filepath)
    
    print("\n\n🧪 FASE 2: Pruebas de Optimización en Vivo")
    try:
        optimizer.optimize_ventas_query()
        optimizer.optimize_tarjetas_query()
        optimizer.optimize_productos_query()
        optimizer.optimize_clientes_query()
    except Exception as e:
        print(f"⚠️  Error en optimización: {e}")
    
    print("\n\n📚 FASE 3: Generación de Guía")
    optimizer.generate_recommendations()
    
    print("\n\n📈 FASE 4: Resumen Final")
    optimizer.print_summary()
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)


if __name__ == '__main__':
    main()
