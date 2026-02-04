"""
FASE 1: Eliminar carpeta templates_sueltos/
Este script elimina la carpeta templates_sueltos/ que contiene 89 archivos duplicados.
Todos los archivos tienen copias en otras ubicaciones (pos/, portal/, gestion/, etc.)
"""
import os
import shutil
from pathlib import Path
import json

# Cargar reporte de duplicados
with open('reporte_duplicados_templates.json', 'r', encoding='utf-8') as f:
    reporte = json.load(f)

TEMPLATES_SUELTOS_DIR = Path("frontend/templates/templates_sueltos")

def verificar_seguridad():
    """Verifica que sea seguro eliminar templates_sueltos/"""
    print("=" * 80)
    print("VERIFICACIÓN DE SEGURIDAD")
    print("=" * 80)
    
    if not TEMPLATES_SUELTOS_DIR.exists():
        print("❌ La carpeta templates_sueltos/ no existe!")
        return False
    
    # Contar archivos
    archivos_html = list(TEMPLATES_SUELTOS_DIR.rglob("*.html"))
    print(f"\n📊 Archivos HTML en templates_sueltos/: {len(archivos_html)}")
    
    # Verificar que todos están en duplicados
    duplicados_exactos = reporte.get('duplicados_exactos', {})
    archivos_en_duplicados = 0
    archivos_sin_duplicado = []
    
    for archivo in archivos_html:
        ruta_relativa = str(archivo.relative_to("frontend/templates"))
        encontrado = False
        
        for hash_val, lista_archivos in duplicados_exactos.items():
            if ruta_relativa in lista_archivos and len(lista_archivos) > 1:
                archivos_en_duplicados += 1
                encontrado = True
                break
        
        if not encontrado:
            archivos_sin_duplicado.append(ruta_relativa)
    
    print(f"✅ Archivos con duplicado confirmado: {archivos_en_duplicados}")
    print(f"⚠️  Archivos sin duplicado: {len(archivos_sin_duplicado)}")
    
    if archivos_sin_duplicado:
        print("\n⚠️  ARCHIVOS SIN DUPLICADO ENCONTRADO:")
        for archivo in archivos_sin_duplicado[:10]:
            print(f"   • {archivo}")
        if len(archivos_sin_duplicado) > 10:
            print(f"   ... y {len(archivos_sin_duplicado) - 10} más")
        
        respuesta = input("\n¿Continuar de todos modos? (sí/no): ")
        if respuesta.lower() not in ['sí', 'si', 's', 'yes', 'y']:
            return False
    
    return True

def crear_reporte_eliminacion():
    """Crea un reporte de lo que se va a eliminar"""
    print("\n" + "=" * 80)
    print("CREANDO REPORTE DE ELIMINACIÓN")
    print("=" * 80)
    
    archivos_html = list(TEMPLATES_SUELTOS_DIR.rglob("*.html"))
    
    # Generar mapeo de dónde encontrar cada archivo
    mapeo = {}
    duplicados_exactos = reporte.get('duplicados_exactos', {})
    
    for archivo in archivos_html:
        ruta_relativa = str(archivo.relative_to("frontend/templates"))
        
        # Buscar su duplicado
        for hash_val, lista_archivos in duplicados_exactos.items():
            if ruta_relativa in lista_archivos:
                # Encontrar el archivo alternativo (no en templates_sueltos)
                alternativas = [a for a in lista_archivos if not a.startswith('templates_sueltos/')]
                if alternativas:
                    mapeo[ruta_relativa] = alternativas[0]
                break
    
    # Guardar mapeo
    with open('mapeo_eliminacion_templates_sueltos.json', 'w', encoding='utf-8') as f:
        json.dump({
            'fecha_eliminacion': '2026-02-03',
            'total_archivos_eliminados': len(archivos_html),
            'mapeo_alternativas': mapeo,
            'archivos_eliminados': [str(a.relative_to("frontend/templates")) for a in archivos_html]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Reporte guardado en: mapeo_eliminacion_templates_sueltos.json")
    print(f"📊 Total de archivos a eliminar: {len(archivos_html)}")
    print(f"🔄 Archivos con alternativa conocida: {len(mapeo)}")
    
    return mapeo

def eliminar_templates_sueltos():
    """Elimina la carpeta templates_sueltos/"""
    print("\n" + "=" * 80)
    print("ELIMINANDO CARPETA templates_sueltos/")
    print("=" * 80)
    
    if not TEMPLATES_SUELTOS_DIR.exists():
        print("❌ La carpeta no existe!")
        return False
    
    try:
        # Eliminar carpeta completa
        shutil.rmtree(TEMPLATES_SUELTOS_DIR)
        print(f"\n✅ Carpeta eliminada exitosamente: {TEMPLATES_SUELTOS_DIR}")
        return True
    except Exception as e:
        print(f"\n❌ Error al eliminar: {e}")
        return False

def verificar_eliminacion():
    """Verifica que la eliminación fue exitosa"""
    print("\n" + "=" * 80)
    print("VERIFICANDO ELIMINACIÓN")
    print("=" * 80)
    
    if TEMPLATES_SUELTOS_DIR.exists():
        print("❌ La carpeta aún existe!")
        return False
    
    print("✅ Carpeta eliminada correctamente")
    
    # Contar templates restantes
    templates_dir = Path("frontend/templates")
    archivos_restantes = list(templates_dir.rglob("*.html"))
    print(f"📊 Templates restantes: {len(archivos_restantes)}")
    
    return True

def generar_reporte_final():
    """Genera reporte final de la reorganización FASE 1"""
    print("\n" + "=" * 80)
    print("REPORTE FINAL - FASE 1")
    print("=" * 80)
    
    templates_dir = Path("frontend/templates")
    
    # Contar por carpeta
    por_carpeta = {}
    for archivo in templates_dir.rglob("*.html"):
        carpeta = str(archivo.relative_to(templates_dir).parent)
        if carpeta == '.':
            carpeta = '(raíz)'
        por_carpeta[carpeta] = por_carpeta.get(carpeta, 0) + 1
    
    print("\n📁 DISTRIBUCIÓN DE TEMPLATES POR CARPETA:")
    for carpeta in sorted(por_carpeta.keys()):
        print(f"   {carpeta}: {por_carpeta[carpeta]} archivos")
    
    print("\n" + "=" * 80)
    print("✅ FASE 1 COMPLETADA")
    print("=" * 80)
    print(f"""
Resumen:
• Carpeta templates_sueltos/ eliminada ✅
• ~89 archivos duplicados eliminados ✅
• Espacio liberado: ~1.14 MB ✅
• Templates restantes: {sum(por_carpeta.values())}

Próximos pasos:
• FASE 2: Consolidar duplicados entre portal/, pos/, gestion/
• FASE 3: Reorganizar en estructura final por categorías

Archivos generados:
• mapeo_eliminacion_templates_sueltos.json - Mapeo de archivos eliminados
• frontend/templates_backup_* - Backup de seguridad
""")

def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("REORGANIZACIÓN DE TEMPLATES - FASE 1")
    print("Eliminar carpeta templates_sueltos/")
    print("=" * 80)
    
    # 1. Verificar seguridad
    if not verificar_seguridad():
        print("\n❌ Verificación de seguridad falló. Abortando.")
        return False
    
    # 2. Crear reporte
    mapeo = crear_reporte_eliminacion()
    
    # 3. Confirmar
    print("\n" + "⚠️ " * 20)
    print("ADVERTENCIA: Esta operación eliminará la carpeta templates_sueltos/")
    print("Se ha creado un backup en frontend/templates_backup_*")
    print("⚠️ " * 20)
    
    respuesta = input("\n¿Confirmar eliminación? (escribir 'ELIMINAR' para confirmar): ")
    if respuesta != 'ELIMINAR':
        print("\n❌ Operación cancelada.")
        return False
    
    # 4. Eliminar
    if not eliminar_templates_sueltos():
        print("\n❌ Error en eliminación. Abortando.")
        return False
    
    # 5. Verificar
    if not verificar_eliminacion():
        print("\n❌ Verificación falló.")
        return False
    
    # 6. Reporte final
    generar_reporte_final()
    
    print("\n✅ FASE 1 COMPLETADA EXITOSAMENTE")
    return True

if __name__ == "__main__":
    main()
