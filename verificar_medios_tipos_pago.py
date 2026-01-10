#!/usr/bin/env python
"""
Script para verificar métodos de pago y tipos de pago en BD
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import MediosPago, TiposPago

print("=" * 60)
print("MEDIOS DE PAGO")
print("=" * 60)
for medio in MediosPago.objects.all():
    print(f"ID: {medio.id_medio_pago} | {medio.descripcion} | Activo: {medio.activo}")

print("\n" + "=" * 60)
print("TIPOS DE PAGO")
print("=" * 60)
for tipo in TiposPago.objects.all():
    print(f"ID: {tipo.id_tipo_pago} | {tipo.descripcion} | Activo: {tipo.activo}")
