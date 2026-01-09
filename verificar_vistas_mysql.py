import mysql.connector

# Conectar a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='cantinatitadb'
)

cursor = conn.cursor()

# Listar todas las vistas
print("="*80)
print("VISTAS DE LA BASE DE DATOS")
print("="*80)

cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
vistas = cursor.fetchall()

for vista in vistas:
    print(f"\n📊 Vista: {vista[0]}")
    
    # Intentar hacer un SELECT para ver si la vista funciona
    try:
        cursor.execute(f"SELECT * FROM {vista[0]} LIMIT 1")
        print(f"   ✅ FUNCIONA CORRECTAMENTE")
    except mysql.connector.Error as err:
        print(f"   ❌ ERROR: {err}")

cursor.close()
conn.close()

print("\n" + "="*80)
print("ANÁLISIS COMPLETO")
print("="*80)
