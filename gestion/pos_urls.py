"""
URLs para el módulo POS (Punto de Venta)
"""
from django.urls import path
from gestion import pos_views, almuerzo_views, cliente_views, seguridad_views

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
    path('cuenta-corriente/unificada/<int:cliente_id>/', pos_views.cuenta_corriente_unificada, name='cuenta_corriente_unificada'),
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
    
    # Sistema de Almuerzos (LEGACY - Sistema antiguo)
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
    
    # Sistema de Almuerzos NUEVO (Diciembre 2025 - Separado de tarjetas)
    path('almuerzo/', almuerzo_views.pos_almuerzo, name='pos_almuerzo'),
    path('almuerzo/api/', almuerzo_views.pos_almuerzo_api, name='pos_almuerzo_api'),
    path('almuerzo/anular/', almuerzo_views.anular_ultimo_almuerzo, name='anular_almuerzo'),
    path('almuerzo/ticket/<int:registro_id>/', almuerzo_views.ticket_almuerzo, name='ticket_almuerzo'),
    path('almuerzo/reportes/', almuerzo_views.almuerzo_reportes, name='almuerzo_reportes'),
    path('almuerzo/reportes/diario/', almuerzo_views.reporte_almuerzos_diarios, name='reporte_almuerzos_diarios'),
    path('almuerzo/reportes/mensual/', almuerzo_views.reporte_mensual_separado, name='reporte_mensual_separado'),
    path('almuerzo/reportes/estudiante/', almuerzo_views.reporte_por_estudiante, name='reporte_por_estudiante'),
    path('almuerzo/cuentas/', almuerzo_views.lista_cuentas_mensuales, name='cuentas_mensuales'),
    path('almuerzo/cuentas/generar/', almuerzo_views.generar_cuentas_mes, name='generar_cuentas'),
    path('almuerzo/cuentas/pagar/', almuerzo_views.registrar_pago_almuerzo, name='pagar_almuerzo'),
    path('almuerzo/configurar-precio/', almuerzo_views.configurar_precio_almuerzo, name='configurar_precio_almuerzo'),
    
    # Sistema de Autorizaciones
    path('autorizacion/validar/', almuerzo_views.validar_autorizacion, name='validar_autorizacion'),
    path('almuerzo/anular/<int:registro_id>/', almuerzo_views.anular_almuerzo, name='anular_almuerzo_id'),
    path('venta/anular/<int:venta_id>/', pos_views.anular_venta, name='anular_venta'),
    path('recarga/anular/<int:recarga_id>/', pos_views.anular_recarga, name='anular_recarga'),
    
    # Administración de Tarjetas de Autorización
    path('admin/autorizaciones/', pos_views.admin_tarjetas_autorizacion, name='admin_autorizaciones'),
    path('admin/autorizaciones/crear/', pos_views.crear_tarjeta_autorizacion, name='crear_tarjeta_autorizacion'),
    path('admin/autorizaciones/editar/<int:tarjeta_id>/', pos_views.editar_tarjeta_autorizacion, name='editar_tarjeta_autorizacion'),
    path('admin/autorizaciones/toggle/<int:tarjeta_id>/', pos_views.toggle_tarjeta_autorizacion, name='toggle_tarjeta_autorizacion'),
    path('admin/autorizaciones/logs/', pos_views.ver_logs_autorizacion, name='logs_autorizaciones'),
    
    # Gestión de Fotos de Hijos
    path('fotos-hijos/', pos_views.gestionar_fotos_hijos, name='gestionar_fotos_hijos'),
    path('hijo/<int:hijo_id>/capturar-foto/', pos_views.capturar_foto_hijo, name='capturar_foto_hijo'),
    path('hijo/<int:hijo_id>/eliminar-foto/', pos_views.eliminar_foto_hijo, name='eliminar_foto_hijo'),
    path('obtener-foto-hijo/', pos_views.obtener_foto_hijo, name='obtener_foto_hijo'),
    
    # Gestión de Grados y Promociones
    path('grados/', pos_views.gestionar_grados_view, name='gestionar_grados'),
    path('hijo/<int:hijo_id>/asignar-grado/', pos_views.asignar_grado_hijo, name='asignar_grado_hijo'),
    path('grados/promocionar/', pos_views.promocionar_grado_masivo, name='promocionar_grado_masivo'),
    path('grados/historial/', pos_views.historial_grados_view, name='historial_grados'),
    
    # Gestión de Clientes y Usuarios Web
    path('clientes/', cliente_views.gestionar_clientes_view, name='gestionar_clientes'),
    path('clientes/crear/', cliente_views.crear_cliente_view, name='crear_cliente'),
    path('clientes/<int:cliente_id>/crear-usuario/', cliente_views.crear_usuario_web_cliente, name='crear_usuario_web_cliente'),
    
    # Portal Web de Clientes
    path('portal/login/', cliente_views.portal_login_view, name='portal_login'),
    path('portal/logout/', cliente_views.portal_logout_view, name='portal_logout'),
    path('portal/', cliente_views.portal_dashboard_view, name='portal_dashboard'),
    path('portal/hijo/<int:hijo_id>/consumos/', cliente_views.portal_consumos_hijo_view, name='portal_consumos_hijo'),
    path('portal/hijo/<int:hijo_id>/restricciones/', cliente_views.portal_restricciones_hijo_view, name='portal_restricciones_hijo'),
    path('portal/recargas/', cliente_views.portal_recargas_view, name='portal_recargas'),
    path('portal/cambiar-password/', cliente_views.portal_cambiar_password_view, name='portal_cambiar_password'),
    path('portal/recuperar-password/', cliente_views.portal_recuperar_password_view, name='portal_recuperar_password'),
    path('portal/reset-password/<str:token>/', cliente_views.portal_reset_password_view, name='portal_reset_password'),
    
    # Autenticación 2FA
    path('portal/configurar-2fa/', cliente_views.configurar_2fa_view, name='configurar_2fa'),
    path('portal/activar-2fa/', cliente_views.activar_2fa_view, name='activar_2fa'),
    path('portal/verificar-2fa/', cliente_views.verificar_2fa_view, name='verificar_2fa'),
    path('portal/deshabilitar-2fa/', cliente_views.deshabilitar_2fa_view, name='deshabilitar_2fa'),
    
    # Dashboard de Seguridad
    path('seguridad/', seguridad_views.dashboard_seguridad_view, name='dashboard_seguridad'),
    path('seguridad/logs/', seguridad_views.logs_auditoria_view, name='logs_auditoria'),
    path('seguridad/exportar-logs/', seguridad_views.exportar_logs_view, name='exportar_logs'),
    path('seguridad/intentos-login/', seguridad_views.intentos_login_view, name='intentos_login'),
    path('seguridad/desbloquear/<int:bloqueo_id>/', seguridad_views.desbloquear_cuenta_view, name='desbloquear_cuenta'),
    
    # Otras vistas
    path('dashboard/', pos_views.dashboard_view, name='dashboard'),
    path('historial/', pos_views.historial_view, name='historial'),
    path('reportes/', pos_views.reportes_view, name='reportes'),
    path('reportes/exportar/', pos_views.exportar_reporte, name='exportar_reporte'),
    
    # =============================================================================
    # NUEVAS FEATURES: RESTRICCIONES Y PROMOCIONES (Diciembre 2025)
    # =============================================================================
    
    # APIs para Matching de Restricciones Alimentarias
    path('analizar-restriccion/', pos_views.analizar_restriccion_producto, name='analizar_restriccion'),
    path('analizar-carrito-restricciones/', pos_views.analizar_carrito_restricciones, name='analizar_carrito_restricciones'),
    
    # APIs para Sistema de Promociones
    path('calcular-promociones/', pos_views.calcular_promociones_carrito, name='calcular_promociones'),
    
    # Autorización de Supervisor (Saldo Insuficiente)
    path('validar-supervisor/', pos_views.validar_supervisor, name='validar_supervisor'),
]




