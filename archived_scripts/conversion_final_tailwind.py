#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final de conversión masiva Bootstrap → Tailwind CSS 3.4
Elimina TODAS las clases Bootstrap y aplica conversiones completas
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Configuración
TEMPLATES_DIR = Path("frontend/templates")
BACKUP_DIR = Path("backup_templates_final")
LOG_FILE = "conversion_final_log.json"

# Mapeo COMPLETO Bootstrap → Tailwind
BOOTSTRAP_TO_TAILWIND = {
    # Layout y Grid
    'container': 'max-w-7xl mx-auto px-4',
    'container-fluid': 'w-full px-4',
    'container-sm': 'max-w-screen-sm mx-auto px-4',
    'container-md': 'max-w-screen-md mx-auto px-4',
    'container-lg': 'max-w-screen-lg mx-auto px-4',
    'container-xl': 'max-w-screen-xl mx-auto px-4',
    'row': 'flex flex-wrap -mx-4',
    'col': 'flex-1 px-4',
    'col-1': 'w-1/12 px-4',
    'col-2': 'w-2/12 px-4',
    'col-3': 'w-3/12 px-4',
    'col-4': 'w-4/12 px-4',
    'col-6': 'w-6/12 px-4',
    'col-8': 'w-8/12 px-4',
    'col-12': 'w-full px-4',
    'col-md': 'md:flex-1 px-4',
    'col-md-3': 'md:w-3/12 px-4',
    'col-md-4': 'md:w-4/12 px-4',
    'col-md-6': 'md:w-6/12 px-4',
    'col-md-8': 'md:w-8/12 px-4',
    'col-md-9': 'md:w-9/12 px-4',
    'col-lg-3': 'lg:w-3/12 px-4',
    'col-lg-4': 'lg:w-4/12 px-4',
    'col-lg-6': 'lg:w-6/12 px-4',
    'col-lg-8': 'lg:w-8/12 px-4',
    
    # Display
    'd-none': 'hidden',
    'd-block': 'block',
    'd-inline': 'inline',
    'd-inline-block': 'inline-block',
    'd-flex': 'flex',
    'd-inline-flex': 'inline-flex',
    'd-grid': 'grid',
    'd-table': 'table',
    'd-table-cell': 'table-cell',
    'd-table-row': 'table-row',
    
    # Flexbox
    'justify-content-start': 'justify-start',
    'justify-content-end': 'justify-end',
    'justify-content-center': 'justify-center',
    'justify-content-between': 'justify-between',
    'justify-content-around': 'justify-around',
    'justify-content-evenly': 'justify-evenly',
    'align-items-start': 'items-start',
    'align-items-end': 'items-end',
    'align-items-center': 'items-center',
    'align-items-baseline': 'items-baseline',
    'align-items-stretch': 'items-stretch',
    'align-self-start': 'self-start',
    'align-self-end': 'self-end',
    'align-self-center': 'self-center',
    'flex-row': 'flex-row',
    'flex-column': 'flex-col',
    'flex-wrap': 'flex-wrap',
    'flex-nowrap': 'flex-nowrap',
    'flex-fill': 'flex-1',
    'flex-grow-1': 'flex-grow',
    'flex-shrink-1': 'flex-shrink',
    
    # Text
    'text-left': 'text-left',
    'text-center': 'text-center',
    'text-right': 'text-right',
    'text-justify': 'text-justify',
    'text-start': 'text-left',
    'text-end': 'text-right',
    'text-uppercase': 'uppercase',
    'text-lowercase': 'lowercase',
    'text-capitalize': 'capitalize',
    'text-decoration-none': 'no-underline',
    'text-decoration-underline': 'underline',
    'text-wrap': 'whitespace-normal',
    'text-nowrap': 'whitespace-nowrap',
    'text-break': 'break-words',
    
    # Text Colors
    'text-primary': 'text-blue-600',
    'text-secondary': 'text-gray-600',
    'text-success': 'text-green-600',
    'text-danger': 'text-red-600',
    'text-warning': 'text-yellow-600',
    'text-info': 'text-cyan-600',
    'text-light': 'text-gray-100',
    'text-dark': 'text-gray-900',
    'text-muted': 'text-gray-500',
    'text-white': 'text-white',
    
    # Background Colors
    'bg-primary': 'bg-blue-600',
    'bg-secondary': 'bg-gray-600',
    'bg-success': 'bg-green-600',
    'bg-danger': 'bg-red-600',
    'bg-warning': 'bg-yellow-500',
    'bg-info': 'bg-cyan-600',
    'bg-light': 'bg-gray-100',
    'bg-dark': 'bg-gray-900',
    'bg-white': 'bg-white',
    'bg-transparent': 'bg-transparent',
    
    # Badges
    'badge': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
    'badge bg-primary': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-600 text-white',
    'badge bg-secondary': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-white',
    'badge bg-success': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-600 text-white',
    'badge bg-danger': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-600 text-white',
    'badge bg-warning': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-500 text-black',
    'badge bg-info': 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-600 text-white',
    
    # Buttons
    'btn': 'px-4 py-2 rounded font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
    'btn btn-primary': 'px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
    'btn btn-secondary': 'px-4 py-2 bg-gray-600 text-white rounded font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500',
    'btn btn-success': 'px-4 py-2 bg-green-600 text-white rounded font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500',
    'btn btn-danger': 'px-4 py-2 bg-red-600 text-white rounded font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500',
    'btn btn-warning': 'px-4 py-2 bg-yellow-500 text-black rounded font-medium hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-500',
    'btn btn-info': 'px-4 py-2 bg-cyan-600 text-white rounded font-medium hover:bg-cyan-700 focus:outline-none focus:ring-2 focus:ring-cyan-500',
    'btn btn-light': 'px-4 py-2 bg-gray-100 text-gray-900 rounded font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500',
    'btn btn-dark': 'px-4 py-2 bg-gray-900 text-white rounded font-medium hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500',
    'btn btn-outline-primary': 'px-4 py-2 border border-blue-600 text-blue-600 rounded font-medium hover:bg-blue-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500',
    'btn btn-outline-secondary': 'px-4 py-2 border border-gray-600 text-gray-600 rounded font-medium hover:bg-gray-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-gray-500',
    'btn btn-outline-success': 'px-4 py-2 border border-green-600 text-green-600 rounded font-medium hover:bg-green-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-green-500',
    'btn btn-outline-danger': 'px-4 py-2 border border-red-600 text-red-600 rounded font-medium hover:bg-red-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-red-500',
    'btn btn-sm': 'px-3 py-1.5 text-sm bg-blue-600 text-white rounded font-medium hover:bg-blue-700',
    'btn btn-lg': 'px-6 py-3 text-lg bg-blue-600 text-white rounded font-medium hover:bg-blue-700',
    
    # Forms
    'form-control': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    'form-control-sm': 'w-full px-2 py-1 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    'form-control-lg': 'w-full px-4 py-3 text-lg border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    'form-select': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white',
    'form-check-input': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500',
    'form-check-label': 'ml-2 text-sm text-gray-900',
    'form-label': 'block text-sm font-medium text-gray-700 mb-1',
    'form-text': 'mt-1 text-sm text-gray-500',
    'input-group': 'flex',
    'input-group-text': 'px-3 py-2 bg-gray-50 border border-gray-300 rounded-l-md text-sm text-gray-500',
    
    # Cards
    'card': 'bg-white rounded-lg shadow border border-gray-200',
    'card-body': 'p-6',
    'card-header': 'px-6 py-4 border-b border-gray-200 bg-gray-50 rounded-t-lg',
    'card-footer': 'px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg',
    'card-title': 'text-lg font-semibold text-gray-900 mb-2',
    'card-subtitle': 'text-sm text-gray-600 mb-2',
    'card-text': 'text-gray-700',
    
    # Alerts
    'alert': 'p-4 mb-4 rounded-md border-l-4',
    'alert alert-primary': 'p-4 mb-4 bg-blue-50 border border-blue-200 rounded-md border-l-4 border-l-blue-500 text-blue-800',
    'alert alert-secondary': 'p-4 mb-4 bg-gray-50 border border-gray-200 rounded-md border-l-4 border-l-gray-500 text-gray-800',
    'alert alert-success': 'p-4 mb-4 bg-green-50 border border-green-200 rounded-md border-l-4 border-l-green-500 text-green-800',
    'alert alert-danger': 'p-4 mb-4 bg-red-50 border border-red-200 rounded-md border-l-4 border-l-red-500 text-red-800',
    'alert alert-warning': 'p-4 mb-4 bg-yellow-50 border border-yellow-200 rounded-md border-l-4 border-l-yellow-500 text-yellow-800',
    'alert alert-info': 'p-4 mb-4 bg-cyan-50 border border-cyan-200 rounded-md border-l-4 border-l-cyan-500 text-cyan-800',
    'alert-dismissible': 'relative pr-12',
    
    # Margins y Padding - Más completo
    'mt-0': 'mt-0', 'mt-1': 'mt-1', 'mt-2': 'mt-2', 'mt-3': 'mt-3', 'mt-4': 'mt-4', 'mt-5': 'mt-5', 'mt-6': 'mt-6',
    'mb-0': 'mb-0', 'mb-1': 'mb-1', 'mb-2': 'mb-2', 'mb-3': 'mb-3', 'mb-4': 'mb-4', 'mb-5': 'mb-5', 'mb-6': 'mb-6', 'mb-8': 'mb-8',
    'ml-0': 'ml-0', 'ml-1': 'ml-1', 'ml-2': 'ml-2', 'ml-3': 'ml-3', 'ml-4': 'ml-4', 'ml-5': 'ml-5', 'ml-6': 'ml-6',
    'mr-0': 'mr-0', 'mr-1': 'mr-1', 'mr-2': 'mr-2', 'mr-3': 'mr-3', 'mr-4': 'mr-4', 'mr-5': 'mr-5', 'mr-6': 'mr-6',
    'ms-1': 'ml-1', 'ms-2': 'ml-2', 'ms-3': 'ml-3', 'ms-4': 'ml-4', 'ms-5': 'ml-5',
    'me-1': 'mr-1', 'me-2': 'mr-2', 'me-3': 'mr-3', 'me-4': 'mr-4', 'me-5': 'mr-5',
    'pt-0': 'pt-0', 'pt-1': 'pt-1', 'pt-2': 'pt-2', 'pt-3': 'pt-3', 'pt-4': 'pt-4', 'pt-5': 'pt-5', 'pt-6': 'pt-6',
    'pb-0': 'pb-0', 'pb-1': 'pb-1', 'pb-2': 'pb-2', 'pb-3': 'pb-3', 'pb-4': 'pb-4', 'pb-5': 'pb-5', 'pb-6': 'pb-6', 'pb-8': 'pb-8',
    'pl-0': 'pl-0', 'pl-1': 'pl-1', 'pl-2': 'pl-2', 'pl-3': 'pl-3', 'pl-4': 'pl-4', 'pl-5': 'pl-5', 'pl-6': 'pl-6',
    'pr-0': 'pr-0', 'pr-1': 'pr-1', 'pr-2': 'pr-2', 'pr-3': 'pr-3', 'pr-4': 'pr-4', 'pr-5': 'pr-5', 'pr-6': 'pr-6',
    'ps-1': 'pl-1', 'ps-2': 'pl-2', 'ps-3': 'pl-3', 'ps-4': 'pl-4', 'ps-5': 'pl-5',
    'pe-1': 'pr-1', 'pe-2': 'pr-2', 'pe-3': 'pr-3', 'pe-4': 'pr-4', 'pe-5': 'pr-5',
    
    # Borders
    'border': 'border border-gray-200',
    'border-0': 'border-0',
    'border-top': 'border-t border-gray-200',
    'border-bottom': 'border-b border-gray-200',
    'border-left': 'border-l border-gray-200',
    'border-right': 'border-r border-gray-200',
    'border-primary': 'border border-blue-600',
    'border-secondary': 'border border-gray-600',
    'border-success': 'border border-green-600',
    'border-danger': 'border border-red-600',
    'border-warning': 'border border-yellow-500',
    'border-info': 'border border-cyan-600',
    'rounded': 'rounded',
    'rounded-0': 'rounded-none',
    'rounded-1': 'rounded-sm',
    'rounded-2': 'rounded',
    'rounded-3': 'rounded-lg',
    'rounded-circle': 'rounded-full',
    'rounded-pill': 'rounded-full',
    
    # Shadows
    'shadow': 'shadow',
    'shadow-sm': 'shadow-sm',
    'shadow-lg': 'shadow-lg',
    'shadow-none': 'shadow-none',
    
    # Modal (Bootstrap 5)
    'modal': 'fixed inset-0 z-50 overflow-y-auto',
    'modal-dialog': 'flex min-h-full items-center justify-center p-4',
    'modal-content': 'bg-white rounded-lg shadow-xl max-w-lg w-full',
    'modal-header': 'px-6 py-4 border-b border-gray-200',
    'modal-body': 'px-6 py-4',
    'modal-footer': 'px-6 py-4 border-t border-gray-200 flex justify-end space-x-2',
    'modal fade': 'fixed inset-0 z-50 overflow-y-auto opacity-0 transition-opacity duration-300',
    
    # Tables
    'table': 'min-w-full divide-y divide-gray-200',
    'table-striped': 'min-w-full divide-y divide-gray-200',
    'table-bordered': 'min-w-full border border-gray-300',
    'table-hover': 'min-w-full divide-y divide-gray-200',
    'table-responsive': 'overflow-x-auto',
    'thead-dark': 'bg-gray-800 text-white',
    'thead-light': 'bg-gray-50 text-gray-700',
    
    # Navigation
    'navbar': 'bg-white shadow',
    'navbar-brand': 'text-xl font-bold text-gray-900',
    'navbar-nav': 'flex space-x-4',
    'nav-link': 'text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md',
    'nav-item': 'flex',
    'breadcrumb': 'flex space-x-2 text-sm text-gray-500',
    'breadcrumb-item': 'flex items-center',
}

def create_backup():
    """Crear backup de los templates antes de la conversión"""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
        
    print(f"📦 Creando backup en {BACKUP_DIR}...")
    
    import shutil
    for template_file in TEMPLATES_DIR.rglob("*.html"):
        backup_file = BACKUP_DIR / template_file.relative_to(TEMPLATES_DIR)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_file, backup_file)
    
    print(f"✅ Backup creado con {len(list(BACKUP_DIR.rglob('*.html')))} archivos")

def convert_bootstrap_classes(content: str) -> tuple[str, int]:
    """Convierte todas las clases Bootstrap a Tailwind"""
    conversions = 0
    modified_content = content
    
    # Convertir clases simples y complejas
    for bootstrap_class, tailwind_class in BOOTSTRAP_TO_TAILWIND.items():
        # Buscar clases exactas en atributos class
        pattern = rf'class="([^"]*)\b{re.escape(bootstrap_class)}\b([^"]*)"'
        matches = re.findall(pattern, modified_content)
        
        if matches:
            for before, after in matches:
                old_class = f'class="{before}{bootstrap_class}{after}"'
                # Limpiar espacios duplicados y mantener otras clases
                other_classes = f"{before} {after}".strip()
                if other_classes:
                    new_class = f'class="{other_classes} {tailwind_class}"'
                else:
                    new_class = f'class="{tailwind_class}"'
                
                modified_content = modified_content.replace(old_class, new_class)
                conversions += 1
    
    # Limpiar clases duplicadas y espacios extra
    def clean_classes(match):
        classes = match.group(1).split()
        # Eliminar duplicados preservando orden
        seen = set()
        unique_classes = []
        for cls in classes:
            if cls not in seen:
                seen.add(cls)
                unique_classes.append(cls)
        return f'class="{" ".join(unique_classes)}"'
    
    modified_content = re.sub(r'class="([^"]+)"', clean_classes, modified_content)
    
    return modified_content, conversions

def remove_bootstrap_dependencies(content: str) -> tuple[str, int]:
    """Elimina todas las dependencias de Bootstrap"""
    removals = 0
    
    # Eliminar enlaces CDN de Bootstrap
    bootstrap_cdn_patterns = [
        r'<link[^>]*bootstrap[^>]*>',
        r'<script[^>]*bootstrap[^>]*></script>',
        r'<link[^>]*href="[^"]*bootstrap[^"]*"[^>]*>',
        r'<script[^>]*src="[^"]*bootstrap[^"]*"[^>]*></script>',
    ]
    
    for pattern in bootstrap_cdn_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        removals += len(matches)
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Eliminar atributos data-bs-* (Bootstrap 5)
    data_bs_pattern = r'\s+data-bs-[^=]*="[^"]*"'
    matches = re.findall(data_bs_pattern, content)
    removals += len(matches)
    content = re.sub(data_bs_pattern, '', content)
    
    return content, removals

def remove_inline_css(content: str) -> tuple[str, int]:
    """Elimina CSS inline básico"""
    removals = 0
    
    # Patrones de CSS inline comunes
    inline_patterns = [
        r'\s+style="[^"]*"',  # style="..."
    ]
    
    for pattern in inline_patterns:
        matches = re.findall(pattern, content)
        removals += len(matches)
        content = re.sub(pattern, '', content)
    
    return content, removals

def update_template_inheritance(content: str) -> tuple[str, int]:
    """Actualiza herencia de templates a base_modern.html"""
    updates = 0
    
    # Patrones de extends a actualizar
    extends_patterns = [
        (r'{%\s*extends\s*["\']base/base\.html["\']\s*%}', '{% extends "base/base_modern.html" %}'),
        (r'{%\s*extends\s*["\']base/base_improved\.html["\']\s*%}', '{% extends "base/base_modern.html" %}'),
        (r'{%\s*extends\s*["\']apps/pos/pos_bootstrap\.html["\']\s*%}', '{% extends "base/base_modern.html" %}'),
        (r'{%\s*extends\s*["\']pos_bootstrap\.html["\']\s*%}', '{% extends "base/base_modern.html" %}'),
    ]
    
    for pattern, replacement in extends_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updates += 1
    
    return content, updates

def add_modern_assets(content: str) -> tuple[str, int]:
    """Añade assets modernos (Vite + Tailwind)"""
    additions = 0
    
    # Si no tiene load vite_tags, añadirlo
    if '{% load vite_tags %}' not in content and '{% extends' in content:
        # Añadir después del extends
        content = re.sub(
            r'({%\s*extends[^%]*%})',
            r'\1\n{% load vite_tags %}',
            content,
            count=1
        )
        additions += 1
    
    # Si no tiene el bloque de assets Vite, añadirlo
    if 'vite_asset' not in content and '{% block' in content:
        # Buscar si hay un bloque extra_css o extra_js
        if '{% block extra_css %}' not in content:
            # Añadir bloque de CSS después del primer bloque encontrado
            first_block_pattern = r'({%\s*block\s+\w+\s*%})'
            match = re.search(first_block_pattern, content)
            if match:
                insert_point = match.start()
                css_block = '''
{% block extra_css %}
    {% vite_asset "src/pos.ts" %}
{% endblock %}

'''
                content = content[:insert_point] + css_block + content[insert_point:]
                additions += 1
    
    return content, additions

def convert_file(file_path: Path) -> Dict:
    """Convierte un archivo individual"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_changes = 0
        
        # 1. Convertir clases Bootstrap
        content, bootstrap_conversions = convert_bootstrap_classes(content)
        total_changes += bootstrap_conversions
        
        # 2. Eliminar dependencias Bootstrap
        content, dependency_removals = remove_bootstrap_dependencies(content)
        total_changes += dependency_removals
        
        # 3. Eliminar CSS inline
        content, css_removals = remove_inline_css(content)
        total_changes += css_removals
        
        # 4. Actualizar herencia de templates
        content, inheritance_updates = update_template_inheritance(content)
        total_changes += inheritance_updates
        
        # 5. Añadir assets modernos
        content, asset_additions = add_modern_assets(content)
        total_changes += asset_additions
        
        # Guardar archivo si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            'file': str(file_path.name),  # Solo el nombre del archivo
            'success': True,
            'changes': {
                'bootstrap_conversions': bootstrap_conversions,
                'dependency_removals': dependency_removals,
                'css_removals': css_removals,
                'inheritance_updates': inheritance_updates,
                'asset_additions': asset_additions,
                'total_changes': total_changes
            },
            'modified': content != original_content
        }
        
    except Exception as e:
        return {
            'file': str(file_path.name),  # Solo el nombre del archivo
            'success': False,
            'error': str(e),
            'changes': {}
        }

def main():
    """Función principal de conversión"""
    print("🚀 CONVERSIÓN FINAL MASIVA: Bootstrap → Tailwind CSS 3.4")
    print("=" * 60)
    
    # Crear backup
    create_backup()
    
    # Buscar todos los archivos HTML, excluyendo backups
    all_html_files = list(TEMPLATES_DIR.rglob("*.html"))
    template_files = [f for f in all_html_files if 'backup' not in str(f).lower()]
    print(f"📁 Encontrados {len(template_files)} archivos HTML (excluyendo backups)")
    
    # Procesar archivos
    results = []
    successful_conversions = 0
    failed_conversions = 0
    total_changes = 0
    
    for i, file_path in enumerate(template_files, 1):
        print(f"🔄 Procesando {i}/{len(template_files)}: {file_path.name}")
        
        result = convert_file(file_path)
        results.append(result)
        
        if result['success']:
            successful_conversions += 1
            total_changes += result['changes'].get('total_changes', 0)
            
            if result.get('modified'):
                changes = result['changes']
                print(f"   ✅ Modificado - Bootstrap: {changes['bootstrap_conversions']}, "
                      f"Deps: {changes['dependency_removals']}, "
                      f"CSS: {changes['css_removals']}, "
                      f"Herencia: {changes['inheritance_updates']}")
            else:
                print(f"   ⏭️  Sin cambios")
        else:
            failed_conversions += 1
            print(f"   ❌ Error: {result['error']}")
    
    # Guardar log detallado
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE CONVERSIÓN")
    print("=" * 60)
    print(f"✅ Archivos procesados exitosamente: {successful_conversions}")
    print(f"❌ Archivos con errores: {failed_conversions}")
    print(f"🔄 Total de cambios aplicados: {total_changes}")
    print(f"📦 Backup guardado en: {BACKUP_DIR}")
    print(f"📄 Log detallado en: {LOG_FILE}")
    
    if failed_conversions == 0:
        print("\n🎉 ¡CONVERSIÓN COMPLETADA EXITOSAMENTE!")
        print("🎯 Todos los templates ahora usan SOLO Tailwind CSS 3.4")
    else:
        print(f"\n⚠️  Conversión completada con {failed_conversions} errores")
        print("🔍 Revisa el log para más detalles")
    
    print("\n🚀 PRÓXIMO PASO: Ejecuta el script de verificación para confirmar")
    print("   python verificacion_templates_tailwind.py")

if __name__ == "__main__":
    main()