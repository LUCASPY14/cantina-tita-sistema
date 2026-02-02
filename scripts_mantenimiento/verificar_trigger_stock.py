import MySQLdb

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("TRIGGERS EN movimientos_stock")
print("=" * 70)

cursor.execute("SHOW TRIGGERS WHERE `Table` = 'movimientos_stock'")
triggers = cursor.fetchall()

for t in triggers:
    print(f"\n📌 Nombre: {t[0]}")
    print(f"   Evento: {t[1]}")
    print(f"   Timing: {t[4]}")
    print(f"   Tabla: {t[2]}")

print("\n" + "=" * 70)
print("DETALLE TRIGGER trg_stock_unico_after_movement")
print("=" * 70)

cursor.execute("SHOW CREATE TRIGGER trg_stock_unico_after_movement")
trigger_def = cursor.fetchone()
if trigger_def:
    print(trigger_def[2])

conn.close()
