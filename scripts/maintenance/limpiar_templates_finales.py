#!/usr/bin/env python3
"""
Script final para limpiar completamente todos los templates restantes 
de la estructura antigua y organizarlos en la nueva estructura profesional
"""

import os
import shutil
from pathlib import Path

def limpiar_templates_finales():
    """Limpieza final de todos los templates restantes"""
    
    base_dir = Path("D:/anteproyecto20112025")
    templates_dir = base_dir / "templates"
    
    # Mapeo de archivos de la estructura antigua a la nueva
    archivos_por_mover = {
        # Templates base antiguos - mover a base/
        "base.html": "base/base.html",
        "base_improved.html": "base/base_improved.html",
        
        # Templates de clientes - mover a apps/gestion/clientes/
        "clientes/crear_cliente.html": "apps/gestion/clientes/crear_cliente.html",
        
        # Templates de seguridad - mover a apps/auth/
        "seguridad/logs_auditoria.html": "apps/auth/logs_auditoria.html",
        "seguridad/intentos_login.html": "apps/auth/intentos_login.html",
        "seguridad/dashboard.html": "pages/dashboard/dashboard.html",
        
        # Templates de registration - mover a apps/auth/
        "registration/login.html": "apps/auth/login.html",
    }
    
    templates_movidos = 0
    errores = []
    
    print("🔄 LIMPIEZA FINAL DE TEMPLATES")
    print("=" * 40)
    
    for origen_rel, destino_rel in archivos_por_mover.items():
        try:
            origen = templates_dir / origen_rel
            destino = templates_dir / destino_rel
            
            if origen.exists():
                # Crear directorio de destino
                destino.parent.mkdir(parents=True, exist_ok=True)
                
                # Si ya existe en destino, hacer backup
                if destino.exists():
                    backup_path = destino.with_suffix('.backup.html')
                    shutil.move(str(destino), str(backup_path))
                    print(f"   📋 Backup: {backup_path.name}")
                
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
    
    # Eliminar carpetas vacías de la estructura antigua
    eliminar_carpetas_antiguas_vacias(templates_dir)
    
    print("\n" + "=" * 40)
    print("📊 RESULTADO FINAL:")
    print(f"   ✅ Templates movidos: {templates_movidos}")
    print(f"   ❌ Errores: {len(errores)}")
    
    return templates_movidos, errores

def eliminar_carpetas_antiguas_vacias(templates_dir):
    """Eliminar carpetas vacías de la estructura antigua"""
    
    carpetas_antigua = [
        "clientes",
        "seguridad", 
        "registration",
        "dashboard",
        "emails",
        "portal"
    ]
    
    carpetas_eliminadas = 0
    
    print("\n🧹 ELIMINANDO CARPETAS ANTIGUAS VACÍAS:")
    
    for carpeta in carpetas_antigua:
        carpeta_path = templates_dir / carpeta
        if carpeta_path.exists():
            try:
                # Verificar si está vacía o solo tiene archivos de backup
                archivos_reales = [f for f in carpeta_path.rglob("*") 
                                 if f.is_file() and not f.name.endswith('.backup.html')]
                
                if not archivos_reales:
                    # Eliminar recursivamente
                    shutil.rmtree(str(carpeta_path))
                    print(f"   🗑️  Eliminada: {carpeta}/")
                    carpetas_eliminadas += 1
                else:
                    print(f"   📂 Mantenida (tiene archivos): {carpeta}/")
            except Exception as e:
                print(f"   ❌ Error eliminando {carpeta}: {e}")
    
    return carpetas_eliminadas

def verificar_estructura_final():
    """Verificar la estructura final"""
    
    base_dir = Path("D:/anteproyecto20112025")
    templates_dir = base_dir / "templates"
    
    print("\n📁 VERIFICACIÓN ESTRUCTURA FINAL:")
    print("=" * 35)
    
    # Contar archivos por directorio
    estructura_final = {}
    
    for carpeta in templates_dir.iterdir():
        if carpeta.is_dir() and not carpeta.name.startswith('.'):
            total_html = len(list(carpeta.rglob("*.html")))
            estructura_final[carpeta.name] = total_html
            print(f"   📂 {carpeta.name}/: {total_html} templates")
    
    total_templates = sum(estructura_final.values())
    print(f"\n📊 TOTAL TEMPLATES EN ESTRUCTURA PROFESIONAL: {total_templates}")
    
    return estructura_final, total_templates

if __name__ == "__main__":
    templates_movidos, errores = limpiar_templates_finales()
    estructura, total = verificar_estructura_final()
    
    if errores:
        print(f"\n⚠️  Se completó con {len(errores)} errores")
    else:
        print(f"\n🎉 ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
        print(f"    {templates_movidos} templates movidos")
        print(f"    {total} templates en estructura profesional")