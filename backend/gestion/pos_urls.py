from django.urls import path
from . import pos_views_basicas as pos_views

app_name = 'pos'

urlpatterns = [
    # Dashboard principal POS
    path('', pos_views.dashboard, name='dashboard'),
    path('dashboard/', pos_views.dashboard, name='dashboard_pos'),
    
    # Funciones básicas existentes
    path('venta/', pos_views.venta, name='venta'),
    path('recargas/', pos_views.recargas, name='recargas'),
    path('inventario/', pos_views.inventario_dashboard, name='inventario_dashboard'),
    path('inventario/productos/', pos_views.inventario_dashboard, name='inventario_productos'),
    path('cuenta-corriente/', pos_views.cuenta_corriente, name='cuenta_corriente'),
    path('reportes/', pos_views.reportes, name='reportes'),
    
    # Nuevas rutas POS
    path('historial/', pos_views.historial_ventas, name='historial'),
    path('cierre-caja/', pos_views.cierre_caja, name='cierre_caja'),
    path('clientes/', pos_views.gestionar_clientes, name='gestionar_clientes'),
]