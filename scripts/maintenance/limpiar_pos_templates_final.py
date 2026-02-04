#!/usr/bin/env python3
"""
Script para mover todos los templates restantes de pos/templates/ 
hacia la estructura organizada en /templates
"""

import os
import shutil
from pathlib import Path

def limpiar_pos_templates():
    """Mover todos los templates de pos/templates/ a la estructura profesional"""
    
    base_dir = Path("D:/anteproyecto20112025")
    pos_templates = base_dir / "pos" / "templates" / "pos"
    templates_dir = base_dir / "templates"
    
    templates_movidos = 0
    duplicados_encontrados = 0
    
    print("🔄 LIMPIANDO TEMPLATES DE POS/TEMPLATES/")
    print("=" * 50)
    
    if not pos_templates.exists():
        print("❌ No se encontró la carpeta pos/templates/pos/")
        return 0, 0
    
    # Recorrer todos los archivos HTML en pos/templates/pos/
    for archivo_origen in pos_templates.rglob("*.html"):
        try:
            # Calcular la ruta relativa desde pos/templates/pos/
            ruta_relativa = archivo_origen.relative_to(pos_templates)
            
            # Determinar destino basado en la estructura de carpetas
            if "admin" in str(ruta_relativa):
                destino = templates_dir / "apps" / "pos" / "admin" / archivo_origen.name
            elif "almuerzo" in str(ruta_relativa):
                destino = templates_dir / "apps" / "pos" / "almuerzo" / archivo_origen.name
            elif "modales" in str(ruta_relativa):
                destino = templates_dir / "shared" / "modals" / archivo_origen.name
            elif "partials" in str(ruta_relativa):
                destino = templates_dir / "shared" / "components" / archivo_origen.name
            elif "reportes" in str(ruta_relativa):
                destino = templates_dir / "apps" / "pos" / "reportes" / archivo_origen.name
            elif "cajas" in archivo_origen.name or "caja" in archivo_origen.name:
                destino = templates_dir / "apps" / "pos" / "cajas" / archivo_origen.name
            elif "dashboard" in archivo_origen.name or "ventas" in archivo_origen.name:
                destino = templates_dir / "apps" / "pos" / "ventas" / archivo_origen.name
            elif "inventario" in archivo_origen.name or "kardex" in archivo_origen.name:
                destino = templates_dir / "apps" / "pos" / "inventario" / archivo_origen.name
            elif "ticket" in archivo_origen.name or "comprobante" in archivo_origen.name:
                destino = templates_dir / "apps" / "pos" / "ventas" / archivo_origen.name
            else:
                # Por defecto va a pos general
                destino = templates_dir / "apps" / "pos" / archivo_origen.name
            
            # Crear directorio de destino si no existe
            destino.parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar si ya existe
            if destino.exists():
                duplicados_encontrados += 1
                print(f"   🔄 Reemplazando duplicado: {archivo_origen.name}")
                destino.unlink()  # Eliminar el existente
            
            # Mover archivo
            shutil.move(str(archivo_origen), str(destino))
            templates_movidos += 1
            print(f"   ✅ Movido: {str(ruta_relativa)} → {destino.relative_to(templates_dir)}")
            
        except Exception as e:
            print(f"   ❌ Error moviendo {archivo_origen.name}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO:")
    print(f"   ✅ Templates movidos: {templates_movidos}")
    print(f"   🔄 Duplicados reemplazados: {duplicados_encontrados}")
    
    return templates_movidos, duplicados_encontrados

def eliminar_carpetas_pos_vacias():
    """Eliminar carpetas vacías de pos/templates/"""
    
    base_dir = Path("D:/anteproyecto20112025")
    pos_templates_root = base_dir / "pos" / "templates"
    
    carpetas_eliminadas = 0
    
    print("\n🧹 ELIMINANDO CARPETAS VACÍAS DE POS:")
    
    # Eliminar carpetas vacías de forma recursiva
    for root, dirs, files in os.walk(str(pos_templates_root), topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            try:
                if not any(dir_path.iterdir()):  # Si está vacía
                    dir_path.rmdir()
                    print(f"   🗑️  Eliminada: {dir_path.relative_to(pos_templates_root.parent)}")
                    carpetas_eliminadas += 1
            except OSError:
                pass  # No vacía o error de permisos
    
    # Eliminar la carpeta pos/templates si quedó vacía
    try:
        if pos_templates_root.exists() and not any(pos_templates_root.iterdir()):
            pos_templates_root.rmdir()
            print(f"   🗑️  Eliminada carpeta principal: templates")
            carpetas_eliminadas += 1
    except OSError:
        pass
    
    return carpetas_eliminadas

if __name__ == "__main__":
    templates_movidos, duplicados = limpiar_pos_templates()
    carpetas_eliminadas = eliminar_carpetas_pos_vacias()
    
    print(f"\n🎉 ¡LIMPIEZA DE POS COMPLETADA!")
    print(f"   📁 {templates_movidos} templates movidos")
    print(f"   🔄 {duplicados} duplicados reemplazados")
    print(f"   🗑️  {carpetas_eliminadas} carpetas eliminadas")