"""
Script para crear datos de prueba completos para el Sistema de Almuerzos
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import (
    PlanesAlmuerzo, SuscripcionesAlmuerzo, 
    RegistroConsumoAlmuerzo, PagosAlmuerzoMensual,
    Cliente, Hijo, ListaPrecios, TipoCliente
)
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

def print_separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f"  {title}")
        print("="*60)

def print_result(test_name, success, message=""):
    status = "✅ OK" if success else "❌ ERROR"
    print(f"{status} - {test_name}")
    if message:
        print(f"      {message}")

def limpiar_datos_prueba():
    """Eliminar datos de prueba anteriores"""
    print_separator("LIMPIEZA DE DATOS ANTERIORES")
    
    try:
        # Obtener IDs de hijos test
        hijos_test = Hijo.objects.filter(nombre__startswith='TEST_')
        hijos_ids = list(hijos_test.values_list('id_hijo', flat=True))
        
        if hijos_ids:
            # Eliminar en orden inverso por dependencias
            deleted_pagos = PagosAlmuerzoMensual.objects.filter(
                id_suscripcion__id_hijo_id__in=hijos_ids
            ).delete()
            print_result("Pagos eliminados", True, f"{deleted_pagos[0]} registros")
            
            deleted_consumos = RegistroConsumoAlmuerzo.objects.filter(
                id_hijo_id__in=hijos_ids
            ).delete()
            print_result("Consumos eliminados", True, f"{deleted_consumos[0]} registros")
            
            deleted_suscripciones = SuscripcionesAlmuerzo.objects.filter(
                id_hijo_id__in=hijos_ids
            ).delete()
            print_result("Suscripciones eliminadas", True, f"{deleted_suscripciones[0]} registros")
            
            deleted_hijos = hijos_test.delete()
            print_result("Hijos eliminados", True, f"{deleted_hijos[0]} registros")
        else:
            print_result("Sin datos previos", True, "No hay datos test anteriores")
        
        # Eliminar clientes test
        deleted_clientes = Cliente.objects.filter(nombres__startswith='Cliente Test').delete()
        print_result("Clientes eliminados", True, f"{deleted_clientes[0]} registros")
        
        # Eliminar planes con nombres específicos de prueba
        deleted_planes = PlanesAlmuerzo.objects.filter(
            nombre_plan__in=['Plan Básico', 'Plan Premium', 'Plan Económico', 'Plan 3 Días', 'Plan Especial']
        ).delete()
        print_result("Planes Test eliminados", True, f"{deleted_planes[0]} registros")
        
        return True
    except Exception as e:
        print_result("Error en limpieza", False, str(e))
        return False

def crear_planes():
    """Crear planes de almuerzo de prueba"""
    print_separator("CREAR PLANES DE ALMUERZO")
    
    planes_data = [
        {
            'nombre_plan': 'Plan Básico',
            'descripcion': 'Plan básico con almuerzo completo de lunes a viernes',
            'precio_mensual': Decimal('45000.00'),
            'dias_semana_incluidos': 'Lunes,Martes,Miércoles,Jueves,Viernes',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Premium',
            'descripcion': 'Plan premium con menú especial y postre',
            'precio_mensual': Decimal('65000.00'),
            'dias_semana_incluidos': 'Lunes,Martes,Miércoles,Jueves,Viernes',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Económico',
            'descripcion': 'Plan económico con menú del día',
            'precio_mensual': Decimal('35000.00'),
            'dias_semana_incluidos': 'Lunes,Martes,Miércoles,Jueves,Viernes',
            'activo': True
        },
        {
            'nombre_plan': 'Plan 3 Días',
            'descripcion': 'Plan para 3 días a la semana (L-M-V)',
            'precio_mensual': Decimal('30000.00'),
            'dias_semana_incluidos': 'Lunes,Miércoles,Viernes',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Especial',
            'descripcion': 'Plan con dieta especial o restricciones',
            'precio_mensual': Decimal('55000.00'),
            'dias_semana_incluidos': 'Lunes,Martes,Miércoles,Jueves,Viernes',
            'activo': True
        },
    ]
    
    planes_creados = []
    for plan_data in planes_data:
        try:
            plan = PlanesAlmuerzo.objects.create(
                fecha_creacion=timezone.now(),
                **plan_data
            )
            planes_creados.append(plan)
            print_result(f"Plan: {plan.nombre_plan}", True, 
                        f"ID: {plan.id_plan_almuerzo} - ${plan.precio_mensual:,.0f}")
        except Exception as e:
            print_result(f"Plan: {plan_data['nombre_plan']}", False, str(e))
    
    return planes_creados

def crear_clientes_e_hijos():
    """Crear clientes e hijos de prueba"""
    print_separator("CREAR CLIENTES Y ESTUDIANTES")
    
    # Obtener requisitos
    lista_precios = ListaPrecios.objects.first()
    if not lista_precios:
        print_result("Lista de Precios", False, "No hay listas de precios")
        return [], []
    
    tipo_cliente = TipoCliente.objects.first()
    if not tipo_cliente:
        print_result("Tipo Cliente", False, "No hay tipos de cliente")
        return [], []
    
    clientes_data = [
        {
            'nombres': 'Cliente Test 1',
            'apellidos': 'Pérez García',
            'ruc_ci': 'TEST001',
            'email': 'cliente1@test.com',
            'telefono': '3001234567'
        },
        {
            'nombres': 'Cliente Test 2',
            'apellidos': 'González López',
            'ruc_ci': 'TEST002',
            'email': 'cliente2@test.com',
            'telefono': '3009876543'
        },
        {
            'nombres': 'Cliente Test 3',
            'apellidos': 'Rodríguez Martínez',
            'ruc_ci': 'TEST003',
            'email': 'cliente3@test.com',
            'telefono': '3005556789'
        },
        {
            'nombres': 'Cliente Test 4',
            'apellidos': 'Hernández Silva',
            'ruc_ci': 'TEST004',
            'email': 'cliente4@test.com',
            'telefono': '3007778899'
        },
        {
            'nombres': 'Cliente Test 5',
            'apellidos': 'Ramírez Castro',
            'ruc_ci': 'TEST005',
            'email': 'cliente5@test.com',
            'telefono': '3002223344'
        },
    ]
    
    hijos_por_cliente = [
        ['María', 'Juan'],
        ['Carlos'],
        ['Ana', 'Pedro', 'Luis'],
        ['Sofía', 'Diego'],
        ['Valentina']
    ]
    
    grados = ['1° Primaria', '2° Primaria', '3° Primaria', '4° Primaria', '5° Primaria',
              '6° Bachillerato', '7° Bachillerato', '8° Bachillerato', '9° Bachillerato']
    
    clientes_creados = []
    hijos_creados = []
    
    for idx, cliente_data in enumerate(clientes_data):
        try:
            cliente = Cliente.objects.create(
                id_lista_por_defecto=lista_precios,
                id_tipo_cliente=tipo_cliente,
                **cliente_data
            )
            clientes_creados.append(cliente)
            print_result(f"Cliente: {cliente.nombres}", True, f"ID: {cliente.id_cliente}")
            
            # Crear hijos para este cliente
            for hijo_idx, nombre_hijo in enumerate(hijos_por_cliente[idx]):
                hijo = Hijo.objects.create(
                    nombre=f'TEST_{nombre_hijo}_{idx+1:02d}{hijo_idx+1:02d}',
                    apellido=cliente.apellidos,
                    id_cliente_responsable=cliente,
                    activo=True
                )
                hijos_creados.append(hijo)
                print_result(f"  Hijo: {hijo.nombre} {hijo.apellido}", True, 
                           f"ID: {hijo.id_hijo}")
        except Exception as e:
            print_result(f"Cliente: {cliente_data['nombres']}", False, str(e))
    
    return clientes_creados, hijos_creados

def crear_suscripciones(hijos, planes):
    """Crear suscripciones para los estudiantes"""
    print_separator("CREAR SUSCRIPCIONES")
    
    if not hijos or not planes:
        print_result("Suscripciones", False, "No hay hijos o planes disponibles")
        return []
    
    suscripciones_creadas = []
    hoy = date.today()
    
    # Crear suscripciones con diferentes estados
    estados = ['Activa', 'Activa', 'Activa', 'Activa', 'Vencida']
    
    for idx, hijo in enumerate(hijos):
        try:
            plan = random.choice(planes)
            estado = random.choice(estados)
            
            if estado == 'Activa':
                # Suscripciones activas iniciadas hace 20-60 días
                fecha_inicio = hoy - timedelta(days=random.randint(20, 60))
                fecha_fin = hoy + timedelta(days=random.randint(30, 90))
            else:
                # Suscripciones vencidas
                fecha_inicio = hoy - timedelta(days=random.randint(90, 180))
                fecha_fin = hoy - timedelta(days=random.randint(1, 30))
            
            suscripcion = SuscripcionesAlmuerzo.objects.create(
                id_hijo=hijo,
                id_plan_almuerzo=plan,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado
            )
            suscripciones_creadas.append(suscripcion)
            
            print_result(
                f"Suscripción: {hijo.nombre} {hijo.apellido}", 
                True, 
                f"Plan: {plan.nombre_plan} - Estado: {estado} - Hasta: {fecha_fin.strftime('%d/%m/%Y')}"
            )
        except Exception as e:
            print_result(f"Suscripción: {hijo.nombres}", False, str(e))
    
    return suscripciones_creadas

def crear_consumos(suscripciones):
    """Crear registros de consumo para las suscripciones activas"""
    print_separator("CREAR REGISTROS DE CONSUMO")
    
    if not suscripciones:
        print_result("Consumos", False, "No hay suscripciones disponibles")
        return []
    
    consumos_creados = []
    hoy = date.today()
    
    print(f"\n  Hoy es: {hoy.strftime('%d/%m/%Y')}")
    print(f"  Suscripciones totales: {len(suscripciones)}")
    
    # Crear consumos de los últimos 30 días
    activas = [s for s in suscripciones if s.estado == 'Activa']
    print(f"  Suscripciones activas: {len(activas)}\n")
    
    # Mapeo de días de la semana en español
    dias_semana_es = {
        0: 'Lunes',
        1: 'Martes', 
        2: 'Miércoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    for suscripcion in activas:
        # Verificar que haya pago para el mes actual
        mes_actual_inicio = hoy.replace(day=1)
        tiene_pago = PagosAlmuerzoMensual.objects.filter(
            id_suscripcion=suscripcion,
            mes_pagado__year=hoy.year,
            mes_pagado__month=hoy.month,
            estado='Pagado'
        ).exists()
        
        if not tiene_pago:
            print(f"  Omitiendo {suscripcion.id_hijo.nombre}: No tiene pago del mes actual\n")
            continue
        
        # Obtener días incluidos en el plan
        dias_plan = suscripcion.id_plan_almuerzo.dias_semana_incluidos
        print(f"  Procesando {suscripcion.id_hijo.nombre}:")
        print(f"    - Plan: {suscripcion.id_plan_almuerzo.nombre_plan}")
        print(f"    - Días incluidos: {dias_plan}")
        
        # Generar consumos aleatorios en los últimos 30 días
        fecha_inicio_consumo = max(suscripcion.fecha_inicio, hoy - timedelta(days=30))
        dias_a_generar = (hoy - fecha_inicio_consumo).days
        
        print(f"    - Fecha inicio consumos: {fecha_inicio_consumo}")
        print(f"    - Días a generar: {dias_a_generar}")
        
        consumos_hijo = 0
        for dia in range(dias_a_generar + 1):
            fecha_consumo = fecha_inicio_consumo + timedelta(days=dia)
            
            # No crear consumos futuros
            if fecha_consumo > hoy:
                continue
            
            # Obtener nombre del día en español
            dia_semana_num = fecha_consumo.weekday()
            dia_semana_nombre = dias_semana_es[dia_semana_num]
            
            # Verificar si el día está incluido en el plan
            if dia_semana_nombre not in dias_plan:
                continue
            
            # 85% de probabilidad de asistencia
            if random.random() < 0.85:
                try:
                    # Verificar si ya existe
                    existe = RegistroConsumoAlmuerzo.objects.filter(
                        id_hijo=suscripcion.id_hijo,
                        fecha_consumo=fecha_consumo
                    ).exists()
                    
                    if not existe:
                        # Hora aleatoria entre 11:30 y 13:00
                        hora_base = 11 * 60 + 30  # 11:30 en minutos
                        minutos_aleatorios = random.randint(0, 90)  # 0-90 minutos adicionales
                        total_minutos = hora_base + minutos_aleatorios
                        hora = total_minutos // 60
                        minuto = total_minutos % 60
                        
                        hora_registro = datetime.strptime(f'{hora:02d}:{minuto:02d}', '%H:%M').time()
                        
                        try:
                            consumo = RegistroConsumoAlmuerzo.objects.create(
                                id_hijo=suscripcion.id_hijo,
                                id_suscripcion=suscripcion,
                                fecha_consumo=fecha_consumo,
                                hora_registro=hora_registro
                            )
                            consumos_creados.append(consumo)
                            consumos_hijo += 1
                        except Exception as create_error:
                            # Solo mostrar el primer error
                            if consumos_hijo == 0:
                                print(f"      ERROR en {fecha_consumo} ({dia_semana_nombre}): {str(create_error)[:100]}")
                except Exception as e:
                    pass
        
        print(f"    ✓ Creados: {consumos_hijo} consumos\n")
    
    print_result("Total consumos creados", True, f"{len(consumos_creados)} registros")
    
    # Mostrar resumen por estudiante
    from collections import defaultdict
    consumos_por_hijo = defaultdict(int)
    for consumo in consumos_creados:
        consumos_por_hijo[consumo.id_hijo.nombre] += 1
    
    if consumos_por_hijo:
        print(f"\n  Consumos por estudiante:")
        for nombre, cantidad in sorted(consumos_por_hijo.items(), key=lambda x: -x[1])[:10]:
            print_result(f"    {nombre}", True, f"{cantidad} almuerzos")
    
    return consumos_creados

def crear_facturacion(suscripciones):
    """Crear facturación mensual para las suscripciones"""
    print_separator("CREAR FACTURACIÓN MENSUAL")
    
    if not suscripciones:
        print_result("Facturación", False, "No hay suscripciones disponibles")
        return []
    
    pagos_creados = []
    hoy = date.today()
    
    # Crear facturación para los últimos 3 meses
    for mes_offset in range(3):
        fecha_mes = hoy.replace(day=1) - timedelta(days=mes_offset * 30)
        fecha_mes = fecha_mes.replace(day=1)
        
        print(f"\n  Mes: {fecha_mes.strftime('%B %Y')}")
        
        for suscripcion in suscripciones:
            # Verificar que la suscripción estaba activa ese mes
            if suscripcion.fecha_inicio > fecha_mes or suscripcion.fecha_fin < fecha_mes:
                continue
            
            try:
                # Verificar si ya existe facturación
                existe = PagosAlmuerzoMensual.objects.filter(
                    id_suscripcion=suscripcion,
                    mes_pagado__year=fecha_mes.year,
                    mes_pagado__month=fecha_mes.month
                ).exists()
                
                if existe:
                    continue
                
                # Calcular monto
                monto = suscripcion.id_plan_almuerzo.precio_mensual
                
                # Estado aleatorio: 70% pagado, 30% pendiente
                estado = 'Pagado' if random.random() < 0.7 else 'Pendiente'
                
                # Fecha de pago solo si está pagado
                if estado == 'Pagado':
                    fecha_pago_dt = timezone.now() - timedelta(days=random.randint(1, 15))
                else:
                    fecha_pago_dt = timezone.now()
                
                pago = PagosAlmuerzoMensual.objects.create(
                    id_suscripcion=suscripcion,
                    fecha_pago=fecha_pago_dt,
                    monto_pagado=monto,
                    mes_pagado=fecha_mes,
                    estado=estado
                )
                pagos_creados.append(pago)
                
                print_result(
                    f"    {suscripcion.id_hijo.nombre}", 
                    True, 
                    f"${monto:,.0f} - {estado}"
                )
            except Exception as e:
                print_result(f"    Error: {suscripcion.id_hijo.nombre}", False, str(e))
    
    return pagos_creados

def mostrar_estadisticas():
    """Mostrar estadísticas finales"""
    print_separator("ESTADÍSTICAS FINALES")
    
    from django.db.models import Count, Sum
    
    # Planes
    planes = PlanesAlmuerzo.objects.filter(activo=True)
    print_result("Planes Activos", True, f"{planes.count()} planes")
    for plan in planes:
        subs = SuscripcionesAlmuerzo.objects.filter(id_plan_almuerzo=plan).count()
        print(f"      - {plan.nombre_plan}: {subs} suscripciones")
    
    # Suscripciones
    suscripciones_activas = SuscripcionesAlmuerzo.objects.filter(estado='Activa').count()
    suscripciones_vencidas = SuscripcionesAlmuerzo.objects.filter(estado='Vencida').count()
    print_result("Suscripciones Activas", True, f"{suscripciones_activas}")
    print_result("Suscripciones Vencidas", True, f"{suscripciones_vencidas}")
    
    # Consumos
    hoy = date.today()
    consumos_hoy = RegistroConsumoAlmuerzo.objects.filter(fecha_consumo=hoy).count()
    consumos_mes = RegistroConsumoAlmuerzo.objects.filter(
        fecha_consumo__year=hoy.year,
        fecha_consumo__month=hoy.month
    ).count()
    print_result("Consumos Hoy", True, f"{consumos_hoy} almuerzos")
    print_result("Consumos Este Mes", True, f"{consumos_mes} almuerzos")
    
    # Facturación
    fecha_inicio = hoy.replace(day=1)
    if hoy.month == 12:
        fecha_fin = hoy.replace(year=hoy.year + 1, month=1, day=1)
    else:
        fecha_fin = hoy.replace(month=hoy.month + 1, day=1)
    
    pagos_mes = PagosAlmuerzoMensual.objects.filter(
        mes_pagado__gte=fecha_inicio,
        mes_pagado__lt=fecha_fin
    )
    
    total_facturado = pagos_mes.aggregate(total=Sum('monto_pagado'))['total'] or 0
    total_pagado = pagos_mes.filter(estado='Pagado').aggregate(total=Sum('monto_pagado'))['total'] or 0
    total_pendiente = total_facturado - total_pagado
    
    print_result("Total Facturado Este Mes", True, f"${total_facturado:,.0f}")
    print_result("Total Pagado", True, f"${total_pagado:,.0f}")
    print_result("Total Pendiente", True, f"${total_pendiente:,.0f}")
    
    # Estudiantes
    total_estudiantes = Hijo.objects.filter(nombre__startswith='TEST_').count()
    print_result("Total Estudiantes Test", True, f"{total_estudiantes} estudiantes")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("  CREACIÓN DE DATOS DE PRUEBA - SISTEMA DE ALMUERZOS")
    print("="*60)
    
    try:
        # 1. Limpiar datos anteriores
        limpiar_datos_prueba()
        
        # 2. Crear planes
        planes = crear_planes()
        if not planes:
            print("\n⚠️  No se pudieron crear planes. Abortando...")
            return
        
        # 3. Crear clientes e hijos
        clientes, hijos = crear_clientes_e_hijos()
        if not hijos:
            print("\n⚠️  No se pudieron crear estudiantes. Abortando...")
            return
        
        # 4. Crear suscripciones
        suscripciones = crear_suscripciones(hijos, planes)
        if not suscripciones:
            print("\n⚠️  No se pudieron crear suscripciones. Abortando...")
            return
        
        # 5. Crear facturación (DEBE IR ANTES DE CONSUMOS)
        pagos = crear_facturacion(suscripciones)
        
        # 6. Crear consumos (requiere que existan pagos)
        consumos = crear_consumos(suscripciones)
        
        # 7. Mostrar estadísticas
        mostrar_estadisticas()
        
        print("\n" + "="*60)
        print("  ✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("="*60)
        print("\nPuedes acceder al sistema en: http://127.0.0.1:8000/pos/almuerzos/")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
