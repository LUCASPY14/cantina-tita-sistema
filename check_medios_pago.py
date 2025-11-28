import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Ver estructura real de medios_pago
print("\n=== ESTRUCTURA REAL: medios_pago ===")
cursor.execute("SHOW COLUMNS FROM medios_pago")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]:30s} {col[1]:20s} {'NULL' if col[2]=='YES' else 'NOT NULL':10s} {col[3] if col[3] else ''}")

print("\n=== DATOS ===")
cursor.execute("SELECT * FROM medios_pago")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row}")
