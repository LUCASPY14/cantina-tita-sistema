"""
Script para mover archivos únicos de templates_sueltos/ a sus ubicaciones correctas
antes de eliminar la carpeta
"""
import os
import shutil
from pathlib import Path

# Mapeo de archivos únicos a sus ubicaciones correctas
MAPEO_ARCHIVOS_UNICOS = {
    # Dashboards
    'templates_sueltos/comisiones_dashboard.html': 'pos/commissions/dashboard.html',
    'templates_sueltos/compras_dashboard.html': 'pos/purchases/dashboard.html',
    'templates_sueltos/dashboard_saldos_tiempo_real.html': 'dashboard/saldos_tiempo_real.html',
    'templates_sueltos/dashboard_ventas.html': 'pos/sales/dashboard.html',
    'templates_sueltos/dashboard_ventas_mejorado.html': 'dashboard/sales.html',
    'templates_sueltos/inventario_dashboard.html': 'pos/inventory/dashboard.html',
    
    # Reportes y facturación
    'templates_sueltos/facturacion_reporte_cumplimiento.html': 'reports/billing/cumplimiento.html',
    
    # Ventas
    'templates_sueltos/lista_ventas.html': 'sales/list.html',
    
    # Productos
    'templates_sueltos/productos_importar.html': 'inventory/products/import.html',
    'templates_sueltos/productos_importar_preview.html': 'inventory/products/import_preview.html',
    
    # Comprobantes
    'templates_sueltos/comprobante_recarga.html': 'payments/voucher/recarga.html',
    
    # Productos list (con error en el nombre)
    'templates_sueltos/productos_list_paginado.html': 'inventory/products/list_paginado.html',
    'templates_sueltos/productos_lista.html': 'inventory/products/list.html',
    
    # Reportes
    'templates_sueltos/reportes_almuerzos.html': 'reports/lunch/almuerzos.html',
    'templates_sueltos/reportes_pos.html': 'reports/sales/pos.html',
}

def crear_directorios():
    """Crea los directorios necesarios"""
    print("Creando directorios...")
    
    dirs_to_create = set()
    for destino in MAPEO_ARCHIVOS_UNICOS.values():
        dir_path = Path('frontend/templates') / Path(destino).parent
        dirs_to_create.add(dir_path)
    
    for dir_path in sorted(dirs_to_create):
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")

def mover_archivos():
    """Mueve los archivos únicos a sus ubicaciones correctas"""
    print("\nMoviendo archivos únicos...")
    
    movidos = 0
    errores = 0
    
    for origen_rel, destino_rel in MAPEO_ARCHIVOS_UNICOS.items():
        origen = Path('frontend/templates') / origen_rel
        destino = Path('frontend/templates') / destino_rel
        
        if not origen.exists():
            print(f"  ⚠️  No existe: {origen_rel}")
            continue
        
        try:
            # Crear directorio de destino si no existe
            destino.parent.mkdir(parents=True, exist_ok=True)
            
            # Mover archivo
            shutil.copy2(origen, destino)
            print(f"  ✅ {origen_rel} → {destino_rel}")
            movidos += 1
        except Exception as e:
            print(f"  ❌ Error moviendo {origen_rel}: {e}")
            errores += 1
    
    print(f"\n📊 Archivos movidos: {movidos}")
    print(f"❌ Errores: {errores}")
    
    return movidos, errores

def actualizar_referencias():
    """Genera script de actualización de referencias en vistas"""
    print("\nGenerando script de actualización de referencias...")
    
    # Generar mapeo de referencias a actualizar
    referencias = {
        # Dashboards
        'pos/dashboard_saldos_tiempo_real.html': 'dashboard/saldos_tiempo_real.html',
        'apps/pos/dashboards/comisiones_dashboard.html': 'pos/commissions/dashboard.html',
        'pos/comisiones_dashboard.html': 'pos/commissions/dashboard.html',
        
        # Productos
        'gestion/productos_importar.html': 'inventory/products/import.html',
        'gestion/productos_importar_preview.html': 'inventory/products/import_preview.html',
        
        # Facturación
        'gestion/facturacion_reporte_cumplimiento.html': 'reports/billing/cumplimiento.html',
    }
    
    script_bash = []
    script_bash.append("#!/bin/bash")
    script_bash.append("# Script para actualizar referencias en vistas")
    script_bash.append("")
    
    for viejo, nuevo in referencias.items():
        # Comando find/replace para Linux/Mac
        script_bash.append(f"# {viejo} → {nuevo}")
        script_bash.append(f"find backend -name '*.py' -type f -exec sed -i 's|{viejo}|{nuevo}|g' {{}} +")
        script_bash.append("")
    
    with open('actualizar_referencias.sh', 'w') as f:
        f.write('\n'.join(script_bash))
    
    # Versión PowerShell
    script_ps = []
    script_ps.append("# Script para actualizar referencias en vistas")
    script_ps.append("")
    
    for viejo, nuevo in referencias.items():
        script_ps.append(f"# {viejo} → {nuevo}")
        script_ps.append(f'Get-ChildItem -Path backend -Filter *.py -Recurse | ForEach-Object {{ (Get-Content $_.FullName) -replace "{viejo}", "{nuevo}" | Set-Content $_.FullName }}')
        script_ps.append("")
    
    with open('actualizar_referencias.ps1', 'w') as f:
        f.write('\n'.join(script_ps))
    
    print("  ✅ actualizar_referencias.sh creado")
    print("  ✅ actualizar_referencias.ps1 creado")

def main():
    print("=" * 80)
    print("MOVER ARCHIVOS ÚNICOS DE templates_sueltos/")
    print("=" * 80)
    
    # 1. Crear directorios
    crear_directorios()
    
    # 2. Mover archivos
    movidos, errores = mover_archivos()
    
    # 3. Generar scripts de actualización
    actualizar_referencias()
    
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print(f"""
Resumen:
• Archivos movidos: {movidos}
• Errores: {errores}

Próximo paso:
Ejecutar actualizar_referencias.ps1 para actualizar las referencias en las vistas
""")

if __name__ == "__main__":
    main()
