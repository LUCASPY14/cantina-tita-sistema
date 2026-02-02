#!/usr/bin/env python3
"""
Script para mover los templates restantes desde gestion/templates/ 
hacia la estructura organizada en /templates
"""

import os
import shutil
from pathlib import Path

def limpiar_templates_restantes():
    """Mover todos los templates restantes a la estructura profesional"""
    
    base_dir = Path("D:/anteproyecto20112025")
    gestion_templates = base_dir / "gestion" / "templates"
    templates_dir = base_dir / "templates"
    
    # Mapeo de archivos a mover
    archivos_por_mover = {
        # Templates de admin
        "admin/dashboard.html": "templates/apps/gestion/admin/dashboard.html",
        
        # Templates de gestion principal
        "gestion/almuerzos_dashboard.html": "templates/apps/gestion/almuerzos_dashboard.html",
        "gestion/base.html": "templates/base/gestion_base.html", 
        "gestion/cambiar_contrasena_empleado.html": "templates/apps/gestion/empleados/cambiar_contrasena_empleado.html",
        "gestion/categorias_lista.html": "templates/apps/gestion/categorias_lista.html",
        "gestion/categoria_form.html": "templates/apps/gestion/categoria_form.html",
        "gestion/clientes_lista.html": "templates/apps/gestion/clientes/clientes_lista.html",
        "gestion/dashboard.html": "templates/apps/gestion/dashboard.html",
        "gestion/facturacion_dashboard.html": "templates/apps/gestion/facturacion_dashboard.html",
        "gestion/facturacion_listado.html": "templates/apps/gestion/facturacion_listado.html",
        "gestion/facturacion_mensual_almuerzos.html": "templates/apps/gestion/facturacion_mensual_almuerzos.html",
        "gestion/facturacion_reporte_cumplimiento.html": "templates/apps/gestion/reportes/facturacion_reporte_cumplimiento.html",
        "gestion/gestionar_empleados.html": "templates/apps/gestion/empleados/gestionar_empleados.html",
        "gestion/index.html": "templates/apps/gestion/index.html",
        "gestion/menu_diario.html": "templates/apps/gestion/menu_diario.html",
        "gestion/perfil_empleado.html": "templates/apps/gestion/empleados/perfil_empleado.html",
        "gestion/planes_almuerzo.html": "templates/apps/gestion/planes_almuerzo.html",
        "gestion/productos_importar.html": "templates/apps/gestion/productos/productos_importar.html",
        "gestion/productos_importar_preview.html": "templates/apps/gestion/productos/productos_importar_preview.html",
        "gestion/productos_lista.html": "templates/apps/gestion/productos/productos_lista.html",
        "gestion/producto_form.html": "templates/apps/gestion/productos/producto_form.html",
        "gestion/registro_consumo_almuerzo.html": "templates/apps/gestion/registro_consumo_almuerzo.html",
        "gestion/reportes_almuerzos.html": "templates/apps/gestion/reportes/reportes_almuerzos.html",
        "gestion/suscripciones_almuerzo.html": "templates/apps/gestion/suscripciones_almuerzo.html",
        "gestion/validar_pagos.html": "templates/apps/gestion/validar_pagos.html",
        "gestion/ventas_lista.html": "templates/apps/gestion/ventas_lista.html",
        
        # Templates de pos en gestion
        "pos/lista_cargas_pendientes.html": "templates/apps/gestion/lista_cargas_pendientes.html",
        "pos/lista_pagos_pendientes.html": "templates/apps/gestion/lista_pagos_pendientes.html", 
        "pos/validar_carga.html": "templates/apps/gestion/validar_carga.html",
        "pos/validar_pago.html": "templates/apps/gestion/validar_pago.html",
    }
    
    templates_movidos = 0
    errores = []
    
    print("🔄 INICIANDO LIMPIEZA DE TEMPLATES RESTANTES")
    print("=" * 50)
    
    # Mover cada archivo
    for origen_rel, destino_rel in archivos_por_mover.items():
        try:
            origen = gestion_templates / origen_rel
            destino = base_dir / destino_rel
            
            if origen.exists():
                # Crear directorio de destino si no existe
                destino.parent.mkdir(parents=True, exist_ok=True)
                
                # Si ya existe, hacer backup
                if destino.exists():
                    backup_path = destino.with_suffix('.backup.html')
                    shutil.move(str(destino), str(backup_path))
                    print(f"   📋 Backup creado: {backup_path.name}")
                
                # Mover archivo
                shutil.move(str(origen), str(destino))
                templates_movidos += 1
                print(f"   ✅ Movido: {origen_rel} → {destino_rel}")
            else:
                print(f"   ⚠️  No encontrado: {origen_rel}")
                
        except Exception as e:
            error_msg = f"Error moviendo {origen_rel}: {str(e)}"
            errores.append(error_msg)
            print(f"   ❌ {error_msg}")
    
    # Verificar carpetas de componentes y emails restantes
    componentes_gestion = gestion_templates / "gestion" / "components"
    emails_gestion = gestion_templates / "gestion" / "emails"
    ejemplos_gestion = gestion_templates / "gestion" / "ejemplos"
    
    if componentes_gestion.exists():
        print(f"\n📁 Carpeta components encontrada: {componentes_gestion}")
        for archivo in componentes_gestion.rglob("*.html"):
            print(f"   - {archivo.name}")
    
    if emails_gestion.exists():
        print(f"\n📁 Carpeta emails encontrada: {emails_gestion}")
        for archivo in emails_gestion.rglob("*.html"):
            print(f"   - {archivo.name}")
            
    if ejemplos_gestion.exists():
        print(f"\n📁 Carpeta ejemplos encontrada: {ejemplos_gestion}")
        for archivo in ejemplos_gestion.rglob("*.html"):
            print(f"   - {archivo.name}")
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DE LA LIMPIEZA:")
    print(f"   ✅ Templates movidos: {templates_movidos}")
    print(f"   ❌ Errores: {len(errores)}")
    
    if errores:
        print("\n🚨 ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"   - {error}")
    
    # Verificar si quedan carpetas vacías
    verificar_carpetas_vacias(gestion_templates)
    
    return templates_movidos, errores

def verificar_carpetas_vacias(directorio):
    """Verificar y reportar carpetas vacías"""
    print("\n🔍 VERIFICANDO CARPETAS VACÍAS:")
    
    for root, dirs, files in os.walk(directorio, topdown=False):
        root_path = Path(root)
        
        # Si la carpeta no tiene archivos HTML y no tiene subcarpetas con archivos HTML
        html_files = list(root_path.rglob("*.html"))
        if not html_files:
            print(f"   📂 Carpeta vacía de templates: {root_path.relative_to(directorio.parent)}")

if __name__ == "__main__":
    templates_movidos, errores = limpiar_templates_restantes()
    
    if errores:
        print(f"\n⚠️  Se completó con {len(errores)} errores")
    else:
        print(f"\n🎉 ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
        print(f"    {templates_movidos} templates movidos correctamente")