#!/usr/bin/env python3
"""
Script para limpiar carpetas vacías finales
"""

import shutil
from pathlib import Path

def limpiar_carpetas_vacias_finales():
    """Eliminar todas las carpetas vacías restantes"""
    
    base_dir = Path("D:/anteproyecto20112025")
    templates_dir = base_dir / "templates"
    
    carpetas_vacias = []
    
    # Buscar carpetas vacías
    for carpeta in templates_dir.iterdir():
        if carpeta.is_dir():
            # Contar archivos HTML reales (no backups)
            archivos_html = [f for f in carpeta.rglob("*.html") 
                           if not f.name.endswith('.backup.html')]
            
            if not archivos_html:
                carpetas_vacias.append(carpeta)
    
    print("🧹 ELIMINANDO CARPETAS COMPLETAMENTE VACÍAS")
    print("=" * 45)
    
    carpetas_eliminadas = 0
    for carpeta in carpetas_vacias:
        try:
            shutil.rmtree(str(carpeta))
            print(f"   🗑️  Eliminada: {carpeta.name}/")
            carpetas_eliminadas += 1
        except Exception as e:
            print(f"   ❌ Error eliminando {carpeta.name}: {e}")
    
    return carpetas_eliminadas

def verificar_estructura_limpia():
    """Verificar estructura final limpia"""
    
    base_dir = Path("D:/anteproyecto20112025")
    templates_dir = base_dir / "templates"
    
    print("\n📁 ESTRUCTURA FINAL LIMPIA:")
    print("=" * 30)
    
    estructura_final = {}
    total_templates = 0
    
    for carpeta in sorted(templates_dir.iterdir()):
        if carpeta.is_dir():
            # Contar solo archivos HTML reales
            archivos_html = [f for f in carpeta.rglob("*.html") 
                           if not f.name.endswith('.backup.html')]
            
            if archivos_html:
                estructura_final[carpeta.name] = len(archivos_html)
                total_templates += len(archivos_html)
                print(f"   📂 {carpeta.name}/: {len(archivos_html)} templates")
    
    print(f"\n📊 TOTAL: {total_templates} templates organizados profesionalmente")
    return estructura_final, total_templates

if __name__ == "__main__":
    eliminadas = limpiar_carpetas_vacias_finales()
    estructura, total = verificar_estructura_limpia()
    
    print(f"\n🎉 ¡ESTRUCTURA COMPLETAMENTE LIMPIA!")
    print(f"    🗑️  {eliminadas} carpetas vacías eliminadas")
    print(f"    📂 {len(estructura)} carpetas activas")
    print(f"    📄 {total} templates organizados")