import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Ver triggers
print("\n=== TRIGGERS en registro_consumo_almuerzo ===\n")
cursor.execute("SHOW TRIGGERS WHERE `Table` = 'registro_consumo_almuerzo'")
triggers = cursor.fetchall()

if triggers:
    for trigger in triggers:
        print(f"Trigger: {trigger[0]}")
        print(f"  Event: {trigger[1]}")
        print(f"  Table: {trigger[2]}")
        print(f"  Statement: {trigger[3][:200]}...")
        print(f"  Timing: {trigger[4]}")
        print()
else:
    print("No hay triggers")

# Ver definición completa de un trigger si existe
print("\n=== DEFINICIÓN COMPLETA DE TRIGGERS ===\n")
for trigger in triggers:
    cursor.execute(f"SHOW CREATE TRIGGER {trigger[0]}")
    result = cursor.fetchone()
    if result:
        print(f"--- {trigger[0]} ---")
        print(result[2])
        print("\n" + "="*60 + "\n")
