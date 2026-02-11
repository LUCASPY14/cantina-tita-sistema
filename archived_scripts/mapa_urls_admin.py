"""
Script para generar un mapa de URLs del admin correctas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib import admin
from django.apps import apps

print("=" * 80)
print("MAPA DE URLs DEL ADMIN - SISTEMA CANTINA TITA".center(80))
print("=" * 80 + "\n")

# Obtener todos los modelos registrados en el admin
admin_site = admin.site

gestion_models = []

for model, model_admin in admin_site._registry.items():
    if model._meta.app_label == 'gestion':
        # Obtener la URL del modelo
        model_name = model._meta.model_name
        url = f"/admin/gestion/{model_name}/"
        verbose_name = model._meta.verbose_name
        verbose_name_plural = model._meta.verbose_name_plural
        
        gestion_models.append({
            'model': model.__name__,
            'url': url,
            'verbose_name': verbose_name,
            'verbose_name_plural': verbose_name_plural
        })

# Ordenar alfabéticamente
gestion_models.sort(key=lambda x: x['model'])

print(f"Total de modelos en Gestión: {len(gestion_models)}\n")
print("MODELO".ljust(30) + "URL".ljust(40) + "NOMBRE")
print("-" * 80)

for item in gestion_models:
    print(f"{item['model'][:29].ljust(30)}{item['url'][:39].ljust(40)}{item['verbose_name']}")

print("\n" + "=" * 80)
print("\n📝 URLs IMPORTANTES:\n")

important = [
    ('Ventas', 'ventas'),
    ('Cliente', 'cliente'),
    ('Producto', 'producto'),
    ('Tarjeta', 'tarjeta'),
    ('CargasSaldo', 'cargassaldo'),
    ('Empleado', 'empleado'),
]

for model_name, url_name in important:
    url = f"http://127.0.0.1:8000/admin/gestion/{url_name}/"
    print(f"  • {model_name}: {url}")

print("\n" + "=" * 80)
