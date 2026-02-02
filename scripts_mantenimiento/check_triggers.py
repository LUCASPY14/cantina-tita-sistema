import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Ver triggers en la tabla tarjetas
    cursor.execute("SHOW TRIGGERS FROM cantinatitadb WHERE `Table` = 'tarjetas'")
    print("=== TRIGGERS EN TABLA 'tarjetas' ===")
    triggers = cursor.fetchall()
    if triggers:
        for trigger in triggers:
            print(f"\nTrigger: {trigger[0]}")
            print(f"Event: {trigger[1]}")
            print(f"Table: {trigger[2]}")
            print(f"Statement: {trigger[3][:200]}...")
    else:
        print("No hay triggers en la tabla 'tarjetas'")
    
    # Ver triggers en la tabla consumos_tarjeta
    cursor.execute("SHOW TRIGGERS FROM cantinatitadb WHERE `Table` = 'consumos_tarjeta'")
    print("\n\n=== TRIGGERS EN TABLA 'consumos_tarjeta' ===")
    triggers = cursor.fetchall()
    if triggers:
        for trigger in triggers:
            print(f"\nTrigger: {trigger[0]}")
            print(f"Event: {trigger[1]}")
            print(f"Table: {trigger[2]}")
            print(f"Statement completo:\n{trigger[3]}")
    else:
        print("No hay triggers en la tabla 'consumos_tarjeta'")
    
    # Verificar si existe la tabla Cta_Corriente
    cursor.execute("SHOW TABLES LIKE '%Corriente%'")
    print("\n\n=== TABLAS CON 'Corriente' ===")
    tables = cursor.fetchall()
    if tables:
        for table in tables:
            print(f"Tabla: {table[0]}")
    else:
        print("No se encontró ninguna tabla con 'Corriente' en el nombre")
