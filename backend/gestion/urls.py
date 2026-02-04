

from django.urls import path
from . import views_basicas as views

app_name = 'gestion'

urlpatterns = [
    # Dashboard principal
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_unificado, name='dashboard'),
    
    # Funciones básicas disponibles
    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/importar/', views.importar_productos, name='importar_productos'),
    path('productos/exportar/excel/', views.exportar_productos_excel, name='exportar_productos_excel'),
    path('productos/exportar/csv/', views.exportar_productos_csv, name='exportar_productos_csv'),
    
    # Gestión de categorías
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Gestión de clientes
    path('clientes/', views.clientes_lista, name='clientes_lista'),
    
    # Gestión de ventas
    path('ventas/', views.ventas_lista, name='ventas_lista'),
    
    path('empleados/', views.gestionar_empleados, name='gestionar_empleados'),
    path('empleados/crear/', views.crear_empleado, name='crear_empleado'),
    
    # Facturación electrónica
    path('facturacion/', views.facturacion_listado, name='facturacion_listado'),
    path('facturacion/kude/', views.facturacion_kude, name='facturacion_kude'),
    path('facturacion/anular/', views.facturacion_anular_api, name='facturacion_anular_api'),
    path('facturacion/reporte/', views.facturacion_reporte_cumplimiento, name='facturacion_reporte_cumplimiento'),
    
    # Reportes
    path('reportes/mensual/', views.reporte_mensual_completo, name='reporte_mensual_completo'),
    
    # Validaciones
    path('validar-pago/', views.validar_pago_action, name='validar_pago_action'),
    
    # Portal de padres - URLs principales
    path('portal/', views.portal_dashboard, name='portal_dashboard'),
    path('portal/login/', views.portal_login, name='portal_login'),
    path('portal/logout/', views.portal_logout, name='portal_logout'),
    path('portal/perfil/', views.portal_perfil, name='portal_perfil'),
    path('portal/password/', views.portal_cambiar_password, name='portal_cambiar_password'),
    
    # Portal - 2FA
    path('portal/2fa/configurar/', views.portal_configurar_2fa, name='portal_configurar_2fa'),
    path('portal/2fa/verificar/', views.portal_verificar_2fa, name='portal_verificar_2fa'),
    path('portal/2fa/activar/', views.portal_activar_2fa, name='portal_activar_2fa'),
    path('portal/2fa/deshabilitar/', views.portal_deshabilitar_2fa, name='portal_deshabilitar_2fa'),
    path('portal/password/restablecer/', views.portal_restablecer_password, name='portal_restablecer_password'),
    path('portal/terminos/revocar/', views.portal_revocar_terminos, name='portal_revocar_terminos'),
    
    # Portal - Gestión de hijos
    path('portal/hijos/', views.portal_mis_hijos, name='portal_mis_hijos'),
    path('portal/hijos/<int:hijo_id>/consumos/', views.portal_consumos_hijo, name='portal_consumos_hijo'),
    path('portal/hijos/<int:hijo_id>/restricciones/', views.portal_restricciones_hijo, name='portal_restricciones_hijo'),
    
    # Portal - Recargas y pagos
    path('portal/cargar-saldo/', views.portal_cargar_saldo, name='portal_cargar_saldo'),
    path('portal/pagos/', views.portal_pagos, name='portal_pagos'),
    path('portal/recargas/', views.portal_recargas, name='portal_recargas'),
    path('portal/recargar/<int:tarjeta_id>/', views.portal_recargar_tarjeta, name='portal_recargar_tarjeta'),
    path('portal/notificaciones/', views.portal_notificaciones_saldo, name='portal_notificaciones_saldo'),
    
    # Portal - APIs
    path('api/portal/movimientos/', views.api_portal_movimientos, name='api_portal_movimientos'),
    path('api/portal/saldo/', views.api_portal_saldo, name='api_portal_saldo'),
]
