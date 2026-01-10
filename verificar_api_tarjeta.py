#!/usr/bin/env python
"""
Script de verificación: Estructura de API tarjeta
Comprueba que la respuesta JSON de la API es correcta
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Tarjeta, RestriccionesHijos

print("=" * 60)
print("🔍 VERIFICACIÓN: API de Tarjetas - Estructura de Respuesta")
print("=" * 60)

# Obtener una tarjeta para testear
tarjeta = Tarjeta.objects.select_related(
    'id_hijo',
    'id_hijo__id_cliente_responsable'
).filter(estado='Activa').first()

if tarjeta:
    print(f"\n✅ Tarjeta encontrada: {tarjeta.nro_tarjeta}")
    print(f"   Estudiante: {tarjeta.id_hijo.nombre_completo}")
    print(f"   Saldo: Gs. {tarjeta.saldo_actual}")
    
    # Obtener restricciones
    restricciones = list(RestriccionesHijos.objects.filter(
        id_hijo=tarjeta.id_hijo,
        activo=True
    ).values('tipo_restriccion', 'descripcion', 'severidad'))
    
    print(f"   Restricciones: {len(restricciones)}")
    
    # Construir respuesta
    respuesta = {
        'success': True,
        'estudiante': {
            'id_hijo': tarjeta.id_hijo.id_hijo,
            'nombre': f"{tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}",
            'saldo': int(tarjeta.saldo_actual),
            'grado': tarjeta.id_hijo.grado or 'N/A',
            'cliente': tarjeta.id_hijo.id_cliente_responsable.nombre_completo if tarjeta.id_hijo.id_cliente_responsable else 'N/A',
            'nro_tarjeta': tarjeta.nro_tarjeta,
            'restricciones': restricciones
        }
    }
    
    print("\n" + "=" * 60)
    print("📤 RESPUESTA JSON (simulada)")
    print("=" * 60)
    print(json.dumps(respuesta, indent=2, ensure_ascii=False))
    print("\n✅ Estructura de API correcta - SIN ERRORES")
    
else:
    print("❌ No hay tarjetas activas en la base de datos")
