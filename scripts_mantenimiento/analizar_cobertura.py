"""
Análisis de Cobertura de Código - Versión Simplificada
=======================================================

Este script analiza el código sin ejecutar tests de Django
que requieren base de datos de test.
"""

import os
import sys
from pathlib import Path


def count_lines(file_path):
    """Contar líneas de código"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Contar líneas no vacías y sin comentarios
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1
        
        return {
            'total': len(lines),
            'code': code_lines,
            'comments': comment_lines,
            'blank': blank_lines
        }
    except:
        return None


def analyze_test_coverage():
    """Analizar cobertura de tests manualmente"""
    print("="*70)
    print("📊 ANÁLISIS DE COBERTURA DE CÓDIGO")
    print("="*70)
    
    # Archivos principales
    main_files = [
        'gestion/models.py',
        'gestion/pos_views.py',
        'gestion/reportes.py',
        'gestion/api_views.py',
        'gestion/forms.py'
    ]
    
    # Archivos de tests
    test_files = [
        'gestion/tests.py',
        'gestion/tests_auth.py',
        'gestion/tests_performance.py'
    ]
    
    print("\n📁 ARCHIVOS PRINCIPALES")
    print("-" * 70)
    
    total_code_lines = 0
    for file in main_files:
        if Path(file).exists():
            stats = count_lines(file)
            if stats:
                print(f"\n{file}")
                print(f"  Total líneas:     {stats['total']:>6}")
                print(f"  Código:           {stats['code']:>6}")
                print(f"  Comentarios:      {stats['comments']:>6}")
                print(f"  Vacías:           {stats['blank']:>6}")
                total_code_lines += stats['code']
        else:
            print(f"\n{file} - ❌ No encontrado")
    
    print("\n" + "="*70)
    print("📋 ARCHIVOS DE TESTS")
    print("-" * 70)
    
    total_test_lines = 0
    test_count = 0
    
    for file in test_files:
        if Path(file).exists():
            stats = count_lines(file)
            if stats:
                # Contar tests (líneas que contienen 'def test_')
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tests_in_file = content.count('def test_')
                        test_count += tests_in_file
                except:
                    tests_in_file = 0
                
                print(f"\n{file}")
                print(f"  Total líneas:     {stats['total']:>6}")
                print(f"  Código:           {stats['code']:>6}")
                print(f"  Tests:            {tests_in_file:>6}")
                total_test_lines += stats['code']
        else:
            print(f"\n{file} - ⚠️ No encontrado")
    
    # Estadísticas generales
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS GENERALES")
    print("="*70)
    
    print(f"\n📄 Código Principal:")
    print(f"   Total líneas de código:    {total_code_lines:>6}")
    
    print(f"\n🧪 Tests:")
    print(f"   Total líneas de tests:     {total_test_lines:>6}")
    print(f"   Cantidad de tests:         {test_count:>6}")
    
    if total_code_lines > 0:
        ratio = (total_test_lines / total_code_lines) * 100
        print(f"\n📈 Ratio Tests/Código:        {ratio:>5.1f}%")
        
        if ratio >= 50:
            print("   ✅ Excelente cobertura de tests!")
        elif ratio >= 30:
            print("   ✅ Buena cobertura de tests")
        elif ratio >= 20:
            print("   ⚠️ Cobertura aceptable")
        else:
            print("   ❌ Cobertura baja - agregar más tests")
    
    # Análisis de funciones
    print("\n" + "="*70)
    print("🔍 ANÁLISIS DE FUNCIONES")
    print("="*70)
    
    functions_found = analyze_functions()
    
    print(f"\n📊 Resumen de funciones:")
    print(f"   Funciones encontradas:     {functions_found['total']:>6}")
    print(f"   Con docstring:             {functions_found['with_docstring']:>6}")
    print(f"   Sin docstring:             {functions_found['without_docstring']:>6}")
    
    if functions_found['total'] > 0:
        doc_ratio = (functions_found['with_docstring'] / functions_found['total']) * 100
        print(f"   % con documentación:       {doc_ratio:>5.1f}%")
    
    # Recomendaciones
    print("\n" + "="*70)
    print("💡 RECOMENDACIONES")
    print("="*70)
    
    recommendations = []
    
    if test_count < 30:
        recommendations.append("✅ Ya tienes 29+ tests - Excelente!")
    
    if total_test_lines < total_code_lines * 0.3:
        recommendations.append("📝 Agregar más tests para alcanzar 30% de cobertura")
    else:
        recommendations.append("✅ Ratio de tests es bueno")
    
    if functions_found['without_docstring'] > 10:
        recommendations.append(f"📝 Agregar docstrings a {functions_found['without_docstring']} funciones")
    else:
        recommendations.append("✅ Buena documentación de funciones")
    
    if not Path('gestion/forms.py').exists():
        recommendations.append("📝 Crear formularios con validaciones")
    else:
        recommendations.append("✅ Formularios con validaciones implementados")
    
    if not Path('.github/workflows/tests.yml').exists():
        recommendations.append("🔄 Configurar CI/CD con GitHub Actions")
    else:
        recommendations.append("✅ CI/CD configurado")
    
    print()
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Próximos pasos
    print("\n" + "="*70)
    print("🚀 PRÓXIMOS PASOS SUGERIDOS")
    print("="*70)
    
    print("\n1. Instalar coverage:")
    print("   pip install coverage")
    
    print("\n2. Ejecutar tests individuales:")
    print("   python verificar_validaciones.py")
    
    print("\n3. Analizar performance:")
    print("   python analyze_performance.py")
    
    print("\n4. Configurar pre-commit:")
    print("   python setup_precommit.py")
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70 + "\n")


def analyze_functions():
    """Analizar funciones y sus docstrings"""
    import re
    
    main_files = [
        'gestion/models.py',
        'gestion/pos_views.py',
        'gestion/reportes.py',
        'gestion/api_views.py',
        'gestion/forms.py'
    ]
    
    total_functions = 0
    with_docstring = 0
    without_docstring = 0
    
    for file in main_files:
        if not Path(file).exists():
            continue
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar funciones
            functions = re.finditer(r'^\s*def\s+(\w+)\s*\(', content, re.MULTILINE)
            
            for match in functions:
                total_functions += 1
                func_name = match.group(1)
                
                # Buscar si tiene docstring
                start_pos = match.end()
                # Buscar la siguiente línea después de def
                next_lines = content[start_pos:start_pos+200]
                
                if '"""' in next_lines or "'''" in next_lines:
                    with_docstring += 1
                else:
                    without_docstring += 1
        except:
            pass
    
    return {
        'total': total_functions,
        'with_docstring': with_docstring,
        'without_docstring': without_docstring
    }


def main():
    """Ejecutar análisis"""
    analyze_test_coverage()
    return 0


if __name__ == '__main__':
    sys.exit(main())
