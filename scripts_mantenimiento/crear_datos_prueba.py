"""
Script para crear datos de prueba para Cuenta Corriente y Recargas
"""
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Cliente, Hijo, Tarjeta, Empleado, CargasSaldo

def crear_datos_prueba():
    print("=" * 60)
    print("CREANDO DATOS DE PRUEBA")
    print("=" * 60)
    
    # Obtener o crear empleado
    try:
        empleado = Empleado.objects.filter(activo=True).first()
        if not empleado:
            print("⚠ No hay empleados en el sistema. Usando None.")
            empleado = None
        else:
            print(f"✓ Usando empleado existente: {empleado.nombre} {empleado.apellido}")
    except Exception as e:
        print(f"⚠ Error al obtener empleado: {e}")
        empleado = None
    
    print("\n" + "-" * 60)
    print("CREANDO CLIENTES CON CUENTA CORRIENTE")
    print("-" * 60)
    
    # Crear clientes
    clientes_data = [
        {
            'nombre': 'María González',
            'ruc_ci': '1234567-8',
            'direccion': 'Av. España 123',
            'telefono': '0981-234567',
            'limite_credito': Decimal('500000'),
            'deuda_actual': Decimal('150000'),
            'estado': 'activo'
        },
        {
            'nombre': 'Juan Pérez Rodríguez',
            'ruc_ci': '2345678-9',
            'direccion': 'Calle Palma 456',
            'telefono': '0982-345678',
            'limite_credito': Decimal('800000'),
            'deuda_actual': Decimal('0'),
            'estado': 'activo'
        },
        {
            'nombre': 'Ana Silva de Martínez',
            'ruc_ci': '3456789-0',
            'direccion': 'Av. Artigas 789',
            'telefono': '0983-456789',
            'limite_credito': Decimal('300000'),
            'deuda_actual': Decimal('280000'),
            'estado': 'activo'
        },
        {
            'nombre': 'Roberto López',
            'ruc_ci': '4567890-1',
            'direccion': 'Calle Cerro Corá 321',
            'telefono': '0984-567890',
            'limite_credito': Decimal('1000000'),
            'deuda_actual': Decimal('450000'),
            'estado': 'activo'
        },
        {
            'nombre': 'Carmen Benítez',
            'ruc_ci': '5678901-2',
            'direccion': 'Av. San Martín 654',
            'telefono': '0985-678901',
            'limite_credito': Decimal('200000'),
            'deuda_actual': Decimal('200000'),
            'estado': 'bloqueado'  # Cliente con límite alcanzado
        }
    ]
    
    clientes_creados = []
    for data in clientes_data:
        cliente, created = Cliente.objects.get_or_create(
            ruc_ci=data['ruc_ci'],
            defaults={
                'nombre': data['nombre'],
                'direccion': data['direccion'],
                'telefono': data['telefono'],
                'limite_credito': data['limite_credito'],
                'deuda_actual': data['deuda_actual'],
                'estado': data['estado'],
                'id_empleado': empleado
            }
        )
        
        if created:
            print(f"✓ Cliente creado: {cliente.nombre}")
            print(f"  - Límite: Gs. {cliente.limite_credito:,.0f}")
            print(f"  - Deuda: Gs. {cliente.deuda_actual:,.0f}")
            print(f"  - Disponible: Gs. {cliente.limite_credito - cliente.deuda_actual:,.0f}")
        else:
            print(f"✓ Cliente existente: {cliente.nombre}")
        
        clientes_creados.append(cliente)
    
    print("\n" + "-" * 60)
    print("CREANDO HIJOS Y TARJETAS")
    print("-" * 60)
    
    # Crear hijos y tarjetas para cada cliente
    hijos_data = [
        # Hijos de María González
        {
            'cliente': clientes_creados[0],
            'nombre': 'Pedro González',
            'grado_curso': '5to Grado',
            'tarjeta': '1001',
            'saldo': Decimal('25000')
        },
        {
            'cliente': clientes_creados[0],
            'nombre': 'Lucía González',
            'grado_curso': '3er Grado',
            'tarjeta': '1002',
            'saldo': Decimal('18000')
        },
        # Hijos de Juan Pérez
        {
            'cliente': clientes_creados[1],
            'nombre': 'Santiago Pérez',
            'grado_curso': '6to Grado',
            'tarjeta': '1003',
            'saldo': Decimal('45000')
        },
        # Hijos de Ana Silva
        {
            'cliente': clientes_creados[2],
            'nombre': 'Valentina Martínez',
            'grado_curso': '4to Grado',
            'tarjeta': '1004',
            'saldo': Decimal('8000')
        },
        {
            'cliente': clientes_creados[2],
            'nombre': 'Mateo Martínez',
            'grado_curso': '2do Grado',
            'tarjeta': '1005',
            'saldo': Decimal('12000')
        },
        {
            'cliente': clientes_creados[2],
            'nombre': 'Emma Martínez',
            'grado_curso': '1er Grado',
            'tarjeta': '1006',
            'saldo': Decimal('5000')
        },
        # Hijos de Roberto López
        {
            'cliente': clientes_creados[3],
            'nombre': 'Sofía López',
            'grado_curso': '5to Grado',
            'tarjeta': '1007',
            'saldo': Decimal('95000')
        },
        # Hijos de Carmen Benítez
        {
            'cliente': clientes_creados[4],
            'nombre': 'Benjamín Benítez',
            'grado_curso': '3er Grado',
            'tarjeta': '1008',
            'saldo': Decimal('2000')
        }
    ]
    
    tarjetas_creadas = []
    for data in hijos_data:
        # Crear o obtener tarjeta
        tarjeta, created = Tarjeta.objects.get_or_create(
            nro_tarjeta=data['tarjeta'],
            defaults={
                'saldo_actual': data['saldo'],
                'estado': 'activa'
            }
        )
        
        if not created:
            print(f"✓ Tarjeta existente: {tarjeta.nro_tarjeta}")
        else:
            print(f"✓ Tarjeta creada: {tarjeta.nro_tarjeta} - Saldo: Gs. {tarjeta.saldo_actual:,.0f}")
        
        # Crear hijo
        hijo, created = Hijo.objects.get_or_create(
            nro_tarjeta=tarjeta,
            defaults={
                'nombre': data['nombre'],
                'grado_curso': data['grado_curso'],
                'id_responsable': data['cliente']
            }
        )
        
        if created:
            print(f"  └─ Hijo creado: {hijo.nombre} ({hijo.grado_curso})")
            print(f"     Responsable: {data['cliente'].nombre}")
        
        tarjetas_creadas.append(tarjeta)
    
    print("\n" + "-" * 60)
    print("CREANDO RECARGAS DE PRUEBA")
    print("-" * 60)
    
    # Crear recargas de los últimos días
    formas_pago = ['efectivo', 'transferencia', 'tarjeta_credito']
    
    recargas_count = 0
    for i, tarjeta in enumerate(tarjetas_creadas):
        # Crear 2-5 recargas por tarjeta en los últimos 30 días
        num_recargas = random.randint(2, 5)
        
        for j in range(num_recargas):
            # Fecha aleatoria en los últimos 30 días
            dias_atras = random.randint(0, 30)
            fecha_recarga = datetime.now() - timedelta(days=dias_atras)
            
            # Monto aleatorio
            montos_posibles = [10000, 20000, 50000, 100000, 200000]
            monto = Decimal(random.choice(montos_posibles))
            
            # Calcular saldos
            saldo_anterior = tarjeta.saldo_actual - monto if j == 0 else tarjeta.saldo_actual
            saldo_posterior = saldo_anterior + monto
            
            recarga, created = CargasSaldo.objects.get_or_create(
                nro_tarjeta=tarjeta,
                fecha=fecha_recarga,
                monto=monto,
                defaults={
                    'forma_pago': random.choice(formas_pago),
                    'saldo_anterior': saldo_anterior,
                    'saldo_posterior': saldo_posterior,
                    'observaciones': f'Recarga de prueba #{j+1}',
                    'id_empleado': empleado
                }
            )
            
            if created:
                recargas_count += 1
    
    print(f"✓ {recargas_count} recargas creadas")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE DATOS CREADOS")
    print("=" * 60)
    print(f"✓ {len(clientes_creados)} clientes")
    print(f"✓ {len(tarjetas_creadas)} tarjetas/hijos")
    print(f"✓ {recargas_count} recargas")
    
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS")
    print("=" * 60)
    
    total_limite = sum(c.limite_credito for c in clientes_creados)
    total_deuda = sum(c.deuda_actual for c in clientes_creados)
    total_disponible = total_limite - total_deuda
    clientes_con_deuda = sum(1 for c in clientes_creados if c.deuda_actual > 0)
    
    print(f"Límite total: Gs. {total_limite:,.0f}")
    print(f"Deuda total: Gs. {total_deuda:,.0f}")
    print(f"Disponible total: Gs. {total_disponible:,.0f}")
    print(f"Clientes con deuda: {clientes_con_deuda}/{len(clientes_creados)}")
    
    total_saldo = sum(t.saldo_actual for t in tarjetas_creadas)
    print(f"\nSaldo total en tarjetas: Gs. {total_saldo:,.0f}")
    
    print("\n" + "=" * 60)
    print("URLS PARA PROBAR:")
    print("=" * 60)
    print("Recargas: http://127.0.0.1:8000/pos/recargas/")
    print("Historial Recargas: http://127.0.0.1:8000/pos/recargas/historial/")
    print("Cuenta Corriente: http://127.0.0.1:8000/pos/cuenta-corriente/")
    print("\nEjemplo detalle cliente:")
    print(f"http://127.0.0.1:8000/pos/cuenta-corriente/detalle/{clientes_creados[0].id_cliente}/")
    
    print("\n✅ ¡Datos de prueba creados exitosamente!")

if __name__ == '__main__':
    crear_datos_prueba()
