#!/usr/bin/env python3
"""
Script para verificar que todos los templates HTML estén usando solo Tailwind CSS 3.4
y no tengan dependencias de Bootstrap u otros frameworks CSS.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def analizar_template(filepath):
    """Analiza un template HTML buscando clases y referencias CSS problemáticas."""
    
    # Patrones Bootstrap a detectar
    bootstrap_patterns = [
        r'container-fluid|container(?!-[a-z])|row|col-(?:xs|sm|md|lg|xl)',
        r'btn\s+btn-(?!ghost|primary|secondary|accent|info|success|warning|error)', # Bootstrap btn classes
        r'form-(?:control|group|check|select)',
        r'd-(?:flex|none|block|inline|grid)',
        r'text-(?:left|right|center|justify|muted|success|danger|warning|info)(?!-[0-9])', # Bootstrap text utils
        r'bg-(?:primary|secondary|success|danger|warning|info|light|dark)(?!-[0-9])', # Bootstrap bg colors
        r'(?:me|ms|pe|ps|pt|pb|mt|mb)-[0-9]', # Bootstrap spacing
        r'justify-content-(?:start|end|center|between|around)',
        r'align-items-(?:start|end|center|baseline|stretch)',
        r'border-(?:start|end|top|bottom)(?!\-[a-z])',
        r'rounded-pill',
        r'list-group',
        r'badge\s+bg-',
        r'card-(?:header|body|footer)',
        r'alert\s+alert-',
        r'modal\s+fade',
        r'data-bs-'
    ]
    
    # Patrones de CSS inline a evitar
    css_inline_patterns = [
        r'style\s*=\s*["\'][^"\']*["\']'
    ]
    
    # CDN links problemáticos
    cdn_patterns = [
        r'bootstrap',
        r'cdn\.jsdelivr.*bootstrap',
        r'stackpath.*bootstrap',
        r'maxcdn.*bootstrap'
    ]
    
    problemas = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Verificar extends base correcto
        if re.search(r"extends\s+['\"](?:base\.html|pos_bootstrap\.html)['\"]", contenido):
            problemas.append("❌ Extiende de template base legacy")
            
        # Verificar patrones Bootstrap
        for pattern in bootstrap_patterns:
            matches = re.findall(pattern, contenido, re.IGNORECASE)
            if matches:
                problemas.append(f"🔵 Bootstrap classes: {', '.join(set(matches))}")
        
        # Verificar CSS inline
        for pattern in css_inline_patterns:
            matches = re.findall(pattern, contenido, re.IGNORECASE)
            if matches:
                problemas.append(f"🎨 CSS inline encontrado: {len(matches)} ocurrencias")
        
        # Verificar CDN links
        for pattern in cdn_patterns:
            if re.search(pattern, contenido, re.IGNORECASE):
                problemas.append("🌐 CDN Bootstrap/legacy detectado")
                
        # Verificar si usa Tailwind correctamente
        tailwind_classes = re.findall(r'class\s*=\s*["\'][^"\']*(?:bg-|text-|p-|m-|flex|grid|w-|h-)[^"\']*["\']', contenido)
        usa_tailwind = len(tailwind_classes) > 0
        
        return {
            'problemas': problemas,
            'usa_tailwind': usa_tailwind,
            'total_problemas': len(problemas)
        }
        
    except Exception as e:
        return {
            'problemas': [f"❌ Error al leer archivo: {str(e)}"],
            'usa_tailwind': False,
            'total_problemas': 1
        }

def main():
    """Ejecuta la verificación en todos los templates."""
    
    # Directorios a revisar
    template_dirs = [
        Path('frontend/templates'),
    ]
    
    resultados = {}
    total_templates = 0
    templates_problematicos = 0
    
    for template_dir in template_dirs:
        if not template_dir.exists():
            print(f"⚠️  Directorio no encontrado: {template_dir}")
            continue
            
        for html_file in template_dir.rglob('*.html'):
            # Ignorar archivos de respaldo
            if any(exclude in str(html_file) for exclude in ['backup', 'cache', '.git']):
                continue
                
            total_templates += 1
            rel_path = str(html_file.relative_to('.'))
            
            resultado = analizar_template(html_file)
            
            if resultado['total_problemas'] > 0:
                templates_problematicos += 1
                resultados[rel_path] = resultado
    
    # Generar reporte
    print("=" * 80)
    print("🎯 VERIFICACIÓN TAILWIND CSS 3.4 - REPORTE COMPLETO")
    print("=" * 80)
    print(f"📊 Templates analizados: {total_templates}")
    print(f"❌ Templates con problemas: {templates_problematicos}")
    print(f"✅ Templates sin problemas: {total_templates - templates_problematicos}")
    print(f"📈 Progreso: {((total_templates - templates_problematicos) / total_templates * 100):.1f}%")
    print()
    
    if resultados:
        print("📋 TEMPLATES QUE NECESITAN ACTUALIZACIÓN:")
        print("-" * 50)
        
        # Agrupar por tipo de problema
        por_categoria = defaultdict(list)
        
        for template, resultado in sorted(resultados.items()):
            print(f"\n📁 {template}")
            for problema in resultado['problemas']:
                print(f"  {problema}")
                categoria = problema.split()[0]
                por_categoria[categoria].append(template)
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN POR CATEGORÍA:")
        print("-" * 50)
        
        for categoria, templates in por_categoria.items():
            print(f"{categoria} {len(templates)} templates")
        
        print("\n" + "=" * 50)
        print("🎯 PRIORIDADES DE ACTUALIZACIÓN:")
        print("-" * 50)
        
        print("1️⃣ CRÍTICO - Templates con Bootstrap:")
        for template in sorted(resultados.keys()):
            if any('Bootstrap' in p for p in resultados[template]['problemas']):
                print(f"   • {template}")
                
        print("\n2️⃣ IMPORTANTE - Templates con CSS inline:")
        for template in sorted(resultados.keys()):
            if any('CSS inline' in p for p in resultados[template]['problemas']):
                print(f"   • {template}")
                
        print("\n3️⃣ REVISAR - Templates con base legacy:")
        for template in sorted(resultados.keys()):
            if any('base legacy' in p for p in resultados[template]['problemas']):
                print(f"   • {template}")
                
    else:
        print("🎉 ¡EXCELENTE! Todos los templates están usando Tailwind CSS correctamente.")
        
    print("\n" + "=" * 80)
    print("🚀 PRÓXIMOS PASOS:")
    print("1. Actualizar templates críticos con Bootstrap")
    print("2. Convertir CSS inline a clases Tailwind")  
    print("3. Migrar extends a base_modern.html")
    print("4. Verificar funcionalidad tras cada cambio")
    print("=" * 80)
    
    # Generar reporte JSON
    with open('reporte_tailwind.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_templates': total_templates,
            'templates_problematicos': templates_problematicos,
            'porcentaje_completo': (total_templates - templates_problematicos) / total_templates * 100,
            'problemas_detallados': resultados
        }, f, indent=2, ensure_ascii=False)
        
    print(f"📄 Reporte detallado guardado en: reporte_tailwind.json")

if __name__ == "__main__":
    main()