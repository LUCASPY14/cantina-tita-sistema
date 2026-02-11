#!/usr/bin/env python
"""
Script para verificar todas las rutas y URLs después de las modificaciones
"""

import os
import re
import json
from pathlib import Path

def obtener_urls_django():
    """Analiza todos los archivos urls.py"""
    urls_encontradas = []
    
    # URLs principales
    archivos_urls = [
        'config/urls.py',
        'backend/apps/pos/urls.py', 
        'backend/apps/gestion/urls.py',
        'backend/apps/auth/urls.py',
        'backend/apps/portal/urls.py'
    ]
    
    for archivo in archivos_urls:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                # Buscar patterns de URL
                patterns = re.findall(r"path\(['\"]([^'\"]*)['\"]", contenido)
                urls_encontradas.extend([
                    {'archivo': archivo, 'pattern': pattern, 'tipo': 'django_url'}
                    for pattern in patterns
                ])
            except Exception as e:
                print(f"⚠️  Error leyendo {archivo}: {e}")
    
    return urls_encontradas

def obtener_rutas_templates():
    """Analiza rutas en templates HTML"""
    rutas_templates = []
    
    templates_dir = Path('frontend/templates')
    if not templates_dir.exists():
        return rutas_templates
    
    for html_file in templates_dir.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            # Buscar diferentes tipos de rutas
            patterns_buscar = [
                (r"{% url ['\"]([^'\"]*)['\"]", 'django_url_tag'),
                (r"action=['\"]([^'\"]*)['\"]", 'form_action'),
                (r"href=['\"]([^'\"]*)['\"]", 'link_href'),
                (r"src=['\"]([^'\"]*)['\"]", 'resource_src'),
                (r"{% load static %}", 'static_load'),
                (r"{% static ['\"]([^'\"]*)['\"]", 'static_file'),
                (r"{% vite_asset ['\"]([^'\"]*)['\"]", 'vite_asset')
            ]
            
            for pattern, tipo in patterns_buscar:
                matches = re.findall(pattern, contenido)
                for match in matches:
                    rutas_templates.append({
                        'archivo': str(html_file),
                        'ruta': match if isinstance(match, str) else match,
                        'tipo': tipo
                    })
                    
        except Exception as e:
            print(f"⚠️  Error leyendo {html_file}: {e}")
    
    return rutas_templates

def verificar_archivos_estaticos():
    """Verifica archivos estáticos y su configuración"""
    estaticos = {
        'django_static': [],
        'vite_assets': [],
        'missing': []
    }
    
    # Django staticfiles
    static_dirs = [
        'staticfiles',
        'frontend/static',
        'backend/static'
    ]
    
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    ruta_completa = os.path.join(root, file)
                    ruta_relativa = os.path.relpath(ruta_completa, static_dir)
                    estaticos['django_static'].append(ruta_relativa)
    
    # Vite assets
    vite_manifest = 'frontend/dist/.vite/manifest.json'
    if os.path.exists(vite_manifest):
        try:
            with open(vite_manifest, 'r') as f:
                manifest = json.load(f)
                estaticos['vite_assets'] = list(manifest.keys())
        except Exception as e:
            print(f"⚠️  Error leyendo manifest Vite: {e}")
    
    return estaticos

def verificar_configuracion_urls():
    """Verifica configuración de URLs en settings"""
    config_urls = {}
    
    settings_files = [
        'config/settings/base.py',
        'config/settings.py'
    ]
    
    for settings_file in settings_files:
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                # Buscar configuraciones relevantes
                configs = {
                    'STATIC_URL': re.search(r"STATIC_URL\s*=\s*['\"]([^'\"]*)['\"]", contenido),
                    'MEDIA_URL': re.search(r"MEDIA_URL\s*=\s*['\"]([^'\"]*)['\"]", contenido),
                    'LOGIN_URL': re.search(r"LOGIN_URL\s*=\s*['\"]([^'\"]*)['\"]", contenido),
                    'LOGIN_REDIRECT_URL': re.search(r"LOGIN_REDIRECT_URL\s*=\s*['\"]([^'\"]*)['\"]", contenido),
                }
                
                for key, match in configs.items():
                    if match:
                        config_urls[key] = match.group(1)
                        
            except Exception as e:
                print(f"⚠️  Error leyendo {settings_file}: {e}")
    
    return config_urls

def detectar_rutas_rotas():
    """Detecta posibles rutas rotas o inconsistencias"""
    problemas = []
    
    # Obtener todas las rutas
    urls_django = obtener_urls_django()
    rutas_templates = obtener_rutas_templates()
    
    # URLs definidas en Django
    urls_definidas = set()
    for url in urls_django:
        if url['pattern'] and not url['pattern'].startswith('<'):
            urls_definidas.add(url['pattern'].strip('/'))
    
    # URLs usadas en templates
    urls_usadas = set()
    for ruta in rutas_templates:
        if ruta['tipo'] == 'django_url_tag':
            urls_usadas.add(ruta['ruta'])
    
    # Buscar URLs usadas pero no definidas
    for url_usada in urls_usadas:
        if url_usada not in urls_definidas:
            # Verificar si existe con variaciones comunes
            variaciones = [
                url_usada,
                url_usada + '/',
                url_usada.rstrip('/'),
                url_usada.replace('_', '-'),
                url_usada.replace('-', '_')
            ]
            
            if not any(var in urls_definidas for var in variaciones):
                problemas.append({
                    'tipo': 'url_no_definida',
                    'url': url_usada,
                    'mensaje': f'URL "{url_usada}" usada en templates pero no definida en urls.py'
                })
    
    # Buscar archivos estáticos referenciados pero inexistentes
    archivos_estaticos = verificar_archivos_estaticos()
    static_files = set(archivos_estaticos['django_static'])
    
    for ruta in rutas_templates:
        if ruta['tipo'] == 'static_file':
            archivo_static = ruta['ruta']
            if archivo_static not in static_files:
                problemas.append({
                    'tipo': 'archivo_static_missing',
                    'archivo': archivo_static,
                    'template': ruta['archivo'],
                    'mensaje': f'Archivo estático "{archivo_static}" no encontrado'
                })
    
    return problemas

def generar_reporte():
    """Genera reporte completo de rutas y URLs"""
    print("🔍 VERIFICACIÓN INTEGRAL DE RUTAS Y URLs")
    print("=" * 60)
    
    # URLs Django
    print("\n📋 URLs DEFINIDAS EN DJANGO:")
    urls_django = obtener_urls_django()
    for url in urls_django[:10]:  # Mostrar primeras 10
        print(f"  • {url['pattern']} ({url['archivo']})")
    if len(urls_django) > 10:
        print(f"  ... y {len(urls_django) - 10} más")
    
    # Configuración URLs
    print("\n⚙️  CONFIGURACIÓN DE URLs:")
    config = verificar_configuracion_urls()
    for key, value in config.items():
        print(f"  • {key}: {value}")
    
    # Archivos estáticos
    print("\n📁 ARCHIVOS ESTÁTICOS:")
    estaticos = verificar_archivos_estaticos()
    print(f"  • Django static files: {len(estaticos['django_static'])}")
    print(f"  • Vite assets: {len(estaticos['vite_assets'])}")
    
    # Problemas detectados
    print("\n🚨 PROBLEMAS DETECTADOS:")
    problemas = detectar_rutas_rotas()
    
    if not problemas:
        print("  ✅ No se detectaron problemas críticos")
    else:
        for problema in problemas:
            print(f"  ❌ {problema['mensaje']}")
            if 'template' in problema:
                print(f"      └─ En: {problema['template']}")
    
    # Resumen rutas en templates
    print("\n📝 RESUMEN RUTAS EN TEMPLATES:")
    rutas_templates = obtener_rutas_templates()
    tipos_rutas = {}
    for ruta in rutas_templates:
        tipo = ruta['tipo']
        tipos_rutas[tipo] = tipos_rutas.get(tipo, 0) + 1
    
    for tipo, cantidad in sorted(tipos_rutas.items()):
        print(f"  • {tipo}: {cantidad}")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    
    if len(problemas) > 0:
        print("  🔧 Corregir URLs y archivos faltantes detectados")
    
    # Verificar si Vite está configurado
    if not os.path.exists('frontend/dist/.vite/manifest.json'):
        print("  🏗️  Ejecutar 'npm run build' para generar assets de Vite")
    
    # Verificar templates base
    templates_base = [
        'frontend/templates/base/base.html',
        'frontend/templates/base/pos_base.html',
        'frontend/templates/base/portal_base.html'
    ]
    
    for template in templates_base:
        if not os.path.exists(template):
            print(f"  📄 Template base faltante: {template}")
    
    print("\n" + "=" * 60)
    print(f"📊 ESTADÍSTICAS:")
    print(f"  • URLs Django: {len(urls_django)}")
    print(f"  • Rutas en templates: {len(rutas_templates)}")
    print(f"  • Archivos estáticos: {len(estaticos['django_static'])}")
    print(f"  • Problemas encontrados: {len(problemas)}")

if __name__ == "__main__":
    if not os.path.exists("frontend/templates"):
        print("❌ Error: No se encuentra la carpeta frontend/templates")
        print("   Ejecuta este script desde la raíz del proyecto Django")
        exit(1)
    
    generar_reporte()