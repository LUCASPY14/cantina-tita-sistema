"""
Views básicas para módulo POS - Implementación Fase 1
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from gestion.models import *

@login_required  
def dashboard(request):
    """Dashboard principal POS"""
    context = {
        'title': 'POS - Dashboard',
        'ventas_hoy': Ventas.objects.filter(fecha_venta__date=timezone.now().date()).count(),
        'productos_activos': Producto.objects.filter(activo=True).count()
    }
    return render(request, 'apps/pos/dashboard/dashboard.html', context)

@login_required
def inventario_dashboard(request):
    """Dashboard de inventario"""
    context = {
        'title': 'Inventario - Dashboard',
        'productos_stock_bajo': Producto.objects.filter(stock__lte=F('stock_minimo')).count()
    }
    return render(request, 'apps/pos/inventario/dashboard.html', context)

@login_required
def reportes(request):
    """Reportes POS"""
    context = {'title': 'Reportes POS'}
    return render(request, 'apps/pos/reportes/index.html', context)

@login_required
def venta(request):
    """Interfaz de venta POS"""
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    context = {
        'title': 'Nueva Venta',
        'productos': productos
    }
    return render(request, 'apps/pos/ventas/nueva_venta.html', context)

@login_required
def recargas(request):
    """Gestión de recargas"""
    context = {'title': 'Recargas'}
    return render(request, 'apps/pos/recargas/index.html', context)

@login_required
def cuenta_corriente(request):
    """Cuenta corriente"""
    context = {'title': 'Cuenta Corriente'}
    return render(request, 'apps/pos/cuenta_corriente/index.html', context)
