#!/usr/bin/env python
"""
Script para identificar y limpiar templates duplicados en el proyecto Django
"""
import os
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict
import re


def get_file_hash(filepath):
    """Calcula el hash MD5 de un archivo para identificar duplicados exactos"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


def get_content_similarity(filepath):
    """Extrae el contenido principal del template sin espacios ni comentarios para comparar similitud"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover comentarios HTML
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # Remover espacios en blanco extras
        content = re.sub(r'\s+', ' ', content).strip()
        # Remover líneas vacías
        content = re.sub(r'\n\s*\n', '\n', content)
        
        return content
    except:
        return None


def analyze_template_usage():
    """Analiza qué templates están siendo usados en las vistas y URLs"""
    used_templates = set()
    
    # Buscar en archivos Python (views.py)
    for root, dirs, files in os.walk('.'):
        # Ignorar directorios específicos
        dirs[:] = [d for d in dirs if d not in ['.venv', 'node_modules', '__pycache__', 'migrations']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Buscar patrones de uso de templates
                    template_patterns = [
                        r"render\([^,]+,\s*['\"]([^'\"]+\.html)['\"]",
                        r"template_name\s*=\s*['\"]([^'\"]+\.html)['\"]",
                        r"TemplateResponse\([^,]+,\s*['\"]([^'\"]+\.html)['\"]"
                    ]
                    
                    for pattern in template_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            used_templates.add(match)
                            
                except:
                    continue
    
    return used_templates


def find_duplicate_templates():
    """Encuentra templates duplicados por contenido"""
    hash_to_files = defaultdict(list)
    content_to_files = defaultdict(list)
    
    template_dirs = [
        'templates',
        'pos/templates',
        'gestion/templates'
    ]
    
    all_templates = []
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        filepath = os.path.join(root, file)
                        all_templates.append(filepath)
    
    print(f"\n📊 ANÁLISIS DE TEMPLATES")
    print("=" * 50)
    print(f"Total de templates encontrados: {len(all_templates)}")
    
    for filepath in all_templates:
        # Hash exacto
        file_hash = get_file_hash(filepath)
        if file_hash:
            hash_to_files[file_hash].append(filepath)
        
        # Contenido similar
        content = get_content_similarity(filepath)
        if content and len(content) > 100:  # Solo archivos con contenido significativo
            content_hash = hashlib.md5(content.encode()).hexdigest()
            content_to_files[content_hash].append(filepath)
    
    # Encontrar duplicados exactos
    exact_duplicates = []
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            exact_duplicates.append(files)
    
    # Encontrar duplicados similares
    similar_duplicates = []
    for content_hash, files in content_to_files.items():
        if len(files) > 1:
            # Solo agregar si no son duplicados exactos
            if files not in exact_duplicates:
                similar_duplicates.append(files)
    
    return exact_duplicates, similar_duplicates, all_templates


def analyze_template_structure():
    """Analiza la estructura de herencia de templates"""
    template_inheritance = {}
    base_templates = set()
    
    template_dirs = [
        'templates',
        'pos/templates', 
        'gestion/templates'
    ]
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Buscar {% extends %}
                            extends_match = re.search(r'{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%}', content)
                            if extends_match:
                                parent_template = extends_match.group(1)
                                template_inheritance[filepath] = parent_template
                            else:
                                # Podría ser un template base
                                if 'base' in file.lower() or 'layout' in file.lower():
                                    base_templates.add(filepath)
                        except:
                            continue
    
    return template_inheritance, base_templates


def identify_potential_removals(exact_duplicates, similar_duplicates, used_templates, all_templates):
    """Identifica templates que pueden ser eliminados"""
    files_to_remove = []
    
    # Para duplicados exactos, mantener solo el primero
    for duplicate_group in exact_duplicates:
        # Ordenar por prioridad (templates/ > pos/templates > gestion/templates)
        priority_order = ['templates/', 'pos/templates/', 'gestion/templates/']
        sorted_files = sorted(duplicate_group, key=lambda x: next((i for i, p in enumerate(priority_order) if x.startswith(p)), 999))
        
        # Mantener el primero, marcar los otros para eliminación
        files_to_remove.extend(sorted_files[1:])
    
    # Verificar templates no utilizados
    unused_templates = []
    for template in all_templates:
        template_name = template.replace('\\', '/').replace('templates/', '').replace('pos/templates/', '').replace('gestion/templates/', '')
        
        # Buscar variaciones del nombre
        variations = [
            template_name,
            template_name.split('/')[-1],  # Solo el nombre del archivo
            '/'.join(template_name.split('/')[1:]),  # Sin el primer directorio
        ]
        
        is_used = any(var in used_templates for var in variations)
        
        if not is_used:
            unused_templates.append(template)
    
    return files_to_remove, unused_templates


def create_backup():
    """Crea backup de templates antes de eliminar"""
    backup_dir = 'backups_templates_eliminados'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    return backup_dir


def main():
    print("🧹 LIMPIEZA DE TEMPLATES DUPLICADOS")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    os.chdir('D:/anteproyecto20112025')
    
    # Analizar uso de templates
    print("🔍 Analizando uso de templates...")
    used_templates = analyze_template_usage()
    print(f"Templates identificados en uso: {len(used_templates)}")
    
    # Buscar duplicados
    print("🔍 Buscando templates duplicados...")
    exact_duplicates, similar_duplicates, all_templates = find_duplicate_templates()
    
    # Analizar estructura
    print("🔍 Analizando estructura de herencia...")
    template_inheritance, base_templates = analyze_template_structure()
    
    # Identificar qué eliminar
    files_to_remove, unused_templates = identify_potential_removals(
        exact_duplicates, similar_duplicates, used_templates, all_templates
    )
    
    # Mostrar resultados
    print(f"\n📈 RESULTADOS DEL ANÁLISIS")
    print("=" * 50)
    print(f"Total de templates: {len(all_templates)}")
    print(f"Templates base identificados: {len(base_templates)}")
    print(f"Duplicados exactos encontrados: {len(exact_duplicates)} grupos")
    print(f"Duplicados similares encontrados: {len(similar_duplicates)} grupos")
    print(f"Templates aparentemente no utilizados: {len(unused_templates)}")
    print(f"Templates marcados para eliminación: {len(files_to_remove)}")
    
    # Mostrar detalles
    if exact_duplicates:
        print(f"\n🔄 DUPLICADOS EXACTOS:")
        for i, group in enumerate(exact_duplicates, 1):
            print(f"\nGrupo {i}:")
            for file in group:
                print(f"  - {file}")
    
    if similar_duplicates:
        print(f"\n🔄 DUPLICADOS SIMILARES:")
        for i, group in enumerate(similar_duplicates, 1):
            print(f"\nGrupo {i}:")
            for file in group:
                print(f"  - {file}")
    
    if base_templates:
        print(f"\n🏗️ TEMPLATES BASE:")
        for template in sorted(base_templates):
            print(f"  - {template}")
    
    if unused_templates:
        print(f"\n🗑️ TEMPLATES NO UTILIZADOS (potencial eliminación):")
        for template in sorted(unused_templates)[:20]:  # Mostrar solo los primeros 20
            print(f"  - {template}")
        if len(unused_templates) > 20:
            print(f"  ... y {len(unused_templates) - 20} más")
    
    # Preguntar si proceder con la limpieza
    print(f"\n❓ ACCIÓN REQUERIDA")
    print("=" * 30)
    response = input("¿Desea proceder con la limpieza automática? (y/N): ").lower().strip()
    
    if response == 'y':
        # Crear backup
        backup_dir = create_backup()
        print(f"📁 Creando backup en: {backup_dir}")
        
        removed_count = 0
        
        # Eliminar duplicados exactos (excepto el primero de cada grupo)
        for duplicate_group in exact_duplicates:
            priority_order = ['templates/', 'pos/templates/', 'gestion/templates/']
            sorted_files = sorted(duplicate_group, key=lambda x: next((i for i, p in enumerate(priority_order) if x.startswith(p)), 999))
            
            for file_to_remove in sorted_files[1:]:
                try:
                    # Crear estructura de directorios en backup
                    backup_path = os.path.join(backup_dir, file_to_remove)
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    # Mover archivo a backup
                    shutil.move(file_to_remove, backup_path)
                    removed_count += 1
                    print(f"✅ Eliminado: {file_to_remove}")
                except Exception as e:
                    print(f"❌ Error eliminando {file_to_remove}: {e}")
        
        print(f"\n🎉 LIMPIEZA COMPLETADA")
        print(f"Archivos eliminados: {removed_count}")
        print(f"Backup creado en: {backup_dir}")
        print(f"Templates restantes: {len(all_templates) - removed_count}")
    
    else:
        print("❌ Operación cancelada por el usuario")


if __name__ == "__main__":
    main()