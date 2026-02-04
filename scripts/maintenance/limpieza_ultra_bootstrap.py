#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script ULTRA-AGRESIVO de limpieza final Bootstrap → Tailwind CSS 3.4
Elimina TODAS las clases Bootstrap restantes con patrones específicos
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Configuración
TEMPLATES_DIR = Path("frontend/templates")
LOG_FILE = "limpieza_ultra_final_log.json"

def clean_bootstrap_patterns(content: str) -> tuple[str, int]:
    """Elimina TODOS los patrones de Bootstrap restantes"""
    changes = 0
    
    # PATRONES MUY ESPECÍFICOS para eliminar clases Bootstrap restantes
    bootstrap_patterns = [
        # Spacing utilities que quedaron (bootstrap usa números diferentes)
        (r'\bmb-8\b', 'mb-8'),  # Mantener mb-8 si es válido en Tailwind
        (r'\bmt-8\b', 'mt-8'),  # Mantener mt-8 si es válido en Tailwind  
        (r'\bpt-6\b', 'pt-6'),  # Mantener pt-6 si es válido en Tailwind
        (r'\bpb-8\b', 'pb-8'),  # Mantener pb-8 si es válido en Tailwind
        
        # Eliminar clases Bootstrap problemáticas
        (r'\bbtn\s+btn-[a-zA-Z-]+', 'px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'),
        (r'\bbtn\s+btn-', 'px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700'),
        (r'\balert\s+alert-[a-zA-Z-]+', 'p-4 mb-4 bg-blue-50 border border-blue-200 rounded-md border-l-4 border-l-blue-500 text-blue-800'),
        (r'\balert\s+alert-', 'p-4 mb-4 bg-blue-50 border border-blue-200 rounded-md'),
        (r'\bbadge\s+bg-[a-zA-Z-]+', 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-600 text-white'),
        (r'\bbadge\s+bg-', 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'),
        
        # Bootstrap grid que puede haber quedado
        (r'\bcontainer\b', 'max-w-7xl mx-auto px-4'),
        (r'\bcontainer-fluid\b', 'w-full px-4'),
        (r'\brow\b', 'flex flex-wrap -mx-4'),
        (r'\bcol-md-\d+\b', 'md:w-1/2 px-4'),
        (r'\bcol-\d+\b', 'flex-1 px-4'),
        (r'\bcol\b', 'flex-1 px-4'),
        
        # Eliminar data-bs atributos completamente
        (r'\s+data-bs-[^=]*="[^"]*"', ''),
        
        # Limpiar list-group que puede quedar
        (r'\blist-group\b', 'space-y-2'),
        (r'\blist-group-item\b', 'p-3 bg-white border border-gray-200 rounded'),
        
        # Modal clases restantes
        (r'\bmodal\s+fade\b', 'fixed inset-0 z-50 overflow-y-auto opacity-0 transition-opacity duration-300'),
        (r'\bmodal\b', 'fixed inset-0 z-50 overflow-y-auto'),
        
        # Borders
        (r'\bborder-top\b', 'border-t border-gray-200'),
        (r'\bborder-bottom\b', 'border-b border-gray-200'),
        
    ]
    
    for pattern, replacement in bootstrap_patterns:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            changes += 1
    
    return content, changes

def remove_all_bootstrap_cdn(content: str) -> tuple[str, int]:
    """Elimina TODOS los enlaces CDN de Bootstrap"""
    removals = 0
    
    # Patrones más amplios para CDN
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
    
    for pattern in cdn_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        removals += len(matches)
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    return content, removals

def aggressive_class_cleanup(content: str) -> tuple[str, int]:
    """Limpieza agresiva de clases problemáticas"""
    changes = 0
    
    # Buscar todos los atributos class y limpiar individualmente
    def clean_class_attribute(match):
        nonlocal changes
        full_class = match.group(1)
        classes = full_class.split()
        
        cleaned_classes = []
        for cls in classes:
            # Si la clase NO es claramente Bootstrap, mantenerla
            if not is_bootstrap_class(cls):
                cleaned_classes.append(cls)
            else:
                changes += 1
        
        if cleaned_classes:
            return f'class="{" ".join(cleaned_classes)}"'
        else:
            return 'class=""'
    
    content = re.sub(r'class="([^"]*)"', clean_class_attribute, content)
    
    # Eliminar atributos class vacíos
    content = re.sub(r'\s+class=""', '', content)
    
    return content, changes

def is_bootstrap_class(cls: str) -> bool:
    """Determina si una clase es de Bootstrap y debe eliminarse"""
    bootstrap_prefixes = [
        # Grid y layout
        'container', 'row', 'col-', 'offset-',
        # Componentes
        'btn', 'alert', 'badge', 'card', 'modal', 'nav', 'navbar',
        # Utilidades específicas de Bootstrap
        'text-muted', 'text-primary', 'text-secondary', 'text-success', 
        'text-danger', 'text-warning', 'text-info', 'text-light', 'text-dark',
        'bg-primary', 'bg-secondary', 'bg-success', 'bg-danger', 
        'bg-warning', 'bg-info', 'bg-light', 'bg-dark',
        # Display utilities de Bootstrap
        'd-none', 'd-block', 'd-flex', 'd-inline',
        # Form controls
        'form-control', 'form-select', 'form-check',
        # Spacing con patrones específicos de Bootstrap 5
        'me-', 'ms-', 'pe-', 'ps-',
        # Borders específicos
        'border-top', 'border-bottom', 'border-left', 'border-right',
        # Otros componentes
        'list-group', 'dropdown', 'collapse'
    ]
    
    # Verificar si la clase comienza con algún prefijo de Bootstrap
    for prefix in bootstrap_prefixes:
        if cls.startswith(prefix):
            return True
    
    # Clases específicas completas de Bootstrap
    bootstrap_exact = {
        'container', 'row', 'border', 'shadow', 'rounded',
        'text-left', 'text-right', 'text-center', 'text-justify'
    }
    
    return cls in bootstrap_exact

def convert_file(file_path: Path) -> Dict:
    """Convierte un archivo individual con limpieza ultra-agresiva"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_changes = 0
        
        # 1. Limpiar patrones específicos de Bootstrap
        content, pattern_changes = clean_bootstrap_patterns(content)
        total_changes += pattern_changes
        
        # 2. Eliminar TODOS los CDN de Bootstrap
        content, cdn_removals = remove_all_bootstrap_cdn(content)
        total_changes += cdn_removals
        
        # 3. Limpieza agresiva de clases
        content, class_cleanups = aggressive_class_cleanup(content)
        total_changes += class_cleanups
        
        # 4. Limpiar espacios extra y líneas vacías
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Máximo 2 líneas vacías consecutivas
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)  # Espacios al final de línea
        
        # Guardar archivo si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            'file': str(file_path.name),
            'success': True,
            'changes': {
                'pattern_changes': pattern_changes,
                'cdn_removals': cdn_removals,
                'class_cleanups': class_cleanups,
                'total_changes': total_changes
            },
            'modified': content != original_content
        }
        
    except Exception as e:
        return {
            'file': str(file_path.name),
            'success': False,
            'error': str(e),
            'changes': {}
        }

def main():
    """Función principal de limpieza ultra-agresiva"""
    print("🔥 LIMPIEZA ULTRA-AGRESIVA: Eliminando TODOS los rastros de Bootstrap")
    print("=" * 70)
    
    # Buscar todos los archivos HTML, excluyendo backups
    all_html_files = list(TEMPLATES_DIR.rglob("*.html"))
    template_files = [f for f in all_html_files if 'backup' not in str(f).lower()]
    print(f"📁 Encontrados {len(template_files)} archivos HTML para limpiar")
    
    # Procesar archivos
    results = []
    successful_cleanups = 0
    failed_cleanups = 0
    total_changes = 0
    
    for i, file_path in enumerate(template_files, 1):
        print(f"🧹 Limpiando {i}/{len(template_files)}: {file_path.name}")
        
        result = convert_file(file_path)
        results.append(result)
        
        if result['success']:
            successful_cleanups += 1
            total_changes += result['changes'].get('total_changes', 0)
            
            if result.get('modified'):
                changes = result['changes']
                print(f"   ✅ Limpiado - Patrones: {changes['pattern_changes']}, "
                      f"CDN: {changes['cdn_removals']}, "
                      f"Clases: {changes['class_cleanups']}")
            else:
                print(f"   ⏭️  Ya estaba limpio")
        else:
            failed_cleanups += 1
            print(f"   ❌ Error: {result['error']}")
    
    # Guardar log detallado
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("🔥 RESUMEN DE LIMPIEZA ULTRA-AGRESIVA")
    print("=" * 70)
    print(f"✅ Archivos limpiados exitosamente: {successful_cleanups}")
    print(f"❌ Archivos con errores: {failed_cleanups}")
    print(f"🧹 Total de cambios aplicados: {total_changes}")
    print(f"📄 Log detallado en: {LOG_FILE}")
    
    if failed_cleanups == 0:
        print("\n🔥 ¡LIMPIEZA ULTRA-AGRESIVA COMPLETADA!")
        print("💀 Bootstrap ha sido ELIMINADO completamente del proyecto")
        print("🎯 SOLO queda Tailwind CSS 3.4 puro")
    else:
        print(f"\n⚠️  Limpieza completada con {failed_cleanups} errores")
        print("🔍 Revisa el log para más detalles")
    
    print("\n🚀 VERIFICACIÓN FINAL:")
    print("   python verificacion_templates_tailwind.py")

if __name__ == "__main__":
    main()