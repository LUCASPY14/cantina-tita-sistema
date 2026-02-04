#!/usr/bin/env python
"""
Análisis detallado de templates y reorganización de estructura
"""
import os
import re
from pathlib import Path
from collections import defaultdict


def analyze_template_inheritance_detailed():
    """Análisis detallado de herencia de templates"""
    template_map = {}
    inheritance_tree = defaultdict(list)
    
    template_dirs = [
        'templates',
        'pos/templates',
        'gestion/templates'
    ]
    
    print("🔍 ANÁLISIS DETALLADO DE HERENCIA")
    print("=" * 50)
    
    # Mapear todos los templates
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        filepath = os.path.join(root, file)
                        relative_path = filepath.replace('\\', '/').replace(template_dir + '/', '')
                        template_map[relative_path] = filepath
    
    # Analizar herencia
    for relative_path, full_path in template_map.items():
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar {% extends %}
            extends_match = re.search(r'{%\s*extends\s+[\'"]([^\'"]+)[\'"]\s*%}', content)
            if extends_match:
                parent_template = extends_match.group(1)
                inheritance_tree[parent_template].append(relative_path)
                print(f"  {relative_path} → extends → {parent_template}")
        except:
            continue
    
    print(f"\n🌳 ÁRBOL DE HERENCIA")
    print("=" * 30)
    
    # Mostrar árbol de herencia
    def show_tree(template, level=0):
        indent = "  " * level
        print(f"{indent}📄 {template}")
        if template in inheritance_tree:
            for child in sorted(inheritance_tree[template]):
                show_tree(child, level + 1)
    
    # Encontrar templates raíz (no extienden de otros)
    all_children = set()
    for children in inheritance_tree.values():
        all_children.update(children)
    
    root_templates = set(inheritance_tree.keys()) - all_children
    
    for root in sorted(root_templates):
        show_tree(root)
        print()


def check_templates_in_views():
    """Busca más detalladamente el uso de templates en código Python"""
    template_usage = defaultdict(list)
    
    print("🔍 BÚSQUEDA DETALLADA DE USO EN CÓDIGO")
    print("=" * 50)
    
    # Buscar en todos los archivos Python
    for root, dirs, files in os.walk('.'):
        # Ignorar directorios
        dirs[:] = [d for d in dirs if d not in ['.venv', 'node_modules', '__pycache__', 'migrations', 'htmlcov']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Patrones más extensos
                    patterns = [
                        r"render\([^,)]+,\s*['\"]([^'\"]+\.html)['\"]",
                        r"render_to_response\(['\"]([^'\"]+\.html)['\"]",
                        r"template_name\s*=\s*['\"]([^'\"]+\.html)['\"]",
                        r"TemplateResponse\([^,)]+,\s*['\"]([^'\"]+\.html)['\"]",
                        r"get_template\(['\"]([^'\"]+\.html)['\"]",
                        r"select_template\(\[[^]]*['\"]([^'\"]+\.html)['\"]",
                        r"\.html['\"][^'\"]*['\"]([^'\"]+\.html)['\"]"  # Referencias en cadenas
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                        for match in matches:
                            # Limpiar el match
                            match = match.strip()
                            if match and not match.startswith('{{'):  # Excluir variables Django
                                template_usage[match].append(f"{filepath}:{content.count(chr(10), 0, content.find(match)) + 1}")
                
                except:
                    continue
    
    return template_usage


def check_specific_templates():
    """Verifica específicamente los templates que parecen no usados"""
    potentially_unused = [
        'base.html',
        'portal/base_portal.html', 
        'pos/base_pos.html',
        'gestion/base.html',
        'emails/recordatorio_deuda_amable.html',
        'emails/recordatorio_deuda_critico.html',
        'emails/recordatorio_deuda_urgente.html',
        'emails/tarjeta_bloqueada.html'
    ]
    
    print("🔍 VERIFICACIÓN ESPECÍFICA DE TEMPLATES")
    print("=" * 50)
    
    for template in potentially_unused:
        print(f"\n📄 Verificando: {template}")
        
        # Buscar referencias directas
        found_refs = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ['.venv', 'node_modules', '__pycache__', 'migrations']]
            
            for file in files:
                if file.endswith(('.py', '.html')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if template in content:
                            # Encontrar línea específica
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if template in line:
                                    found_refs.append(f"  {filepath}:{i+1} → {line.strip()[:80]}...")
                                    break
                    except:
                        continue
        
        if found_refs:
            print(f"  ✅ Template en uso:")
            for ref in found_refs[:5]:  # Mostrar máximo 5 referencias
                print(ref)
            if len(found_refs) > 5:
                print(f"    ... y {len(found_refs) - 5} referencias más")
        else:
            print(f"  ❌ No se encontraron referencias")


def reorganize_templates_structure():
    """Propone una reorganización de la estructura de templates"""
    print("💡 PROPUESTA DE REORGANIZACIÓN")
    print("=" * 50)
    
    current_structure = {
        'templates/': [],
        'pos/templates/': [],
        'gestion/templates/': []
    }
    
    # Mapear estructura actual
    for template_dir in current_structure.keys():
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        filepath = os.path.join(root, file)
                        relative = filepath.replace(template_dir, '').replace('\\', '/')
                        current_structure[template_dir].append(relative)
    
    print("📊 ESTRUCTURA ACTUAL:")
    for dir_name, templates in current_structure.items():
        print(f"\n{dir_name} ({len(templates)} templates)")
        for template in sorted(templates)[:5]:
            print(f"  - {template}")
        if len(templates) > 5:
            print(f"  ... y {len(templates) - 5} más")
    
    print(f"\n💡 RECOMENDACIONES:")
    print("1. Consolidar templates base en /templates/")
    print("2. Mover templates compartidos a /templates/shared/")
    print("3. Mantener templates específicos de app en sus respectivas carpetas")
    print("4. Crear estructura consistente: /templates/app_name/feature/")


def main():
    print("📋 ANÁLISIS COMPLETO DE TEMPLATES")
    print("=" * 60)
    
    os.chdir('D:/anteproyecto20112025')
    
    # Análisis de herencia
    analyze_template_inheritance_detailed()
    
    # Búsqueda detallada de uso
    template_usage = check_templates_in_views()
    
    print(f"📊 TEMPLATES ENCONTRADOS EN CÓDIGO: {len(template_usage)}")
    
    # Verificación específica
    check_specific_templates()
    
    # Propuesta de reorganización
    reorganize_templates_structure()
    
    print(f"\n✨ ANÁLISIS COMPLETADO")


if __name__ == "__main__":
    main()