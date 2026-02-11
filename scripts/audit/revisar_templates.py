#!/usr/bin/env python
"""
Script para hacer una revisión exhaustiva de todos los templates
"""
import os
from pathlib import Path
from collections import defaultdict

def analizar_templates():
    base_path = Path('frontend/templates')
    
    # Estructura para organizar templates
    estructura = defaultdict(list)
    templates_vacios = []
    templates_con_contenido = []
    
    print("=" * 80)
    print("REVISIÓN EXHAUSTIVA DE TEMPLATES - Cantina Tita")
    print("=" * 80)
    print()
    
    # Recolectar todos los templates
    for html_file in sorted(base_path.rglob('*.html')):
        rel_path = html_file.relative_to(base_path)
        size = html_file.stat().st_size
        
        # Categorizar por directorio principal
        if len(rel_path.parts) > 1:
            categoria = rel_path.parts[0]
        else:
            categoria = 'base'
        
        estructura[categoria].append({
            'path': str(rel_path),
            'size': size,
            'full_path': str(html_file)
        })
        
        if size == 0:
            templates_vacios.append(str(rel_path))
        else:
            templates_con_contenido.append(str(rel_path))
    
    # Mostrar resumen general
    print("📊 RESUMEN GENERAL")
    print("-" * 80)
    print(f"Total de templates: {len(templates_con_contenido) + len(templates_vacios)}")
    print(f"  ✅ Con contenido: {len(templates_con_contenido)}")
    print(f"  ⚠️  Vacíos: {len(templates_vacios)}")
    print()
    
    # Mostrar por categoría
    print("📁 ESTRUCTURA POR CATEGORÍA")
    print("-" * 80)
    print()
    
    categorias_orden = ['base', 'auth', 'pos', 'portal', 'gestion']
    
    for categoria in categorias_orden:
        if categoria not in estructura:
            continue
            
        templates = estructura[categoria]
        print(f"{'=' * 80}")
        print(f"📂 {categoria.upper()} ({len(templates)} archivos)")
        print(f"{'=' * 80}")
        
        # Agrupar por subcategoría si existe
        subcategorias = defaultdict(list)
        archivos_raiz = []
        
        for t in templates:
            parts = Path(t['path']).parts
            if len(parts) == 1:
                archivos_raiz.append(t)
            elif len(parts) == 2:
                subcategorias[parts[0]].append(t)
            else:
                subcategorias[f"{parts[0]}/{parts[1]}"].append(t)
        
        # Mostrar archivos raíz
        if archivos_raiz:
            for t in archivos_raiz:
                size_kb = t['size'] / 1024
                status = "✅" if t['size'] > 0 else "⚠️ "
                print(f"  {status} {t['path']:<50} ({size_kb:>6.1f} KB)")
        
        # Mostrar por subcategoría
        for subcat in sorted(subcategorias.keys()):
            print(f"\n  📁 {subcat}/")
            for t in subcategorias[subcat]:
                size_kb = t['size'] / 1024
                status = "✅" if t['size'] > 0 else "⚠️ "
                filename = Path(t['path']).name
                print(f"    {status} {filename:<45} ({size_kb:>6.1f} KB)")
        
        print()
    
    # Templates vacíos que requieren atención
    if templates_vacios:
        print("=" * 80)
        print("⚠️  TEMPLATES VACÍOS (Requieren implementación)")
        print("=" * 80)
        for t in templates_vacios:
            print(f"  • {t}")
        print()
    
    # Análisis de contenido básico
    print("=" * 80)
    print("🔍 ANÁLISIS DE CONTENIDO")
    print("=" * 80)
    
    # Verificar templates base
    print("\n📌 Templates Base:")
    base_templates = ['base.html', 'base_pos.html', 'base_gestion.html']
    for bt in base_templates:
        path = base_path / bt
        if path.exists():
            size = path.stat().st_size / 1024
            print(f"  ✅ {bt:<25} ({size:>6.1f} KB)")
            
            # Verificar componentes clave
            content = path.read_text(encoding='utf-8')
            checks = {
                'Alpine.js': 'alpine' in content.lower() or 'x-data' in content,
                'Tailwind': 'tailwind' in content.lower(),
                'DaisyUI': 'daisyui' in content.lower() or 'daisy' in content.lower(),
                'Notificaciones': 'notification' in content.lower() or 'toast' in content.lower(),
            }
            for check, resultado in checks.items():
                icon = "✓" if resultado else "✗"
                print(f"     {icon} {check}")
        else:
            print(f"  ❌ {bt} - NO EXISTE")
    
    # Verificar templates críticos por módulo
    print("\n📌 Templates Críticos por Módulo:")
    
    criticos = {
        'POS': [
            'pos/venta.html',
            'pos/dashboard.html',
            'pos/cierre_caja.html',
        ],
        'Portal Padres': [
            'portal/dashboard.html',
            'portal/mis_hijos.html',
            'portal/recargar_tarjeta.html',
        ],
        'Gestión': [
            'gestion/dashboard.html',
            'gestion/productos/lista.html',
            'gestion/clientes/lista.html',
            'gestion/ventas/lista.html',
        ],
        'Auth': [
            'auth/login.html',
            'auth/registro.html',
        ]
    }
    
    for modulo, templates in criticos.items():
        print(f"\n  {modulo}:")
        for t in templates:
            path = base_path / t
            if path.exists():
                size = path.stat().st_size / 1024
                status = "✅" if size > 0 else "⚠️ "
                print(f"    {status} {t:<40} ({size:>6.1f} KB)")
            else:
                print(f"    ❌ {t:<40} - NO EXISTE")
    
    print("\n" + "=" * 80)
    print("✅ Revisión completada")
    print("=" * 80)

if __name__ == '__main__':
    analizar_templates()
