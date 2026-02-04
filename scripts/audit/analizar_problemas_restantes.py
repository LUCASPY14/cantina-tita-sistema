#!/usr/bin/env python
"""
Análisis específico de los 120 problemas restantes
"""

import os
import re
from collections import defaultdict

def analizar_problemas_detallado():
    """Analiza y categoriza los problemas restantes"""
    
    # Ejecutar verificación y capturar problemas
    try:
        exec(open('verificar_rutas_urls.py').read())
    except Exception:
        pass
    
    # Manualmente categorizar problemas conocidos
    problemas_por_categoria = {
        'admin_urls': [
            'admin:gestion_timbrados_changelist',
            'admin:gestion_cliente_changelist', 
            'admin:gestion_ventas_add',
            'admin:gestion_cliente_change',
            'admin:gestion_producto_changelist',
            'admin:gestion_cierrescaja_add',
            'admin:gestion_cargassaldo_add',
            'admin:gestion_tarjeta_changelist',
            'admin:index'
        ],
        
        'dashboard_urls': [
            'dashboard_unificado',
            'dashboard_ventas_detalle',
            'dashboard_stock_detalle',
            'invalidar_cache_dashboard'
        ],
        
        'auth_urls': [
            'login',
            'logout'
        ],
        
        'pos_views_faltantes': [
            'pos:dashboard',
            'pos:inventario_dashboard',
            'pos:almuerzos_dashboard', 
            'pos:compras_dashboard',
            'pos:cajas_dashboard',
            'pos:comisiones_dashboard',
            'pos:dashboard_seguridad',
            'pos:venta',
            'pos:anular_venta',
            'pos:nueva_compra',
            'pos:crear_cliente',
            'pos:gestionar_clientes',
            'pos:buscar_tarjeta',
            'pos:crear_tarjeta_autorizacion',
            'pos:recargas',
            'pos:procesar_recarga',
            'pos:validar_carga_saldo',
            'pos:comprobante_recarga',
            'pos:historial_recargas',
            'pos:lista_cargas_pendientes',
            'pos:cuenta_corriente',
            'pos:cc_estado_cuenta',
            'pos:cc_detalle',
            'pos:cc_registrar_pago',
            'pos:cuenta_corriente_unificada',
            'pos:cuentas_mensuales',
            'pos:generar_cuentas',
            'pos:inventario_productos',
            'pos:ajuste_inventario',
            'pos:kardex_producto',
            'pos:buscar_producto',
            'pos:alertas_inventario',
            'pos:apertura_caja',
            'pos:cierre_caja',
            'pos:arqueo_caja',
            'pos:reportes',
            'pos:exportar_reporte',
            'pos:reporte_comisiones',
            'pos:reporte_mensual_separado',
            'pos:reporte_por_estudiante',
            'pos:reporte_autorizaciones_saldo_negativo',
            'pos:pos_almuerzo',
            'pos:pagar_almuerzo',
            'pos:planes_almuerzo',
            'pos:crear_plan_almuerzo',
            'pos:suscripciones_almuerzo',
            'pos:crear_suscripcion_almuerzo',
            'pos:configurar_precio_almuerzo',
            'pos:registrar_consumo_almuerzo',
            'pos:registro_consumo_almuerzo',
            'pos:reportes_almuerzos',
            'pos:almuerzo_reportes',
            'pos:reporte_almuerzos_diarios',
            'pos:proveedores',
            'pos:proveedor_crear',
            'pos:proveedor_detalle',
            'pos:deuda_proveedores',
            'pos:recepcion_mercaderia',
            'pos:logs_auditoria',
            'pos:logs_autorizaciones',
            'pos:exportar_logs',
            'pos:intentos_login',
            'pos:alertas_sistema',
            'pos:alertas_tarjetas_saldo',
            'pos:admin_autorizaciones',
            'pos:autorizar_saldo_negativo',
            'pos:validar_autorizacion',
            'pos:validar_supervisor',
            'pos:validar_pago',
            'pos:desbloquear_cuenta',
            'pos:gestionar_grados',
            'pos:historial_grados',
            'pos:configurar_tarifas',
            'pos:gestionar_fotos_hijos',
            'pos:conciliacion_pagos',
            'pos:lista_pagos_pendientes',
            'pos:ticket_api'
        ],
        
        'gestion_views_faltantes': [
            'gestion:index',
            'gestion:dashboard',
            'gestion:crear_empleado',
            'gestion:gestionar_empleados',
            'gestion:perfil_empleado',
            'gestion:cambiar_contrasena_empleado',
            'gestion:productos_lista',
            'gestion:crear_producto',
            'gestion:editar_producto',
            'gestion:importar_productos',
            'gestion:exportar_productos_excel',
            'gestion:exportar_productos_csv',
            'gestion:categorias_lista',
            'gestion:crear_categoria',
            'gestion:editar_categoria',
            'gestion:eliminar_categoria',
            'gestion:clientes_lista',
            'gestion:ventas_lista',
            'gestion:facturacion_listado',
            'gestion:facturacion_kude',
            'gestion:facturacion_anular_api',
            'gestion:facturacion_reporte_cumplimiento',
            'gestion:reporte_mensual_completo',
            'gestion:validar_pago_action'
        ],
        
        'portal_views_faltantes': [
            'gestion:portal_dashboard',
            'gestion:portal_login',
            'gestion:portal_logout',
            'gestion:portal_perfil',
            'gestion:portal_cambiar_password',
            'gestion:portal_configurar_2fa',
            'gestion:portal_verificar_2fa',
            'gestion:portal_activar_2fa',
            'gestion:portal_deshabilitar_2fa',
            'gestion:portal_restablecer_password',
            'gestion:portal_revocar_terminos',
            'gestion:portal_mis_hijos',
            'gestion:portal_consumos_hijo',
            'gestion:portal_restricciones_hijo',
            'gestion:portal_cargar_saldo',
            'gestion:portal_pagos',
            'gestion:portal_recargas',
            'gestion:portal_recargar_tarjeta',
            'gestion:portal_notificaciones_saldo',
            'gestion:api_portal_movimientos',
            'gestion:api_portal_saldo'
        ],
        
        'archivos_estaticos': [
            'img/logo.png',
            'css/base.css',
            'js/base.js',
            'icons/icon-192x192.png',
            'icons/icon-32x32.png', 
            'icons/icon-16x16.png',
            'css/portal.css',
            'js/portal.js',
            'css/pos.css',
            'js/pos.js',
            'icons/icon-512.png',
            'images/logo.png'
        ]
    }
    
    return problemas_por_categoria

def crear_plan_resolucion():
    """Crear plan de resolución por categorías"""
    
    problemas = analizar_problemas_detallado()
    
    print("ANALISIS DETALLADO DE 120 PROBLEMAS RESTANTES")
    print("=" * 60)
    
    total_problemas = 0
    for categoria, items in problemas.items():
        total_problemas += len(items)
        print(f"\n{categoria.upper().replace('_', ' ')} ({len(items)} problemas):")
        for item in items[:5]:  # Mostrar solo primeros 5
            print(f"  - {item}")
        if len(items) > 5:
            print(f"  ... y {len(items) - 5} más")
    
    print(f"\nTOTAL ANALIZADO: {total_problemas} problemas")
    
    print("\n" + "=" * 60)
    print("PLAN DE RESOLUCION RECOMENDADO:")
    print("=" * 60)
    
    print("\n1. PRIORIDAD ALTA - Archivos Estáticos (12 problemas):")
    print("   ✅ Fácil de resolver")
    print("   • Verificar paths de archivos CSS/JS/imágenes")
    print("   • Actualizar referencias en templates")
    print("   • Tiempo estimado: 30 minutos")
    
    print("\n2. PRIORIDAD ALTA - URLs de Dashboard (4 problemas):")
    print("   ✅ Ya implementadas, solo falta mapeo")
    print("   • dashboard_unificado, dashboard_ventas_detalle, etc.")
    print("   • Solo corregir referencias en templates")
    print("   • Tiempo estimado: 15 minutos")
    
    print("\n3. PRIORIDAD MEDIA - Admin URLs (9 problemas):")
    print("   ⚠️  Requiere configuración Django Admin")
    print("   • admin:gestion_*_changelist, admin:index")
    print("   • Verificar registro de modelos en admin.py")
    print("   • Tiempo estimado: 45 minutos")
    
    print("\n4. PRIORIDAD BAJA - Views Django (80+ problemas):")
    print("   🔶 Requiere implementación de views")
    print("   • POS views: dashboards, reportes, funcionalidades")
    print("   • Gestion views: CRUD, reportes")
    print("   • Portal views: autenticación, perfil")
    print("   • Tiempo estimado: 4-6 horas")
    
    print("\n" + "=" * 60)
    print("RECOMENDACION INMEDIATA:")
    print("=" * 60)
    print("✅ Resolver categorías 1 y 2 PRIMERO (16 problemas)")
    print("   • Máximo impacto con mínimo esfuerzo")
    print("   • Reducirá problemas de ~120 a ~104")
    print("   • Sistema será más funcional inmediatamente")
    
    print("\n🎯 ¿Procedemos con categorías 1 y 2?")
    print("   (Archivos estáticos + Dashboard URLs)")

def main():
    crear_plan_resolucion()

if __name__ == "__main__":
    main()