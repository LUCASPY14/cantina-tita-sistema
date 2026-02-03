"""
Template tags para integración con Vite
"""
import json
import os
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def vite_asset(entry_name):
    """
    Renderiza las etiquetas <script> y <link> para un entry point de Vite
    """
    if settings.DEBUG:
        # En desarrollo, usar servidor de Vite
        vite_dev_server = getattr(settings, 'VITE_DEV_SERVER', 'http://localhost:3000')
        
        if entry_name.endswith('.css'):
            return mark_safe(f'<link rel="stylesheet" href="{vite_dev_server}/{entry_name}">')
        else:
            return mark_safe(f'<script type="module" src="{vite_dev_server}/{entry_name}"></script>')
    
    else:
        # En producción, usar manifest
        manifest_path = os.path.join(settings.STATIC_ROOT or '', 'manifest.json')
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            if entry_name in manifest:
                file_path = manifest[entry_name]['file']
                static_url = settings.STATIC_URL
                
                if entry_name.endswith('.css'):
                    return mark_safe(f'<link rel="stylesheet" href="{static_url}{file_path}">')
                else:
                    return mark_safe(f'<script type="module" src="{static_url}{file_path}"></script>')
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
    
    return ''

@register.simple_tag
def vite_hmr():
    """
    Incluye el script de HMR de Vite en desarrollo
    """
    if settings.DEBUG:
        vite_dev_server = getattr(settings, 'VITE_DEV_SERVER', 'http://localhost:3000')
        return mark_safe(f'<script type="module" src="{vite_dev_server}/@vite/client"></script>')
    return ''

@register.simple_tag
def vite_preload_module(entry_name):
    """
    Precargar módulos para mejor performance
    """
    if not settings.DEBUG:
        manifest_path = os.path.join(settings.STATIC_ROOT or '', 'manifest.json')
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            if entry_name in manifest:
                imports = manifest[entry_name].get('imports', [])
                static_url = settings.STATIC_URL
                preloads = []
                
                for imp in imports:
                    if imp in manifest:
                        file_path = manifest[imp]['file']
                        preloads.append(f'<link rel="modulepreload" href="{static_url}{file_path}">')
                
                return mark_safe(''.join(preloads))
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
    
    return ''