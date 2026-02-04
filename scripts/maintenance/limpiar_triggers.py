import MySQLdb

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 80)
print("LIMPIANDO TRIGGERS DUPLICADOS")
print("=" * 80)

# Eliminar el trigger antiguo que causa conflicto
print("\n1. Eliminando trigger antiguo (trg_movimiento_stock_before_insert)...")
try:
    cursor.execute("DROP TRIGGER IF EXISTS trg_movimiento_stock_before_insert")
    conn.commit()
    print("✓ Trigger antiguo eliminado")
except Exception as e:
    print(f"✗ Error: {e}")

# Verificar que solo quede el trigger correcto
print("\n2. Verificando triggers restantes...")
cursor.execute("SHOW TRIGGERS WHERE `Trigger` LIKE '%stock%'")
triggers = cursor.fetchall()

print(f"\nTriggers activos: {len(triggers)}")
for trigger in triggers:
    print(f"  - {trigger[0]} ({trigger[1]} {trigger[2]} on {trigger[3]})")

# Verificar productos configurados
print("\n3. Productos con stock negativo permitido:")
cursor.execute("""
    SELECT p.ID_Producto, p.Codigo, p.Descripcion, 
           IFNULL(s.Stock_Actual, 0) as Stock_Actual
    FROM productos p
    LEFT JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
    WHERE p.Permite_Stock_Negativo = TRUE
""")
productos = cursor.fetchall()

for prod in productos:
    print(f"  ✓ {prod[1]} - {prod[2]} (Stock: {prod[3]})")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ LIMPIEZA COMPLETADA")
print("=" * 80)
print("\nAhora puedes:")
print("1. Intentar crear movimiento de stock para productos de almuerzo")
print("2. El trigger trg_validar_stock_movimiento respetará Permite_Stock_Negativo")
print("3. Otros triggers (after insert, update) seguirán funcionando normalmente")
