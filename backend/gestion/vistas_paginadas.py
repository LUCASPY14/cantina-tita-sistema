"""
Vistas para gestión de productos con paginación
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F
from django.http import JsonResponse
from gestion.models import Producto, StockUnico, Categoria, UnidadMedida
from gestion.pagination import StandardPagination


@login_required
def productos_lista(request):
    """
    Vista paginada de productos con filtros
    """
    # Obtener productos con relaciones
    productos_query = Producto.objects.select_related(
        'id_categoria',
        'id_unidad_medida'
    ).all()
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    categoria_id = request.GET.get('categoria', '')
    estado_stock = request.GET.get('estado_stock', '')
    
    # Aplicar filtros
    if buscar:
        productos_query = productos_query.filter(
            Q(descripcion__icontains=buscar) |
            Q(codigo_barra__icontains=buscar)
        )
    
    if categoria_id:
        productos_query = productos_query.filter(id_categoria_id=categoria_id)
    
    if estado_stock:
        if estado_stock == 'sin_stock':
            # Productos con stock 0 o sin registro de stock
            productos_con_stock = StockUnico.objects.filter(
                cantidad__lte=0
            ).values_list('id_producto_id', flat=True)
            productos_query = productos_query.filter(id__in=productos_con_stock)
        elif estado_stock == 'bajo':
            # Productos con stock bajo
            productos_con_stock = StockUnico.objects.filter(
                cantidad__gt=0,
                cantidad__lt=F('stock_minimo')
            ).values_list('id_producto_id', flat=True)
            productos_query = productos_query.filter(id__in=productos_con_stock)
        elif estado_stock == 'normal':
            # Productos con stock normal
            productos_con_stock = StockUnico.objects.filter(
                cantidad__gte=F('stock_minimo')
            ).values_list('id_producto_id', flat=True)
            productos_query = productos_query.filter(id__in=productos_con_stock)
    
    # Ordenar
    productos_query = productos_query.order_by('descripcion')
    
    # Paginar
    paginator = StandardPagination()
    productos = paginator.paginate_queryset(productos_query, request)
    
    # Estadísticas
    productos_en_stock = StockUnico.objects.filter(cantidad__gt=0).values_list('id_producto_id', flat=True)
    productos_bajo_stock = StockUnico.objects.filter(
        cantidad__gt=0,
        cantidad__lt=F('stock_minimo')
    ).values_list('id_producto_id', flat=True)
    productos_sin_stock = StockUnico.objects.filter(cantidad__lte=0).values_list('id_producto_id', flat=True)
    
    stats = {
        'en_stock': len(productos_en_stock),
        'stock_bajo': len(productos_bajo_stock),
        'sin_stock': len(productos_sin_stock),
    }
    
    # Categorías para filtro
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'productos': productos,
        'stats': stats,
        'categorias': categorias,
        'buscar': buscar,
        'categoria_id': categoria_id,
        'estado_stock': estado_stock,
    }
    
    return render(request, 'gestion/productos_lista.html', context)


@login_required
def clientes_lista(request):
    """
    Vista paginada de clientes con filtros
    """
    from gestion.models import Cliente, TipoCliente
    
    # Obtener clientes con anotaciones
    clientes_query = Cliente.objects.select_related(
        'id_tipo_cliente'
    ).annotate(
        num_hijos=Count('hijos')
    ).all()
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    estado = request.GET.get('estado', '')
    tipo_id = request.GET.get('tipo', '')
    
    # Aplicar filtros
    if buscar:
        clientes_query = clientes_query.filter(
            Q(nombres__icontains=buscar) |
            Q(apellidos__icontains=buscar) |
            Q(ruc_ci__icontains=buscar) |
            Q(email__icontains=buscar)
        )
    
    if estado:
        clientes_query = clientes_query.filter(activo=(estado == 'activo'))
    
    if tipo_id:
        clientes_query = clientes_query.filter(id_tipo_cliente_id=tipo_id)
    
    # Ordenar
    clientes_query = clientes_query.order_by('apellidos', 'nombres')
    
    # Paginar
    paginator = StandardPagination()
    clientes = paginator.paginate_queryset(clientes_query, request)
    
    # Estadísticas
    stats = {
        'activos': Cliente.objects.filter(activo=True).count(),
        'con_hijos': Cliente.objects.annotate(
            num_hijos=Count('hijos')
        ).filter(num_hijos__gt=0).count(),
        'con_credito': Cliente.objects.filter(
            limite_credito__gt=0
        ).count(),
    }
    
    # Tipos de cliente para filtro
    tipos_cliente = TipoCliente.objects.filter(activo=True).order_by('descripcion')
    
    context = {
        'clientes': clientes,
        'stats': stats,
        'tipos_cliente': tipos_cliente,
        'buscar': buscar,
        'estado': estado,
        'tipo_id': tipo_id,
    }
    
    return render(request, 'gestion/clientes_lista.html', context)


@login_required
def ventas_lista(request):
    """
    Vista paginada de ventas con filtros
    """
    from pos.models import Venta as Ventas
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum
    
    # Obtener ventas con relaciones
    ventas_query = Ventas.objects.select_related(
        'id_cliente'
    ).all()
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    cliente = request.GET.get('cliente', '')
    estado = request.GET.get('estado', '')
    medio_pago = request.GET.get('medio_pago', '')
    
    # Fechas por defecto (últimos 30 días)
    if not fecha_desde and not fecha_hasta:
        fecha_hasta = timezone.now().date()
        fecha_desde = fecha_hasta - timedelta(days=30)
    
    # Aplicar filtros
    if fecha_desde:
        ventas_query = ventas_query.filter(fecha__date__gte=fecha_desde)
    
    if fecha_hasta:
        ventas_query = ventas_query.filter(fecha__date__lte=fecha_hasta)
    
    if cliente:
        ventas_query = ventas_query.filter(
            Q(id_cliente__nombres__icontains=cliente) |
            Q(id_cliente__apellidos__icontains=cliente) |
            Q(id_cliente__ruc_ci__icontains=cliente)
        )
    
    if estado:
        ventas_query = ventas_query.filter(estado=estado)
    
    if medio_pago:
        ventas_query = ventas_query.filter(medio_pago=medio_pago)
    
    # Ordenar
    ventas_query = ventas_query.order_by('-fecha')
    
    # Paginar
    paginator = StandardPagination()
    ventas = paginator.paginate_queryset(ventas_query, request)
    
    # Estadísticas
    stats_query = Ventas.objects.all()
    if fecha_desde:
        stats_query = stats_query.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        stats_query = stats_query.filter(fecha__date__lte=fecha_hasta)
    
    stats_data = stats_query.aggregate(
        monto_total=Sum('total'),
        pendientes=Count('id_venta', filter=Q(estado='Pendiente'))
    )
    
    total_ventas = stats_query.count()
    
    stats = {
        'monto_total': stats_data['monto_total'] or 0,
        'pendientes': stats_data['pendientes'] or 0,
        'promedio': (stats_data['monto_total'] / total_ventas) if total_ventas > 0 else 0,
    }
    
    context = {
        'ventas': ventas,
        'stats': stats,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cliente': cliente,
        'estado': estado,
        'medio_pago': medio_pago,
    }
    
    return render(request, 'gestion/ventas_lista.html', context)
