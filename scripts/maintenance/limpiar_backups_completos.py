#!/usr/bin/env python
"""
Script para limpiar archivos backup del proyecto después de modernización completa
Elimina de forma segura backups innecesarios manteniendo BD y scripts importantes
"""

import os
import shutil
from pathlib import Path

def limpiar_backups_proyecto():
    """
    Limpia archivos backup del proyecto manteniendo solo los esenciales
    """
    
    # Carpetas grandes de backup a eliminar (completamente redundantes)
    carpetas_backup_eliminar = [
        "backup_reorganizacion_profesional",
        "backup_templates_antes_reorganizacion", 
        "backup_templates_final",
        "backups_templates_eliminados"
    ]
    
    # Archivos .backup.html individuales a eliminar
    archivos_backup_templates = [
        "frontend/templates/apps/auth/intentos_login.backup.html",
        "frontend/templates/apps/auth/login.backup.html",
        "frontend/templates/apps/auth/logs_auditoria.backup.html",
        "frontend/templates/apps/gestion/admin/dashboard.backup.html",
        "frontend/templates/apps/gestion/almuerzos_dashboard.backup.html",
        "frontend/templates/apps/gestion/categoria_form.backup.html",
        "frontend/templates/apps/gestion/categorias_lista.backup.html",
        "frontend/templates/apps/gestion/clientes/clientes_lista.backup.html",
        "frontend/templates/apps/gestion/clientes/crear_cliente.backup.html",
        "frontend/templates/apps/gestion/dashboard.backup.html",
        "frontend/templates/apps/gestion/empleados/cambiar_contrasena_empleado.backup.html",
        "frontend/templates/apps/gestion/empleados/gestionar_empleados.backup.html",
        "frontend/templates/apps/gestion/empleados/perfil_empleado.backup.html",
        "frontend/templates/apps/gestion/facturacion_dashboard.backup.html",
        "frontend/templates/apps/gestion/facturacion_listado.backup.html",
        "frontend/templates/apps/gestion/facturacion_mensual_almuerzos.backup.html",
        "frontend/templates/apps/gestion/index.backup.html",
        "frontend/templates/apps/gestion/lista_cargas_pendientes.backup.html",
        "frontend/templates/apps/gestion/lista_pagos_pendientes.backup.html",
        "frontend/templates/apps/gestion/menu_diario.backup.html",
        "frontend/templates/apps/gestion/planes_almuerzo.backup.html",
        "frontend/templates/apps/gestion/productos/producto_form.backup.html",
        "frontend/templates/apps/gestion/productos/productos_importar.backup.html",
        "frontend/templates/apps/gestion/productos/productos_importar_preview.backup.html",
        "frontend/templates/apps/gestion/productos/productos_lista.backup.html",
        "frontend/templates/apps/gestion/registro_consumo_almuerzo.backup.html",
        "frontend/templates/apps/gestion/reportes/facturacion_reporte_cumplimiento.backup.html",
        "frontend/templates/apps/gestion/reportes/reportes_almuerzos.backup.html",
        "frontend/templates/apps/gestion/suscripciones_almuerzo.backup.html",
        "frontend/templates/apps/gestion/validar_carga.backup.html",
        "frontend/templates/apps/gestion/validar_pago.backup.html",
        "frontend/templates/apps/gestion/validar_pagos.backup.html",
        "frontend/templates/apps/gestion/ventas_lista.backup.html",
        "frontend/templates/apps/pos/ventas/dashboard_ventas_backup.html",
        "frontend/templates/base/base.backup.html",
        "frontend/templates/base/base_improved.backup.html",
        "frontend/templates/base/gestion_base.backup.html",
        "frontend/templates/pages/dashboard/dashboard.backup.html"
    ]
    
    # Script backup individual
    scripts_backup_eliminar = [
        "scripts_mantenimiento/fix_middleware_and_warnings.py.backup"
    ]
    
    print("🧹 INICIANDO LIMPIEZA DE ARCHIVOS BACKUP")
    print("=" * 60)
    
    eliminados = {
        'carpetas': 0,
        'archivos_template': 0, 
        'scripts': 0,
        'errores': []
    }
    
    # 1. Eliminar carpetas grandes de backup
    print("\n📁 ELIMINANDO CARPETAS DE BACKUP GRANDES:")
    for carpeta in carpetas_backup_eliminar:
        if os.path.exists(carpeta):
            try:
                # Calcular tamaño antes de eliminar
                tamano = sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, dirnames, filenames in os.walk(carpeta)
                           for filename in filenames) / (1024 * 1024)  # MB
                
                shutil.rmtree(carpeta)
                print(f"  ✅ {carpeta} ({tamano:.1f} MB)")
                eliminados['carpetas'] += 1
            except Exception as e:
                error_msg = f"Error eliminando {carpeta}: {str(e)}"
                print(f"  ❌ {error_msg}")
                eliminados['errores'].append(error_msg)
        else:
            print(f"  ⏭️  {carpeta} (no existe)")
    
    # 2. Eliminar archivos .backup.html individuales
    print("\n📄 ELIMINANDO ARCHIVOS .backup.html:")
    for archivo in archivos_backup_templates:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"  ✅ {os.path.basename(archivo)}")
                eliminados['archivos_template'] += 1
            except Exception as e:
                error_msg = f"Error eliminando {archivo}: {str(e)}"
                print(f"  ❌ {error_msg}")
                eliminados['errores'].append(error_msg)
        else:
            print(f"  ⏭️  {os.path.basename(archivo)} (no existe)")
    
    # 3. Eliminar scripts backup
    print("\n🔧 ELIMINANDO SCRIPTS BACKUP:")
    for script in scripts_backup_eliminar:
        if os.path.exists(script):
            try:
                os.remove(script)
                print(f"  ✅ {os.path.basename(script)}")
                eliminados['scripts'] += 1
            except Exception as e:
                error_msg = f"Error eliminando {script}: {str(e)}"
                print(f"  ❌ {error_msg}")
                eliminados['errores'].append(error_msg)
        else:
            print(f"  ⏭️  {os.path.basename(script)} (no existe)")
    
    # MANTENER: backups de base de datos y scripts importantes
    print("\n💾 MANTENIENDO (NO TOCAR):")
    print("  🔒 backups/ - Backups de base de datos")
    print("  🔒 scripts_db/ - Scripts de migración BD")
    print("  🔒 configurar_backup_tareas.py - Script de backup automático")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LIMPIEZA:")
    print(f"  • Carpetas eliminadas: {eliminados['carpetas']}")
    print(f"  • Templates .backup.html eliminados: {eliminados['archivos_template']}")
    print(f"  • Scripts backup eliminados: {eliminados['scripts']}")
    
    if eliminados['errores']:
        print(f"\n⚠️  ERRORES ENCONTRADOS ({len(eliminados['errores'])}):")
        for error in eliminados['errores']:
            print(f"  • {error}")
    else:
        print("\n✅ LIMPIEZA COMPLETADA SIN ERRORES")
    
    print("\n🎯 RESULTADO:")
    print("  • Proyecto más limpio y organizado")
    print("  • Backups importantes mantenidos")
    print("  • Templates activos intactos")
    print("  • Funcionalidad preservada")

if __name__ == "__main__":
    # Confirmar que estamos en el directorio correcto
    if not os.path.exists("frontend/templates"):
        print("❌ Error: No se encuentra la carpeta frontend/templates")
        print("   Ejecuta este script desde la raíz del proyecto Django")
        exit(1)
    
    print("🚀 SCRIPT DE LIMPIEZA DE BACKUPS")
    print("Este script eliminará archivos backup redundantes manteniendo:")
    print("• Backups de base de datos (carpeta backups/)")
    print("• Scripts de migración (scripts_db/)")
    print("• Templates activos funcionando")
    print()
    
    confirmar = input("¿Proceder con la limpieza? (s/N): ").strip().lower()
    if confirmar in ['s', 'si', 'y', 'yes']:
        limpiar_backups_proyecto()
    else:
        print("❌ Operación cancelada")