
# Contenido completo para backend/gestion/pos_urls.py
from django.urls import path
from . import pos_views, pos_views_basicas

app_name = 'pos'

urlpatterns = [
    # Dashboard principal POS
    path('', pos_views.dashboard, name='dashboard'),
    path('dashboard/inventario/', pos_views.inventario_dashboard, name='inventario_dashboard'),
    path('dashboard/almuerzos/', pos_views.almuerzos_dashboard, name='almuerzos_dashboard'),
    path('dashboard/compras/', pos_views.compras_dashboard, name='compras_dashboard'),
    path('dashboard/cajas/', pos_views.cajas_dashboard, name='cajas_dashboard'),
    path('dashboard/comisiones/', pos_views.comisiones_dashboard, name='comisiones_dashboard'),
    path('dashboard/seguridad/', pos_views.dashboard_seguridad, name='dashboard_seguridad'),
    
    # Ventas
    path('venta/', pos_views.venta, name='venta'),
    path('venta/anular/', pos_views.anular_venta, name='anular_venta'),
    
    # Compras
    path('compras/nueva/', pos_views.nueva_compra, name='nueva_compra'),
    
    # Clientes
    path('clientes/crear/', pos_views.crear_cliente, name='crear_cliente'),
    path('clientes/', pos_views.gestionar_clientes, name='gestionar_clientes'),
    
    # Tarjetas
    path('tarjetas/buscar/', pos_views.buscar_tarjeta, name='buscar_tarjeta'),
    path('tarjetas/crear/', pos_views.crear_tarjeta_autorizacion, name='crear_tarjeta_autorizacion'),
    
    # Recargas
    path('recargas/', pos_views.recargas, name='recargas'),
    path('recargas/procesar/', pos_views.procesar_recarga, name='procesar_recarga'),
    path('recargas/validar/', pos_views.validar_carga_saldo, name='validar_carga_saldo'),
    path('recargas/comprobante/', pos_views.comprobante_recarga, name='comprobante_recarga'),
    path('recargas/historial/', pos_views.historial_recargas, name='historial_recargas'),
    path('recargas/pendientes/', pos_views.lista_cargas_pendientes, name='lista_cargas_pendientes'),
    
    # Cuenta corriente
    path('cuenta-corriente/', pos_views.cuenta_corriente, name='cuenta_corriente'),
    path('cuenta-corriente/estado/', pos_views.cc_estado_cuenta, name='cc_estado_cuenta'),
    path('cuenta-corriente/detalle/', pos_views.cc_detalle, name='cc_detalle'),
    path('cuenta-corriente/pago/', pos_views.cc_registrar_pago, name='cc_registrar_pago'),
    path('cuenta-corriente/unificada/', pos_views.cuenta_corriente_unificada, name='cuenta_corriente_unificada'),
    path('cuentas/mensuales/', pos_views.cuentas_mensuales, name='cuentas_mensuales'),
    path('cuentas/generar/', pos_views.generar_cuentas, name='generar_cuentas'),
    
    # Inventario
    path('inventario/', pos_views.inventario_productos, name='inventario_productos'),
    path('inventario/ajuste/', pos_views.ajuste_inventario, name='ajuste_inventario'),
    path('inventario/kardex/<int:producto_id>/', pos_views.kardex_producto, name='kardex_producto'),
    path('productos/buscar/', pos_views.buscar_producto, name='buscar_producto'),
    path('inventario/alertas/', pos_views.alertas_inventario, name='alertas_inventario'),
    
    # Cajas
    path('caja/apertura/', pos_views.apertura_caja, name='apertura_caja'),
    path('caja/cierre/', pos_views.cierre_caja, name='cierre_caja'),
    path('caja/arqueo/', pos_views.arqueo_caja, name='arqueo_caja'),
    
    # Reportes
    path('reportes/', pos_views.reportes, name='reportes'),
    path('reportes/exportar/', pos_views.exportar_reporte, name='exportar_reporte'),
    path('reportes/comisiones/', pos_views.reporte_comisiones, name='reporte_comisiones'),
    path('reportes/mensual/', pos_views.reporte_mensual_separado, name='reporte_mensual_separado'),
    path('reportes/estudiante/', pos_views.reporte_por_estudiante, name='reporte_por_estudiante'),
    path('reportes/autorizaciones/', pos_views.reporte_autorizaciones_saldo_negativo, name='reporte_autorizaciones_saldo_negativo'),
    
    # Almuerzos
    path('almuerzos/', pos_views.pos_almuerzo, name='pos_almuerzo'),
    path('almuerzos/pagar/', pos_views.pagar_almuerzo, name='pagar_almuerzo'),
    path('almuerzos/planes/', pos_views.planes_almuerzo, name='planes_almuerzo'),
    path('almuerzos/planes/crear/', pos_views.crear_plan_almuerzo, name='crear_plan_almuerzo'),
    path('almuerzos/suscripciones/', pos_views.suscripciones_almuerzo, name='suscripciones_almuerzo'),
    path('almuerzos/suscripciones/crear/', pos_views.crear_suscripcion_almuerzo, name='crear_suscripcion_almuerzo'),
    path('almuerzos/precio/', pos_views.configurar_precio_almuerzo, name='configurar_precio_almuerzo'),
    path('almuerzos/consumo/', pos_views.registrar_consumo_almuerzo, name='registrar_consumo_almuerzo'),
    path('almuerzos/registro/', pos_views.registro_consumo_almuerzo, name='registro_consumo_almuerzo'),
    path('almuerzos/reportes/', pos_views.reportes_almuerzos, name='reportes_almuerzos'),
    path('reportes/almuerzos/', pos_views.almuerzo_reportes, name='almuerzo_reportes'),
    path('reportes/almuerzos/diarios/', pos_views.reporte_almuerzos_diarios, name='reporte_almuerzos_diarios'),
    
    # Proveedores
    path('proveedores/', pos_views.proveedores, name='proveedores'),
    path('proveedores/crear/', pos_views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:pk>/', pos_views.proveedor_detalle, name='proveedor_detalle'),
    path('proveedores/deudas/', pos_views.deuda_proveedores, name='deuda_proveedores'),
    path('mercaderia/recepcion/', pos_views.recepcion_mercaderia, name='recepcion_mercaderia'),
    
    # Auditoría y logs
    path('logs/', pos_views.logs_auditoria, name='logs_auditoria'),
    path('logs/autorizaciones/', pos_views.logs_autorizaciones, name='logs_autorizaciones'),
    path('logs/exportar/', pos_views.exportar_logs, name='exportar_logs'),
    path('logs/intentos/', pos_views.intentos_login, name='intentos_login'),
    
    # Alertas y seguridad
    path('alertas/', pos_views.alertas_sistema, name='alertas_sistema'),
    path('alertas/saldo/', pos_views.alertas_tarjetas_saldo, name='alertas_tarjetas_saldo'),
    path('autorizaciones/', pos_views.admin_autorizaciones, name='admin_autorizaciones'),
    path('autorizaciones/saldo/', pos_views.autorizar_saldo_negativo, name='autorizar_saldo_negativo'),
    path('autorizaciones/validar/', pos_views.validar_autorizacion, name='validar_autorizacion'),
    path('supervisor/validar/', pos_views.validar_supervisor, name='validar_supervisor'),
    path('pagos/validar/', pos_views.validar_pago, name='validar_pago'),
    path('cuentas/desbloquear/', pos_views.desbloquear_cuenta, name='desbloquear_cuenta'),
    
    # Configuración
    path('grados/', pos_views.gestionar_grados, name='gestionar_grados'),
    path('grados/historial/', pos_views.historial_grados, name='historial_grados'),
    path('tarifas/', pos_views.configurar_tarifas, name='configurar_tarifas'),
    path('fotos/', pos_views.gestionar_fotos_hijos, name='gestionar_fotos_hijos'),
    
    # Pagos y conciliación
    path('pagos/conciliacion/', pos_views.conciliacion_pagos, name='conciliacion_pagos'),
    path('pagos/pendientes/', pos_views.lista_pagos_pendientes, name='lista_pagos_pendientes'),
    
    # API
    path('api/ticket/', pos_views.ticket_api, name='ticket_api'),
]
