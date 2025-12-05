from django.urls import path
from . import views
from . import almuerzo_views

app_name = 'gestion'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs para reportes PDF
    path('reportes/ventas/pdf/', views.reporte_ventas_pdf, name='reporte_ventas_pdf'),
    path('reportes/productos/pdf/', views.reporte_productos_pdf, name='reporte_productos_pdf'),
    path('reportes/inventario/pdf/', views.reporte_inventario_pdf, name='reporte_inventario_pdf'),
    path('reportes/consumos/pdf/', views.reporte_consumos_pdf, name='reporte_consumos_pdf'),
    path('reportes/clientes/pdf/', views.reporte_clientes_pdf, name='reporte_clientes_pdf'),
    path('reportes/cta-corriente-cliente/pdf/', views.reporte_cta_corriente_cliente_pdf, name='reporte_cta_corriente_cliente_pdf'),
    path('reportes/cta-corriente-proveedor/pdf/', views.reporte_cta_corriente_proveedor_pdf, name='reporte_cta_corriente_proveedor_pdf'),
    
    # URLs para reportes Excel
    path('reportes/ventas/excel/', views.reporte_ventas_excel, name='reporte_ventas_excel'),
    path('reportes/productos/excel/', views.reporte_productos_excel, name='reporte_productos_excel'),
    path('reportes/inventario/excel/', views.reporte_inventario_excel, name='reporte_inventario_excel'),
    path('reportes/consumos/excel/', views.reporte_consumos_excel, name='reporte_consumos_excel'),
    path('reportes/clientes/excel/', views.reporte_clientes_excel, name='reporte_clientes_excel'),
    path('reportes/cta-corriente-cliente/excel/', views.reporte_cta_corriente_cliente_excel, name='reporte_cta_corriente_cliente_excel'),
    path('reportes/cta-corriente-proveedor/excel/', views.reporte_cta_corriente_proveedor_excel, name='reporte_cta_corriente_proveedor_excel'),
    
    # URLs para módulo de almuerzos
    path('pos/almuerzo/', almuerzo_views.pos_almuerzo, name='pos_almuerzo'),
    path('pos/almuerzo/api/', almuerzo_views.pos_almuerzo_api, name='pos_almuerzo_api'),
    path('pos/almuerzo/anular/', almuerzo_views.anular_ultimo_almuerzo, name='anular_almuerzo'),
    path('almuerzo/cuentas/', almuerzo_views.lista_cuentas_mensuales, name='cuentas_mensuales'),
    path('almuerzo/cuentas/generar/', almuerzo_views.generar_cuentas_mes, name='generar_cuentas'),
    path('almuerzo/cuentas/pagar/', almuerzo_views.registrar_pago_almuerzo, name='pagar_almuerzo'),
    path('almuerzo/reportes/diario/', almuerzo_views.reporte_almuerzos_diarios, name='reporte_almuerzos'),
    path('almuerzo/reportes/mensual/', almuerzo_views.reporte_mensual_separado, name='reporte_mensual_separado'),
]


