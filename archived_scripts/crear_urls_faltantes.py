#!/usr/bin/env python
"""
Script para crear las URLs de Django que faltan más críticas
"""

import os

def crear_urls_portal():
    """Crear portal_urls.py con las URLs del portal que faltan"""
    
    portal_urls_content = '''"""
URLs para el portal de clientes/padres de familia
"""
from django.urls import path
from gestion import views

app_name = 'portal'

urlpatterns = [
    # Autenticación
    path('login/', views.portal_login, name='portal_login'),
    path('logout/', views.portal_logout, name='portal_logout'),
    path('dashboard/', views.portal_dashboard, name='portal_dashboard'),
    
    # Perfil
    path('perfil/', views.portal_perfil, name='portal_perfil'),
    path('cambiar-password/', views.portal_cambiar_password, name='portal_cambiar_password'),
    
    # 2FA
    path('configurar-2fa/', views.portal_configurar_2fa, name='portal_configurar_2fa'),
    path('verificar-2fa/', views.portal_verificar_2fa, name='portal_verificar_2fa'),
    path('activar-2fa/', views.portal_activar_2fa, name='portal_activar_2fa'),
    path('deshabilitar-2fa/', views.portal_deshabilitar_2fa, name='portal_deshabilitar_2fa'),
    
    # Recuperación de password
    path('restablecer-password/', views.portal_restablecer_password, name='portal_restablecer_password'),
    path('revocar-terminos/', views.portal_revocar_terminos, name='portal_revocar_terminos'),
    
    # Hijos
    path('mis-hijos/', views.portal_mis_hijos, name='portal_mis_hijos'),
    path('consumos-hijo/<int:hijo_id>/', views.portal_consumos_hijo, name='portal_consumos_hijo'),
    path('restricciones-hijo/<int:hijo_id>/', views.portal_restricciones_hijo, name='portal_restricciones_hijo'),
    
    # Pagos y recargas
    path('cargar-saldo/', views.portal_cargar_saldo, name='portal_cargar_saldo'),
    path('pagos/', views.portal_pagos, name='portal_pagos'),
    path('recargas/', views.portal_recargas, name='portal_recargas'),
    path('recargar-tarjeta/', views.portal_recargar_tarjeta, name='portal_recargar_tarjeta'),
    
    # Notificaciones
    path('notificaciones-saldo/', views.portal_notificaciones_saldo, name='portal_notificaciones_saldo'),
    
    # APIs
    path('api/movimientos/<int:tarjeta_id>/', views.api_portal_movimientos, name='api_portal_movimientos'),
    path('api/saldo/<int:tarjeta_id>/', views.api_portal_saldo, name='api_portal_saldo'),
]
'''
    
    with open('backend/portal_urls.py', 'w', encoding='utf-8') as f:
        f.write(portal_urls_content)
    
    print("✅ portal_urls.py creado")

def crear_urls_principales():
    """Crear/completar las URLs principales en cantina_project/urls.py"""
    
    urls_principales = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # URLs principales
    path('', views.dashboard_unificado, name='dashboard_unificado'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/stock-detalle/', views.dashboard_stock_detalle, name='dashboard_stock_detalle'),
    path('dashboard/ventas-detalle/', views.dashboard_ventas_detalle, name='dashboard_ventas_detalle'),
    path('invalidar-cache-dashboard/', views.invalidar_cache_dashboard, name='invalidar_cache_dashboard'),
    
    # Apps
    path('pos/', include('pos.urls')),
    path('gestion/', include('gestion.urls')),
    path('portal/', include('portal_urls')),  # Incluir portal URLs
]

# Archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
'''
    
    urls_file = 'backend/cantina_project/urls.py'
    if os.path.exists(urls_file):
        print("✅ URLs principales ya existen en cantina_project/urls.py")
        # Solo agregar portal si no existe
        with open(urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'portal_urls' not in content:
            # Agregar include de portal_urls
            if "path('gestion/', include('gestion.urls'))," in content:
                content = content.replace(
                    "path('gestion/', include('gestion.urls')),",
                    "path('gestion/', include('gestion.urls')),\n    path('portal/', include('portal_urls')),"
                )
                with open(urls_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Agregado portal_urls a cantina_project/urls.py")
    else:
        print("⚠️  No encontrado cantina_project/urls.py")

def completar_pos_urls():
    """Completar URLs faltantes en pos/urls.py"""
    
    urls_faltantes = [
        # Dashboards
        "path('dashboard/', views.dashboard, name='dashboard'),",
        "path('inventario-dashboard/', views.inventario_dashboard, name='inventario_dashboard'),",
        "path('almuerzos-dashboard/', views.almuerzos_dashboard, name='almuerzos_dashboard'),",
        "path('compras-dashboard/', views.compras_dashboard, name='compras_dashboard'),",
        "path('cajas-dashboard/', views.cajas_dashboard, name='cajas_dashboard'),",
        "path('comisiones-dashboard/', views.comisiones_dashboard, name='comisiones_dashboard'),",
        "path('dashboard-seguridad/', views.dashboard_seguridad, name='dashboard_seguridad'),",
        
        # Ventas
        "path('venta/', views.venta, name='venta'),",
        "path('anular-venta/', views.anular_venta, name='anular_venta'),",
        "path('nueva-compra/', views.nueva_compra, name='nueva_compra'),",
        
        # Clientes y tarjetas
        "path('crear-cliente/', views.crear_cliente, name='crear_cliente'),",
        "path('gestionar-clientes/', views.gestionar_clientes, name='gestionar_clientes'),",
        "path('buscar-tarjeta/', views.buscar_tarjeta, name='buscar_tarjeta'),",
        "path('crear-tarjeta-autorizacion/', views.crear_tarjeta_autorizacion, name='crear_tarjeta_autorizacion'),",
        
        # Recargas
        "path('recargas/', views.recargas, name='recargas'),",
        "path('procesar-recarga/', views.procesar_recarga, name='procesar_recarga'),",
        "path('validar-carga-saldo/', views.validar_carga_saldo, name='validar_carga_saldo'),",
        "path('comprobante-recarga/', views.comprobante_recarga, name='comprobante_recarga'),",
        "path('historial-recargas/', views.historial_recargas, name='historial_recargas'),",
        "path('lista-cargas-pendientes/', views.lista_cargas_pendientes, name='lista_cargas_pendientes'),",
        
        # Cuenta corriente
        "path('cuenta-corriente/', views.cuenta_corriente, name='cuenta_corriente'),",
        "path('cc-estado-cuenta/', views.cc_estado_cuenta, name='cc_estado_cuenta'),",
        "path('cc-detalle/<int:cuenta_id>/', views.cc_detalle, name='cc_detalle'),",
        "path('cc-registrar-pago/', views.cc_registrar_pago, name='cc_registrar_pago'),",
        "path('cuenta-corriente-unificada/', views.cuenta_corriente_unificada, name='cuenta_corriente_unificada'),",
        "path('cuentas-mensuales/', views.cuentas_mensuales, name='cuentas_mensuales'),",
        "path('generar-cuentas/', views.generar_cuentas, name='generar_cuentas'),",
        
        # Inventario
        "path('inventario-productos/', views.inventario_productos, name='inventario_productos'),",
        "path('ajuste-inventario/', views.ajuste_inventario, name='ajuste_inventario'),",
        "path('kardex-producto/<int:producto_id>/', views.kardex_producto, name='kardex_producto'),",
        "path('buscar-producto/', views.buscar_producto, name='buscar_producto'),",
        "path('alertas-inventario/', views.alertas_inventario, name='alertas_inventario'),",
        
        # Cajas
        "path('apertura-caja/', views.apertura_caja, name='apertura_caja'),",
        "path('cierre-caja/', views.cierre_caja, name='cierre_caja'),",
        "path('arqueo-caja/', views.arqueo_caja, name='arqueo_caja'),",
        
        # Reportes
        "path('reportes/', views.reportes, name='reportes'),",
        "path('exportar-reporte/', views.exportar_reporte, name='exportar_reporte'),",
        "path('reporte-comisiones/', views.reporte_comisiones, name='reporte_comisiones'),",
        "path('reporte-mensual-separado/', views.reporte_mensual_separado, name='reporte_mensual_separado'),",
        "path('reporte-por-estudiante/', views.reporte_por_estudiante, name='reporte_por_estudiante'),",
        "path('reporte-autorizaciones-saldo-negativo/', views.reporte_autorizaciones_saldo_negativo, name='reporte_autorizaciones_saldo_negativo'),",
        
        # Almuerzos
        "path('pos-almuerzo/', views.pos_almuerzo, name='pos_almuerzo'),",
        "path('pagar-almuerzo/', views.pagar_almuerzo, name='pagar_almuerzo'),",
        "path('planes-almuerzo/', views.planes_almuerzo, name='planes_almuerzo'),",
        "path('crear-plan-almuerzo/', views.crear_plan_almuerzo, name='crear_plan_almuerzo'),",
        "path('suscripciones-almuerzo/', views.suscripciones_almuerzo, name='suscripciones_almuerzo'),",
        "path('crear-suscripcion-almuerzo/', views.crear_suscripcion_almuerzo, name='crear_suscripcion_almuerzo'),",
        "path('configurar-precio-almuerzo/', views.configurar_precio_almuerzo, name='configurar_precio_almuerzo'),",
        "path('registrar-consumo-almuerzo/', views.registrar_consumo_almuerzo, name='registrar_consumo_almuerzo'),",
        "path('registro-consumo-almuerzo/', views.registro_consumo_almuerzo, name='registro_consumo_almuerzo'),",
        "path('reportes-almuerzos/', views.reportes_almuerzos, name='reportes_almuerzos'),",
        "path('almuerzo-reportes/', views.almuerzo_reportes, name='almuerzo_reportes'),",
        "path('reporte-almuerzos-diarios/', views.reporte_almuerzos_diarios, name='reporte_almuerzos_diarios'),",
        
        # Proveedores
        "path('proveedores/', views.proveedores, name='proveedores'),",
        "path('proveedor-crear/', views.proveedor_crear, name='proveedor_crear'),",
        "path('proveedor-detalle/<int:proveedor_id>/', views.proveedor_detalle, name='proveedor_detalle'),",
        "path('deuda-proveedores/', views.deuda_proveedores, name='deuda_proveedores'),",
        "path('recepcion-mercaderia/', views.recepcion_mercaderia, name='recepcion_mercaderia'),",
        
        # Seguridad y logs
        "path('logs-auditoria/', views.logs_auditoria, name='logs_auditoria'),",
        "path('logs-autorizaciones/', views.logs_autorizaciones, name='logs_autorizaciones'),",
        "path('exportar-logs/', views.exportar_logs, name='exportar_logs'),",
        "path('intentos-login/', views.intentos_login, name='intentos_login'),",
        "path('alertas-sistema/', views.alertas_sistema, name='alertas_sistema'),",
        "path('alertas-tarjetas-saldo/', views.alertas_tarjetas_saldo, name='alertas_tarjetas_saldo'),",
        
        # Autorizaciones
        "path('admin-autorizaciones/', views.admin_autorizaciones, name='admin_autorizaciones'),",
        "path('autorizar-saldo-negativo/', views.autorizar_saldo_negativo, name='autorizar_saldo_negativo'),",
        "path('validar-autorizacion/', views.validar_autorizacion, name='validar_autorizacion'),",
        "path('validar-supervisor/', views.validar_supervisor, name='validar_supervisor'),",
        "path('validar-pago/', views.validar_pago, name='validar_pago'),",
        "path('desbloquear-cuenta/', views.desbloquear_cuenta, name='desbloquear_cuenta'),",
        
        # Otros
        "path('gestionar-grados/', views.gestionar_grados, name='gestionar_grados'),",
        "path('historial-grados/', views.historial_grados, name='historial_grados'),",
        "path('configurar-tarifas/', views.configurar_tarifas, name='configurar_tarifas'),",
        "path('gestionar-fotos-hijos/', views.gestionar_fotos_hijos, name='gestionar_fotos_hijos'),",
        "path('conciliacion-pagos/', views.conciliacion_pagos, name='conciliacion_pagos'),",
        "path('lista-pagos-pendientes/', views.lista_pagos_pendientes, name='lista_pagos_pendientes'),",
        
        # API
        "path('api/ticket/', views.ticket_api, name='ticket_api'),",
    ]
    
    pos_urls_file = 'backend/gestion/pos_urls.py'
    if os.path.exists(pos_urls_file):
        with open(pos_urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar cuántas URLs ya existen
        urls_existentes = 0
        urls_agregadas = 0
        
        for url in urls_faltantes:
            # Extraer el nombre de la URL
            name_start = url.find("name='") + 6
            name_end = url.find("')", name_start)
            if name_start > 5 and name_end > name_start:
                name = url[name_start:name_end]
                if f"name='{name}'" not in content:
                    # Agregar antes del último ]
                    last_bracket = content.rfind(']')
                    if last_bracket > 0:
                        content = content[:last_bracket] + f"    {url}\n" + content[last_bracket:]
                        urls_agregadas += 1
                else:
                    urls_existentes += 1
        
        # Escribir el archivo actualizado
        with open(pos_urls_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ pos/urls.py actualizado: {urls_agregadas} URLs agregadas, {urls_existentes} ya existían")
    else:
        print("⚠️  No encontrado pos/urls.py")

def completar_gestion_urls():
    """Completar URLs faltantes en gestion/urls.py"""
    
    urls_faltantes = [
        # Dashboard y principal
        "path('', views.index, name='index'),",
        "path('dashboard/', views.dashboard, name='dashboard'),",
        
        # Empleados
        "path('crear-empleado/', views.crear_empleado, name='crear_empleado'),",
        "path('gestionar-empleados/', views.gestionar_empleados, name='gestionar_empleados'),",
        "path('perfil-empleado/', views.perfil_empleado, name='perfil_empleado'),",
        "path('cambiar-contrasena-empleado/', views.cambiar_contrasena_empleado, name='cambiar_contrasena_empleado'),",
        
        # Productos
        "path('productos/', views.productos_lista, name='productos_lista'),",
        "path('crear-producto/', views.crear_producto, name='crear_producto'),",
        "path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),",
        "path('importar-productos/', views.importar_productos, name='importar_productos'),",
        "path('exportar-productos-excel/', views.exportar_productos_excel, name='exportar_productos_excel'),",
        "path('exportar-productos-csv/', views.exportar_productos_csv, name='exportar_productos_csv'),",
        
        # Categorías
        "path('categorias/', views.categorias_lista, name='categorias_lista'),",
        "path('crear-categoria/', views.crear_categoria, name='crear_categoria'),",
        "path('editar-categoria/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),",
        "path('eliminar-categoria/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),",
        
        # Clientes
        "path('clientes/', views.clientes_lista, name='clientes_lista'),",
        
        # Ventas
        "path('ventas/', views.ventas_lista, name='ventas_lista'),",
        
        # Facturación
        "path('facturacion-listado/', views.facturacion_listado, name='facturacion_listado'),",
        "path('facturacion-kude/', views.facturacion_kude, name='facturacion_kude'),",
        "path('facturacion-anular-api/', views.facturacion_anular_api, name='facturacion_anular_api'),",
        "path('facturacion-reporte-cumplimiento/', views.facturacion_reporte_cumplimiento, name='facturacion_reporte_cumplimiento'),",
        
        # Reportes
        "path('reporte-mensual-completo/', views.reporte_mensual_completo, name='reporte_mensual_completo'),",
        
        # Validaciones
        "path('validar-pago-action/', views.validar_pago_action, name='validar_pago_action'),",
    ]
    
    gestion_urls_file = 'backend/gestion/urls.py'
    if os.path.exists(gestion_urls_file):
        with open(gestion_urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        urls_agregadas = 0
        urls_existentes = 0
        
        for url in urls_faltantes:
            # Extraer el nombre de la URL
            name_start = url.find("name='") + 6
            name_end = url.find("')", name_start)
            if name_start > 5 and name_end > name_start:
                name = url[name_start:name_end]
                if f"name='{name}'" not in content:
                    # Agregar antes del último ]
                    last_bracket = content.rfind(']')
                    if last_bracket > 0:
                        content = content[:last_bracket] + f"    {url}\n" + content[last_bracket:]
                        urls_agregadas += 1
                else:
                    urls_existentes += 1
        
        # Escribir el archivo actualizado
        with open(gestion_urls_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ gestion/urls.py actualizado: {urls_agregadas} URLs agregadas, {urls_existentes} ya existían")
    else:
        print("⚠️  No encontrado gestion/urls.py")

def main():
    """Crear todas las URLs faltantes"""
    print("🔗 CREANDO URLs FALTANTES")
    print("=" * 50)
    
    # 1. Crear portal_urls.py
    crear_urls_portal()
    
    # 2. Completar URLs principales
    crear_urls_principales()
    
    # 3. Completar pos/urls.py
    completar_pos_urls()
    
    # 4. Completar gestion/urls.py
    completar_gestion_urls()
    
    print(f"\n✅ URLs CREADAS Y ACTUALIZADAS")
    print(f"\n🎯 VERIFICACIÓN:")
    print(f"  python verificar_rutas_urls.py")

if __name__ == "__main__":
    main()