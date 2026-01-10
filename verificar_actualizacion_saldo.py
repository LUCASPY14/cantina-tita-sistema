#!/usr/bin/env python
"""
Script para verificar que el saldo se actualiza correctamente al procesar ventas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Hijos, ConsumoTarjeta, Ventas
from django.utils import timezone

print("=" * 80)
print("VERIFICACIÓN DE ACTUALIZACIÓN DE SALDO EN VENTAS")
print("=" * 80)

# Buscar una tarjeta estudiante
hijos = Hijos.objects.filter(nro_tarjeta__isnull=False).order_by('-id_hijo')[:3]

if not hijos:
    print("❌ No hay estudiantes con tarjeta registrados")
    exit()

for hijo in hijos:
    print(f"\n📚 Estudiante: {hijo.descripcions} {hijo.apellidos}")
    print(f"   Tarjeta: {hijo.nro_tarjeta}")
    print(f"   Saldo actual: Gs. {hijo.saldo_actual:,.2f}")
    
    # Buscar últimos consumos
    consumos = ConsumoTarjeta.objects.filter(nro_tarjeta=hijo.nro_tarjeta).order_by('-fecha_consumo')[:5]
    
    if consumos:
        print(f"   Últimos {len(consumos)} consumos:")
        for consumo in consumos:
            print(f"     • {consumo.fecha_consumo.strftime('%d/%m/%Y %H:%M:%S')} - Monto: Gs. {consumo.monto_consumido:,.0f}")
            print(f"       Saldo anterior: Gs. {consumo.saldo_anterior:,.0f} → Posterior: Gs. {consumo.saldo_posterior:,.0f}")
            
            # Verificar que el saldo posterior coincida con el saldo anterior del consumo siguiente
            siguiente = ConsumoTarjeta.objects.filter(
                nro_tarjeta=hijo.nro_tarjeta,
                fecha_consumo__lt=consumo.fecha_consumo
            ).first()
            
            if siguiente and siguiente.saldo_anterior != consumo.saldo_posterior:
                print(f"       ⚠️ INCONSISTENCIA: El siguiente consumo tiene saldo anterior {siguiente.saldo_anterior:,.0f}")
            elif siguiente:
                print(f"       ✓ Saldo consistente con siguiente consumo")
    else:
        print("   ℹ️ Sin consumos registrados")

print("\n" + "=" * 80)
print("VENTAS RECIENTES")
print("=" * 80)

ventas = Ventas.objects.select_related('id_tarjeta_estudiante').order_by('-fecha')[:10]

for venta in ventas:
    print(f"\nVenta #{venta.id_venta}")
    print(f"  Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Monto: Gs. {venta.monto_total:,.2f}")
    if venta.id_tarjeta_estudiante:
        print(f"  Tarjeta: {venta.id_tarjeta_estudiante.nro_tarjeta}")
        # Buscar el consumo asociado
        consumo = ConsumoTarjeta.objects.filter(
            nro_tarjeta=venta.id_tarjeta_estudiante.nro_tarjeta,
            monto_consumido=int(venta.monto_total),
            fecha_consumo__date=venta.fecha.date()
        ).first()
        
        if consumo:
            print(f"  ✓ Consumo registrado: ID {consumo.id_consumo}")
            print(f"    Saldo: {consumo.saldo_anterior:,.0f} → {consumo.saldo_posterior:,.0f}")
        else:
            print(f"  ⚠️ Consumo NO encontrado en BD")
    else:
        print(f"  Forma de pago: Otro (no tarjeta estudiante)")

print("\n" + "=" * 80)
