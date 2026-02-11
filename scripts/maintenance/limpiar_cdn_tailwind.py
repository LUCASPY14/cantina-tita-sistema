#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar TODOS los CDN de Tailwind CSS
Reemplaza con configuración Vite moderna
"""

import os
import re
from pathlib import Path

# Configuración
TEMPLATES_DIR = Path("frontend/templates")

def clean_tailwind_cdn(file_path: Path) -> bool:
    """Elimina CDN de Tailwind y añade configuración Vite si es necesario"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Eliminar CDN de Tailwind
        tailwind_cdn_patterns = [
            r'<script src="https://cdn\.tailwindcss\.com"></script>',
            r'<script src="https://cdn\.tailwindcss\.com"></script>\n',
            r'\n\s*<script src="https://cdn\.tailwindcss\.com"></script>',
            r'<script src="https://cdn\.tailwindcss\.com"></script>\s*\n',
        ]
        
        for pattern in tailwind_cdn_patterns:
            old_content = content
            content = re.sub(pattern, '', content)
            if content != old_content:
                changes_made = True
        
        # Verificar si tiene {% load vite_tags %}
        if '{% load vite_tags %}' not in content and '{% extends' in content:
            # Añadir load vite_tags después del extends
            content = re.sub(
                r'({%\s*extends[^%]*%})',
                r'\1\n{% load vite_tags %}',
                content,
                count=1
            )
            changes_made = True
        
        # Verificar si tiene assets Vite en el block javascript/head
        if 'vite_asset' not in content and 'block javascript' in content:
            # Añadir Vite asset en el bloque javascript
            vite_block = '''{% block javascript %}
    {% vite_asset "src/pos.ts" %}
    {{ block.super }}
{% endblock %}'''
            
            # Si no hay bloque javascript, añadirlo
            if '{% block javascript %}' not in content:
                # Buscar después del title block
                title_block_pattern = r'({%\s*block\s+title\s*%}[^{]*{%\s*endblock\s*%})'
                if re.search(title_block_pattern, content):
                    content = re.sub(
                        title_block_pattern,
                        r'\1\n\n' + vite_block,
                        content,
                        count=1
                    )
                    changes_made = True
        
        # Limpiar líneas vacías excesivas
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Guardar si hubo cambios
        if changes_made and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🧹 ELIMINANDO CDN de Tailwind CSS de TODOS los templates")
    print("=" * 60)
    
    # Buscar archivos HTML (excluyendo backups)
    all_html_files = list(TEMPLATES_DIR.rglob("*.html"))
    template_files = [f for f in all_html_files if 'backup' not in str(f).lower()]
    
    print(f"📁 Procesando {len(template_files)} archivos HTML...")
    print()
    
    files_cleaned = 0
    files_with_cdn = []
    
    # Procesar cada archivo
    for file_path in template_files:
        # Verificar si tiene CDN de Tailwind
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'cdn.tailwindcss.com' in content:
                files_with_cdn.append(file_path)
                if clean_tailwind_cdn(file_path):
                    files_cleaned += 1
                    print(f"✅ Limpiado: {file_path.relative_to(TEMPLATES_DIR)}")
                else:
                    print(f"⚠️  Sin cambios: {file_path.relative_to(TEMPLATES_DIR)}")
        except Exception as e:
            print(f"❌ Error: {file_path.relative_to(TEMPLATES_DIR)} - {e}")
    
    # Resumen
    print()
    print("=" * 60)
    print("📊 RESUMEN DE LIMPIEZA")
    print("=" * 60)
    print(f"🔍 Archivos con CDN encontrados: {len(files_with_cdn)}")
    print(f"✅ Archivos limpiados exitosamente: {files_cleaned}")
    print(f"📄 Total archivos procesados: {len(template_files)}")
    
    if files_cleaned > 0:
        print()
        print("🎉 ¡CDN de Tailwind eliminado exitosamente!")
        print("🎯 Todos los templates ahora usan Tailwind local via Vite")
        print()
        print("🔧 Archivos limpiados:")
        for file_path in files_with_cdn:
            print(f"   • {file_path.relative_to(TEMPLATES_DIR)}")
    else:
        print()
        print("✨ No se encontraron CDN de Tailwind para limpiar")
    
    print()
    print("🚀 PRÓXIMO PASO: Verificar que todo funcione correctamente")

if __name__ == "__main__":
    main()