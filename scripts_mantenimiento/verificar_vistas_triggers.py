import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='cantinatitadb'
)

cursor = conn.cursor()

# Verificar vistas
print("=" * 60)
print("VISTAS EN LA BASE DE DATOS")
print("=" * 60)
cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
views = cursor.fetchall()
if views:
    for view in views:
        print(f"✓ {view[0]}")
else:
    print("No hay vistas en la BD")

# Verificar triggers
print("\n" + "=" * 60)
print("TRIGGERS EN LA BASE DE DATOS")
print("=" * 60)
cursor.execute("SHOW TRIGGERS")
triggers = cursor.fetchall()
if triggers:
    for trigger in triggers:
        print(f"✓ {trigger[0]}")
        print(f"  Evento: {trigger[1]} {trigger[2]}")
        print(f"  Tabla: {trigger[3]}")
        print()
else:
    print("No hay triggers en la BD")

# Verificar tablas relacionadas con cuenta corriente
print("\n" + "=" * 60)
print("TABLAS DE CUENTA CORRIENTE")
print("=" * 60)
cursor.execute("SHOW TABLES LIKE '%corriente%'")
cta_cte_tables = cursor.fetchall()
for table in cta_cte_tables:
    cursor.execute(f"SHOW FULL TABLES LIKE '{table[0]}'")
    table_info = cursor.fetchone()
    tipo = "VISTA" if table_info[1] == 'VIEW' else "TABLA"
    print(f"{tipo}: {table[0]}")
    
    if tipo == "TABLA":
        cursor.execute(f"DESCRIBE {table[0]}")
        campos = cursor.fetchall()
        for campo in campos:
            print(f"  - {campo[0]} ({campo[1]})")

cursor.close()
conn.close()
