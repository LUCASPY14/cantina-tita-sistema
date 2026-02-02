"""
Script simplificado para crear datos de prueba para Recargas
"""
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Tarjeta, Hijo, Cliente, Empleado, CargasSaldo

def crear_datos_recargas():
    print("=" * 60)
    print("CREANDO DATOS DE PRUEBA PARA RECARGAS")
    print("=" * 60)
    
    # Obtener empleado
    empleado = Empleado.objects.filter(activo=True).first()
    if not empleado:
        print("❌ No hay empleados en el sistema")
        return
    
    print(f"✓ Usando empleado: {empleado.nombre} {empleado.apellido}")
    
    # Obtener clientes existentes
    clientes = Cliente.objects.filter(activo=True)[:5]
    if not clientes:
        print("❌ No hay clientes en el sistema")
        return
    
    print(f"✓ Encontrados {clientes.count()} clientes")
    
    print("\n" + "-" * 60)
    print("CREANDO TARJETAS Y ESTUDIANTES")
    print("-" * 60)
    
    # Crear tarjetas para testing
    tarjetas_data = [
        {'nro': '2001', 'nombre': 'Ana María López', 'grado': '5to Grado', 'saldo': 25000},
        {'nro': '2002', 'nombre': 'Carlos Benítez', 'grado': '4to Grado', 'saldo': 18000},
        {'nro': '2003', 'nombre': 'María Rodríguez', 'grado': '6to Grado', 'saldo': 42000},
        {'nro': '2004', 'nombre': 'Pedro Sánchez', 'grado': '3er Grado', 'saldo': 8500},
        {'nro': '2005', 'nombre': 'Lucía González', 'grado': '2do Grado', 'saldo': 15000},
        {'nro': '2006', 'nombre': 'Santiago Pérez', 'grado': '1er Grado', 'saldo': 3500},
        {'nro': '2007', 'nombre': 'Valentina Silva', 'grado': '5to Grado', 'saldo': 52000},
        {'nro': '2008', 'nombre': 'Mateo Fernández', 'grado': '4to Grado', 'saldo': 12000},
    ]
    
    tarjetas_creadas = []
    for i, data in enumerate(tarjetas_data):
        # Crear tarjeta
        tarjeta, created = Tarjeta.objects.get_or_create(
            nro_tarjeta=data['nro'],
            defaults={
                'saldo_actual': Decimal(data['saldo']),
                'estado': 'activa'
            }
        )
        
        if created:
            print(f"✓ Tarjeta {data['nro']} creada - Saldo: Gs. {data['saldo']:,}")
            
            # Crear hijo asociado
            responsable = clientes[i % len(clientes)]  # Distribuir entre clientes
            
            hijo, h_created = Hijo.objects.get_or_create(
                nro_tarjeta=tarjeta,
                defaults={
                    'nombre': data['nombre'],
                    'grado_curso': data['grado'],
                    'id_responsable': responsable
                }
            )
            
            if h_created:
                print(f"  └─ Estudiante: {hijo.nombre} ({hijo.grado_curso})")
        else:
            print(f"✓ Tarjeta {data['nro']} ya existe - Saldo actual: Gs. {tarjeta.saldo_actual:,.0f}")
        
        tarjetas_creadas.append(tarjeta)
    
    print("\n" + "-" * 60)
    print("CREANDO RECARGAS DE PRUEBA")
    print("-" * 60)
    
    formas_pago = ['efectivo', 'transferencia', 'tarjeta_credito']
    montos_posibles = [10000, 20000, 50000, 100000, 200000]
    
    recargas_count = 0
    
    for tarjeta in tarjetas_creadas:
        # Crear 3-7 recargas por tarjeta en los últimos 30 días
        num_recargas = random.randint(3, 7)
        
        for j in range(num_recargas):
            # Fecha aleatoria en los últimos 30 días
            dias_atras = random.randint(0, 30)
            fecha_recarga = datetime.now() - timedelta(days=dias_atras)
            
            # Monto aleatorio
            monto = Decimal(random.choice(montos_posibles))
            
            # Saldo simulado (para registros históricos)
            saldo_anterior = Decimal(random.randint(5000, 30000))
            saldo_posterior = saldo_anterior + monto
            
            observaciones_opciones = [
                'Recarga regular',
                'Recarga para semana completa',
                'Pago del padre/madre',
                '',
                'Recarga mensual',
                ''
            ]
            
            try:
                recarga = CargasSaldo.objects.create(
                    nro_tarjeta=tarjeta,
                    fecha=fecha_recarga,
                    monto=monto,
                    forma_pago=random.choice(formas_pago),
                    saldo_anterior=saldo_anterior,
                    saldo_posterior=saldo_posterior,
                    observaciones=random.choice(observaciones_opciones),
                    id_empleado=empleado
                )
                recargas_count += 1
            except Exception as e:
                print(f"  ⚠ Error al crear recarga: {e}")
    
    print(f"✓ {recargas_count} recargas creadas")
    
    # Crear algunas recargas de HOY para probar estadísticas
    print("\n" + "-" * 60)
    print("CREANDO RECARGAS DE HOY")
    print("-" * 60)
    
    hoy_count = 0
    for tarjeta in random.sample(tarjetas_creadas, min(4, len(tarjetas_creadas))):
        monto = Decimal(random.choice([20000, 50000, 100000]))
        saldo_anterior = tarjeta.saldo_actual
        saldo_posterior = saldo_anterior + monto
        
        try:
            recarga = CargasSaldo.objects.create(
                nro_tarjeta=tarjeta,
                fecha=datetime.now(),
                monto=monto,
                forma_pago=random.choice(formas_pago),
                saldo_anterior=saldo_anterior,
                saldo_posterior=saldo_posterior,
                observaciones='Recarga de hoy',
                id_empleado=empleado
            )
            
            # Actualizar saldo de tarjeta
            tarjeta.saldo_actual = saldo_posterior
            tarjeta.save()
            
            hoy_count += 1
            print(f"✓ Recarga hoy: Tarjeta {tarjeta.nro_tarjeta} - Gs. {monto:,}")
        except Exception as e:
            print(f"  ⚠ Error: {e}")
    
    print(f"✓ {hoy_count} recargas de hoy creadas")
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"✓ {len(tarjetas_creadas)} tarjetas activas")
    print(f"✓ {recargas_count + hoy_count} recargas totales")
    print(f"  - {recargas_count} recargas históricas")
    print(f"  - {hoy_count} recargas de hoy")
    
    total_saldo = sum(t.saldo_actual for t in tarjetas_creadas)
    print(f"\nSaldo total en tarjetas: Gs. {total_saldo:,.0f}")
    
    # Mostrar URLs para probar
    print("\n" + "=" * 60)
    print("URLS PARA PROBAR:")
    print("=" * 60)
    print("✅ Recargas (principal): http://127.0.0.1:8000/pos/recargas/")
    print("✅ Historial: http://127.0.0.1:8000/pos/recargas/historial/")
    
    print("\nEjemplos de tarjetas para buscar:")
    for tarjeta in tarjetas_creadas[:3]:
        print(f"  - {tarjeta.nro_tarjeta}")
    
    print("\n✅ ¡Datos de prueba creados exitosamente!")
    print("📝 Ahora puedes probar el módulo de recargas")

if __name__ == '__main__':
    crear_datos_recargas()
