from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Producto, Cliente, Proveedor
from .reportes import ReportesPDF, ReportesExcel
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


# =============================================================================
# VISTAS PARA REPORTES
# =============================================================================

@login_required
def reporte_ventas_pdf(request):
    """Genera reporte de ventas en PDF con filtros avanzados"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    id_cliente = request.GET.get('id_cliente')
    id_cajero = request.GET.get('id_cajero')
    estado = request.GET.get('estado')
    id_tipo_pago = request.GET.get('id_tipo_pago')
    monto_minimo = request.GET.get('monto_minimo')
    monto_maximo = request.GET.get('monto_maximo')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesPDF.reporte_ventas(
        fecha_inicio, fecha_fin, id_cliente, id_cajero,
        estado, id_tipo_pago, monto_minimo, monto_maximo
    )


@login_required
def reporte_ventas_excel(request):
    """Genera reporte de ventas en Excel con filtros avanzados"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    id_cliente = request.GET.get('id_cliente')
    id_cajero = request.GET.get('id_cajero')
    estado = request.GET.get('estado')
    id_tipo_pago = request.GET.get('id_tipo_pago')
    monto_minimo = request.GET.get('monto_minimo')
    monto_maximo = request.GET.get('monto_maximo')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesExcel.reporte_ventas(
        fecha_inicio, fecha_fin, id_cliente, id_cajero,
        estado, id_tipo_pago, monto_minimo, monto_maximo
    )


@login_required
def reporte_productos_pdf(request):
    """Genera reporte de productos en PDF con filtro de categoría"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    id_categoria = request.GET.get('id_categoria')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesPDF.reporte_productos_vendidos(fecha_inicio, fecha_fin, id_categoria)


@login_required
def reporte_productos_excel(request):
    """Genera reporte de productos en Excel con filtro de categoría"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    id_categoria = request.GET.get('id_categoria')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesExcel.reporte_productos_vendidos(fecha_inicio, fecha_fin, id_categoria)


@login_required
def reporte_inventario_pdf(request):
    """Genera reporte de inventario en PDF"""
    return ReportesPDF.reporte_inventario()


@login_required
def reporte_inventario_excel(request):
    """Genera reporte de inventario en Excel"""
    return ReportesExcel.reporte_inventario()


@login_required
def reporte_consumos_pdf(request):
    """Genera reporte de consumos en PDF"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesPDF.reporte_consumos_tarjeta(fecha_inicio, fecha_fin)


@login_required
def reporte_consumos_excel(request):
    """Genera reporte de consumos en Excel"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesExcel.reporte_consumos_tarjeta(fecha_inicio, fecha_fin)


@login_required
def reporte_clientes_pdf(request):
    """Genera reporte de clientes en PDF"""
    return ReportesPDF.reporte_clientes()


@login_required
def reporte_clientes_excel(request):
    """Genera reporte de clientes en Excel"""
    return ReportesExcel.reporte_clientes()


@login_required
def reporte_cta_corriente_cliente_pdf(request):
    """Genera reporte de cuenta corriente cliente en PDF"""
    id_cliente = request.GET.get('id_cliente', None)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesPDF.reporte_cta_corriente_cliente(id_cliente, fecha_inicio, fecha_fin)


@login_required
def reporte_cta_corriente_cliente_excel(request):
    """Genera reporte de cuenta corriente cliente en Excel"""
    id_cliente = request.GET.get('id_cliente', None)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesExcel.reporte_cta_corriente_cliente(id_cliente, fecha_inicio, fecha_fin)


@login_required
def reporte_cta_corriente_proveedor_pdf(request):
    """Genera reporte de cuenta corriente proveedor en PDF"""
    id_proveedor = request.GET.get('id_proveedor', None)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesPDF.reporte_cta_corriente_proveedor(id_proveedor, fecha_inicio, fecha_fin)


@login_required
def reporte_cta_corriente_proveedor_excel(request):
    """Genera reporte de cuenta corriente proveedor en Excel"""
    id_proveedor = request.GET.get('id_proveedor', None)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    return ReportesExcel.reporte_cta_corriente_proveedor(id_proveedor, fecha_inicio, fecha_fin)


