#!/usr/bin/env python
"""
Script para verificar timbrados disponibles
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Timbrados

print("=" * 80)
print("TIMBRADOS DISPONIBLES")
print("=" * 80)
print()

timbrados = Timbrados.objects.all().order_by('-fecha_fin')

for t in timbrados:
    print(f"Nro Timbrado: {t.nro_timbrado}")
    print(f"  Tipo: {'Electrónico' if t.es_electronico else 'Físico'}")
    print(f"  Estado: {'Activo' if t.activo else 'Inactivo'}")
    print(f"  Fecha Inicio: {t.fecha_inicio.strftime('%d/%m/%Y') if t.fecha_inicio else 'N/A'}")
    print(f"  Fecha Fin: {t.fecha_fin.strftime('%d/%m/%Y') if t.fecha_fin else 'N/A'}")
    
    # Verificar si está vencido
    hoy = datetime.now().date()
    if t.fecha_fin:
        if t.fecha_fin < hoy:
            print(f"  ⚠️  VENCIDO (hace {(hoy - t.fecha_fin).days} días)")
        else:
            dias_restantes = (t.fecha_fin - hoy).days
            print(f"  ✅ Vigente ({dias_restantes} días restantes)")
    
    print()
