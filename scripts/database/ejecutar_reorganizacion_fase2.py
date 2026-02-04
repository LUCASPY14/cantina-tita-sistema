"""
FASE 2: Consolidar duplicados entre portal/, pos/ y gestion/
Elimina ~50 duplicados restantes y organiza templates por función
"""
import os
import shutil
from pathlib import Path
import json

# Mapeo de duplicados a consolidar
# Formato: 'archivo_a_eliminar': 'archivo_a_mantener'
CONSOLIDACION = {
    # ALMUERZOS (12 duplicados) - MANTENER portal/
    'pos/lunch/almuerzo.html': 'portal/almuerzo.html',
    'pos/lunch/almuerzo_cuentas_mensuales.html': 'portal/almuerzo_cuentas_mensuales.html',
    'pos/lunch/almuerzo_generar_cuentas.html': 'portal/almuerzo_generar_cuentas.html',
    'pos/lunch/almuerzo_pagar.html': 'portal/almuerzo_pagar.html',
    'pos/lunch/almuerzo_reportes.html': 'portal/almuerzo_reportes.html',
    'pos/lunch/almuerzo_reporte_diario.html': 'portal/almuerzo_reporte_diario.html',
    'pos/lunch/almuerzo_reporte_estudiante.html': 'portal/almuerzo_reporte_estudiante.html',
    'pos/lunch/almuerzo_reporte_mensual.html': 'portal/almuerzo_reporte_mensual.html',
    'pos/lunch/configurar_precio.html': 'portal/configurar_precio.html',
    'pos/lunch/ticket_almuerzo.html': 'portal/ticket_almuerzo.html',
    
    # CAJA (5 duplicados) - MANTENER portal/
    'pos/cash_register/apertura_caja.html': 'portal/apertura_caja.html',
    'pos/cash_register/cierre_caja.html': 'portal/cierre_caja.html',
    'pos/cash_register/arqueo_caja.html': 'portal/arqueo_caja.html',
    'pos/cash_register/cajas_dashboard.html': 'portal/cajas_dashboard.html',
    
    # CUENTAS (3 duplicados) - MANTENER pos/ (versión más completa)
    'portal/cuenta_corriente.html': 'pos/cuenta_corriente.html',
    'portal/cuenta_corriente_unificada.html': 'pos/cuenta_corriente_unificada.html',
    'pos/accounts/index.html': 'pos/cuenta_corriente.html',  # Duplicado adicional
    'pos/accounts/unificada.html': 'pos/cuenta_corriente_unificada.html',  # Duplicado adicional
    
    # COMPROBANTES Y RECARGAS
    'portal/comprobante_recargas.html': 'pos/recharges/comprobante.html',
    'portal/procesar_recargas.html': 'pos/recharges/procesar.html',
    'portal/recargas_lista.html': 'pos/recharges/recargas_lista.html',
    'portal/_recargas.html': 'pos/recharges/index.html',
    
    # DASHBOARDS (consolidar versiones)
    'portal/dashboard.html': 'pos/cash_register/dashboard.html',
    'portal/dashboard_comisiones.html': 'pos/commissions/dashboard.html',
    'portal/dashboard_compras.html': 'pos/purchases/dashboard.html',
    'portal/inventario_dashboard.html': 'pos/inventory/dashboard.html',
    'portal/pos_dashboard.html': 'pos/dashboard/main.html',
    
    # INVENTARIO
    'portal/ajuste_inventario.html': 'pos/inventory/adjust_inventory.html',
    'portal/alertas_inventario.html': 'pos/inventory/alerts.html',
    'portal/inventario_productos.html': 'pos/inventory/products_list.html',
    'portal/productos.html': 'pos/inventory/products_list.html',
    
    # ADMIN
    'portal/admin_autorizaciones.html': 'admin/admin_autorizaciones.html',
    'portal/configurar_limites_masivo.html': 'admin/configurar_limites_masivo.html',
    
    # GESTION - Duplicados con pos/
    'gestion/employees/cambiar_contrasena_empleado.html': 'portal/auth/cambiar_password.html',
    'gestion/employees/perfil_empleado.html': 'portal/profile/perfil.html',
    'gestion/employees/gestionar_empleados.html': 'employees/list.html',  # Mover a nueva ubicación
    'gestion/employees/crear.html': 'employees/create.html',  # Mover a nueva ubicación
    
    # CLIENTES - Consolidar versiones
    'gestion/clients/crear_cliente.html': 'pos/crear_cliente.html',  # pos es más completo
    'gestion/clients/clientes_lista.html': 'clients/list.html',  # Mover a nueva ubicación
    'gestion/clients/clientes_list_paginado.html': 'clients/list_paginado.html',  # Mover a nueva ubicación
    
    # PRODUCTOS/CATEGORIAS - Mover gestion/ a inventory/
    'gestion/categoria_form.html': 'inventory/categories/form.html',
    'gestion/categories/create.html': 'inventory/categories/create.html',
    'gestion/categories/edit.html': 'inventory/categories/edit.html',
    'gestion/categories/list.html': 'inventory/categories/list.html',
    'gestion/products/create.html': 'inventory/products/create.html',
    'gestion/products/edit.html': 'inventory/products/edit.html',
    'gestion/products/list.html': 'inventory/products/list.html',
    
    # FACTURACION - Mover a reports/
    'gestion/facturacion_dashboard.html': 'reports/billing/dashboard.html',
    'gestion/facturacion_listado.html': 'reports/billing/listado.html',
    'gestion/facturacion_mensual_almuerzos.html': 'reports/billing/mensual_almuerzos.html',
    
    # VALIDACIONES - Mover a payments/
    'gestion/validar_carga.html': 'payments/validate/carga.html',
    'gestion/validar_pago.html': 'payments/validate/pago.html',
    'gestion/validar_pagos.html': 'payments/validate/pagos.html',
    'gestion/lista_cargas_pendientes.html': 'payments/pending/cargas.html',
    'gestion/lista_pagos_pendientes.html': 'payments/pending/pagos.html',
    
    # ALMUERZOS GESTION - Mover a lunch/
    'gestion/almuerzos_dashboard.html': 'lunch/dashboard.html',
    'gestion/menu_diario.html': 'lunch/menu/daily.html',
    'gestion/planes_almuerzo.html': 'lunch/plans/list.html',
    'gestion/registro_consumo_almuerzo.html': 'lunch/registration/consume.html',
    'gestion/suscripciones_almuerzo.html': 'lunch/plans/subscriptions.html',
}

# Mapeo de referencias a actualizar en vistas
REFERENCIAS_A_ACTUALIZAR = {
    # Almuerzos
    'pos/lunch/almuerzo.html': 'portal/almuerzo.html',
    'pos/lunch/almuerzo_cuentas_mensuales.html': 'portal/almuerzo_cuentas_mensuales.html',
    'pos/lunch/almuerzo_generar_cuentas.html': 'portal/almuerzo_generar_cuentas.html',
    'pos/lunch/almuerzo_pagar.html': 'portal/almuerzo_pagar.html',
    'pos/lunch/almuerzo_reportes.html': 'portal/almuerzo_reportes.html',
    'pos/lunch/almuerzo_reporte_diario.html': 'portal/almuerzo_reporte_diario.html',
    'pos/lunch/almuerzo_reporte_estudiante.html': 'portal/almuerzo_reporte_estudiante.html',
    'pos/lunch/almuerzo_reporte_mensual.html': 'portal/almuerzo_reporte_mensual.html',
    'pos/lunch/configurar_precio.html': 'portal/configurar_precio.html',
    'pos/lunch/ticket_almuerzo.html': 'portal/ticket_almuerzo.html',
    
    # Caja
    'pos/cash_register/apertura_caja.html': 'portal/apertura_caja.html',
    'pos/cash_register/cierre_caja.html': 'portal/cierre_caja.html',
    'pos/cash_register/arqueo_caja.html': 'portal/arqueo_caja.html',
    'pos/cash_register/cajas_dashboard.html': 'portal/cajas_dashboard.html',
    
    # Cuentas (invertido - mantener pos)
    'portal/cuenta_corriente.html': 'pos/cuenta_corriente.html',
    'portal/cuenta_corriente_unificada.html': 'pos/cuenta_corriente_unificada.html',
    
    # Recargas
    'portal/comprobante_recargas.html': 'pos/recharges/comprobante.html',
    'portal/procesar_recargas.html': 'pos/recharges/procesar.html',
    'portal/recargas_lista.html': 'pos/recharges/recargas_lista.html',
    
    # Dashboards
    'portal/dashboard_comisiones.html': 'pos/commissions/dashboard.html',
    'portal/dashboard_compras.html': 'pos/purchases/dashboard.html',
    
    # Gestion
    'gestion/facturacion_dashboard.html': 'reports/billing/dashboard.html',
    'gestion/facturacion_listado.html': 'reports/billing/listado.html',
    'gestion/facturacion_mensual_almuerzos.html': 'reports/billing/mensual_almuerzos.html',
    'gestion/validar_carga.html': 'payments/validate/carga.html',
    'gestion/validar_pago.html': 'payments/validate/pago.html',
    'gestion/validar_pagos.html': 'payments/validate/pagos.html',
    'gestion/lista_cargas_pendientes.html': 'payments/pending/cargas.html',
    'gestion/lista_pagos_pendientes.html': 'payments/pending/pagos.html',
    'gestion/almuerzos_dashboard.html': 'lunch/dashboard.html',
    'gestion/menu_diario.html': 'lunch/menu/daily.html',
    'gestion/planes_almuerzo.html': 'lunch/plans/list.html',
    'gestion/registro_consumo_almuerzo.html': 'lunch/registration/consume.html',
    'gestion/suscripciones_almuerzo.html': 'lunch/plans/subscriptions.html',
}

def crear_directorios_necesarios():
    """Crea los directorios necesarios para la nueva estructura"""
    print("=" * 80)
    print("CREANDO DIRECTORIOS")
    print("=" * 80)
    
    dirs_necesarios = {
        'clients',
        'employees',
        'inventory/categories',
        'lunch/menu',
        'lunch/plans',
        'lunch/registration',
        'payments/validate',
        'payments/pending',
        'reports/billing',
    }
    
    base_path = Path('frontend/templates')
    for dir_rel in sorted(dirs_necesarios):
        dir_path = base_path / dir_rel
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_rel}/")
    
    print(f"\n✅ {len(dirs_necesarios)} directorios creados/verificados")

def mover_y_consolidar():
    """Mueve archivos a nuevas ubicaciones y elimina duplicados"""
    print("\n" + "=" * 80)
    print("CONSOLIDANDO TEMPLATES")
    print("=" * 80)
    
    base_path = Path('frontend/templates')
    movidos = 0
    eliminados = 0
    errores = 0
    
    # Primero, copiar archivos que necesitan moverse a nuevas ubicaciones
    archivos_a_mover = {}
    for origen_rel, destino_rel in CONSOLIDACION.items():
        origen = base_path / origen_rel
        destino = base_path / destino_rel
        
        if not origen.exists():
            continue
        
        # Si el destino no existe, es un movimiento
        if not destino.exists():
            archivos_a_mover[origen] = destino
    
    # Mover archivos
    print("\n📦 MOVIENDO ARCHIVOS A NUEVAS UBICACIONES:")
    for origen, destino in archivos_a_mover.items():
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)
            origen_rel = origen.relative_to(base_path)
            destino_rel = destino.relative_to(base_path)
            print(f"  ✅ {origen_rel} → {destino_rel}")
            movidos += 1
        except Exception as e:
            print(f"  ❌ Error moviendo {origen.relative_to(base_path)}: {e}")
            errores += 1
    
    # Ahora eliminar duplicados
    print("\n🗑️  ELIMINANDO DUPLICADOS:")
    for origen_rel, destino_rel in CONSOLIDACION.items():
        origen = base_path / origen_rel
        destino = base_path / destino_rel
        
        if not origen.exists():
            continue
        
        # Si el destino existe, eliminar el origen (es duplicado)
        if destino.exists() and origen != destino:
            try:
                origen.unlink()
                print(f"  ❌ {origen_rel} (→ mantener {destino_rel})")
                eliminados += 1
            except Exception as e:
                print(f"  ⚠️  Error eliminando {origen_rel}: {e}")
                errores += 1
    
    print(f"\n📊 RESUMEN:")
    print(f"   • Archivos movidos: {movidos}")
    print(f"   • Archivos eliminados: {eliminados}")
    print(f"   • Errores: {errores}")
    
    return movidos, eliminados, errores

def buscar_referencias():
    """Busca referencias a templates en vistas Python"""
    print("\n" + "=" * 80)
    print("BUSCANDO REFERENCIAS EN CÓDIGO")
    print("=" * 80)
    
    referencias_encontradas = {}
    backend_path = Path('backend')
    
    # Buscar en todos los archivos .py
    for py_file in backend_path.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Buscar referencias a templates que vamos a consolidar
            for viejo, nuevo in REFERENCIAS_A_ACTUALIZAR.items():
                if viejo in contenido:
                    if viejo not in referencias_encontradas:
                        referencias_encontradas[viejo] = []
                    referencias_encontradas[viejo].append(str(py_file))
        except:
            pass
    
    if referencias_encontradas:
        print(f"\n⚠️  REFERENCIAS ENCONTRADAS: {len(referencias_encontradas)}")
        for template, archivos in sorted(referencias_encontradas.items()):
            print(f"\n  📄 {template}:")
            for archivo in archivos[:3]:
                print(f"     • {archivo}")
            if len(archivos) > 3:
                print(f"     ... y {len(archivos) - 3} más")
    else:
        print("\n✅ No se encontraron referencias directas")
    
    return referencias_encontradas

def limpiar_carpetas_vacias():
    """Elimina carpetas vacías después de la consolidación"""
    print("\n" + "=" * 80)
    print("LIMPIANDO CARPETAS VACÍAS")
    print("=" * 80)
    
    base_path = Path('frontend/templates')
    eliminadas = 0
    
    # Buscar carpetas vacías (recursivamente, de abajo hacia arriba)
    for _ in range(5):  # Múltiples pasadas para carpetas anidadas
        for dir_path in sorted(base_path.rglob('*'), reverse=True):
            if dir_path.is_dir():
                try:
                    # Intentar eliminar si está vacía
                    if not any(dir_path.iterdir()):
                        dir_rel = dir_path.relative_to(base_path)
                        dir_path.rmdir()
                        print(f"  🗑️  {dir_rel}/")
                        eliminadas += 1
                except:
                    pass
    
    print(f"\n✅ {eliminadas} carpetas vacías eliminadas")
    return eliminadas

def generar_reporte_final():
    """Genera reporte final de FASE 2"""
    print("\n" + "=" * 80)
    print("GENERANDO REPORTE FINAL")
    print("=" * 80)
    
    base_path = Path('frontend/templates')
    
    # Contar templates
    total_templates = len(list(base_path.rglob('*.html')))
    
    # Contar por carpeta principal
    por_carpeta = {}
    for template in base_path.rglob('*.html'):
        carpeta = str(template.relative_to(base_path).parts[0])
        por_carpeta[carpeta] = por_carpeta.get(carpeta, 0) + 1
    
    print("\n📊 ESTRUCTURA FINAL:")
    for carpeta in sorted(por_carpeta.keys()):
        print(f"   {carpeta}/: {por_carpeta[carpeta]} archivos")
    
    print(f"\n📈 TOTAL TEMPLATES: {total_templates}")
    
    return total_templates, por_carpeta

def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("REORGANIZACIÓN DE TEMPLATES - FASE 2")
    print("Consolidar duplicados entre portal/, pos/ y gestion/")
    print("=" * 80)
    
    # Confirmación
    print("\n⚠️  ADVERTENCIA:")
    print("Esta operación:")
    print("  • Moverá ~20 archivos a nuevas ubicaciones")
    print("  • Eliminará ~50 archivos duplicados")
    print("  • Limpiará carpetas vacías")
    print("\nSe recomienda tener backup actualizado.")
    
    respuesta = input("\n¿Continuar? (sí/no): ")
    if respuesta.lower() not in ['sí', 'si', 's', 'yes', 'y']:
        print("\n❌ Operación cancelada.")
        return False
    
    # 1. Crear directorios
    crear_directorios_necesarios()
    
    # 2. Mover y consolidar
    movidos, eliminados, errores = mover_y_consolidar()
    
    # 3. Buscar referencias
    referencias = buscar_referencias()
    
    # 4. Limpiar carpetas vacías
    carpetas_eliminadas = limpiar_carpetas_vacias()
    
    # 5. Reporte final
    total, distribucion = generar_reporte_final()
    
    # Resumen
    print("\n" + "=" * 80)
    print("✅ FASE 2 COMPLETADA")
    print("=" * 80)
    print(f"""
Resumen:
• Archivos movidos: {movidos}
• Archivos eliminados: {eliminados}
• Carpetas limpiadas: {carpetas_eliminadas}
• Templates totales: {total}
• Errores: {errores}

{f"⚠️  Referencias a actualizar: {len(referencias)}" if referencias else "✅ Sin referencias pendientes"}

Siguiente paso:
• Actualizar referencias en vistas (si las hay)
• Testing de templates
• Proceder con FASE 3 (opcional - reorganización final)
""")
    
    return True

if __name__ == "__main__":
    main()
