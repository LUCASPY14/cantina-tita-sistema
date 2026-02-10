#!/usr/bin/env python
"""
Script para corregir db_column en TODOS los archivos de la carpeta models/
"""
import os
import re
import glob

CARPETA_MODELS = r'D:\anteproyecto20112025\backend\gestion\models'

def convertir_a_lowercase(db_column_value):
    """Convierte db_column de uppercase a lowercase"""
    if db_column_value.startswith("'") or db_column_value.startswith('"'):
        match = re.match(r"['\"](.+)['\"]", db_column_value)
        if match:
            original = match.group(1)
            lowercase = original.lower()
            quote = db_column_value[0]
            return f"{quote}{lowercase}{quote}"
    return db_column_value.lower()

def procesar_archivo(archivo_path):
    """Procesa un archivo y corrige los db_column"""
    with open(archivo_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    patron = r"(db_column\s*=\s*)(['\"][^'\"]+['\"])"
    
    cambios = 0
    def reemplazar(match):
        nonlocal cambios
        prefijo = match.group(1)
        valor_original = match.group(2)
        valor_lowercase = convertir_a_lowercase(valor_original)
        
        if valor_original != valor_lowercase:
            print(f"    🔄 {valor_original} → {valor_lowercase}")
            cambios += 1
            return prefijo + valor_lowercase
        return match.group(0)
    
    contenido_nuevo = re.sub(patron, reemplazar, contenido)
    
    if contenido_nuevo != contenido_original:
        # Backup
        backup_path = archivo_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(contenido_original)
        
        # Guardar
        with open(archivo_path, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print(f"  ✅ {cambios} cambios en: {os.path.basename(archivo_path)}")
        return True
    else:
        print(f"  ✓  Sin cambios: {os.path.basename(archivo_path)}")
        return False

def main():
    print("="*80)
    print("🔧 CORRECCIÓN DE db_column EN CARPETA models/")
    print("="*80)
    print()
    
    archivos = glob.glob(os.path.join(CARPETA_MODELS, '*.py'))
    archivos_modificados = 0
    total_cambios = 0
    
    for archivo in sorted(archivos):
        nombre = os.path.basename(archivo)
        print(f"\n📄 {nombre}")
        
        if procesar_archivo(archivo):
            archivos_modificados += 1
    
    print("\n" + "="*80)
    print("📊 RESUMEN")
    print("="*80)
    print(f"Archivos procesados:  {len(archivos)}")
    print(f"Archivos modificados: {archivos_modificados}")
    print()

if __name__ == '__main__':
    main()
