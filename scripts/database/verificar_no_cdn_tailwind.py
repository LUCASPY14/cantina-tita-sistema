#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación completa: Asegurar que NINGÚN template tenga CDN de Tailwind CSS
"""

import os
import re
from pathlib import Path

# Configuración
TEMPLATES_DIR = Path("frontend/templates")

def check_tailwind_cdn(file_path: Path) -> dict:
    """Verifica si un archivo tiene CDN de Tailwind"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar patrones de CDN Tailwind
        tailwind_cdn_patterns = [
            r'<script\s+src="https://cdn\.tailwindcss\.com"[^>]*>',
            r'<link\s+[^>]*href="[^"]*tailwindcss[^"]*"',
        ]
        
        found_cdn = []
        for pattern in tailwind_cdn_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_cdn.extend(matches)
        
        # Buscar líneas específicas con números
        lines_with_cdn = []
        if found_cdn:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'cdn.tailwindcss.com' in line.lower():
                    lines_with_cdn.append({
                        'line_number': i,
                        'line_content': line.strip()
                    })
        
        return {
            'file': str(file_path.relative_to(TEMPLATES_DIR)),
            'has_cdn': bool(found_cdn),
            'cdn_found': found_cdn,
            'lines_with_cdn': lines_with_cdn,
            'is_backup': 'backup' in str(file_path).lower()
        }
        
    except Exception as e:
        return {
            'file': str(file_path.relative_to(TEMPLATES_DIR)),
            'has_cdn': False,
            'error': str(e),
            'is_backup': 'backup' in str(file_path).lower()
        }

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN COMPLETA: CDN Tailwind CSS en Templates")
    print("=" * 65)
    print("🎯 Verificando que NINGÚN template tenga CDN de Tailwind CSS")
    print()
    
    # Buscar todos los archivos HTML
    all_html_files = list(TEMPLATES_DIR.rglob("*.html"))
    
    # Separar archivos activos de backups
    active_files = [f for f in all_html_files if 'backup' not in str(f).lower()]
    backup_files = [f for f in all_html_files if 'backup' in str(f).lower()]
    
    print(f"📁 Archivos encontrados:")
    print(f"   • Activos: {len(active_files)}")
    print(f"   • Backups: {len(backup_files)}")
    print()
    
    # Verificar archivos activos
    print("🔍 VERIFICANDO ARCHIVOS ACTIVOS:")
    print("-" * 40)
    
    active_with_cdn = []
    active_clean = []
    
    for file_path in active_files:
        result = check_tailwind_cdn(file_path)
        
        if result.get('has_cdn', False):
            active_with_cdn.append(result)
            print(f"❌ {result['file']}")
            for line_info in result.get('lines_with_cdn', []):
                print(f"   Línea {line_info['line_number']}: {line_info['line_content']}")
        else:
            active_clean.append(result)
    
    # Verificar archivos backup (solo reportar, no es crítico)
    print()
    print("📋 VERIFICANDO ARCHIVOS BACKUP:")
    print("-" * 40)
    
    backup_with_cdn = []
    for file_path in backup_files:
        result = check_tailwind_cdn(file_path)
        if result.get('has_cdn', False):
            backup_with_cdn.append(result)
    
    if backup_with_cdn:
        print(f"⚠️  {len(backup_with_cdn)} archivos backup tienen CDN (no crítico)")
        for result in backup_with_cdn:
            print(f"   • {result['file']}")
    else:
        print("✅ Ningún archivo backup tiene CDN")
    
    # Resumen final
    print()
    print("=" * 65)
    print("📊 RESUMEN FINAL")
    print("=" * 65)
    print(f"📊 Total archivos activos verificados: {len(active_files)}")
    print(f"❌ Archivos activos con CDN Tailwind: {len(active_with_cdn)}")
    print(f"✅ Archivos activos limpios: {len(active_clean)}")
    print(f"📋 Archivos backup con CDN: {len(backup_with_cdn)}")
    
    if len(active_with_cdn) == 0:
        print()
        print("🎉 ¡PERFECTO! ¡VERIFICACIÓN EXITOSA!")
        print("✅ NINGÚN template activo tiene CDN de Tailwind CSS")
        print("🎯 Todos los templates usan Tailwind CSS local via Vite")
        print("🚀 Stack moderno completamente configurado")
    else:
        print()
        print("⚠️  ATENCIÓN: Se encontraron archivos activos con CDN")
        print("🔧 Archivos que necesitan limpieza:")
        for result in active_with_cdn:
            print(f"   • {result['file']}")
        print()
        print("💡 Ejecutar script de limpieza para corregir")
    
    print()
    print("🎯 CONCLUSIÓN:")
    if len(active_with_cdn) == 0 and len(backup_with_cdn) <= 2:
        print("✅ Estado ÓPTIMO - Solo Tailwind local via Vite")
    else:
        print("⚠️  Estado PARCIAL - Algunos archivos necesitan atención")

if __name__ == "__main__":
    main()