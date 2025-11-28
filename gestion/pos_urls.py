"""
URLs para el módulo POS (Punto de Venta)
"""
from django.urls import path
from gestion import pos_views

app_name = 'pos'

urlpatterns = [
    # Vista principal
    path('', pos_views.venta_view, name='venta'),
    
    # Búsqueda y filtros (HTMX)
    path('buscar-productos/', pos_views.buscar_productos, name='buscar_productos'),
    path('productos-categoria/', pos_views.productos_por_categoria, name='productos_categoria'),
    
    # Tarjetas
    path('buscar-tarjeta/', pos_views.buscar_tarjeta, name='buscar_tarjeta'),
    
    # Procesar venta
    path('procesar-venta/', pos_views.procesar_venta, name='procesar_venta'),
    
    # Ticket
    path('ticket/<int:venta_id>/', pos_views.ticket_view, name='ticket'),
    
    # Recargas
    path('recargas/', pos_views.recargas_view, name='recargas'),
    path('recargas/procesar/', pos_views.procesar_recarga, name='procesar_recarga'),
    path('recargas/historial/', pos_views.historial_recargas_view, name='historial_recargas'),
    path('recargas/comprobante/<int:recarga_id>/', pos_views.comprobante_recarga_view, name='comprobante_recarga'),
    
    # Cuenta Corriente
    path('cuenta-corriente/', pos_views.cuenta_corriente_view, name='cuenta_corriente'),
    path('cuenta-corriente/detalle/<int:cliente_id>/', pos_views.cc_detalle_view, name='cc_detalle'),
    path('cuenta-corriente/pago/', pos_views.cc_registrar_pago, name='cc_registrar_pago'),
    path('cuenta-corriente/estado/<int:cliente_id>/', pos_views.cc_estado_cuenta, name='cc_estado_cuenta'),
    
    # Proveedores
    path('proveedores/', pos_views.proveedores_view, name='proveedores'),
    path('proveedores/detalle/<int:proveedor_id>/', pos_views.proveedor_detalle_view, name='proveedor_detalle'),
    path('proveedores/crear/', pos_views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/editar/<int:proveedor_id>/', pos_views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/eliminar/<int:proveedor_id>/', pos_views.proveedor_eliminar, name='proveedor_eliminar'),
    
    # Inventario Avanzado
    path('inventario/', pos_views.inventario_dashboard, name='inventario_dashboard'),
    path('inventario/productos/', pos_views.inventario_productos, name='inventario_productos'),
    path('inventario/kardex/<int:producto_id>/', pos_views.kardex_producto, name='kardex_producto'),
    path('inventario/ajuste/', pos_views.ajuste_inventario_view, name='ajuste_inventario'),
    path('inventario/alertas/', pos_views.alertas_inventario, name='alertas_inventario'),
    path('inventario/stock-masivo/', pos_views.actualizar_stock_masivo, name='actualizar_stock_masivo'),
    
    # Sistema de Alertas
    path('alertas/', pos_views.alertas_sistema_view, name='alertas_sistema'),
    path('alertas/tarjetas-saldo/', pos_views.alertas_tarjetas_saldo_view, name='alertas_tarjetas_saldo'),
    path('alertas/marcar-vista/', pos_views.marcar_alerta_vista, name='marcar_alerta_vista'),
    path('alertas/notificar-saldo/<str:tarjeta_id>/', pos_views.enviar_notificacion_saldo, name='enviar_notificacion_saldo'),
    
    # Sistema de Cajas
    path('cajas/', pos_views.cajas_dashboard_view, name='cajas_dashboard'),
    path('cajas/apertura/', pos_views.apertura_caja_view, name='apertura_caja'),
    path('cajas/cierre/', pos_views.cierre_caja_view, name='cierre_caja'),
    path('cajas/arqueo/', pos_views.arqueo_caja_view, name='arqueo_caja'),
    path('cajas/conciliacion/', pos_views.conciliacion_pagos_view, name='conciliacion_pagos'),
    
    # Sistema de Compras
    path('compras/', pos_views.compras_dashboard_view, name='compras_dashboard'),
    path('compras/nueva/', pos_views.nueva_compra_view, name='nueva_compra'),
    path('compras/recepcion/<int:id_compra>/', pos_views.recepcion_mercaderia_view, name='recepcion_mercaderia'),
    path('compras/deuda-proveedores/', pos_views.deuda_proveedores_view, name='deuda_proveedores'),
    
    # Sistema de Comisiones
    path('comisiones/', pos_views.comisiones_dashboard_view, name='comisiones_dashboard'),
    path('comisiones/configurar/', pos_views.configurar_tarifas_view, name='configurar_tarifas'),
    path('comisiones/reporte/', pos_views.reporte_comisiones_view, name='reporte_comisiones'),
    
    # Sistema de Almuerzos
    path('almuerzos/', pos_views.almuerzos_dashboard_view, name='almuerzos_dashboard'),
    path('almuerzos/planes/', pos_views.planes_almuerzo_view, name='planes_almuerzo'),
    path('almuerzos/planes/crear/', pos_views.crear_plan_almuerzo, name='crear_plan_almuerzo'),
    path('almuerzos/planes/editar/<int:plan_id>/', pos_views.editar_plan_almuerzo, name='editar_plan_almuerzo'),
    path('almuerzos/suscripciones/', pos_views.suscripciones_almuerzo_view, name='suscripciones_almuerzo'),
    path('almuerzos/suscripciones/crear/', pos_views.crear_suscripcion_almuerzo, name='crear_suscripcion_almuerzo'),
    path('almuerzos/registro/', pos_views.registro_consumo_almuerzo_view, name='registro_consumo_almuerzo'),
    path('almuerzos/registro/consumo/', pos_views.registrar_consumo_almuerzo, name='registrar_consumo_almuerzo'),
    path('almuerzos/menu/', pos_views.menu_diario_view, name='menu_diario'),
    path('almuerzos/facturacion/', pos_views.facturacion_mensual_almuerzos_view, name='facturacion_mensual_almuerzos'),
    path('almuerzos/facturacion/generar/', pos_views.generar_facturacion_mensual, name='generar_facturacion_mensual'),
    path('almuerzos/reportes/', pos_views.reportes_almuerzos_view, name='reportes_almuerzos'),
    
    # Otras vistas
    path('dashboard/', pos_views.dashboard_view, name='dashboard'),
    path('historial/', pos_views.historial_view, name='historial'),
    path('reportes/', pos_views.reportes_view, name='reportes'),
    path('reportes/exportar/', pos_views.exportar_reporte, name='exportar_reporte'),
]



