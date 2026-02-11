#!/usr/bin/env python3
"""
Script mejorado para convertir modelos Django de PascalCase a snake_case
Maneja correctamente casos mixtos como ID_Cliente -> id_cliente
"""
import re
import os

def convert_mixed_case_to_snake(name):
    """
    Convierte nombres mixtos como 'ID_Cliente' o 'Nro_Factura_Venta' a snake_case
    
    Reglas:
    - ID_Cliente -> id_cliente
    - Nro_Factura_Venta -> nro_factura_venta  
    - Ruc_CI -> ruc_ci
    - Cliente_Responsable -> cliente_responsable
    """
    # Primero, reemplazar underscores existentes entre palabras ya separadas
    # y convertir todo a snake_case apropiado
    
    # Dividir por underscores existentes
    parts = name.split('_')
    snake_parts = []
    
    for part in parts:
        if not part:  # Evitar partes vacías
            continue
            
        # Convertir cada parte de PascalCase a snake_case
        # Insertar underscore antes de mayúscula que sigue a minúscula
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', part)
        # Insertar underscore antes de mayúscula que sigue a minúscula/número
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        snake_parts.append(s2.lower())
    
    result = '_'.join(snake_parts)
    
    # Limpiar múltiples underscores consecutivos
    result = re.sub('_+', '_', result)
    
    return result

def fix_models_file(file_path):
    """Arregla un archivo de modelos restaurando desde backup y aplicando conversión correcta"""
    
    backup_path = f"{file_path}.backup_before_snake_case"
    
    if not os.path.exists(backup_path):
        print(f"Error: No se encuentra backup {backup_path}")
        return False
    
    print(f"Restaurando desde backup: {backup_path}")
    
    # Restaurar desde backup
    with open(backup_path, 'r', encoding='utf-8') as backup_f:
        content = backup_f.read()
    
    changes_made = 0
    
    # Convertir db_column con la función mejorada
    def replace_db_column(match):
        nonlocal changes_made
        original_name = match.group(1)
        snake_name = convert_mixed_case_to_snake(original_name)
        changes_made += 1
        print(f"  {original_name} -> {snake_name}")
        return f"db_column='{snake_name}'"
    
    print("Convirtiendo db_column con lógica mejorada:")
    content = re.sub(r"db_column='([A-Za-z_0-9]+)'", replace_db_column, content)
    
    # Cambiar managed settings
    content = re.sub(r"managed = False", "managed = True", content)
    content = re.sub(r"managed = 'test' not in sys\.argv", "managed = True", content)
    
    # Limpiar comentarios
    content = re.sub(r"\s*# True para tests, False para producción", "", content)
    content = re.sub(r"\s*# Tabla existente, Django no la administra", "", content)
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Total de cambios: {changes_made}")
    return True

if __name__ == "__main__":
    # Test de la función de conversión
    test_cases = {
        'ID_Cliente': 'id_cliente',
        'Nro_Factura_Venta': 'nro_factura_venta', 
        'Ruc_CI': 'ruc_ci',
        'Fecha_Ultima_Actualizacion': 'fecha_ultima_actualizacion',
        'Cliente': 'cliente',
        'Nombres': 'nombres'
    }
    
    print("=== Probando conversión ===")
    for original, expected in test_cases.items():
        result = convert_mixed_case_to_snake(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} {original} -> {result} (esperado: {expected})")
    
    print("\n=== Aplicando corrección ===")
    files_to_fix = [
        "d:/anteproyecto20112025/backend/gestion/models.py",
        "d:/anteproyecto20112025/backend/pos/models.py"
    ]
    
    for file_path in files_to_fix:
        print(f"\nProcesando {file_path}")
        success = fix_models_file(file_path)
        if success:
            print(f"✓ {file_path} corregido exitosamente")
        else:
            print(f"✗ Error procesando {file_path}")