#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación CORREGIDO para Tailwind CSS 3.4
NO marca clases válidas de Tailwind como Bootstrap
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuración
TEMPLATES_DIR = Path("frontend/templates")
REPORT_FILE = "reporte_tailwind_corregido.json"

# Clases que NO son de Bootstrap sino de Tailwind (VÁLIDAS)
TAILWIND_VALID_CLASSES = {
    # Spacing utilities válidos en Tailwind
    'mb-0', 'mb-1', 'mb-2', 'mb-3', 'mb-4', 'mb-5', 'mb-6', 'mb-8', 'mb-10', 'mb-12',
    'mt-0', 'mt-1', 'mt-2', 'mt-3', 'mt-4', 'mt-5', 'mt-6', 'mt-8', 'mt-10', 'mt-12',
    'ml-0', 'ml-1', 'ml-2', 'ml-3', 'ml-4', 'ml-5', 'ml-6', 'ml-8', 'ml-10', 'ml-12',
    'mr-0', 'mr-1', 'mr-2', 'mr-3', 'mr-4', 'mr-5', 'mr-6', 'mr-8', 'mr-10', 'mr-12',
    'pt-0', 'pt-1', 'pt-2', 'pt-3', 'pt-4', 'pt-5', 'pt-6', 'pt-8', 'pt-10', 'pt-12',
    'pb-0', 'pb-1', 'pb-2', 'pb-3', 'pb-4', 'pb-5', 'pb-6', 'pb-8', 'pb-10', 'pb-12',
    'pl-0', 'pl-1', 'pl-2', 'pl-3', 'pl-4', 'pl-5', 'pl-6', 'pl-8', 'pl-10', 'pl-12',
    'pr-0', 'pr-1', 'pr-2', 'pr-3', 'pr-4', 'pr-5', 'pr-6', 'pr-8', 'pr-10', 'pr-12',
}

# Clases que SÍ son Bootstrap y deben eliminarse
BOOTSTRAP_CLASSES_TO_REMOVE = {
    # Grid system
    'container', 'container-fluid', 'row', 'col', 'col-1', 'col-2', 'col-3', 'col-4', 
    'col-6', 'col-8', 'col-12', 'col-md', 'col-md-3', 'col-md-4', 'col-md-6', 'col-md-8', 'col-md-9',
    'col-lg-3', 'col-lg-4', 'col-lg-6', 'col-lg-8',
    
    # Display utilities
    'd-none', 'd-block', 'd-inline', 'd-inline-block', 'd-flex', 'd-inline-flex',
    
    # Text utilities específicos de Bootstrap
    'text-muted', 'text-primary', 'text-secondary', 'text-success', 'text-danger', 
    'text-warning', 'text-info', 'text-light', 'text-dark', 'text-right',
    
    # Background colors específicos de Bootstrap
    'bg-primary', 'bg-secondary', 'bg-success', 'bg-danger', 'bg-warning', 
    'bg-info', 'bg-light', 'bg-dark',
    
    # Components
    'btn', 'alert', 'badge', 'card', 'modal', 'nav', 'navbar',
    'form-control', 'form-select', 'form-check',
    'list-group', 'dropdown',
    
    # Bootstrap 5 spacing (me, ms, pe, ps)
    'me-1', 'me-2', 'me-3', 'me-4', 'me-5',
    'ms-1', 'ms-2', 'ms-3', 'ms-4', 'ms-5',
    'pe-1', 'pe-2', 'pe-3', 'pe-4', 'pe-5',
    'ps-1', 'ps-2', 'ps-3', 'ps-4', 'ps-5',
    
    # Borders específicos de Bootstrap
    'border-top', 'border-bottom', 'border-left', 'border-right',
}

def find_bootstrap_classes(content: str) -> Set[str]:
    """Encuentra clases Bootstrap REALES (no clases válidas de Tailwind)"""
    bootstrap_found = set()
    
    # Buscar atributos class
    class_matches = re.findall(r'class="([^"]*)"', content)
    
    for class_attr in class_matches:
        classes = class_attr.split()
        for cls in classes:
            # Solo marcar si es una clase Bootstrap real y NO una clase válida de Tailwind
            if cls in BOOTSTRAP_CLASSES_TO_REMOVE:
                bootstrap_found.add(cls)
            # Patrones específicos de Bootstrap
            elif re.match(r'^btn\s+btn-', cls):  # btn btn-primary, etc.
                bootstrap_found.add(cls)
            elif re.match(r'^alert\s+alert-', cls):  # alert alert-success, etc.
                bootstrap_found.add(cls)
            elif re.match(r'^badge\s+bg-', cls):  # badge bg-primary, etc.
                bootstrap_found.add(cls)
    
    return bootstrap_found

def find_bootstrap_cdn(content: str) -> List[str]:
    """Encuentra enlaces CDN de Bootstrap"""
    cdn_patterns = [
        r'<link[^>]*bootstrap[^>]*>',
        r'<script[^>]*bootstrap[^>]*></script>',
        r'<link[^>]*href="[^"]*bootstrap[^"]*"[^>]*>',
        r'<script[^>]*src="[^"]*bootstrap[^"]*"[^>]*></script>',
        r'<link[^>]*cdn\.jsdelivr\.net[^>]*bootstrap[^>]*>',
        r'<script[^>]*cdn\.jsdelivr\.net[^>]*bootstrap[^>]*></script>',
        r'<link[^>]*stackpath\.bootstrapcdn\.com[^>]*>',
        r'<script[^>]*stackpath\.bootstrapcdn\.com[^>]*></script>',
    ]
    
    cdn_found = []
    for pattern in cdn_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        cdn_found.extend(matches)
    
    return cdn_found

def find_data_bs_attributes(content: str) -> List[str]:
    """Encuentra atributos data-bs-* de Bootstrap"""
    return re.findall(r'data-bs-[^=]*="[^"]*"', content)

def find_inline_css(content: str) -> List[str]:
    """Encuentra CSS inline"""
    return re.findall(r'style="[^"]*"', content)

def analyze_template(file_path: Path) -> Dict:
    """Analiza un template individual"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Análisis
        bootstrap_classes = find_bootstrap_classes(content)
        bootstrap_cdn = find_bootstrap_cdn(content)
        data_bs = find_data_bs_attributes(content)
        inline_css = find_inline_css(content)
        
        # Determinar si tiene problemas
        has_problems = bool(bootstrap_classes or bootstrap_cdn or data_bs or inline_css)
        
        return {
            'file': str(file_path.relative_to(TEMPLATES_DIR)),
            'has_problems': has_problems,
            'issues': {
                'bootstrap_classes': sorted(list(bootstrap_classes)),
                'bootstrap_cdn': bootstrap_cdn,
                'data_bs_attributes': data_bs,
                'inline_css': inline_css
            },
            'problems_count': len(bootstrap_classes) + len(bootstrap_cdn) + len(data_bs) + len(inline_css)
        }
        
    except Exception as e:
        return {
            'file': str(file_path.relative_to(TEMPLATES_DIR)),
            'has_problems': True,
            'error': str(e),
            'issues': {},
            'problems_count': 1
        }

def main():
    """Función principal de verificación"""
    print("🎯 VERIFICACIÓN CORREGIDA: Tailwind CSS 3.4 vs Bootstrap")
    print("=" * 65)
    print("📋 Verificando SOLO clases Bootstrap reales (no clases válidas de Tailwind)")
    print("")
    
    # Buscar todos los archivos HTML
    all_html_files = list(TEMPLATES_DIR.rglob("*.html"))
    template_files = [f for f in all_html_files if 'backup' not in str(f).lower()]
    
    print(f"📁 Analizando {len(template_files)} templates...")
    print("")
    
    # Analizar archivos
    results = []
    templates_with_problems = 0
    templates_without_problems = 0
    total_problems = 0
    
    problem_files = []
    clean_files = []
    
    for file_path in template_files:
        result = analyze_template(file_path)
        results.append(result)
        
        if result.get('has_problems', False):
            templates_with_problems += 1
            total_problems += result.get('problems_count', 0)
            problem_files.append(result)
        else:
            templates_without_problems += 1
            clean_files.append(result)
    
    # Mostrar solo archivos CON problemas reales
    if problem_files:
        print("❌ ARCHIVOS CON PROBLEMAS BOOTSTRAP REALES:")
        print("-" * 50)
        for result in problem_files:
            print(f"📁 {result['file']}")
            issues = result.get('issues', {})
            
            if issues.get('bootstrap_classes'):
                print(f"  🔵 Bootstrap classes: {', '.join(issues['bootstrap_classes'])}")
            
            if issues.get('bootstrap_cdn'):
                print(f"  🌐 CDN Bootstrap: {len(issues['bootstrap_cdn'])} enlaces")
            
            if issues.get('data_bs_attributes'):
                print(f"  📊 Atributos data-bs: {len(issues['data_bs_attributes'])}")
            
            if issues.get('inline_css'):
                print(f"  🎨 CSS inline: {len(issues['inline_css'])} instancias")
            
            print("")
    
    # Resumen final
    progress = (templates_without_problems / len(template_files)) * 100
    
    print("=" * 65)
    print("📊 RESUMEN CORREGIDO")
    print("=" * 65)
    print(f"📊 Templates analizados: {len(template_files)}")
    print(f"❌ Templates con problemas Bootstrap REALES: {templates_with_problems}")
    print(f"✅ Templates completamente limpios: {templates_without_problems}")
    print(f"📈 Progreso hacia Tailwind puro: {progress:.1f}%")
    print(f"🔢 Total problemas Bootstrap reales: {total_problems}")
    
    if templates_with_problems == 0:
        print("\n🎉 ¡FELICITACIONES! ¡OBJETIVO COMPLETADO!")
        print("🎯 TODOS los templates usan SOLO Tailwind CSS 3.4")
        print("💀 Bootstrap ha sido COMPLETAMENTE eliminado")
    else:
        print(f"\n🎯 Quedan {templates_with_problems} archivos con problemas Bootstrap REALES")
        print("🚀 Estos necesitan limpieza final")
    
    # Guardar reporte detallado
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_templates': len(template_files),
                'templates_with_problems': templates_with_problems,
                'templates_clean': templates_without_problems,
                'progress_percentage': progress,
                'total_problems': total_problems
            },
            'problem_files': problem_files,
            'clean_files': [f['file'] for f in clean_files]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte detallado guardado en: {REPORT_FILE}")

if __name__ == "__main__":
    main()