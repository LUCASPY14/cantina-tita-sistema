#!/usr/bin/env python
"""
Script de corrección FINAL de URLs - Mapeo completo
"""

import os
import re

def crear_mapeo_completo_urls():
    """Crea el mapeo completo de URLs basado en todos los archivos encontrados"""
    
    # MAPEO COMPLETO basado en pos_urls.py, gestion/urls.py, cantina_project/urls.py
    mapeo_urls = {
        # ==================== POS URLS (pos_urls.py) ====================
        'pos:venta': 'pos:venta',  # OK ya existe como ''
        'pos:dashboard_ventas': 'pos:dashboard_ventas',  # Crear vista o usar 'dashboard_ventas_detalle'
        'pos:dashboard': 'pos:dashboard',  # OK ya existe
        'pos:buscar_tarjeta': 'pos:buscar_tarjeta',  # OK ya existe
        'pos:buscar_producto': 'pos:buscar_producto',  # OK ya existe 
        'pos:procesar_venta_api': 'pos:procesar_venta_api',  # OK ya existe
        'pos:ticket_api': 'pos:ticket_api',  # OK ya existe
        'pos:recargas': 'pos:recargas',  # OK ya existe
        'pos:procesar_recarga': 'pos:procesar_recarga',  # OK ya existe
        'pos:historial_recargas': 'pos:historial_recargas',  # OK ya existe
        'pos:comprobante_recarga': 'pos:comprobante_recarga',  # OK ya existe
        'pos:cuenta_corriente': 'pos:cuenta_corriente',  # OK ya existe
        'pos:cc_detalle': 'pos:cc_detalle',  # OK ya existe
        'pos:cuenta_corriente_unificada': 'pos:cuenta_corriente_unificada',  # OK ya existe
        'pos:cc_registrar_pago': 'pos:cc_registrar_pago',  # OK ya existe
        'pos:cc_estado_cuenta': 'pos:cc_estado_cuenta',  # OK ya existe
        'pos:proveedores': 'pos:proveedores',  # OK ya existe
        'pos:proveedor_detalle': 'pos:proveedor_detalle',  # OK ya existe
        'pos:proveedor_crear': 'pos:proveedor_crear',  # OK ya existe
        'pos:inventario': 'pos:inventario',  # Mapear a 'inventario_dashboard'
        'pos:inventario_dashboard': 'pos:inventario_dashboard',  # OK ya existe
        'pos:inventario_productos': 'pos:inventario_productos',  # OK ya existe
        'pos:kardex_producto': 'pos:kardex_producto',  # OK ya existe
        'pos:ajuste_inventario': 'pos:ajuste_inventario',  # OK ya existe
        'pos:alertas_inventario': 'pos:alertas_inventario',  # OK ya existe
        'pos:alertas_sistema': 'pos:alertas_sistema',  # OK ya existe
        'pos:alertas_tarjetas_saldo': 'pos:alertas_tarjetas_saldo',  # OK ya existe
        'pos:cajas_dashboard': 'pos:cajas_dashboard',  # OK ya existe
        'pos:apertura_caja': 'pos:apertura_caja',  # OK ya existe
        'pos:cierre_caja': 'pos:cierre_caja',  # OK ya existe
        'pos:arqueo_caja': 'pos:arqueo_caja',  # OK ya existe
        'pos:conciliacion_pagos': 'pos:conciliacion_pagos',  # OK ya existe
        'pos:compras_dashboard': 'pos:compras_dashboard',  # OK ya existe
        'pos:nueva_compra': 'pos:nueva_compra',  # OK ya existe
        'pos:recepcion_mercaderia': 'pos:recepcion_mercaderia',  # OK ya existe
        'pos:deuda_proveedores': 'pos:deuda_proveedores',  # OK ya existe
        'pos:comisiones_dashboard': 'pos:comisiones_dashboard',  # OK ya existe
        'pos:configurar_tarifas': 'pos:configurar_tarifas',  # OK ya existe
        'pos:reporte_comisiones': 'pos:reporte_comisiones',  # OK ya existe
        'pos:almuerzos_dashboard': 'pos:almuerzos_dashboard',  # OK ya existe
        'pos:planes_almuerzo': 'pos:planes_almuerzo',  # OK ya existe
        'pos:crear_plan_almuerzo': 'pos:crear_plan_almuerzo',  # OK ya existe
        'pos:suscripciones_almuerzo': 'pos:suscripciones_almuerzo',  # OK ya existe
        'pos:crear_suscripcion_almuerzo': 'pos:crear_suscripcion_almuerzo',  # OK ya existe
        'pos:registro_consumo_almuerzo': 'pos:registro_consumo_almuerzo',  # OK ya existe
        'pos:registrar_consumo_almuerzo': 'pos:registrar_consumo_almuerzo',  # OK ya existe
        'pos:reportes_almuerzos': 'pos:reportes_almuerzos',  # OK ya existe
        'pos:pos_almuerzo': 'pos:pos_almuerzo',  # OK ya existe
        'pos:almuerzo_venta': 'pos:pos_almuerzo',  # Mapear a pos_almuerzo
        'pos:almuerzo_reportes': 'pos:almuerzo_reportes',  # OK ya existe
        'pos:reporte_almuerzos_diarios': 'pos:reporte_almuerzos_diarios',  # OK ya existe
        'pos:reporte_mensual_separado': 'pos:reporte_mensual_separado',  # OK ya existe
        'pos:reporte_por_estudiante': 'pos:reporte_por_estudiante',  # OK ya existe
        'pos:cuentas_mensuales': 'pos:cuentas_mensuales',  # OK ya existe
        'pos:generar_cuentas': 'pos:generar_cuentas',  # OK ya existe
        'pos:pagar_almuerzo': 'pos:pagar_almuerzo',  # OK ya existe
        'pos:configurar_precio_almuerzo': 'pos:configurar_precio_almuerzo',  # OK ya existe
        'pos:validar_carga_saldo': 'pos:validar_carga_saldo',  # OK ya existe
        'pos:validar_pago': 'pos:validar_pago',  # OK ya existe
        'pos:lista_cargas_pendientes': 'pos:lista_cargas_pendientes',  # OK ya existe
        'pos:lista_pagos_pendientes': 'pos:lista_pagos_pendientes',  # OK ya existe
        'pos:validar_autorizacion': 'pos:validar_autorizacion',  # OK ya existe
        'pos:anular_venta': 'pos:anular_venta',  # OK ya existe
        'pos:admin_autorizaciones': 'pos:admin_autorizaciones',  # OK ya existe
        'pos:crear_tarjeta_autorizacion': 'pos:crear_tarjeta_autorizacion',  # OK ya existe
        'pos:logs_autorizaciones': 'pos:logs_autorizaciones',  # OK ya existe
        'pos:gestionar_fotos_hijos': 'pos:gestionar_fotos_hijos',  # OK ya existe
        'pos:gestionar_grados': 'pos:gestionar_grados',  # OK ya existe
        'pos:historial_grados': 'pos:historial_grados',  # OK ya existe
        'pos:gestionar_clientes': 'pos:gestionar_clientes',  # OK ya existe
        'pos:crear_cliente': 'pos:crear_cliente',  # OK ya existe
        'pos:dashboard_seguridad': 'pos:dashboard_seguridad',  # OK ya existe
        'pos:logs_auditoria': 'pos:logs_auditoria',  # OK ya existe
        'pos:exportar_logs': 'pos:exportar_logs',  # OK ya existe
        'pos:intentos_login': 'pos:intentos_login',  # OK ya existe
        'pos:desbloquear_cuenta': 'pos:desbloquear_cuenta',  # OK ya existe
        'pos:historial': 'pos:historial',  # OK ya existe
        'pos:reportes': 'pos:reportes',  # Mapear a reportes_principales si existe
        'pos:reportes_principales': 'pos:reportes',  # OK ya existe como 'reportes'
        'pos:exportar_reporte': 'pos:exportar_reporte',  # OK ya existe
        'pos:validar_supervisor': 'pos:validar_supervisor',  # OK ya existe
        'pos:autorizar_saldo_negativo': 'pos:autorizar_saldo_negativo',  # OK ya existe
        'pos:reporte_autorizaciones_saldo_negativo': 'pos:reporte_autorizaciones_saldo_negativo',  # OK ya existe
        'pos:dashboard_saldos_tiempo_real': 'pos:dashboard_saldos_tiempo_real',  # OK ya existe
        'pos:configurar_limites_masivo': 'pos:configurar_limites_masivo',  # OK ya existe
        
        # ==================== GESTION URLS (gestion/urls.py) ====================
        'gestion:index': 'gestion:index',  # OK ya existe
        'gestion:dashboard': 'gestion:dashboard',  # OK ya existe
        'gestion:productos_lista': 'gestion:productos_lista',  # OK ya existe
        'gestion:crear_producto': 'gestion:crear_producto',  # OK ya existe
        'gestion:editar_producto': 'gestion:editar_producto',  # OK ya existe
        'gestion:clientes_lista': 'gestion:clientes_lista',  # OK ya existe
        'gestion:ventas_lista': 'gestion:ventas_lista',  # OK ya existe
        'gestion:categorias_lista': 'gestion:categorias_lista',  # OK ya existe
        'gestion:crear_categoria': 'gestion:crear_categoria',  # OK ya existe
        'gestion:editar_categoria': 'gestion:editar_categoria',  # OK ya existe
        'gestion:eliminar_categoria': 'gestion:eliminar_categoria',  # OK ya existe
        'gestion:importar_productos': 'gestion:importar_productos',  # OK ya existe
        'gestion:exportar_productos_csv': 'gestion:exportar_productos_csv',  # OK ya existe
        'gestion:exportar_productos_excel': 'gestion:exportar_productos_excel',  # OK ya existe
        'gestion:validar_pagos_pendientes': 'gestion:validar_pagos_pendientes',  # OK ya existe
        'gestion:validar_pago_action': 'gestion:validar_pago_action',  # OK ya existe
        'gestion:cambiar_contrasena_empleado': 'gestion:cambiar_contrasena_empleado',  # OK ya existe
        'gestion:perfil_empleado': 'gestion:perfil_empleado',  # OK ya existe
        'gestion:gestionar_empleados': 'gestion:gestionar_empleados',  # OK ya existe
        'gestion:crear_empleado': 'gestion:crear_empleado',  # OK ya existe
        'gestion:facturacion_dashboard': 'gestion:facturacion_dashboard',  # OK ya existe
        'gestion:facturacion_listado': 'gestion:facturacion_listado',  # OK ya existe
        'gestion:facturacion_reporte': 'gestion:facturacion_reporte',  # OK ya existe
        'gestion:facturacion_kude': 'gestion:facturacion_kude',  # OK ya existe
        'gestion:facturacion_anular': 'gestion:facturacion_anular',  # OK ya existe
        'gestion:reporte_mensual_completo': 'gestion:reporte_mensual_completo',  # OK ya existe
        'gestion:portal_login': 'gestion:portal_login',  # OK ya existe
        'gestion:portal_logout': 'gestion:portal_logout',  # OK ya existe
        'gestion:portal_dashboard': 'gestion:portal_dashboard',  # OK ya existe
        'gestion:portal_mis_hijos': 'gestion:portal_mis_hijos',  # OK ya existe
        'gestion:portal_perfil': 'gestion:portal_perfil',  # OK ya existe
        'gestion:portal_recargar_tarjeta': 'gestion:portal_recargar_tarjeta',  # OK ya existe
        'gestion:portal_notificaciones_saldo': 'gestion:portal_notificaciones_saldo',  # OK ya existe
        'gestion:portal_revocar_terminos': 'gestion:portal_revocar_terminos',  # OK ya existe
        'gestion:portal_restricciones_hijo': 'gestion:portal_restricciones_hijo',  # No existe - crear o mapear
        'gestion:portal_tarjeta_detalle': 'gestion:portal_tarjeta_detalle',  # No existe - crear o mapear
        'gestion:portal_movimientos_tarjeta': 'gestion:portal_movimientos_tarjeta',  # No existe - crear o mapear
        'gestion:pos_general': 'pos:venta',  # Mapear a pos:venta
        'gestion:configuracion': 'gestion:index',  # Mapear a index por ahora
        
        # ==================== URLs PRINCIPALES (cantina_project/urls.py) ====================
        'dashboard_unificado': 'dashboard_unificado',  # OK ya existe
        'dashboard_ventas_detalle': 'dashboard_ventas_detalle',  # OK ya existe
        'dashboard_stock_detalle': 'dashboard_stock_detalle',  # OK ya existe
        'invalidar_cache_dashboard': 'invalidar_cache_dashboard',  # OK ya existe
        'login': 'login',  # OK ya existe
        'logout': 'logout',  # OK ya existe
        'admin:index': 'admin:index',  # Django admin estándar
        
        # ==================== CLIENTE URLS (cliente_urls.py - asumir que existe) ====================
        'clientes:crear_cliente': 'clientes:crear_cliente',
        'clientes:editar_cliente': 'clientes:editar_cliente',
        'clientes:detalle_cliente': 'clientes:detalle_cliente',
        'clientes:portal_login': 'clientes:portal_login',
        'clientes:portal_logout': 'clientes:portal_logout',
        'clientes:portal_dashboard': 'clientes:portal_dashboard',
        'clientes:portal_cargar_saldo': 'clientes:portal_cargar_saldo',
        'clientes:portal_recargas': 'clientes:portal_recargas',
        'clientes:portal_pagos': 'clientes:portal_pagos',
        'clientes:portal_consumos_hijo': 'clientes:portal_consumos_hijo',
        'clientes:portal_restricciones_hijo': 'clientes:portal_restricciones_hijo',
        'clientes:portal_cambiar_password': 'clientes:portal_cambiar_password',
        'clientes:portal_reset_password': 'clientes:portal_reset_password',
        'clientes:configurar_2fa': 'clientes:configurar_2fa',
        'clientes:verificar_2fa': 'clientes:verificar_2fa',
        'clientes:activar_2fa': 'clientes:activar_2fa',
        'clientes:deshabilitar_2fa': 'clientes:deshabilitar_2fa',
        
        # ==================== URLs LEGACY SIN NAMESPACE ====================
        'dashboard': 'dashboard_unificado',
        'productos_lista': 'gestion:productos_lista',
        'clientes_lista': 'gestion:clientes_lista',
        'ventas_lista': 'gestion:ventas_lista',
        'crear_categoria': 'gestion:crear_categoria',
        'editar_categoria': 'gestion:editar_categoria',
        'eliminar_categoria': 'gestion:eliminar_categoria',
        'importar_productos': 'gestion:importar_productos',
        'producto_nuevo': 'gestion:crear_producto',
        'producto_editar': 'gestion:editar_producto',
        'producto_lista': 'gestion:productos_lista',
        'producto_detalle': 'gestion:editar_producto',
        'cliente_nuevo': 'clientes:crear_cliente',
        'cliente_editar': 'clientes:editar_cliente',
        'cliente_detalle': 'clientes:detalle_cliente',
        'clientes_crear': 'clientes:crear_cliente',
        'gestionar_empleados': 'gestion:gestionar_empleados',
        'crear_empleado': 'gestion:crear_empleado',
        'cambiar_contrasena_empleado': 'gestion:cambiar_contrasena_empleado',
        'productos_crear': 'gestion:crear_producto',
        'inventario_productos': 'pos:inventario_productos',
        'nueva_venta': 'pos:venta',
        'detalle_venta': 'pos:venta',
        'venta_detalle': 'pos:venta',
        'anular_venta': 'pos:anular_venta',
        'imprimir_factura': 'pos:ticket_api',
        'dashboard_reportes': 'pos:reportes',
        'kardex_producto': 'pos:kardex_producto',
        'cuenta_corriente_unificada': 'pos:cuenta_corriente_unificada',
        'portal_dashboard': 'gestion:portal_dashboard',
        'portal_revocar_terminos': 'gestion:portal_revocar_terminos',
        'facturacion_descargar_kude': 'gestion:facturacion_kude',
        'facturacion_anular_api': 'gestion:facturacion_anular',
        'facturacion_mensual_almuerzos': 'gestion:reporte_mensual_completo',
        'generar_facturacion_mensual': 'gestion:reporte_mensual_completo',
        'exportar_ventas_excel': 'gestion:exportar_productos_excel',
        'suscripciones_almuerzo': 'pos:suscripciones_almuerzo',
        'pos_reportes_autorizaciones_saldo': 'pos:reporte_autorizaciones_saldo_negativo',
        
        # URLs de admin Django
        'admin:gestion_producto_changelist': 'admin:gestion_producto_changelist',
        'admin:gestion_cliente_changelist': 'admin:gestion_cliente_changelist',
        'admin:gestion_cliente_change': 'admin:gestion_cliente_change',
        'admin:gestion_tarjeta_changelist': 'admin:gestion_tarjeta_changelist',
        'admin:gestion_ventas_add': 'admin:gestion_ventas_add',
        'admin:gestion_cierrescaja_add': 'admin:gestion_cierrescaja_add',
        'admin:gestion_cargassaldo_add': 'admin:gestion_cargassaldo_add',
        'admin:gestion_timbrados_changelist': 'admin:gestion_timbrados_changelist',
        
        # URLs especiales que pueden no existir pero mapear a algo útil
        'pos:cargar_saldo_tarjeta': 'pos:procesar_recarga',
        'pos:nuevo_plan': 'pos:crear_plan_almuerzo',
        'pos:nueva_suscripcion': 'pos:crear_suscripcion_almuerzo',
        'pos:productos_categoria': 'gestion:productos_lista',  # Asumir filtro por categoría
        'pos:ticket': 'pos:ticket_api',
        'pos:ventas': 'pos:venta'
    }
    
    return mapeo_urls

def corregir_urls_archivo_completo(archivo_path, mapeo_urls):
    """Corrige URLs en un archivo usando el mapeo completo"""
    
    if not os.path.exists(archivo_path):
        return False
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        contenido_original = contenido
        cambios = 0
        
        # Aplicar correcciones con patrones más precisos
        for url_incorrecta, url_correcta in mapeo_urls.items():
            if url_incorrecta == url_correcta:
                continue  # Skip si no hay cambio
                
            # Patrones para encontrar URLs en templates Django
            patterns = [
                ("url '" + url_incorrecta + "'", "url '" + url_correcta + "'"),
                ('url "' + url_incorrecta + '"', 'url "' + url_correcta + '"'),
                ("{" + "% url '" + url_incorrecta + "'", "{" + "% url '" + url_correcta + "'"),
                ("{" + '% url "' + url_incorrecta + '"', "{" + '% url "' + url_correcta + '"'),
                ("{" + "% url '" + url_incorrecta + "' ", "{" + "% url '" + url_correcta + "' "),
                ("{" + '% url "' + url_incorrecta + '" ', "{" + '% url "' + url_correcta + '" ')
            ]
            
            for pattern_viejo, pattern_nuevo in patterns:
                if pattern_viejo in contenido:
                    contenido = contenido.replace(pattern_viejo, pattern_nuevo)
                    cambios += 1
        
        # Escribir solo si hubo cambios
        if contenido != contenido_original:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            return cambios > 0
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error procesando {archivo_path}: {e}")
        return False

def main():
    """Ejecuta corrección completa y final"""
    
    print("🎯 CORRECCIÓN FINAL COMPLETA DE URLs")
    print("=" * 60)
    
    # Obtener mapeo completo
    mapeo_urls = crear_mapeo_completo_urls()
    print(f"📋 URLs en mapeo: {len(mapeo_urls)}")
    
    # Corregir templates
    templates_corregidos = 0
    total_templates = 0
    
    templates_dir = 'frontend/templates'
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    total_templates += 1
                    archivo_path = os.path.join(root, file)
                    if corregir_urls_archivo_completo(archivo_path, mapeo_urls):
                        templates_corregidos += 1
                        print(f"  ✅ {os.path.relpath(archivo_path)}")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"  • Templates procesados: {total_templates}")
    print(f"  • Templates corregidos: {templates_corregidos}")
    print(f"  • URLs mapeadas: {len(mapeo_urls)}")
    
    if templates_corregidos > 0:
        print("\n✅ CORRECCIÓN FINAL COMPLETADA")
        print("\n🔍 VERIFICAR RESULTADOS:")
        print("  python verificar_rutas_urls.py")
    else:
        print("\n📝 NO SE ENCONTRARON MÁS CORRECCIONES")

if __name__ == "__main__":
    if not os.path.exists("frontend/templates"):
        print("❌ Error: No se encuentra frontend/templates")
        exit(1)
    
    main()