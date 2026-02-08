#!/usr/bin/env python3
"""
Script para convertir modelos Django de PascalCase a snake_case
Actualiza db_column y managed para mapear correctamente a la nueva base MySQL
"""
import re
import os
import sys

def pascal_to_snake(name):
    """Convierte PascalCase a snake_case"""
    # Insertar underscore antes de mayúsculas (excepto al inicio)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insertar underscore antes de secuencias de mayúsculas seguidas de minúsculas
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def convert_models_file(file_path, backup=True):
    """Convierte un archivo de modelos Django completo"""
    
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe")
        return False
    
    # Crear backup si se solicita
    if backup:
        backup_path = f"{file_path}.backup_before_snake_case"
        with open(file_path, 'r', encoding='utf-8') as f:
            with open(backup_path, 'w', encoding='utf-8') as backup_f:
                backup_f.write(f.read())
        print(f"Backup creado: {backup_path}")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = 0
    
    # 1. Convertir db_column de PascalCase a snake_case
    def replace_db_column(match):
        nonlocal changes_made
        full_match = match.group(0)
        column_name = match.group(1)
        snake_name = pascal_to_snake(column_name)
        changes_made += 1
        print(f"  {column_name} -> {snake_name}")
        return f"db_column='{snake_name}'"
    
    print("Convirtiendo db_column:")
    content = re.sub(r"db_column='([A-Z][A-Za-z_0-9]*)'", replace_db_column, content)
    
    # 2. Cambiar managed = False a managed = True
    managed_false_pattern = r"managed = False"
    managed_false_matches = len(re.findall(managed_false_pattern, content))
    if managed_false_matches > 0:
        content = re.sub(managed_false_pattern, "managed = True", content)
        changes_made += managed_false_matches
        print(f"Cambiados {managed_false_matches} managed = False -> managed = True")
    
    # 3. Cambiar managed = 'test' not in sys.argv a managed = True
    managed_test_pattern = r"managed = 'test' not in sys\.argv"
    managed_test_matches = len(re.findall(managed_test_pattern, content))
    if managed_test_matches > 0:
        content = re.sub(managed_test_pattern, "managed = True", content)
        changes_made += managed_test_matches
        print(f"Cambiados {managed_test_matches} managed = 'test' not in sys.argv -> managed = True")
    
    # 4. Remover comentarios sobre managed
    content = re.sub(r"\s*# True para tests, False para producción", "", content)
    content = re.sub(r"\s*# Tabla existente, Django no la administra", "", content)
    content = re.sub(r"\s*# Django administra la tabla", "", content)
    
    # Escribir archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Total de cambios realizados: {changes_made}")
    return True

if __name__ == "__main__":
    # Archivos a procesar
    files_to_convert = [
        "d:/anteproyecto20112025/backend/gestion/models.py",
        "d:/anteproyecto20112025/backend/pos/models.py"
    ]
    
    for file_path in files_to_convert:
        print(f"\n=== Procesando {file_path} ===")
        success = convert_models_file(file_path)
        if success:
            print(f"✓ {file_path} actualizado exitosamente")
        else:
            print(f"✗ Error procesando {file_path}")