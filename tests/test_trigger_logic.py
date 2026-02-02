import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import SuscripcionesAlmuerzo, PlanesAlmuerzo

# Obtener una suscripción real
suscripcion = SuscripcionesAlmuerzo.objects.filter(estado='Activa').first()

if suscripcion:
    print(f"\n=== ANÁLISIS DE SUSCRIPCIÓN ===")
    print(f"ID Suscripción: {suscripcion.id_suscripcion}")
    print(f"Estudiante: {suscripcion.id_hijo.nombre} {suscripcion.id_hijo.apellido}")
    print(f"Plan: {suscripcion.id_plan_almuerzo.nombre_plan}")
    print(f"Estado: {suscripcion.estado}")
    
    # Obtener días del plan
    plan = suscripcion.id_plan_almuerzo
    dias_plan = plan.dias_semana_incluidos
    print(f"\nDías incluidos en plan: '{dias_plan}'")
    print(f"Tipo de dato: {type(dias_plan)}")
    print(f"Longitud: {len(dias_plan)}")
    print(f"Representación bytes: {dias_plan.encode('utf-8')}")
    
    # Probar validación de días
    print(f"\n=== VALIDACIÓN DE DÍAS ===")
    dias_semana_es = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miércoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    # Probar con diferentes fechas
    hoy = date(2025, 11, 27)  # Miércoles
    for i in range(7):
        fecha_test = hoy + timedelta(days=i)
        dia_num = fecha_test.weekday()
        dia_nombre = dias_semana_es[dia_num]
        
        # Método 1: substring
        valido_substring = dia_nombre in dias_plan
        
        # Método 2: split por comas
        dias_lista = [d.strip() for d in dias_plan.replace(' a ', ',').replace(' y ', ',').split(',')]
        valido_lista = dia_nombre in dias_lista
        
        print(f"{fecha_test} ({dia_nombre}): substring={valido_substring}, lista={valido_lista}")
    
    # Ver si hay problemas de encoding
    print(f"\n=== COMPARACIONES DIRECTAS ===")
    print(f"'Lunes' in '{dias_plan}': {'Lunes' in dias_plan}")
    print(f"'Miércoles' in '{dias_plan}': {'Miércoles' in dias_plan}")
    print(f"'Viernes' in '{dias_plan}': {'Viernes' in dias_plan}")
    
    # Verificar el campo en la base de datos directamente
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID_Plan_Almuerzo,
                Nombre_Plan,
                Dias_Semana_Incluidos,
                CHAR_LENGTH(Dias_Semana_Incluidos) as longitud,
                HEX(Dias_Semana_Incluidos) as hex_value
            FROM planes_almuerzo
            WHERE ID_Plan_Almuerzo = %s
        """, [plan.id_plan_almuerzo])
        
        row = cursor.fetchone()
        if row:
            print(f"\n=== DATOS DIRECTOS DE LA BASE DE DATOS ===")
            print(f"ID: {row[0]}")
            print(f"Nombre: {row[1]}")
            print(f"Días: '{row[2]}'")
            print(f"Longitud: {row[3]}")
            print(f"HEX: {row[4]}")

else:
    print("No hay suscripciones activas")
