import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Ver TODOS los triggers
    cursor.execute("SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA = 'cantinatitadb'")
    triggers = cursor.fetchall()
    print("=== TODOS LOS TRIGGERS EN cantinatitadb ===\n")
    
    for trigger_name, event, table in triggers:
        print(f"\n{'='*60}")
        print(f"Trigger: {trigger_name}")
        print(f"Event: {event} on {table}")
        print('='*60)
        
        # Ver el código completo
        cursor.execute(f"SHOW CREATE TRIGGER {trigger_name}")
        result = cursor.fetchone()
        if result:
            statement = result[2]
            # Buscar si menciona Cta_Corriente
            if 'Cta_Corriente' in statement or 'cta_corriente' in statement.lower():
                print("⚠️ ¡ESTE TRIGGER USA Cta_Corriente!")
                print(statement)
