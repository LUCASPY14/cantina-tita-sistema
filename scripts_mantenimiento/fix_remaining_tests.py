#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCRIPT DE CORRECCIÓN - Tests Pendientes
========================================
Aplica correcciones de schema a los 4 módulos restantes.
"""

import re

# ============================================================================
# CORRECCIONES PARA test_modulo_cierres_caja.py
# ============================================================================

fixes_cierres = [
    # 1. Eliminar JOIN con tabla usuarios (no existe)
    (
        r"INNER JOIN usuarios u ON e\.ID_Usuario = u\.ID_Usuario\s*\n\s*INNER JOIN roles r ON u\.ID_Rol = r\.ID_Rol\s*\n\s*WHERE r\.Nombre_Rol = 'CAJERO'",
        "INNER JOIN roles r ON e.ID_Rol = r.ID_Rol\n            WHERE r.Nombre_Rol = 'CAJERO'"
    ),
    # 2. Corregir nombre de columna Nombres -> Nombre
    (r"e\.Nombres", "e.Nombre"),
    # 3. Corregir nombre de columna Apellidos -> Apellido
    (r"e\.Apellidos", "e.Apellido"),
    # 4. Corregir Fecha_Apertura -> Fecha_Hora_Apertura
    (r"Fecha_Apertura(?!_)", "Fecha_Hora_Apertura"),
    # 5. Corregir Fecha_Cierre -> Fecha_Hora_Cierre
    (r"Fecha_Cierre(?!_)", "Fecha_Hora_Cierre"),
]

# ============================================================================
# CORRECCIONES PARA test_modulo_ventas_directas.py
# ============================================================================

fixes_ventas = [
    # 1. Corregir hp.Precio_Venta -> hp.Precio_Nuevo (historico_precios)
    (r"hp\.Precio_Venta", "hp.Precio_Nuevo"),
    # 2. Corregir dv.Precio_Unitario -> dv.Precio_Unitario_Total
    (r"dv\.Precio_Unitario(?!_)", "dv.Precio_Unitario_Total"),
    # 3. Eliminar referencias a dt.Tipo_Documento
    (r"dt\.Tipo_Documento,?\s*", ""),
    # 4. Eliminar WHERE con Tipo_Documento
    (r"WHERE dt\.Tipo_Documento = '[^']*'\s*AND", "WHERE"),
]

# ============================================================================
# CORRECCIONES PARA test_modulo_almuerzos.py
# ============================================================================

fixes_almuerzos = [
    # 1. Corregir h.ID_Cliente -> h.ID_Cliente_Responsable
    (r"h\.ID_Cliente(?!_)", "h.ID_Cliente_Responsable"),
    # 2. Corregir tabla almuerzos_mensuales (si existe, sino dejarlo)
    # Esto lo verificaremos manualmente
]

# ============================================================================
# CORRECCIONES PARA test_modulo_documentos.py
# ============================================================================

fixes_documentos = [
    # 1. Eliminar columna Activo de documentos_tributarios
    (r",\s*Activo\s*(?=FROM)", ""),
    (r"Activo,\s*", ""),
    (r"WHERE\s+Activo\s*=\s*TRUE\s+AND", "WHERE"),
    (r"WHERE\s+Activo\s*=\s*TRUE", "WHERE 1=1"),
    (r"AND\s+Activo\s*=\s*TRUE", ""),
    # 2. Eliminar columna Tipo_Documento
    (r"Tipo_Documento,?\s*", ""),
    # 3. Eliminar referencias a Numero_Inicial, Numero_Final, Numero_Actual
    (r"Numero_Inicial|Numero_Final|Numero_Actual", "Nro_Secuencial"),
]

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def apply_fixes(filename, fixes_list):
    """Aplica una lista de correcciones a un archivo"""
    print(f"\n🔧 Procesando: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_count = 0
        
        for pattern, replacement in fixes_list:
            matches = len(re.findall(pattern, content))
            if matches > 0:
                content = re.sub(pattern, replacement, content)
                changes_count += matches
                print(f"   ✓ Aplicado: {pattern[:50]}... ({matches} ocurrencias)")
        
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filename} corregido ({changes_count} cambios)")
            return True
        else:
            print(f"ℹ️  {filename} - Sin cambios necesarios")
            return False
            
    except Exception as e:
        print(f"❌ Error en {filename}: {str(e)}")
        return False

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("  CORRECCIÓN AUTOMÁTICA - TESTS PENDIENTES")
    print("="*70)
    
    files_to_fix = [
        ('test_modulo_cierres_caja.py', fixes_cierres),
        ('test_modulo_ventas_directas.py', fixes_ventas),
        ('test_modulo_almuerzos.py', fixes_almuerzos),
        ('test_modulo_documentos.py', fixes_documentos),
    ]
    
    success_count = 0
    for filename, fixes in files_to_fix:
        if apply_fixes(filename, fixes):
            success_count += 1
    
    print("\n" + "="*70)
    print(f"✅ Proceso completado: {success_count}/{len(files_to_fix)} archivos modificados")
    print("="*70)
    print("\n🎯 Siguiente paso: Ejecutar cada test para verificar correcciones\n")
