"""
Script para eliminar ventas ficticias (solo almuerzos) de la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Ventas

# Eliminar ventas ficticias que tienen ALMUERZOS en motivo_credito
ventas_ficticias = Ventas.objects.filter(
    motivo_credito__icontains='ALMUERZOS',
    tipo_venta='CREDITO'
)

count = ventas_ficticias.count()
print(f'Encontradas {count} ventas ficticias')

if count > 0:
    for venta in ventas_ficticias:
        print(f'  - Venta #{venta.id_venta}: {venta.motivo_credito[:50]}...')
    
    ventas_ficticias.delete()
    print(f'✅ {count} ventas ficticias eliminadas exitosamente')
else:
    print('✅ No hay ventas ficticias para eliminar')
