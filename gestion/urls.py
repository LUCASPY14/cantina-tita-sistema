from django.urls import path
from . import views
from . import almuerzo_views
from . import restricciones_api
from . import portal_views
from . import portal_api
from . import pos_general_views
from . import pos_sugerencias_api
from . import facturacion_views
from . import pos_facturacion_integracion
from . import vistas_paginadas
from . import pagos_admin_views
from . import empleado_views
from .reportes_gerenciales import ReportesGerenciales

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
    
    # === NUEVOS REPORTES GERENCIALES ===
    path('reportes/gerenciales/mensual/', lambda r: ReportesGerenciales.reporte_mensual_completo(), name='reporte_mensual_completo'),
    path('reportes/gerenciales/conciliacion-bancaria/', lambda r: ReportesGerenciales.conciliacion_bancaria(), name='conciliacion_bancaria'),
    
    # URLs para POS General (ahora en /pos/)
    # NOTA: Las rutas /pos/general/ han sido movidas a /pos/ en pos_urls.py
    
    # ==================== FACTURACIÓN ELECTRÓNICA ====================
    path('facturacion/dashboard/', facturacion_views.dashboard_facturacion, name='facturacion_dashboard'),
    path('facturacion/api/emitir/', facturacion_views.emitir_factura_api, name='facturacion_emitir'),
    path('facturacion/api/anular/', facturacion_views.anular_factura_api, name='facturacion_anular'),
    path('facturacion/kude/<str:cdc>/', facturacion_views.descargar_kude, name='facturacion_kude'),
    path('facturacion/listado/', facturacion_views.listar_facturas, name='facturacion_listado'),
    path('facturacion/reporte-cumplimiento/', facturacion_views.reporte_cumplimiento, name='facturacion_reporte'),
    
    # URLs para módulo de almuerzos - MOVIDAS A pos_urls.py
    # path('pos/almuerzo/', almuerzo_views.pos_almuerzo, name='pos_almuerzo'),
    # path('pos/almuerzo/api/', almuerzo_views.pos_almuerzo_api, name='pos_almuerzo_api'),
    # path('pos/almuerzo/anular/', almuerzo_views.anular_ultimo_almuerzo, name='anular_almuerzo'),
    path('almuerzo/cuentas/pagar/', almuerzo_views.registrar_pago_almuerzo, name='pagar_almuerzo'),
    path('almuerzo/reportes/diario/', almuerzo_views.reporte_almuerzos_diarios, name='reporte_almuerzos'),
    path('almuerzo/reportes/mensual/', almuerzo_views.reporte_mensual_separado, name='reporte_mensual_separado'),
    
    # URLs para API de restricciones alimentarias (matching automático)
    path('api/verificar-restricciones/', restricciones_api.verificar_restricciones_api, name='verificar_restricciones_api'),
    path('api/productos-seguros/<str:tarjeta_codigo>/', restricciones_api.obtener_productos_seguros_api, name='productos_seguros_api'),
    path('api/sugerir-alternativas/', restricciones_api.sugerir_alternativas_api, name='sugerir_alternativas_api'),
    
    # URLs para Portal de Padres (Web)
    path('portal/', portal_views.login_view, name='portal_login'),
    path('portal/registro/', portal_views.registro_view, name='portal_registro'),
    path('portal/logout/', portal_views.logout_view, name='portal_logout'),
    path('portal/verificar-email/<str:token>/', portal_views.verificar_email_view, name='portal_verificar_email'),
    path('portal/recuperar-password/', portal_views.recuperar_password_view, name='portal_recuperar_password'),
    path('portal/restablecer-password/<str:token>/', portal_views.restablecer_password_view, name='portal_restablecer_password'),
    path('portal/dashboard/', portal_views.dashboard_view, name='portal_dashboard'),
    path('portal/mis-hijos/', portal_views.mis_hijos_view, name='portal_mis_hijos'),
    path('portal/perfil/', portal_views.perfil_view, name='portal_perfil'),
    path('portal/recargar/<str:nro_tarjeta>/', portal_views.recargar_tarjeta_view, name='portal_recargar_tarjeta'),
    path('portal/estado-recarga/<str:referencia>/', portal_views.estado_recarga_view, name='portal_estado_recarga'),
    path('portal/pago-exitoso/', portal_views.pago_exitoso_view, name='portal_pago_exitoso'),
    path('portal/pago-cancelado/', portal_views.pago_cancelado_view, name='portal_pago_cancelado'),
    
    # URLs para API REST del Portal (Consultas Móviles)
    path('api/portal/tarjeta/<str:nro_tarjeta>/saldo/', portal_api.api_saldo_tarjeta, name='api_portal_saldo'),
    path('api/portal/tarjeta/<str:nro_tarjeta>/movimientos/', portal_api.api_movimientos_tarjeta, name='api_portal_movimientos'),
    path('api/portal/tarjeta/<str:nro_tarjeta>/consumos/', portal_api.api_consumos_tarjeta, name='api_portal_consumos'),
    path('api/portal/tarjeta/<str:nro_tarjeta>/recargas/', portal_api.api_recargas_tarjeta, name='api_portal_recargas'),
    path('api/portal/mis-tarjetas/', portal_api.api_tarjetas_usuario, name='api_portal_mis_tarjetas'),
    path('api/portal/notificaciones/', portal_api.api_notificaciones_usuario, name='api_portal_notificaciones'),
    path('api/portal/notificaciones/<int:id_notificacion>/marcar-leida/', portal_api.api_marcar_notificacion_leida, name='api_portal_marcar_notificacion'),
    
    # ==================== GESTIÓN DE PRODUCTOS ====================
    path('productos/', vistas_paginadas.productos_lista, name='productos_lista'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    
    # ==================== GESTIÓN DE CLIENTES ====================
    path('clientes/', vistas_paginadas.clientes_lista, name='clientes_lista'),
    
    # ==================== GESTIÓN DE VENTAS ====================
    path('ventas/', vistas_paginadas.ventas_lista, name='ventas_lista'),
    
    # ==================== GESTIÓN DE CATEGORÍAS ====================
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # ==================== IMPORTACIÓN/EXPORTACIÓN ====================
    path('productos/importar/', views.importar_productos, name='importar_productos'),
    path('productos/exportar/csv/', views.exportar_productos_csv, name='exportar_productos_csv'),
    path('productos/exportar/excel/', views.exportar_productos_excel, name='exportar_productos_excel'),
    
    # ==================== VALIDACIÓN DE PAGOS ====================
    path('pagos/validar/', pagos_admin_views.validar_pagos_pendientes, name='validar_pagos_pendientes'),
    path('pagos/validar/action/', pagos_admin_views.validar_pago_action, name='validar_pago_action'),
    
    # ==================== GESTIÓN DE EMPLEADOS ====================
    path('empleado/cambiar-contrasena/', empleado_views.cambiar_contrasena_empleado, name='cambiar_contrasena_empleado'),
    path('empleado/perfil/', empleado_views.perfil_empleado, name='perfil_empleado'),
]


