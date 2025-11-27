from django.urls import path
from . import views

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
]


