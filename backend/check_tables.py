import os, django
os.chdir('D:\\anteproyecto20112025\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

print('=== HISTORICO_PRECIOS ===')
cursor.execute('DESCRIBE historico_precios')
for row in cursor.fetchall():
    print(f'{row[0]:40} {row[1]:20}')

print('\n=== PAGOS_PROVEEDORES ===')
cursor.execute('DESCRIBE pagos_proveedores')
for row in cursor.fetchall():
    print(f'{row[0]:40} {row[1]:20}')

print('\n=== AJUSTES_INVENTARIO ===')
cursor.execute('DESCRIBE ajustes_inventario')
for row in cursor.fetchall():
    print(f'{row[0]:40} {row[1]:20}')
