"""
Script para identificar y analizar duplicados exactos entre templates
"""
import os
import hashlib
from pathlib import Path
from collections import defaultdict
import json

TEMPLATES_DIR = Path("frontend/templates")

def calcular_hash(filepath):
    """Calcula hash MD5 de un archivo"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analizar_duplicados():
    """Encuentra templates duplicados por contenido"""
    print("=" * 80)
    print("ANÁLISIS DE DUPLICADOS EXACTOS")
    print("=" * 80)
    
    # Agrupar por hash
    por_hash = defaultdict(list)
    por_nombre = defaultdict(list)
    
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
            
            filepath = Path(root) / file
            relpath = filepath.relative_to(TEMPLATES_DIR)
            
            # Por hash (duplicados exactos)
            file_hash = calcular_hash(filepath)
            if file_hash:
                por_hash[file_hash].append(str(relpath))
            
            # Por nombre (posibles duplicados)
            por_nombre[file].append(str(relpath))
    
    # Duplicados exactos (mismo contenido)
    duplicados_exactos = {h: files for h, files in por_hash.items() if len(files) > 1}
    
    # Duplicados por nombre (mismo nombre, posiblemente diferente contenido)
    duplicados_nombre = {n: files for n, files in por_nombre.items() if len(files) > 1}
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   • Templates únicos por contenido: {len(por_hash)}")
    print(f"   • Templates únicos por nombre: {len(por_nombre)}")
    print(f"   • Grupos de duplicados exactos: {len(duplicados_exactos)}")
    print(f"   • Grupos de duplicados por nombre: {len(duplicados_nombre)}")
    
    # Mostrar duplicados exactos
    print("\n" + "=" * 80)
    print("DUPLICADOS EXACTOS (mismo contenido)")
    print("=" * 80)
    
    total_archivos_duplicados = 0
    espacio_desperdiciado = 0
    
    for i, (hash_val, archivos) in enumerate(sorted(duplicados_exactos.items(), key=lambda x: len(x[1]), reverse=True), 1):
        print(f"\n{i}. Grupo con {len(archivos)} copias idénticas:")
        for archivo in sorted(archivos):
            filepath = TEMPLATES_DIR / archivo
            size = filepath.stat().st_size if filepath.exists() else 0
            print(f"   • {archivo:<60} ({size:,} bytes)")
        
        total_archivos_duplicados += len(archivos) - 1  # -1 porque uno debería quedarse
        if archivos:
            filepath = TEMPLATES_DIR / archivos[0]
            if filepath.exists():
                espacio_desperdiciado += filepath.stat().st_size * (len(archivos) - 1)
    
    print(f"\n💾 Espacio desperdiciado en duplicados exactos: {espacio_desperdiciado:,} bytes ({espacio_desperdiciado/1024:.1f} KB)")
    print(f"🗑️  Archivos que pueden eliminarse: {total_archivos_duplicados}")
    
    # Mostrar duplicados por nombre (requieren revisión manual)
    print("\n" + "=" * 80)
    print("DUPLICADOS POR NOMBRE (requieren revisión manual)")
    print("=" * 80)
    
    for i, (nombre, archivos) in enumerate(sorted(duplicados_nombre.items(), key=lambda x: len(x[1]), reverse=True), 1):
        if i > 30:  # Limitar a top 30
            break
        print(f"\n{i}. {nombre} ({len(archivos)} versiones):")
        for archivo in sorted(archivos):
            filepath = TEMPLATES_DIR / archivo
            size = filepath.stat().st_size if filepath.exists() else 0
            file_hash = calcular_hash(filepath)
            print(f"   • {archivo:<60} ({size:,} bytes) [hash: {file_hash[:8] if file_hash else 'N/A'}]")
    
    # Generar reporte JSON
    reporte = {
        "duplicados_exactos": {
            hash_val: archivos 
            for hash_val, archivos in duplicados_exactos.items()
        },
        "duplicados_nombre": duplicados_nombre,
        "estadisticas": {
            "total_templates": len(por_hash),
            "grupos_duplicados_exactos": len(duplicados_exactos),
            "archivos_duplicados": total_archivos_duplicados,
            "espacio_desperdiciado_bytes": espacio_desperdiciado,
            "espacio_desperdiciado_kb": round(espacio_desperdiciado / 1024, 2)
        }
    }
    
    with open('reporte_duplicados_templates.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Reporte JSON generado: reporte_duplicados_templates.json")
    
    return duplicados_exactos, duplicados_nombre

def recomendar_consolidacion():
    """Recomienda qué archivo mantener de cada grupo de duplicados"""
    print("\n" + "=" * 80)
    print("RECOMENDACIONES DE CONSOLIDACIÓN")
    print("=" * 80)
    
    # Prioridades de carpetas (de mayor a menor preferencia)
    PRIORIDAD_CARPETAS = [
        "pos/",           # POS es el sistema principal
        "portal/",        # Portal de padres bien estructurado
        "gestion/",       # Gestión como alternativa
        "components/",    # Componentes reutilizables
        "base/",          # Templates base
        "auth/",          # Autenticación
        "emails/",        # Emails
        "admin/",         # Admin
        "templates_sueltos/",  # ÚLTIMA prioridad (eliminar esta carpeta)
    ]
    
    duplicados_exactos, _ = analizar_duplicados()
    
    print("\n🎯 ARCHIVOS A MANTENER (versión maestra):")
    print("-" * 80)
    
    for hash_val, archivos in sorted(duplicados_exactos.items(), key=lambda x: len(x[1]), reverse=True):
        # Ordenar por prioridad de carpeta
        def get_prioridad(archivo):
            for i, carpeta in enumerate(PRIORIDAD_CARPETAS):
                if archivo.startswith(carpeta):
                    return i
            return len(PRIORIDAD_CARPETAS)  # Última prioridad si no coincide
        
        archivos_ordenados = sorted(archivos, key=get_prioridad)
        maestro = archivos_ordenados[0]
        eliminar = archivos_ordenados[1:]
        
        print(f"\n✅ MANTENER: {maestro}")
        print(f"   Grupo de {len(archivos)} duplicados:")
        for archivo in eliminar:
            print(f"   ❌ ELIMINAR: {archivo}")

if __name__ == "__main__":
    recomendar_consolidacion()
    
    print("\n" + "=" * 80)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 80)
