#!/usr/bin/env python3
"""
Script para limpiar templates duplicados y legacy del sistema
Ejecutar solo después de verificar que no se usan activamente
"""

import os
import shutil
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).parent

# ===================================================================
# FASE 1: TEMPLATES DUPLICADOS CONFIRMADOS (Eliminar con seguridad)
# ===================================================================

DUPLICADOS_ELIMINAR = [
    # pos_general.html - Reemplazado por pos_bootstrap.html
    # VERIFICADO: pos_general_views.py usa pos_bootstrap.html
    'templates/pos/pos_general.html',
]

# ===================================================================
# FASE 2: TEMPLATES LEGACY A VERIFICAR
# ===================================================================

LEGACY_REVISAR = [
    # pos_views.py TODAVÍA USA venta.html (línea 87)
    # NO ELIMINAR hasta migrar completamente a pos_general_views.py
    # 'templates/pos/venta.html',  # ⚠️ COMENTADO - AÚN EN USO
    
    # cuenta_corriente - HAY 2 EN USO ACTIVO:
    # pos_views.py línea 1953: cuenta_corriente.html
    # pos_views.py línea 2159: cuenta_corriente_unificada.html
    # NO ELIMINAR
    # 'templates/pos/cuenta_corriente.html',  # ⚠️ EN USO
    # 'templates/pos/cuenta_corriente_v2.html',  # ⚠️ VERIFICAR
    # 'templates/pos/cuenta_corriente_unificada.html',  # ⚠️ EN USO
]

# ===================================================================
# FASE 3: TEMPLATES DE gestion/templates/ (Posible legacy)
# ===================================================================

GESTION_LEGACY = [
    # Estos están en gestion/templates/gestion/
    # Pueden ser legacy si ya NO se usan
    'gestion/templates/gestion/base.html',
    'gestion/templates/gestion/dashboard.html',
    'gestion/templates/gestion/clientes_lista.html',
    'gestion/templates/gestion/productos_lista.html',
    'gestion/templates/gestion/ventas_lista.html',
]

def verificar_uso_en_codigo(template_path):
    """
    Verifica si un template se usa en archivos .py
    Retorna: (bool, list) - (usado, [archivos que lo usan])
    """
    template_name = os.path.basename(template_path)
    archivos_que_usan = []
    
    # Buscar en todos los archivos .py
    for py_file in BASE_DIR.rglob('*.py'):
        if 'venv' in str(py_file) or 'env' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if template_name in contenido:
                    archivos_que_usan.append(str(py_file.relative_to(BASE_DIR)))
        except Exception as e:
            pass
    
    return (len(archivos_que_usan) > 0, archivos_que_usan)

def crear_backup(archivo):
    """Crea backup del archivo antes de eliminarlo"""
    backup_dir = BASE_DIR / 'backups_templates_eliminados'
    backup_dir.mkdir(exist_ok=True)
    
    ruta_archivo = BASE_DIR / archivo
    if ruta_archivo.exists():
        # Preservar estructura de directorios en backup
        rel_path = ruta_archivo.relative_to(BASE_DIR)
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(ruta_archivo, backup_path)
        print(f"   ✅ Backup creado: {backup_path.relative_to(BASE_DIR)}")
        return True
    return False

def eliminar_con_seguridad(archivo):
    """Elimina archivo después de crear backup"""
    ruta_archivo = BASE_DIR / archivo
    if ruta_archivo.exists():
        ruta_archivo.unlink()
        print(f"   ❌ Eliminado: {archivo}")
        return True
    else:
        print(f"   ⚠️ No existe: {archivo}")
        return False

# ===================================================================
# EJECUCIÓN PRINCIPAL
# ===================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("LIMPIEZA DE TEMPLATES - Sistema Cantina Tita")
    print("=" * 70)
    
    # FASE 1: Verificar y eliminar duplicados confirmados
    print("\n📋 FASE 1: Verificación de duplicados confirmados")
    print("-" * 70)
    
    for template in DUPLICADOS_ELIMINAR:
        print(f"\n🔍 Verificando: {template}")
        usado, archivos = verificar_uso_en_codigo(template)
        
        if usado:
            print(f"   ⚠️ TODAVÍA SE USA EN:")
            for archivo in archivos:
                print(f"      - {archivo}")
            print(f"   ⛔ NO SE ELIMINARÁ (requiere migración primero)")
        else:
            print(f"   ✅ NO se encuentra en uso en archivos .py")
            print(f"   🗑️ SEGURO para eliminar")
            
            # Crear backup y eliminar
            if crear_backup(template):
                eliminar_con_seguridad(template)
    
    # FASE 2: Reportar templates legacy para revisión manual
    print("\n\n📋 FASE 2: Templates legacy a revisar manualmente")
    print("-" * 70)
    print("⚠️ Estos templates NO se eliminarán automáticamente")
    print("   Requieren decisión manual después de revisar uso\n")
    
    for template in LEGACY_REVISAR:
        nombre = os.path.basename(template)
        usado, archivos = verificar_uso_en_codigo(template)
        
        if usado:
            print(f"\n⚠️ {nombre}")
            print(f"   Usado en {len(archivos)} archivo(s):")
            for archivo in archivos[:5]:  # Máximo 5 ejemplos
                print(f"      - {archivo}")
            if len(archivos) > 5:
                print(f"      ... y {len(archivos) - 5} más")
        else:
            print(f"\n❓ {nombre}")
            print(f"   NO encontrado en archivos .py")
            print(f"   ⚠️ Puede ser legacy o usado solo en includes")
    
    # FASE 3: Verificar templates de gestion/templates/
    print("\n\n📋 FASE 3: Templates de gestion/templates/gestion/")
    print("-" * 70)
    print("⚠️ Verificando si son legacy...\n")
    
    templates_gestion_en_uso = []
    templates_gestion_sin_uso = []
    
    for template in GESTION_LEGACY:
        nombre = os.path.basename(template)
        usado, archivos = verificar_uso_en_codigo(template)
        
        if usado:
            templates_gestion_en_uso.append((template, archivos))
            print(f"✅ {nombre} - EN USO ({len(archivos)} referencias)")
        else:
            templates_gestion_sin_uso.append(template)
            print(f"❌ {nombre} - SIN USO APARENTE")
    
    # RESUMEN FINAL
    print("\n\n" + "=" * 70)
    print("📊 RESUMEN DE LIMPIEZA")
    print("=" * 70)
    
    print(f"\n✅ Duplicados eliminados: {len([t for t in DUPLICADOS_ELIMINAR if not verificar_uso_en_codigo(t)[0]])}")
    print(f"⚠️ Duplicados pendientes (aún en uso): {len([t for t in DUPLICADOS_ELIMINAR if verificar_uso_en_codigo(t)[0]])}")
    print(f"\n📂 Templates gestion/ en uso: {len(templates_gestion_en_uso)}")
    print(f"🗑️ Templates gestion/ sin uso: {len(templates_gestion_sin_uso)}")
    
    if templates_gestion_sin_uso:
        print("\n\n⚠️ TEMPLATES CANDIDATOS PARA ELIMINACIÓN FUTURA:")
        print("-" * 70)
        for template in templates_gestion_sin_uso:
            print(f"   - {template}")
        print("\n💡 Revisar manualmente antes de eliminar")
        print("   Pueden estar en {% include %} o {% extends %}")
    
    print("\n\n✅ Proceso completado")
    print("📁 Backups guardados en: backups_templates_eliminados/")
    print("=" * 70)
