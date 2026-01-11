"""
Ejemplos de vistas con paginación optimizada
Usar estos patrones para implementar paginación en vistas existentes
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch

from .models import Producto, Cliente, Categoria, StockUnico
from .cache_reportes import ReporteCache


@login_required
def productos_list_paginado(request):
    """
    EJEMPLO: Lista de productos con paginación, filtros y cache
    
    Características:
    - Paginación de 25 items por página
    - Filtros: búsqueda, categoría, estado
    - Optimización de queries con select_related
    - Cache de resultados
    """
    # Parámetros de filtro
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    activo = request.GET.get('activo', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 25))
    
    # Query base optimizado
    productos = Producto.objects.select_related(
        'categoria',
        'stock_unico'
    ).filter(
        activo=True  # Base filter
    )
    
    # Aplicar filtros
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if activo != '':
        productos = productos.filter(activo=(activo == '1'))
    
    # Ordenar
    productos = productos.order_by('nombre')
    
    # Paginación
    paginator = Paginator(productos, per_page)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Obtener categorías para filtro
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'productos': page_obj,  # Alias para compatibilidad
        'categorias': categorias,
        'cache_activo': True,  # Si se usa cache
    }
    
    return render(request, 'gestion/ejemplos/productos_list_paginado.html', context)


@login_required
def clientes_list_paginado(request):
    """
    EJEMPLO: Lista de clientes con paginación y filtros
    
    Características:
    - Paginación de 30 items por página
    - Filtros: búsqueda, tipo, estado
    - Búsqueda por múltiples campos
    """
    # Parámetros
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    activo = request.GET.get('activo', '')
    page = request.GET.get('page', 1)
    
    # Query base
    clientes = Cliente.objects.filter(activo=True)
    
    # Búsqueda multi-campo
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(documento__icontains=query) |
            Q(codigo_cliente__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    if tipo:
        clientes = clientes.filter(tipo_cliente=tipo)
    
    if activo != '':
        clientes = clientes.filter(activo=(activo == '1'))
    
    # Ordenar
    clientes = clientes.order_by('apellido', 'nombre')
    
    # Paginación (30 por página)
    paginator = Paginator(clientes, 30)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'clientes': page_obj,
    }
    
    return render(request, 'gestion/ejemplos/clientes_list_paginado.html', context)


@login_required
def ventas_list_paginado(request):
    """
    EJEMPLO: Lista de ventas con paginación, filtros y cache
    
    Características:
    - Paginación de 20 items por página
    - Filtros: fecha, cliente, cajero, estado
    - Optimización con select_related para FKs
    - Cache opcional de resultados
    """
    from .models import PuntoVentaConsumo
    from datetime import datetime, timedelta
    
    # Parámetros
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    cliente_id = request.GET.get('cliente', '')
    estado = request.GET.get('estado', '')
    page = request.GET.get('page', 1)
    
    # Query base optimizado
    ventas = PuntoVentaConsumo.objects.select_related(
        'cliente',
        'cajero'
    ).all()
    
    # Filtros de fecha
    if fecha_inicio:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        ventas = ventas.filter(fecha_hora__gte=fecha_inicio_dt)
    else:
        # Por defecto: últimos 30 días
        fecha_inicio_dt = datetime.now() - timedelta(days=30)
        ventas = ventas.filter(fecha_hora__gte=fecha_inicio_dt)
    
    if fecha_fin:
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        ventas = ventas.filter(fecha_hora__lte=fecha_fin_dt)
    
    # Otros filtros
    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    # Ordenar por más reciente
    ventas = ventas.order_by('-fecha_hora')
    
    # Paginación (20 por página para ventas)
    paginator = Paginator(ventas, 20)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Clientes para filtro (activos con consumos)
    clientes_con_consumos = Cliente.objects.filter(
        activo=True,
        puntoventaconsumo__isnull=False
    ).distinct().order_by('apellido', 'nombre')[:100]  # Limitar para performance
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'ventas': page_obj,
        'clientes': clientes_con_consumos,
    }
    
    return render(request, 'gestion/ventas_list_paginado.html', context)


# PATRÓN ALTERNATIVO: Paginación AJAX con JSON
@login_required
def productos_api_paginado(request):
    """
    EJEMPLO: API JSON para paginación AJAX
    Retorna datos en formato JSON para cargar con JavaScript
    """
    from django.http import JsonResponse
    
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 25))
    query = request.GET.get('q', '')
    
    # Query
    productos = Producto.objects.select_related('categoria').filter(activo=True)
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(productos, per_page)
    page_obj = paginator.get_page(page)
    
    # Serializar datos
    data = {
        'productos': [
            {
                'id': p.id,
                'codigo': p.codigo,
                'nombre': p.nombre,
                'precio': float(p.precio_venta),
                'categoria': p.categoria.nombre if p.categoria else None,
            }
            for p in page_obj
        ],
        'pagination': {
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_count': paginator.count,
        }
    }
    
    return JsonResponse(data)


# PATRÓN: Paginación con cache
@login_required
def reportes_list_con_cache(request):
    """
    EJEMPLO: Lista con cache de resultados
    Útil para reportes o consultas costosas
    """
    from django.core.cache import cache
    
    page = request.GET.get('page', 1)
    filtros = request.GET.get('filtros', '')
    
    # Generar cache key
    cache_key = f'reportes_list:page_{page}:filtros_{filtros}'
    
    # Intentar obtener de cache
    data = cache.get(cache_key)
    
    if data is None:
        # Cache miss - generar datos
        # ... query pesado ...
        
        # Guardar en cache (10 minutos)
        cache.set(cache_key, data, 600)
    
    return render(request, 'gestion/reportes_list.html', data)
