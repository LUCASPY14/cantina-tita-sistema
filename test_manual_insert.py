import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import SuscripcionesAlmuerzo, RegistroConsumoAlmuerzo, PagosAlmuerzoMensual

# Obtener una suscripción activa con pago
suscripcion = SuscripcionesAlmuerzo.objects.filter(estado='Activa').first()

if suscripcion:
    print(f"\n=== PRUEBA DE INSERCIÓN MANUAL ===")
    print(f"Suscripción: {suscripcion.id_suscripcion}")
    print(f"Estudiante: {suscripcion.id_hijo.nombre} {suscripcion.id_hijo.apellido}")
    print(f"Plan: {suscripcion.id_plan_almuerzo.nombre_plan}")
    print(f"Días del plan: {suscripcion.id_plan_almuerzo.dias_semana_incluidos}")
    
    # Verificar pagos
    pagos = PagosAlmuerzoMensual.objects.filter(
        id_suscripcion=suscripcion,
        estado='Pagado'
    )
    print(f"\nPagos encontrados: {pagos.count()}")
    for pago in pagos:
        print(f"  - Mes: {pago.mes_pagado}, Estado: {pago.estado}, Monto: {pago.monto_mensual}")
    
    # Intentar crear un consumo para una fecha válida (Viernes 28/11/2025)
    fecha_test = date(2025, 11, 28)  # Viernes
    print(f"\n=== INTENTAR CREAR CONSUMO ===")
    print(f"Fecha: {fecha_test} (Viernes)")
    print(f"ID_Hijo: {suscripcion.id_hijo.id_hijo}")
    print(f"ID_Suscripcion: {suscripcion.id_suscripcion}")
    
    try:
        # Verificar si ya existe
        existe = RegistroConsumoAlmuerzo.objects.filter(
            id_hijo=suscripcion.id_hijo,
            fecha_consumo=fecha_test
        ).exists()
        
        if existe:
            print("⚠️  Ya existe un registro para esta fecha")
        else:
            # Intentar crear
            consumo = RegistroConsumoAlmuerzo.objects.create(
                id_hijo=suscripcion.id_hijo,
                fecha_consumo=fecha_test,
                id_suscripcion=suscripcion
            )
            print(f"✅ Consumo creado exitosamente: ID {consumo.id_registro_consumo}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
else:
    print("No hay suscripciones activas")
