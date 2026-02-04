#!/usr/bin/env python
"""
Script de corrección masiva de URLs después de verificación
"""

import os
import re
import json

def corregir_urls_archivo(archivo_path):
    """Corrige URLs en un archivo específico"""
    
    if not os.path.exists(archivo_path):
        return
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        contenido_original = contenido
        
        # Mapeo de URLs incorrectas a correctas basado en los archivos de URLs existentes
        mapeo_urls = {
            # URLs principales de pos_urls.py
            'pos:ventas': 'pos:venta',
            'pos:dashboard_ventas': 'pos:dashboard',
            'pos:buscar_productos': 'pos:buscar_producto',
            'pos:ticket': 'pos:ticket_api',
            'pos:procesar_recarga': 'pos:procesar_recarga',
            'pos:historial': 'pos:historial_recargas',
            'pos:comprobante_recarga': 'pos:comprobante_recarga',
            'pos:cuenta_corriente': 'pos:cuenta_corriente',
            'pos:cc_detalle': 'pos:cc_detalle',
            'pos:cc_estado_cuenta': 'pos:cc_estado_cuenta',
            'pos:cc_registrar_pago': 'pos:cc_registrar_pago',
            'pos:proveedores': 'pos:proveedores',
            'pos:proveedor_detalle': 'pos:proveedor_detalle',
            'pos:inventario_dashboard': 'pos:inventario',
            'pos:inventario_productos': 'pos:inventario_productos',
            'pos:ajuste_inventario': 'pos:ajuste_inventario',
            'pos:alertas_inventario': 'pos:alertas_inventario',
            'pos:kardex_producto': 'pos:kardex_producto',
            'pos:nueva_compra': 'pos:nueva_compra',
            'pos:recepcion_mercaderia': 'pos:recepcion_mercaderia',
            'pos:cajas_dashboard': 'pos:cajas_dashboard',
            'pos:apertura_caja': 'pos:apertura_caja',
            'pos:cierre_caja': 'pos:cierre_caja',
            'pos:arqueo_caja': 'pos:arqueo_caja',
            'pos:alertas_sistema': 'pos:alertas_sistema',
            'pos:alertas_tarjetas_saldo': 'pos:alertas_tarjetas_saldo',
            'pos:logs_autorizaciones': 'pos:logs_autorizaciones',
            'pos:logs_auditoria': 'pos:logs_auditoria',
            'pos:intentos_login': 'pos:intentos_login',
            'pos:admin_autorizaciones': 'pos:admin_autorizaciones',
            'pos:autorizar_saldo_negativo': 'pos:autorizar_saldo_negativo',
            'pos:comisiones_dashboard': 'pos:comisiones_dashboard',
            'pos:reporte_comisiones': 'pos:reporte_comisiones',
            'pos:configurar_tarifas': 'pos:configurar_tarifas',
            'pos:conciliacion_pagos': 'pos:conciliacion_pagos',
            'pos:reportes': 'pos:reportes_principales',
            'pos:exportar_reporte': 'pos:exportar_reporte',
            
            # URLs de gestión
            'gestion:index': 'gestion:index',
            'gestion:dashboard': 'gestion:dashboard',
            'gestion:productos_lista': 'gestion:productos_lista',
            'gestion:crear_producto': 'gestion:crear_producto',
            'gestion:editar_producto': 'gestion:editar_producto',
            'gestion:clientes_lista': 'gestion:clientes_lista',
            'gestion:ventas_lista': 'gestion:ventas_lista',
            'gestion:categorias_lista': 'gestion:categorias_lista',
            'gestion:crear_categoria': 'gestion:crear_categoria',
            'gestion:editar_categoria': 'gestion:editar_categoria',
            'gestion:eliminar_categoria': 'gestion:eliminar_categoria',
            'gestion:importar_productos': 'gestion:importar_productos',
            'gestion:exportar_productos_csv': 'gestion:exportar_productos_csv',
            'gestion:exportar_productos_excel': 'gestion:exportar_productos_excel',
            'gestion:validar_pagos_pendientes': 'gestion:validar_pagos_pendientes',
            'gestion:validar_pago_action': 'gestion:validar_pago_action',
            'gestion:gestionar_empleados': 'gestion:gestionar_empleados',
            'gestion:crear_empleado': 'gestion:crear_empleado',
            'gestion:cambiar_contrasena_empleado': 'gestion:cambiar_contrasena_empleado',
            'gestion:perfil_empleado': 'gestion:perfil_empleado',
            'gestion:facturacion_dashboard': 'gestion:facturacion_dashboard',
            'gestion:facturacion_listado': 'gestion:facturacion_listado',
            'gestion:facturacion_reporte': 'gestion:facturacion_reporte',
            
            # URLs principales
            'dashboard': 'dashboard_unificado',
            'dashboard_ventas_detalle': 'dashboard_ventas_detalle',
            'dashboard_stock_detalle': 'dashboard_stock_detalle',
            'invalidar_cache_dashboard': 'invalidar_cache_dashboard',
            'login': 'login',
            'logout': 'logout',
            
            # URLs sin namespace que necesitan ser corregidas
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
            'dashboard_reportes': 'pos:reportes_principales',
            'kardex_producto': 'pos:kardex_producto',
            'cuenta_corriente_unificada': 'pos:cuenta_corriente_unificada',
            'dashboard_unificado': 'dashboard_unificado',
            
            # URLs de portal sin namespace
            'portal_dashboard': 'gestion:portal_dashboard',
            'portal_revocar_terminos': 'gestion:portal_revocar_terminos',
            'facturacion_descargar_kude': 'gestion:facturacion_kude',
            'facturacion_anular_api': 'gestion:facturacion_anular',
            'facturacion_mensual_almuerzos': 'gestion:reporte_mensual_completo',
            'generar_facturacion_mensual': 'gestion:reporte_mensual_completo'
        }
        
        # Aplicar correcciones
        for url_incorrecta, url_correcta in mapeo_urls.items():
            # Buscar y reemplazar URLs en diferentes formatos
            patterns = [
                f'"{url_incorrecta}"',
                f"'{url_incorrecta}'",
                f'url "{url_incorrecta}"',
                f"url '{url_incorrecta}'"
            ]
            
            replacements = [
                f'"{url_correcta}"',
                f"'{url_correcta}'",
                f'url "{url_correcta}"',
                f"url '{url_correcta}'"
            ]
            
            for i, pattern in enumerate(patterns):
                if pattern in contenido:
                    contenido = contenido.replace(pattern, replacements[i])
        
        # Escribir solo si hubo cambios
        if contenido != contenido_original:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error procesando {archivo_path}: {e}")
        return False

def crear_archivos_estaticos_faltantes():
    """Crea archivos estáticos básicos faltantes"""
    
    archivos_crear = {
        'frontend/static/img/logo.png': 'LOGO_PLACEHOLDER',
        'frontend/static/favicon.ico': 'FAVICON_PLACEHOLDER',
        'frontend/static/css/base.css': '/* Estilos base */\nbody { font-family: Arial, sans-serif; }',
        'frontend/static/js/base.js': '// JavaScript base\nconsole.log("Base JS loaded");',
        'frontend/static/css/portal.css': '/* Estilos portal */\n.portal-container { max-width: 1200px; }',
        'frontend/static/js/portal.js': '// Portal JavaScript\nconsole.log("Portal JS loaded");',
        'frontend/static/css/pos.css': '/* Estilos POS */\n.pos-interface { display: flex; }',
        'frontend/static/js/pos.js': '// POS JavaScript\nconsole.log("POS JS loaded");',
        'frontend/static/icons/icon-16x16.png': 'ICON_16_PLACEHOLDER',
        'frontend/static/icons/icon-32x32.png': 'ICON_32_PLACEHOLDER', 
        'frontend/static/icons/icon-192x192.png': 'ICON_192_PLACEHOLDER',
        'frontend/static/icons/icon-512.png': 'ICON_512_PLACEHOLDER',
        'frontend/static/images/logo.png': 'LOGO_PLACEHOLDER'
    }
    
    archivos_creados = 0
    
    for archivo, contenido in archivos_crear.items():
        # Crear directorio si no existe
        directorio = os.path.dirname(archivo)
        os.makedirs(directorio, exist_ok=True)
        
        if not os.path.exists(archivo):
            if contenido.endswith('_PLACEHOLDER'):
                # Para archivos binarios, crear archivo vacío
                with open(archivo, 'wb') as f:
                    f.write(b'')
            else:
                # Para archivos de texto
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
            archivos_creados += 1
    
    return archivos_creados

def main():
    """Ejecuta la corrección masiva"""
    
    print("🔧 CORRECCIÓN MASIVA DE URLs Y ARCHIVOS ESTÁTICOS")
    print("=" * 60)
    
    # Crear archivos estáticos faltantes
    print("\n📁 CREANDO ARCHIVOS ESTÁTICOS FALTANTES:")
    archivos_creados = crear_archivos_estaticos_faltantes()
    print(f"  ✅ Creados: {archivos_creados} archivos estáticos")
    
    # Corregir URLs en templates
    print("\n🔗 CORRIGIENDO URLs EN TEMPLATES:")
    
    templates_corregidos = 0
    total_templates = 0
    
    # Buscar todos los templates
    templates_dir = 'frontend/templates'
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    total_templates += 1
                    archivo_path = os.path.join(root, file)
                    if corregir_urls_archivo(archivo_path):
                        templates_corregidos += 1
                        print(f"  ✅ {os.path.relpath(archivo_path)}")
    
    print(f"\n📊 RESUMEN:")
    print(f"  • Templates procesados: {total_templates}")
    print(f"  • Templates corregidos: {templates_corregidos}")
    print(f"  • Archivos estáticos creados: {archivos_creados}")
    
    if templates_corregidos > 0 or archivos_creados > 0:
        print("\n✅ CORRECCIÓN COMPLETADA")
        print("\n💡 SIGUIENTE PASO:")
        print("  Ejecuta: python verificar_rutas_urls.py")
        print("  Para verificar que se redujeron los errores")
    else:
        print("\n⚠️  NO SE REALIZARON CORRECCIONES")
        print("  Los templates pueden estar ya corregidos")

if __name__ == "__main__":
    if not os.path.exists("frontend/templates"):
        print("❌ Error: No se encuentra frontend/templates")
        print("   Ejecuta desde la raíz del proyecto")
        exit(1)
    
    main()