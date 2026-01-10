#!/usr/bin/env python
"""
ANÁLISIS COMPLETO DEL SISTEMA CANTINA POS
Revisa: Base de Datos, Backend Django, Frontend, Funcionalidades implementadas
Fecha: 2026-01-09
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def analizar_estructura_django():
    """Analiza la estructura de Django"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    # Analizar apps instaladas
    gestion_path = proyecto_path / 'gestion'
    
    # Archivos importantes en gestion
    files_gestion = {
        'models.py': 'Modelos ORM',
        'views.py': 'Vistas principales',
        'api_views.py': 'Endpoints REST API',
        'pos_general_views.py': 'Vistas del Sistema POS',
        'admin.py': 'Configuracion Admin',
        'serializers.py': 'Serializadores DRF',
        'urls.py': 'URLs principales',
        'forms.py': 'Formularios Django',
    }
    
    print("\n" + "="*80)
    print("ANALISIS 1: ESTRUCTURA DJANGO")
    print("="*80)
    
    print("\n[ARCHIVOS PRINCIPALES EN GESTION APP]")
    for filename, description in files_gestion.items():
        filepath = gestion_path / filename
        if filepath.exists():
            size = filepath.stat().st_size
            lines = len(filepath.read_text(encoding='utf-8', errors='ignore').split('\n'))
            print(f"  OK | {filename:<30} | {lines:>6} lineas | {size:>8} bytes | {description}")
        else:
            print(f"  -- | {filename:<30} | NO EXISTE")
    
    # Analizar templates
    templates_path = proyecto_path / 'templates'
    if templates_path.exists():
        template_files = list(templates_path.rglob('*.html'))
        print(f"\n[TEMPLATES HTML]")
        print(f"  Total de archivos HTML: {len(template_files)}")
        
        # Contar por subcarpeta
        subfolders = defaultdict(int)
        for tpl in template_files:
            relative = tpl.relative_to(templates_path)
            parent = relative.parts[0] if len(relative.parts) > 1 else 'root'
            subfolders[parent] += 1
        
        for folder, count in sorted(subfolders.items()):
            print(f"    - {folder}: {count} archivos")
    
    # Analizar static files
    static_path = proyecto_path / 'static'
    if static_path.exists():
        css_files = list(static_path.rglob('*.css'))
        js_files = list(static_path.rglob('*.js'))
        print(f"\n[STATIC FILES]")
        print(f"  CSS files: {len(css_files)}")
        print(f"  JS files: {len(js_files)}")
    
    return True


def analizar_funcionalidades():
    """Analiza que funcionalidades estan implementadas"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    print("\n" + "="*80)
    print("ANALISIS 2: FUNCIONALIDADES IMPLEMENTADAS")
    print("="*80)
    
    funcionalidades = {
        'Sistema POS': {
            'file': 'gestion/pos_general_views.py',
            'features': ['Procesar ventas', 'Dashboard POS', 'Restricciones', 'Impresora']
        },
        'Sistema de Almuerzos': {
            'file': 'gestion/almuerzo_views.py',
            'features': ['Planes almuerzo', 'Consumos', 'Cuentas mensuales']
        },
        'Portal Padres': {
            'file': 'gestion/portal_views.py',
            'features': ['Recargas tarjeta', 'Ver consumos', 'Historial']
        },
        'Facturacion Electronica': {
            'file': 'gestion/facturacion_electronica.py',
            'features': ['Timbrado', 'Factura electronica', 'Reportes']
        },
        'Restricciones Dietarias': {
            'file': 'gestion/restricciones_matcher.py',
            'features': ['Validar alergias', 'Bloquear productos', 'Matching']
        },
        'Seguridad': {
            'file': 'gestion/seguridad_utils.py',
            'features': ['2FA', 'Autenticacion', 'Permisos']
        },
        'Reportes': {
            'file': 'gestion/reportes.py',
            'features': ['Reportes PDF', 'Graficos', 'Exportar datos']
        },
    }
    
    print("\n[FUNCIONALIDADES POR MODULO]")
    for modulo, info in funcionalidades.items():
        filepath = proyecto_path / info['file']
        exists = "OK" if filepath.exists() else "NO"
        print(f"\n  {modulo} [{exists}]")
        if filepath.exists():
            lines = len(filepath.read_text(encoding='utf-8', errors='ignore').split('\n'))
            print(f"    Archivo: {info['file']} ({lines} lineas)")
        
        for feature in info['features']:
            print(f"      - {feature}")
    
    return True


def analizar_tecnologia():
    """Analiza tecnologias utilizadas"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    print("\n" + "="*80)
    print("ANALISIS 3: TECNOLOGIAS UTILIZADAS")
    print("="*80)
    
    # Leer requirements.txt
    requirements_file = proyecto_path / 'requirements.txt'
    if requirements_file.exists():
        print("\n[DEPENDENCIAS PRINCIPALES]")
        
        reqs = requirements_file.read_text().split('\n')
        categorias = {
            'Django': ['django', 'djangorestframework'],
            'Database': ['mysqlclient', 'mysql-connector'],
            'Autenticacion': ['simplejwt', 'oauthlib'],
            'Frontend': ['bootstrap', 'jquery'],
            'Reportes': ['reportlab', 'openpyxl'],
            'Pagos': ['stripe', 'paypal'],
            'Email': ['django-anymail'],
            'Testing': ['pytest', 'coverage'],
        }
        
        for categoria, keywords in categorias.items():
            found_reqs = [r for r in reqs if any(k.lower() in r.lower() for k in keywords)]
            if found_reqs:
                print(f"\n  {categoria}:")
                for req in found_reqs:
                    req = req.strip()
                    if req and not req.startswith('#'):
                        print(f"    - {req}")
    
    return True


def analizar_apis():
    """Analiza endpoints de API disponibles"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    print("\n" + "="*80)
    print("ANALISIS 4: ENDPOINTS DE API REST")
    print("="*80)
    
    api_files = {
        'gestion/api_views.py': 'Endpoints principales',
        'gestion/pos_general_views.py': 'Endpoints POS',
        'gestion/portal_api.py': 'API Portal padres',
        'gestion/restricciones_api.py': 'API Restricciones',
    }
    
    print("\n[ARCHIVOS CON ENDPOINTS]")
    for filepath, description in api_files.items():
        full_path = proyecto_path / filepath
        if full_path.exists():
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            
            # Buscar funciones con @
            import re
            patterns = [
                (r'@.*api_view', 'Vistas DRF'),
                (r'@.*route', 'Rutas'),
                (r'def \w+\(', 'Funciones'),
            ]
            
            for pattern, ptype in patterns:
                matches = len(re.findall(pattern, content))
                if matches > 0:
                    print(f"  {filepath}")
                    print(f"    - {matches} {ptype} encontradas")


def analizar_tests():
    """Analiza tests existentes"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    print("\n" + "="*80)
    print("ANALISIS 5: TESTS Y COVERAGE")
    print("="*80)
    
    test_files = list(proyecto_path.glob('test_*.py'))
    print(f"\n[TEST SUITES]")
    print(f"  Total de archivos de test: {len(test_files)}")
    
    # Categorizar por tipo
    categories = {
        'API': [t for t in test_files if 'api' in t.name],
        'Modelos': [t for t in test_files if 'model' in t.name],
        'Modulos': [t for t in test_files if 'modulo' in t.name],
        'Funcionalidad': [t for t in test_files if 'funcional' in t.name or 'completo' in t.name],
        'Otros': []
    }
    
    # Asignar "Otros"
    used = set()
    for tests in categories.values():
        if tests != categories['Otros']:
            used.update(tests)
    categories['Otros'] = [t for t in test_files if t not in used]
    
    for cat, tests in categories.items():
        if tests:
            print(f"\n  {cat} ({len(tests)} archivos):")
            for test in tests[:5]:  # Mostrar hasta 5
                print(f"    - {test.name}")
            if len(tests) > 5:
                print(f"    ... y {len(tests) - 5} mas")


def analizar_documentacion():
    """Analiza documentacion disponible"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    print("\n" + "="*80)
    print("ANALISIS 6: DOCUMENTACION")
    print("="*80)
    
    doc_patterns = ['*.md', '*.txt', '*.rst']
    doc_files = []
    for pattern in doc_patterns:
        doc_files.extend(proyecto_path.glob(pattern))
    
    # Categorizar
    categories = {
        'Guias': [d for d in doc_files if 'GUIA' in d.name.upper()],
        'Resumen': [d for d in doc_files if 'RESUMEN' in d.name.upper()],
        'Analisis': [d for d in doc_files if 'ANALISIS' in d.name.upper()],
        'Implementacion': [d for d in doc_files if 'IMPLEMENTACION' in d.name.upper() or 'COMPLETADO' in d.name.upper()],
        'Otro': []
    }
    
    # Asignar "Otro"
    used = set()
    for docs in categories.values():
        if docs != categories['Otro']:
            used.update(docs)
    categories['Otro'] = [d for d in doc_files if d not in used]
    
    print("\n[DOCUMENTACION DISPONIBLE]")
    total_docs = 0
    for cat, docs in categories.items():
        if docs:
            print(f"\n  {cat} ({len(docs)}):")
            total_docs += len(docs)
            for doc in docs[:3]:  # Mostrar hasta 3
                print(f"    - {doc.name}")
            if len(docs) > 3:
                print(f"    ... y {len(docs) - 3} mas")
    
    print(f"\n  TOTAL DE DOCUMENTOS: {total_docs}")


def analizar_problemas_potenciales():
    """Identifica problemas potenciales"""
    proyecto_path = Path('D:/anteproyecto20112025')
    
    print("\n" + "="*80)
    print("ANALISIS 7: POSIBLES MEJORAS Y AREAS CRITICAS")
    print("="*80)
    
    problemas = {
        'Performance': [
            'Revisar indices en BD (120 tablas pueden ser lentas)',
            'Implementar caching Redis',
            'Optimizar queries N+1',
        ],
        'Seguridad': [
            'Implementar rate limiting en APIs',
            'Validar CORS en produccion',
            'Revisar CSRF protection en formularios',
        ],
        'Escalabilidad': [
            'Separar BD en replica (lectura/escritura)',
            'Implementar API gateway',
            'Agregar message queue (Celery)',
        ],
        'Calidad de Codigo': [
            'Aumentar cobertura de tests',
            'Implementar type hints en models',
            'Refactorizar vistas grandes',
        ],
        'Monitoreo': [
            'Implementar logging centralizado',
            'Agregar health checks',
            'Monitoreo de errores (Sentry)',
        ],
    }
    
    print("\n[AREAS DE MEJORA]")
    for area, items in problemas.items():
        print(f"\n  {area}:")
        for item in items:
            print(f"    - {item}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("ANALISIS COMPLETO DEL SISTEMA CANTINA POS")
    print("="*80)
    
    try:
        analizar_estructura_django()
        analizar_funcionalidades()
        analizar_tecnologia()
        analizar_apis()
        analizar_tests()
        analizar_documentacion()
        analizar_problemas_potenciales()
        
        print("\n" + "="*80)
        print("ANALISIS COMPLETADO EXITOSAMENTE")
        print("="*80)
        
    except Exception as e:
        print(f"\nError durante analisis: {e}")
        import traceback
        traceback.print_exc()
