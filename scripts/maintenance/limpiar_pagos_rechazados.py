"""
Script para eliminar ventas rechazadas y permitir que los almuerzos vuelvan a aparecer
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Ventas

# Eliminar todas las ventas rechazadas
ventas_rechazadas = Ventas.objects.filter(motivo_credito__icontains='PAGO_RECHAZADO')
count = ventas_rechazadas.count()
print(f'Encontradas {count} ventas rechazadas')

if count > 0:
    ventas_rechazadas.delete()
    print(f'✅ {count} ventas rechazadas eliminadas exitosamente')
else:
    print('No hay ventas rechazadas para eliminar')
