import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Ver estructura real de la tabla planes_almuerzo
print("\n=== ESTRUCTURA DEL CAMPO Dias_Semana_Incluidos ===\n")
cursor.execute("SHOW COLUMNS FROM planes_almuerzo WHERE Field = 'Dias_Semana_Incluidos'")
column_info = cursor.fetchone()

if column_info:
    print(f"Campo: {column_info[0]}")
    print(f"Tipo: {column_info[1]}")
    print(f"Null: {column_info[2]}")
    print(f"Key: {column_info[3]}")
    print(f"Default: {column_info[4]}")
    print(f"Extra: {column_info[5]}")

# Ver ejemplos de datos
print("\n=== EJEMPLOS DE DATOS ===\n")
cursor.execute("""
    SELECT 
        ID_Plan_Almuerzo,
        Nombre_Plan,
        Dias_Semana_Incluidos,
        LENGTH(Dias_Semana_Incluidos) as len,
        HEX(Dias_Semana_Incluidos) as hex_val
    FROM planes_almuerzo 
    WHERE Activo = 1
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"  Nombre: {row[1]}")
    print(f"  Días: '{row[2]}'")
    print(f"  Longitud: {row[3]}")
    print(f"  HEX: {row[4][:50]}...")
    print()
