import MySQLdb

def verificar_tabla(cursor, nombre_tabla):
    cursor.execute(f"DESCRIBE {nombre_tabla}")
    columnas = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"TABLA: {nombre_tabla}")
    print(f"{'='*60}")
    for col in columnas:
        print(f"  {col[0]} ({col[1]})")

# Conexión
conexion = MySQLdb.connect(
    host="localhost",
    user="root",
    password="Tita.BioMol22",
    database="cantinatitadb",
    charset='utf8mb4'
)

cursor = conexion.cursor()

# Tablas con errores
tablas = [
    'clientes',
    'alertas_sistema',
    'conciliacion_pagos',
    'tarifas_comision',
    'impuestos'
]

for tabla in tablas:
    verificar_tabla(cursor, tabla)

cursor.close()
conexion.close()
