"""
GUÍA DE OPTIMIZACIÓN DE QUERIES DJANGO
Mejores prácticas y ejemplos para optimizar performance
"""

# ========================================
# 1. PROBLEMA N+1 - SOLUCIÓN select_related()
# ========================================

# ❌ MAL - Genera N+1 queries
ventas = Ventas.objects.all()
for venta in ventas:
    print(venta.usuario.nombre)  # Query adicional por cada venta
    print(venta.cliente.nombre)  # Otra query por cada venta

# ✅ BIEN - Una sola query con JOIN
ventas = Ventas.objects.select_related('usuario', 'cliente').all()
for venta in ventas:
    print(venta.usuario.nombre)  # Sin query adicional
    print(venta.cliente.nombre)  # Sin query adicional


# ========================================
# 2. RELACIONES MANY-TO-MANY - prefetch_related()
# ========================================

# ❌ MAL
productos = Producto.objects.all()
for producto in productos:
    categorias = producto.categorias.all()  # Query por cada producto

# ✅ BIEN
productos = Producto.objects.prefetch_related('categorias').all()
for producto in productos:
    categorias = producto.categorias.all()  # Sin queries adicionales


# ========================================
# 3. QUERIES ESPECÍFICAS - only() y defer()
# ========================================

# ❌ MAL - Carga todos los campos
productos = Producto.objects.all()  # SELECT * FROM productos

# ✅ BIEN - Solo campos necesarios
productos = Producto.objects.only('id', 'nombre', 'precio')
# SELECT id, nombre, precio FROM productos

# ✅ BIEN - Excluir campos grandes
productos = Producto.objects.defer('descripcion_larga', 'imagen')


# ========================================
# 4. CONTADORES - count() vs len()
# ========================================

# ❌ MAL - Carga todos los objetos
ventas = Ventas.objects.all()
total = len(ventas)  # Carga todos en memoria

# ✅ BIEN - COUNT en BD
total = Ventas.objects.count()  # SELECT COUNT(*) FROM ventas


# ========================================
# 5. EXISTEN REGISTROS - exists()
# ========================================

# ❌ MAL
if Ventas.objects.filter(fecha=today).count() > 0:
    pass

# ✅ BIEN
if Ventas.objects.filter(fecha=today).exists():
    pass


# ========================================
# 6. PAGINACIÓN - Evitar offset grandes
# ========================================

from django.core.paginator import Paginator

# ❌ MAL - offset grande es lento
productos = Producto.objects.all()
paginator = Paginator(productos, 25)
page = paginator.page(100)  # OFFSET 2475

# ✅ BIEN - Usar cursor (keyset pagination)
ultimo_id = request.GET.get('ultimo_id', 0)
productos = Producto.objects.filter(id__gt=ultimo_id).order_by('id')[:25]


# ========================================
# 7. BULK OPERATIONS
# ========================================

# ❌ MAL - Query por cada insert
for i in range(1000):
    Producto.objects.create(nombre=f"Producto {i}")

# ✅ BIEN - Un solo INSERT
productos = [
    Producto(nombre=f"Producto {i}")
    for i in range(1000)
]
Producto.objects.bulk_create(productos, batch_size=100)

# ✅ BIEN - Update masivo
Producto.objects.filter(categoria_id=5).update(activo=True)


# ========================================
# 8. CACHE DE QUERIES
# ========================================

from django.core.cache import cache

def get_productos_activos():
    cache_key = 'productos_activos'
    productos = cache.get(cache_key)
    
    if productos is None:
        productos = list(
            Producto.objects
            .filter(activo=True)
            .select_related('categoria')
            .values('id', 'nombre', 'precio', 'categoria__nombre')
        )
        cache.set(cache_key, productos, 300)  # 5 minutos
    
    return productos


# ========================================
# 9. RAW SQL PARA QUERIES COMPLEJAS
# ========================================

from django.db import connection

def reporte_ventas_optimizado(fecha_inicio, fecha_fin):
    """
    Para queries muy complejas, usar raw SQL puede ser más eficiente
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.nombre,
                SUM(dv.cantidad) as total_vendido,
                SUM(dv.subtotal) as total_ingresos
            FROM detalle_venta dv
            INNER JOIN productos p ON dv.producto_id = p.id
            INNER JOIN ventas v ON dv.venta_id = v.id
            WHERE v.fecha BETWEEN %s AND %s
            GROUP BY p.id, p.nombre
            ORDER BY total_ingresos DESC
            LIMIT 10
        """, [fecha_inicio, fecha_fin])
        
        results = cursor.fetchall()
        
    return [
        {
            'producto': row[0],
            'cantidad': row[1],
            'ingresos': row[2]
        }
        for row in results
    ]


# ========================================
# 10. ÍNDICES EN MODELOS
# ========================================

# Agregar en models.py

class Ventas(models.Model):
    fecha = models.DateField(db_index=True)  # Crea índice
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_index=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        # Índices compuestos
        indexes = [
            models.Index(fields=['fecha', 'usuario']),
            models.Index(fields=['-fecha']),  # Para ORDER BY fecha DESC
        ]
        # Ordenamiento por defecto
        ordering = ['-fecha']


# ========================================
# 11. AGREGACIONES OPTIMIZADAS
# ========================================

from django.db.models import Sum, Count, Avg, F, Q

# ❌ MAL
ventas = Ventas.objects.filter(fecha=today)
total = 0
for venta in ventas:
    total += venta.total

# ✅ BIEN
total = Ventas.objects.filter(fecha=today).aggregate(
    total=Sum('total')
)['total']

# ✅ MUY BIEN - Múltiples agregaciones
estadisticas = Ventas.objects.filter(fecha=today).aggregate(
    total_ventas=Sum('total'),
    cantidad_ventas=Count('id'),
    promedio=Avg('total')
)


# ========================================
# 12. F() EXPRESSIONS - Operaciones en BD
# ========================================

# ❌ MAL - Carga en memoria y actualiza
productos = Producto.objects.filter(categoria_id=5)
for producto in productos:
    producto.precio = producto.precio * 1.1
    producto.save()

# ✅ BIEN - Operación en BD
Producto.objects.filter(categoria_id=5).update(
    precio=F('precio') * 1.1
)


# ========================================
# 13. QUERIES CONDICIONALES - Q()
# ========================================

from django.db.models import Q

# Búsqueda compleja
productos = Producto.objects.filter(
    Q(nombre__icontains='coca') | Q(codigo__icontains='CC'),
    activo=True
).select_related('categoria')


# ========================================
# 14. VALORES ESPECÍFICOS - values()
# ========================================

# ❌ MAL - Carga objetos completos
productos = Producto.objects.all()
nombres = [p.nombre for p in productos]

# ✅ BIEN - Solo valores necesarios
nombres = Producto.objects.values_list('nombre', flat=True)

# ✅ BIEN - Diccionarios
productos_dict = Producto.objects.values('id', 'nombre', 'precio')


# ========================================
# 15. TRANSACCIONES PARA CONSISTENCIA
# ========================================

from django.db import transaction

@transaction.atomic
def procesar_venta(venta_data):
    """
    Todas las operaciones en una transacción
    Si algo falla, todo se revierte
    """
    venta = Ventas.objects.create(**venta_data)
    
    for item in venta_data['items']:
        DetalleVenta.objects.create(
            venta=venta,
            producto_id=item['producto_id'],
            cantidad=item['cantidad']
        )
        
        # Actualizar stock
        producto = Producto.objects.select_for_update().get(id=item['producto_id'])
        producto.stock -= item['cantidad']
        producto.save()
    
    return venta


# ========================================
# 16. DEBUGGING DE QUERIES
# ========================================

from django.db import connection
from django.test.utils import override_settings

# Ver queries ejecutadas
@override_settings(DEBUG=True)
def debug_queries():
    productos = Producto.objects.select_related('categoria').all()[:10]
    
    print(f"Queries ejecutadas: {len(connection.queries)}")
    for query in connection.queries:
        print(query['sql'])
        print(f"Tiempo: {query['time']}s")


# ========================================
# 17. EJEMPLO COMPLETO OPTIMIZADO
# ========================================

def dashboard_ventas(fecha_inicio, fecha_fin):
    """
    Dashboard optimizado con todas las mejores prácticas
    """
    from django.core.cache import cache
    from django.db.models import Sum, Count, Avg
    
    cache_key = f'dashboard_ventas_{fecha_inicio}_{fecha_fin}'
    resultado = cache.get(cache_key)
    
    if resultado is None:
        # Query optimizada con agregaciones
        ventas = (
            Ventas.objects
            .filter(fecha__range=[fecha_inicio, fecha_fin])
            .select_related('usuario', 'cliente')
            .prefetch_related('detalleventa_set__producto')
            .only(
                'id', 'fecha', 'total', 'estado',
                'usuario__nombre', 'cliente__nombre'
            )
        )
        
        # Estadísticas en una sola query
        stats = ventas.aggregate(
            total_ventas=Sum('total'),
            cantidad=Count('id'),
            promedio=Avg('total')
        )
        
        # Top productos (raw SQL para performance)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.nombre,
                    SUM(dv.cantidad) as cantidad,
                    SUM(dv.subtotal) as total
                FROM detalle_venta dv
                INNER JOIN productos p ON dv.producto_id = p.id
                INNER JOIN ventas v ON dv.venta_id = v.id
                WHERE v.fecha BETWEEN %s AND %s
                GROUP BY p.id
                ORDER BY cantidad DESC
                LIMIT 5
            """, [fecha_inicio, fecha_fin])
            
            top_productos = cursor.fetchall()
        
        resultado = {
            'ventas': list(ventas),
            'estadisticas': stats,
            'top_productos': top_productos
        }
        
        # Cache por 5 minutos
        cache.set(cache_key, resultado, 300)
    
    return resultado


# ========================================
# CHECKLIST DE OPTIMIZACIÓN
# ========================================

"""
[ ] ¿Uso select_related() para ForeignKey?
[ ] ¿Uso prefetch_related() para ManyToMany?
[ ] ¿Uso only() o defer() para campos específicos?
[ ] ¿Uso count() en lugar de len()?
[ ] ¿Uso exists() para verificar existencia?
[ ] ¿Uso bulk_create() para inserts masivos?
[ ] ¿Uso update() para actualizaciones masivas?
[ ] ¿Cacheo queries frecuentes?
[ ] ¿Uso values() cuando no necesito objetos?
[ ] ¿Tengo índices en campos filtrados frecuentemente?
[ ] ¿Uso transacciones para operaciones complejas?
[ ] ¿Evito queries en loops?
[ ] ¿Uso paginación en listados grandes?
"""
