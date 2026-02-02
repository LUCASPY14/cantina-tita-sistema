import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Ver el trigger de alerta saldo bajo completo
    cursor.execute("SHOW CREATE TRIGGER trg_alerta_saldo_bajo")
    print("=== TRIGGER: trg_alerta_saldo_bajo ===")
    result = cursor.fetchone()
    if result:
        print(result[2])  # El statement completo está en la columna 2
