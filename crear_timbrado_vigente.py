#!/usr/bin/env python
"""
Script para crear/actualizar un timbrado válido para facturación electrónica
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Timbrados, PuntosExpedicion

print("=" * 80)
print("CREAR/ACTUALIZAR TIMBRADO VIGENTE PARA FACTURACIÓN ELECTRÓNICA")
print("=" * 80)
print()

# 1. Obtener o crear punto de expedición
try:
    punto = PuntosExpedicion.objects.get(codigo_establecimiento='001', codigo_punto_expedicion='001')
    print(f"✅ Punto de expedición encontrado: {punto}")
except PuntosExpedicion.DoesNotExist:
    print("❌ Punto de expedición 001-001 no existe")
    print("   Necesitas crear uno primero en /admin/gestion/puntosexpedicion/")
    exit(1)

# 2. Crear timbrado vigente
nro_timbrado = 12345678
hoy = datetime.now().date()
fecha_inicio = hoy
fecha_fin = hoy + timedelta(days=365)  # Vigente por 1 año

print()
print(f"Creando/Actualizando timbrado:")
print(f"  Nro Timbrado: {nro_timbrado}")
print(f"  Tipo: Factura")
print(f"  Electrónico: Sí")
print(f"  Fecha Inicio: {fecha_inicio.strftime('%d/%m/%Y')}")
print(f"  Fecha Fin: {fecha_fin.strftime('%d/%m/%Y')} ({(fecha_fin - hoy).days} días)")
print(f"  Rango: 001-001-0000001 a 001-001-9999999")
print()

# 3. Crear o actualizar
timbrado, creado = Timbrados.objects.update_or_create(
    nro_timbrado=nro_timbrado,
    defaults={
        'id_punto': punto,
        'tipo_documento': 'Factura',
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'nro_inicial': 1,
        'nro_final': 9999999,
        'es_electronico': True,
        'activo': True,
    }
)

if creado:
    print("✅ Timbrado CREADO exitosamente")
else:
    print("✅ Timbrado ACTUALIZADO exitosamente")

print()
print(f"Detalles:")
print(f"  Nro Timbrado: {timbrado.nro_timbrado}")
print(f"  Punto: {timbrado.id_punto}")
print(f"  Tipo Documento: {timbrado.tipo_documento}")
print(f"  Vigencia: {timbrado.fecha_inicio.strftime('%d/%m/%Y')} - {timbrado.fecha_fin.strftime('%d/%m/%Y')}")
print(f"  Electrónico: {'Sí' if timbrado.es_electronico else 'No'}")
print(f"  Activo: {'Sí' if timbrado.activo else 'No'}")
print()

# 4. Verificar todos los timbrados
print("=" * 80)
print("TIMBRADOS EN EL SISTEMA")
print("=" * 80)
print()

for t in Timbrados.objects.all().order_by('-fecha_fin'):
    hoy = datetime.now().date()
    if t.fecha_fin < hoy:
        estado = f"⚠️  VENCIDO (hace {(hoy - t.fecha_fin).days} días)"
    else:
        dias = (t.fecha_fin - hoy).days
        estado = f"✅ VIGENTE ({dias} días)"
    
    print(f"Nro Timbrado: {t.nro_timbrado}")
    print(f"  Tipo: {t.tipo_documento} | Electrónico: {'Sí' if t.es_electronico else 'No'}")
    print(f"  Vigencia: {t.fecha_inicio.strftime('%d/%m/%Y')} → {t.fecha_fin.strftime('%d/%m/%Y')}")
    print(f"  Estado: {estado}")
    print()
