#!/usr/bin/env python
"""
Auditoría detallada del contenido de templates
Analiza características UX implementadas en cada archivo
"""
import re
from pathlib import Path
from collections import defaultdict

def analizar_template(file_path):
    """Analiza un template y retorna sus características"""
    try:
        content = file_path.read_text(encoding='utf-8')
    except:
        return None
    
    # Detectar template base
    extends_match = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}', content)
    extends = extends_match.group(1) if extends_match else None
    
    caracteristicas = {
        'extends': extends,
        'lineas': len(content.split('\n')),
        'size_kb': len(content) / 1024,
        
        # Framework y librerías
        'alpine_js': bool(re.search(r'x-data|x-show|x-if|x-for|x-model|@click|@submit', content)),
        'tailwind': bool(re.search(r'class="[^"]*(?:flex|grid|bg-|text-|p-|m-|w-|h-)', content)),
        'daisyui': bool(re.search(r'class="[^"]*(?:btn|card|modal|alert|badge|drawer)', content)),
        
        # Componentes UX
        'loading_states': bool(re.search(r':disabled|loading\s*=|spinner|:class.*loading', content, re.IGNORECASE)),
        'skeleton': bool(re.search(r'skeleton|animate-pulse', content, re.IGNORECASE)),
        'notifications': bool(re.search(r'notification|toast|alert|notify', content, re.IGNORECASE)),
        'modals': bool(re.search(r'modal|dialog|x-show.*modal', content, re.IGNORECASE)),
        
        # Formularios
        'tiene_form': bool(re.search(r'<form', content)),
        'validacion_tiempo_real': bool(re.search(r'@input|@blur|@change.*valid|x-model.*valid', content)),
        'csrf_token': bool(re.search(r'csrf_token', content)),
        
        # Interactividad
        'event_listeners': len(re.findall(r'@\w+|addEventListener', content)),
        'componentes_alpine': len(re.findall(r'x-data\s*=\s*["\'{]', content)),
        
        # Accesibilidad
        'aria_labels': bool(re.search(r'aria-\w+', content)),
        'role_attributes': bool(re.search(r'role\s*=', content)),
        'alt_texts': bool(re.search(r'alt\s*=', content)),
        
        # Responsive
        'responsive_classes': bool(re.search(r'sm:|md:|lg:|xl:|2xl:', content)),
        
        # Búsqueda y filtros
        'search': bool(re.search(r'search|buscar|filtrar', content, re.IGNORECASE)),
        'pagination': bool(re.search(r'pagination|page|siguiente|anterior', content, re.IGNORECASE)),
        
        # API/AJAX
        'fetch_api': bool(re.search(r'fetch\(|axios|ajax', content, re.IGNORECASE)),
        
        # Tablas y listas
        'tables': len(re.findall(r'<table', content)),
        'cards': len(re.findall(r'class="[^"]*card', content)),
    }
    
    return caracteristicas

def generar_reporte():
    """Genera reporte completo de auditoría"""
    base_path = Path('frontend/templates')
    
    print("=" * 100)
    print("🔍 AUDITORÍA DETALLADA DE CONTENIDO - TEMPLATES")
    print("=" * 100)
    print()
    
    # Analizar todos los templates
    templates_data = {}
    for html_file in sorted(base_path.rglob('*.html')):
        rel_path = str(html_file.relative_to(base_path))
        data = analizar_template(html_file)
        if data:
            templates_data[rel_path] = data
    
    # Agrupar por categoría
    categorias = defaultdict(list)
    for path, data in templates_data.items():
        if '/' in path:
            categoria = path.split('/')[0]
        else:
            categoria = 'base'
        categorias[categoria].append((path, data))
    
    # 1. RESUMEN DE TEMPLATES BASE
    print("📌 ANÁLISIS DE TEMPLATES BASE")
    print("-" * 100)
    print()
    
    bases = ['base.html', 'base_pos.html', 'base_gestion.html']
    for base in bases:
        if base in templates_data:
            data = templates_data[base]
            print(f"  {base}")
            print(f"    Líneas: {data['lineas']}")
            print(f"    Tamaño: {data['size_kb']:.1f} KB")
            print(f"    ✓ Alpine.js: {'✅' if data['alpine_js'] else '❌'}")
            print(f"    ✓ Tailwind: {'✅' if data['tailwind'] else '❌'}")
            print(f"    ✓ DaisyUI: {'✅' if data['daisyui'] else '❌'}")
            print(f"    ✓ Notificaciones: {'✅' if data['notifications'] else '❌'}")
            print(f"    ✓ Loading States: {'✅' if data['loading_states'] else '❌'}")
            print()
    
    # 2. ANÁLISIS POR CATEGORÍA
    print("=" * 100)
    print("📂 ANÁLISIS POR CATEGORÍA")
    print("=" * 100)
    print()
    
    orden = ['auth', 'pos', 'portal', 'gestion']
    
    for cat in orden:
        if cat not in categorias:
            continue
        
        templates = categorias[cat]
        print(f"\n{'='*100}")
        print(f"📁 {cat.upper()} ({len(templates)} templates)")
        print(f"{'='*100}\n")
        
        # Estadísticas de la categoría
        stats = {
            'con_alpine': sum(1 for _, d in templates if d['alpine_js']),
            'con_tailwind': sum(1 for _, d in templates if d['tailwind']),
            'con_loading': sum(1 for _, d in templates if d['loading_states']),
            'con_validacion': sum(1 for _, d in templates if d['validacion_tiempo_real']),
            'con_notifications': sum(1 for _, d in templates if d['notifications']),
            'con_modal': sum(1 for _, d in templates if d['modals']),
            'con_aria': sum(1 for _, d in templates if d['aria_labels']),
            'responsive': sum(1 for _, d in templates if d['responsive_classes']),
        }
        
        print("  📊 Estadísticas de la categoría:")
        print(f"    Alpine.js:        {stats['con_alpine']:2d}/{len(templates)} ({stats['con_alpine']/len(templates)*100:.0f}%)")
        print(f"    Tailwind CSS:     {stats['con_tailwind']:2d}/{len(templates)} ({stats['con_tailwind']/len(templates)*100:.0f}%)")
        print(f"    Loading States:   {stats['con_loading']:2d}/{len(templates)} ({stats['con_loading']/len(templates)*100:.0f}%)")
        print(f"    Validación:       {stats['con_validacion']:2d}/{len(templates)} ({stats['con_validacion']/len(templates)*100:.0f}%)")
        print(f"    Notificaciones:   {stats['con_notifications']:2d}/{len(templates)} ({stats['con_notifications']/len(templates)*100:.0f}%)")
        print(f"    Modals:           {stats['con_modal']:2d}/{len(templates)} ({stats['con_modal']/len(templates)*100:.0f}%)")
        print(f"    ARIA Labels:      {stats['con_aria']:2d}/{len(templates)} ({stats['con_aria']/len(templates)*100:.0f}%)")
        print(f"    Responsive:       {stats['responsive']:2d}/{len(templates)} ({stats['responsive']/len(templates)*100:.0f}%)")
        print()
        
        # Detalle de cada template
        print("  📄 Detalle de templates:")
        print()
        for path, data in sorted(templates):
            filename = Path(path).name
            extends = data['extends'] if data['extends'] else 'ninguno'
            
            # Calcular score UX (0-10)
            ux_score = sum([
                data['alpine_js'] * 1,
                data['tailwind'] * 1,
                data['loading_states'] * 1.5,
                data['notifications'] * 1,
                data['validacion_tiempo_real'] * 1.5,
                data['aria_labels'] * 1,
                data['responsive_classes'] * 1,
                data['modals'] * 0.5,
                data['skeleton'] * 1.5,
            ])
            ux_score = min(10, ux_score)
            
            # Clasificación
            if ux_score >= 8:
                clasificacion = "🟢 EXCELENTE"
            elif ux_score >= 6:
                clasificacion = "🟡 BUENO"
            elif ux_score >= 4:
                clasificacion = "🟠 MEJORAR"
            else:
                clasificacion = "🔴 CRÍTICO"
            
            print(f"    {filename}")
            print(f"      📊 Score UX: {ux_score:.1f}/10 {clasificacion}")
            print(f"      📁 Extiende: {extends}")
            print(f"      📏 {data['lineas']} líneas ({data['size_kb']:.1f} KB)")
            
            # Características presentes
            features = []
            if data['alpine_js']: features.append('Alpine')
            if data['tailwind']: features.append('Tailwind')
            if data['daisyui']: features.append('DaisyUI')
            if data['loading_states']: features.append('Loading')
            if data['notifications']: features.append('Notif')
            if data['validacion_tiempo_real']: features.append('Validación')
            if data['skeleton']: features.append('Skeleton')
            if data['modals']: features.append('Modal')
            if data['aria_labels']: features.append('ARIA')
            if data['responsive_classes']: features.append('Responsive')
            
            if features:
                print(f"      ✓ {', '.join(features)}")
            
            # Características faltantes importantes
            missing = []
            if not data['alpine_js']: missing.append('Alpine.js')
            if not data['tailwind']: missing.append('Tailwind')
            if data['tiene_form'] and not data['validacion_tiempo_real']: missing.append('Validación')
            if not data['loading_states']: missing.append('Loading states')
            if not data['responsive_classes']: missing.append('Responsive')
            
            if missing:
                print(f"      ✗ Falta: {', '.join(missing)}")
            
            print()
    
    # 3. RESUMEN GENERAL
    print("\n" + "=" * 100)
    print("📊 RESUMEN GENERAL DEL PROYECTO")
    print("=" * 100)
    print()
    
    total = len(templates_data)
    
    general_stats = {
        'Alpine.js': sum(1 for d in templates_data.values() if d['alpine_js']),
        'Tailwind': sum(1 for d in templates_data.values() if d['tailwind']),
        'DaisyUI': sum(1 for d in templates_data.values() if d['daisyui']),
        'Loading States': sum(1 for d in templates_data.values() if d['loading_states']),
        'Skeleton Loaders': sum(1 for d in templates_data.values() if d['skeleton']),
        'Notificaciones': sum(1 for d in templates_data.values() if d['notifications']),
        'Validación': sum(1 for d in templates_data.values() if d['validacion_tiempo_real']),
        'Modals': sum(1 for d in templates_data.values() if d['modals']),
        'ARIA Labels': sum(1 for d in templates_data.values() if d['aria_labels']),
        'Responsive': sum(1 for d in templates_data.values() if d['responsive_classes']),
    }
    
    print(f"  Total de templates analizados: {total}")
    print()
    print("  Características UX implementadas:")
    print()
    
    for feature, count in sorted(general_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        bar_length = int(percentage / 2)
        bar = '█' * bar_length + '░' * (50 - bar_length)
        print(f"    {feature:20s} │ {bar} │ {count:2d}/{total} ({percentage:5.1f}%)")
    
    print()
    
    # 4. PRIORIDADES DE MEJORA
    print("=" * 100)
    print("🎯 PRIORIDADES DE MEJORA")
    print("=" * 100)
    print()
    
    # Templates críticos con bajo score
    criticos = []
    for path, data in templates_data.items():
        if 'pos/' in path or 'portal/dashboard' in path or 'auth/login' in path:
            ux_score = sum([
                data['alpine_js'] * 1,
                data['tailwind'] * 1,
                data['loading_states'] * 1.5,
                data['notifications'] * 1,
                data['validacion_tiempo_real'] * 1.5,
                data['aria_labels'] * 1,
                data['responsive_classes'] * 1,
            ])
            if ux_score < 6:
                criticos.append((path, ux_score))
    
    if criticos:
        print("  🚨 Templates críticos que necesitan mejora urgente:")
        print()
        for path, score in sorted(criticos, key=lambda x: x[1]):
            print(f"    • {path} (Score: {score:.1f}/10)")
        print()
    
    # Templates base a arreglar
    print("  🔧 Templates base a actualizar:")
    print()
    for base in bases:
        if base in templates_data:
            data = templates_data[base]
            issues = []
            if not data['alpine_js']: issues.append('Alpine.js')
            if not data['tailwind']: issues.append('Tailwind')
            if not data['daisyui']: issues.append('DaisyUI')
            if not data['notifications']: issues.append('Notificaciones')
            if not data['loading_states']: issues.append('Loading states')
            
            if issues:
                print(f"    • {base}: Falta {', '.join(issues)}")
    
    print()
    print("=" * 100)
    print("✅ Auditoría completada")
    print("=" * 100)

if __name__ == '__main__':
    generar_reporte()
