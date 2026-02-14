from django.urls import path
from . import pos_views_basicas as pos_views_basicas
from . import pos_views

app_name = 'pos'

urlpatterns = [
    # Dashboard principal POS - usando la versión completa
    path('', pos_views.dashboard_view, name='dashboard'),
    path('dashboard/', pos_views.dashboard_view, name='dashboard_pos'),
    
    # Funciones básicas existentes
    path('venta/', pos_views_basicas.venta, name='venta'),
    path('recargas/', pos_views_basicas.recargas, name='recargas'),
    path('inventario/', pos_views_basicas.inventario_dashboard, name='inventario_dashboard'),
    path('inventario/productos/', pos_views_basicas.inventario_dashboard, name='inventario_productos'),
    path('cuenta-corriente/', pos_views_basicas.cuenta_corriente, name='cuenta_corriente'),
    path('reportes/', pos_views_basicas.reportes, name='reportes'),
    
    # Nuevas rutas POS
    path('historial/', pos_views_basicas.historial_ventas, name='historial'),
    path('cierre-caja/', pos_views_basicas.cierre_caja, name='cierre_caja'),
    path('clientes/', pos_views_basicas.gestionar_clientes, name='gestionar_clientes'),
    
    # Dashboard de Almuerzos/Lunch
    path('almuerzos/', pos_views.almuerzos_dashboard_view, name='almuerzos_dashboard'),
    path('almuerzos/planes/', pos_views.planes_almuerzo_view, name='planes_almuerzo_view'),
    path('almuerzos/planes/crear/', pos_views.crear_plan_almuerzo, name='crear_plan_almuerzo'),
    path('almuerzos/registro/', pos_views.registro_consumo_almuerzo_view, name='registro_consumo_almuerzo_view'),
    path('almuerzos/suscripciones/', pos_views.suscripciones_almuerzo_view, name='suscripciones_almuerzo_view'),
    path('almuerzos/reportes/', pos_views.reportes_almuerzos_view, name='reportes_almuerzos_view'),
]