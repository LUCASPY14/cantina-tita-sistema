from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone
from .models import Producto, Cliente, Proveedor
# from .models import Venta, CompraProveedor  # Estos modelos están deshabilitados por ahora


def index(request):
    """Vista principal del sistema"""
    context = {
        'titulo': 'Sistema de Gestión de Cantina'
    }
    return render(request, 'gestion/index.html', context)


@login_required
def dashboard(request):
    """Dashboard con estadísticas del sistema"""
    
    # Estadísticas generales
    total_productos = Producto.objects.filter(activo=True).count()
    # productos_bajo_stock = Producto.objects.filter(
    #     activo=True,
    #     stock__lte=F('stock_minimo')
    # ).count()
    productos_bajo_stock = 0  # Temporalmente deshabilitado
    
    total_clientes = Cliente.objects.filter(activo=True).count()
    
    # Estadísticas de ventas (temporalmente deshabilitadas)
    # ventas_hoy = Venta.objects.filter(
    #     fecha_venta__date=timezone.now().date(),
    #     estado='completada'
    # )
    # total_ventas_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    # cantidad_ventas_hoy = ventas_hoy.count()
    total_ventas_hoy = 0
    cantidad_ventas_hoy = 0
    
    context = {
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'total_clientes': total_clientes,
        'total_ventas_hoy': total_ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
    }
    
    return render(request, 'gestion/dashboard.html', context)

