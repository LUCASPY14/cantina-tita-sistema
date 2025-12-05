import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

# Ver triggers en registro_consumo_almuerzo
cursor = connection.cursor()
cursor.execute("SHOW TRIGGERS WHERE `Table` = 'registro_consumo_almuerzo'")
triggers = cursor.fetchall()

print('='*80)
print('TRIGGERS EN TABLA: registro_consumo_almuerzo')
print('='*80)

if not triggers:
    print('✓ No hay triggers en esta tabla')
else:
    for t in triggers:
        print(f'\nTrigger: {t[0]}')
        print(f'Event: {t[1]}')
        print(f'Table: {t[2]}')
        print(f'Statement: {t[3][:200]}...')  # Primeros 200 caracteres
        print(f'Timing: {t[4]}')
        print('-'*80)
        
        # Obtener definición completa
        cursor.execute(f"SHOW CREATE TRIGGER {t[0]}")
        definition = cursor.fetchone()
        if definition:
            print(f'\nDEFINICIÓN COMPLETA:')
            print(definition[2])  # SQL Original Statement
            print('='*80)

cursor.close()
