"""
URLs para el módulo POS (Punto de Venta)
"""
from django.urls import path
from gestion import (
    almuerzo_views, cliente_views, seguridad_views, pos_views, 
    pos_general_views, autorizacion_saldo_views,
    reporte_autorizaciones_views, dashboard_saldos_views,
    admin_configuracion_views
)

app_name = 'pos'

urlpatterns = [
    # ==================== INTERFAZ POS PRINCIPAL ====================
    # Vista principal - Nueva interfaz mejorada
    path('', pos_general_views.pos_general, name='venta'),
    
    # Dashboard de ventas del día
    path('dashboard/', pos_general_views.dashboard_ventas_dia, name='dashboard_ventas'),
    
    # APIs de la interfaz POS mejorada (Bootstrap 5)
    path('buscar-tarjeta/', pos_general_views.verificar_tarjeta_api, name='buscar_tarjeta'),
    path('buscar-producto/', pos_general_views.buscar_producto_api, name='buscar_producto'),
    path('procesar-venta/', pos_general_views.procesar_venta_api, name='procesar_venta_api'),
    path('ticket/<int:id_venta>/', pos_general_views.imprimir_ticket_venta, name='ticket_api'),
    
    # ==================== RECARGAS ====================
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
    
    # ==================== VALIDACIONES PARA ADMINISTRADORES ====================
    path('validaciones/carga-saldo/<int:id_carga>/', pos_views.validar_carga_saldo, name='validar_carga_saldo'),
    path('validaciones/pago/<int:id_venta>/', pos_views.validar_pago, name='validar_pago'),
    path('validaciones/cargas-pendientes/', pos_views.lista_cargas_pendientes, name='lista_cargas_pendientes'),
    path('validaciones/pagos-pendientes/', pos_views.lista_pagos_pendientes, name='lista_pagos_pendientes'),
    
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
    
    # =============================================================================
    # SISTEMA DE AUTORIZACIONES DE SALDO NEGATIVO (Diciembre 2025)
    # =============================================================================
    
    # Verificación de saldo antes de venta
    path('verificar-saldo-venta/', autorizacion_saldo_views.verificar_saldo_venta, name='verificar_saldo_venta'),
    
    # Autorización de venta con saldo negativo
    path('autorizar-saldo-negativo/', autorizacion_saldo_views.autorizar_venta_saldo_negativo_ajax, name='autorizar_saldo_negativo'),
    path('autorizar-saldo-negativo/modal/', autorizacion_saldo_views.modal_autorizar_saldo_negativo, name='modal_autorizar_saldo_negativo'),
    
    # Listado de autorizaciones
    path('autorizaciones-saldo-negativo/', autorizacion_saldo_views.listar_autorizaciones_saldo_negativo, name='listar_autorizaciones_saldo_negativo'),
    
    # =============================================================================
    # NUEVAS FEATURES DE ALTA PRIORIDAD (Enero 2026)
    # =============================================================================
    
    # Reportes de Autorizaciones con Chart.js
    path('reportes/autorizaciones-saldo-negativo/', reporte_autorizaciones_views.reporte_autorizaciones_saldo_negativo, name='reporte_autorizaciones_saldo_negativo'),
    path('reportes/autorizaciones/exportar-excel/', reporte_autorizaciones_views.exportar_autorizaciones_excel, name='exportar_autorizaciones_excel'),
    
    # Dashboard Tiempo Real de Saldos
    path('dashboard-saldos-tiempo-real/', dashboard_saldos_views.dashboard_saldos_tiempo_real, name='dashboard_saldos_tiempo_real'),
    path('api/saldos-tiempo-real/', dashboard_saldos_views.api_saldos_tiempo_real, name='api_saldos_tiempo_real'),
    
    # Panel Admin Configuración Masiva
    path('admin/configurar-limites-masivo/', admin_configuracion_views.configurar_limites_masivo_view, name='configurar_limites_masivo'),
    path('admin/aplicar-configuracion-masiva/', admin_configuracion_views.aplicar_configuracion_masiva, name='aplicar_configuracion_masiva'),
    path('admin/historial-configuraciones/', admin_configuracion_views.historial_configuraciones_masivas, name='historial_configuraciones'),
]




