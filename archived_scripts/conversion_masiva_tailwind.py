#!/usr/bin/env python3
"""
Script para actualizar automáticamente todos los templates para usar solo Tailwind CSS 3.4
"""

import os
import re
from pathlib import Path

def convertir_template_a_tailwind(filepath):
    """Convierte un template HTML para usar únicamente Tailwind CSS"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # 1. Cambiar extends de templates legacy a modernos
        contenido = re.sub(
            r"{% extends ['\"]pos/pos_bootstrap\.html['\"] %}",
            "{% extends 'base/base_modern.html' %}",
            contenido
        )
        
        contenido = re.sub(
            r"{% extends ['\"]base\.html['\"] %}",
            "{% extends 'base/base_modern.html' %}",
            contenido
        )
        
        # 2. Añadir load vite_tags si no existe
        if 'load vite_tags' not in contenido and 'base_modern.html' in contenido:
            contenido = re.sub(
                r'({% load static %})',
                r'\1\n{% load vite_tags %}',
                contenido
            )
        
        # 3. Reemplazar bloques CSS por Javascript block
        contenido = re.sub(
            r'{% block extra_css %}[\s\S]*?{% endblock %}',
            '{% block javascript %}\n    {% vite_asset "src/pos.ts" %}\n{% endblock %}',
            contenido,
            flags=re.MULTILINE
        )
        
        # 4. Convertir clases Bootstrap a Tailwind
        conversiones_clases = {
            # Contenedores
            r'container-fluid': 'w-full px-4',
            r'container(?!-)': 'max-w-7xl mx-auto px-4',
            r'\brow\b': 'flex flex-wrap -mx-2',
            r'col-md-(\d+)': lambda m: f'w-full md:w-{int(m.group(1))/12*100:.0f}% px-2' if int(m.group(1)) <= 12 else f'w-full md:w-{int(m.group(1))*8.33:.0f}% px-2',
            r'col-lg-(\d+)': lambda m: f'w-full lg:w-{int(m.group(1))/12*100:.0f}% px-2',
            r'col-sm-(\d+)': lambda m: f'w-full sm:w-{int(m.group(1))/12*100:.0f}% px-2',
            
            # Botones
            r'btn btn-primary': 'btn btn-primary',
            r'btn btn-secondary': 'btn btn-secondary', 
            r'btn btn-success': 'btn btn-success',
            r'btn btn-danger': 'btn btn-danger',
            r'btn btn-warning': 'btn btn-warning',
            r'btn btn-info': 'btn btn-info',
            r'btn btn-outline-primary': 'btn btn-outline',
            
            # Forms
            r'form-control': 'input',
            r'form-select': 'input',
            r'form-check': 'flex items-center space-x-2',
            r'form-check-input': 'form-checkbox',
            r'form-check-label': 'text-sm text-gray-700',
            r'form-group': 'mb-4',
            r'form-label': 'block text-sm font-medium text-gray-700 mb-2',
            
            # Flexbox
            r'd-flex': 'flex',
            r'justify-content-between': 'justify-between',
            r'justify-content-center': 'justify-center',
            r'align-items-center': 'items-center',
            r'align-items-start': 'items-start',
            
            # Spacing
            r'mb-(\d+)': lambda m: f'mb-{int(m.group(1))*2}',
            r'mt-(\d+)': lambda m: f'mt-{int(m.group(1))*2}',
            r'me-(\d+)': lambda m: f'mr-{int(m.group(1))*2}',
            r'ms-(\d+)': lambda m: f'ml-{int(m.group(1))*2}',
            r'p-(\d+)': lambda m: f'p-{int(m.group(1))*2}',
            
            # Text
            r'text-center': 'text-center',
            r'text-left': 'text-left',
            r'text-right': 'text-right',
            r'text-muted': 'text-gray-500',
            r'text-success': 'text-emerald-600',
            r'text-danger': 'text-red-600',
            r'text-warning': 'text-amber-600',
            r'text-info': 'text-blue-600',
            
            # Background
            r'bg-primary': 'bg-primary-600',
            r'bg-secondary': 'bg-gray-600',
            r'bg-success': 'bg-emerald-600',
            r'bg-danger': 'bg-red-600',
            r'bg-warning': 'bg-amber-600',
            r'bg-info': 'bg-blue-600',
            r'bg-light': 'bg-gray-100',
            r'bg-dark': 'bg-gray-900',
            
            # Cards
            r'card-header': 'card-header',
            r'card-body': 'card-body',
            r'card-footer': 'card-footer',
            
            # Alerts
            r'alert alert-success': 'alert alert-success',
            r'alert alert-danger': 'alert alert-error',
            r'alert alert-warning': 'alert alert-warning',
            r'alert alert-info': 'alert alert-info',
            
            # Borders
            r'border-start': 'border-l',
            r'border-end': 'border-r',
            r'border-top': 'border-t',
            r'border-bottom': 'border-b',
            r'rounded-pill': 'rounded-full',
            
            # Display
            r'd-none': 'hidden',
            r'd-block': 'block',
            r'd-inline': 'inline',
            r'd-inline-block': 'inline-block',
        }
        
        # Aplicar conversiones
        for patron, reemplazo in conversiones_clases.items():
            if callable(reemplazo):
                contenido = re.sub(patron, reemplazo, contenido)
            else:
                contenido = re.sub(patron, reemplazo, contenido)
        
        # 5. Eliminar CSS inline style tags (convertir a clases Tailwind)
        contenido = re.sub(
            r'style\s*=\s*["\'][^"\']*["\']',
            '',
            contenido
        )
        
        # 6. Eliminar referencias Bootstrap CDN
        contenido = re.sub(
            r'<link[^>]*bootstrap[^>]*>',
            '',
            contenido
        )
        
        contenido = re.sub(
            r'<script[^>]*bootstrap[^>]*></script>',
            '',
            contenido
        )
        
        # 7. Actualizar estructura HTML básica
        # Convertir container principal
        contenido = re.sub(
            r'<div class="container(-fluid)?[^"]*">([^<]*<h[1-6][^>]*>)',
            r'<div class="max-w-7xl mx-auto space-y-6">\n    <!-- Header -->\n    <div class="flex items-center justify-between">\2',
            contenido
        )
        
        # Guardar cambios
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(contenido)
            
        return True, f"✅ Convertido: {filepath}"
        
    except Exception as e:
        return False, f"❌ Error en {filepath}: {str(e)}"

def main():
    """Ejecuta la conversión en todos los templates"""
    
    # Directorios a procesar
    template_dirs = [
        Path('frontend/templates/apps'),
        Path('frontend/templates/portal'),
        Path('frontend/templates/dashboard'),
        Path('frontend/templates/pages'),
    ]
    
    resultados = []
    convertidos = 0
    errores = 0
    
    for template_dir in template_dirs:
        if not template_dir.exists():
            continue
            
        for html_file in template_dir.rglob('*.html'):
            # Ignorar archivos de respaldo
            if any(exclude in str(html_file) for exclude in ['backup', '.git', 'cache']):
                continue
                
            exito, mensaje = convertir_template_a_tailwind(html_file)
            resultados.append(mensaje)
            
            if exito:
                convertidos += 1
            else:
                errores += 1
    
    # Mostrar resultados
    print("=" * 80)
    print("🚀 CONVERSIÓN MASIVA A TAILWIND CSS 3.4")
    print("=" * 80)
    print(f"✅ Templates convertidos: {convertidos}")
    print(f"❌ Errores: {errores}")
    print(f"📊 Total procesados: {convertidos + errores}")
    print()
    
    print("📋 DETALLE DE CONVERSIONES:")
    print("-" * 50)
    for resultado in resultados:
        print(resultado)
    
    print()
    print("=" * 80)
    print("🎯 SIGUIENTE: Ejecutar verificacion_templates_tailwind.py para validar")
    print("=" * 80)

if __name__ == "__main__":
    main()