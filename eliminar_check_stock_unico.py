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
print("ELIMINANDO RESTRICCIÓN DE STOCK_UNICO")
print("=" * 80)

# 1. Ver las restricciones de la tabla stock_unico
print("\n1. Verificando restricciones en stock_unico...")
cursor.execute("""
    SELECT CONSTRAINT_NAME, CHECK_CLAUSE
    FROM information_schema.CHECK_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = 'cantinatitadb'
    AND CONSTRAINT_NAME LIKE 'stock_unico%'
""")
constraints = cursor.fetchall()

if constraints:
    print(f"Restricciones encontradas: {len(constraints)}")
    for constraint in constraints:
        print(f"  - {constraint[0]}: {constraint[1]}")
else:
    print("No se encontraron restricciones")

# 2. Eliminar la restricción que bloquea stock negativo
print("\n2. Eliminando restricción stock_unico_chk_1...")
try:
    cursor.execute("ALTER TABLE stock_unico DROP CHECK stock_unico_chk_1")
    conn.commit()
    print("✓ Restricción eliminada correctamente")
except Exception as e:
    print(f"Error: {e}")

# 3. Verificar productos con stock negativo permitido
print("\n3. Productos configurados para stock negativo:")
cursor.execute("""
    SELECT p.ID_Producto, p.Codigo, p.Descripcion, 
           p.Permite_Stock_Negativo,
           IFNULL(s.Stock_Actual, 0) as Stock_Actual
    FROM productos p
    LEFT JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
    WHERE p.Permite_Stock_Negativo = TRUE
""")
productos = cursor.fetchall()

for prod in productos:
    print(f"  ✓ {prod[1]} - {prod[2]}")
    print(f"    Stock: {prod[4]} | Permite negativo: SÍ")

# 4. Verificar estructura de stock_unico
print("\n4. Estructura de tabla stock_unico:")
cursor.execute("SHOW CREATE TABLE stock_unico")
create_table = cursor.fetchone()
if 'CHECK' in create_table[1]:
    print("  ⚠️  Aún hay restricciones CHECK en la tabla")
else:
    print("  ✓ No hay restricciones CHECK bloqueando stock negativo")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print("=" * 80)
print("\nAhora puedes:")
print("1. Reintentar crear el movimiento de stock")
print("2. Los productos ALM001 y ALM002 pueden tener stock negativo")
print("3. El stock se actualizará sin restricciones de valores negativos")
