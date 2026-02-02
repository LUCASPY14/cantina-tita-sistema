#!/usr/bin/env python3
"""
Script para mover los archivos restantes de las subcarpetas
"""

import os
import shutil
from pathlib import Path

def mover_subcarpetas_restantes():
    """Mover archivos de components, emails y ejemplos"""
    
    base_dir = Path("D:/anteproyecto20112025")
    gestion_templates = base_dir / "gestion" / "templates" / "gestion"
    templates_dir = base_dir / "templates"
    
    archivos_movidos = 0
    
    print("🔄 MOVIENDO ARCHIVOS DE SUBCARPETAS")
    print("=" * 40)
    
    # Mover componentes
    components_dir = gestion_templates / "components"
    if components_dir.exists():
        for archivo in components_dir.glob("*.html"):
            destino = templates_dir / "shared" / "components" / archivo.name
            if destino.exists():
                destino.unlink()  # Eliminar duplicado
            shutil.move(str(archivo), str(destino))
            print(f"   ✅ Movido component: {archivo.name}")
            archivos_movidos += 1
    
    # Mover emails
    emails_dir = gestion_templates / "emails" 
    if emails_dir.exists():
        for archivo in emails_dir.glob("*.html"):
            destino = templates_dir / "shared" / "emails" / archivo.name
            if destino.exists():
                destino.unlink()  # Eliminar duplicado
            shutil.move(str(archivo), str(destino))
            print(f"   ✅ Movido email: {archivo.name}")
            archivos_movidos += 1
    
    # Mover ejemplos a la carpeta de gestion
    ejemplos_dir = gestion_templates / "ejemplos"
    if ejemplos_dir.exists():
        for archivo in ejemplos_dir.glob("*.html"):
            if "clientes" in archivo.name:
                destino = templates_dir / "apps" / "gestion" / "clientes" / archivo.name
            elif "productos" in archivo.name:
                destino = templates_dir / "apps" / "gestion" / "productos" / archivo.name
            else:
                destino = templates_dir / "apps" / "gestion" / archivo.name
            
            destino.parent.mkdir(parents=True, exist_ok=True)
            if destino.exists():
                destino.unlink()  # Eliminar duplicado
            shutil.move(str(archivo), str(destino))
            print(f"   ✅ Movido ejemplo: {archivo.name}")
            archivos_movidos += 1
    
    print(f"\n✅ Total archivos movidos: {archivos_movidos}")
    return archivos_movidos

def limpiar_carpetas_vacias():
    """Eliminar carpetas vacías"""
    base_dir = Path("D:/anteproyecto20112025")
    gestion_templates = base_dir / "gestion" / "templates"
    
    print("\n🧹 LIMPIANDO CARPETAS VACÍAS")
    print("=" * 30)
    
    carpetas_eliminadas = 0
    
    # Eliminar carpetas vacías de forma recursiva
    for root, dirs, files in os.walk(str(gestion_templates), topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            try:
                if not any(dir_path.iterdir()):  # Si está vacía
                    dir_path.rmdir()
                    print(f"   🗑️  Eliminada: {dir_path.relative_to(gestion_templates.parent)}")
                    carpetas_eliminadas += 1
            except OSError:
                pass  # No vacía o error de permisos
    
    print(f"✅ Carpetas vacías eliminadas: {carpetas_eliminadas}")
    return carpetas_eliminadas

if __name__ == "__main__":
    archivos_movidos = mover_subcarpetas_restantes()
    carpetas_eliminadas = limpiar_carpetas_vacias()
    
    print(f"\n🎉 ¡PROCESO COMPLETADO!")
    print(f"   📁 {archivos_movidos} archivos movidos")
    print(f"   🗑️  {carpetas_eliminadas} carpetas vacías eliminadas")