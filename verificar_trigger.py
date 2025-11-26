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
print("VERIFICACIÓN DE TRIGGERS Y CONFIGURACIÓN")
print("=" * 80)

# 1. Ver todos los triggers relacionados con stock
print("\n1. TRIGGERS ACTIVOS:")
print("-" * 80)
cursor.execute("SHOW TRIGGERS WHERE `Trigger` LIKE '%stock%'")
triggers = cursor.fetchall()

if triggers:
    for trigger in triggers:
        print(f"\nNombre: {trigger[0]}")
        print(f"Evento: {trigger[1]} {trigger[2]}")
        print(f"Tabla: {trigger[3]}")
        print(f"Timing: {trigger[4]}")
else:
    print("No se encontraron triggers relacionados con stock")

# 2. Ver el código completo del trigger
print("\n\n2. CÓDIGO DEL TRIGGER:")
print("-" * 80)
try:
    cursor.execute("SHOW CREATE TRIGGER trg_validar_stock_movimiento")
    trigger_code = cursor.fetchone()
    if trigger_code:
        print(trigger_code[2])  # El código está en la tercera columna
    else:
        print("No existe el trigger trg_validar_stock_movimiento")
except Exception as e:
    print(f"Error al obtener trigger: {e}")

# 3. Verificar productos con stock negativo permitido
print("\n\n3. PRODUCTOS CON STOCK NEGATIVO PERMITIDO:")
print("-" * 80)
cursor.execute("""
    SELECT p.ID_Producto, p.Codigo, p.Descripcion, p.Permite_Stock_Negativo,
           IFNULL(s.Stock_Actual, 0) as Stock_Actual
    FROM productos p
    LEFT JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
    WHERE p.Permite_Stock_Negativo = TRUE
""")
productos = cursor.fetchall()

if productos:
    for prod in productos:
        print(f"ID: {prod[0]} | Código: {prod[1]} | {prod[2]}")
        print(f"   Stock Negativo: {'SÍ' if prod[3] else 'NO'} | Stock Actual: {prod[4]}")
else:
    print("No hay productos configurados para stock negativo")

# 4. Ver estructura de la tabla productos
print("\n\n4. VERIFICAR CAMPO EN TABLA PRODUCTOS:")
print("-" * 80)
cursor.execute("DESCRIBE productos")
campos = cursor.fetchall()
permite_stock_campo = False
for campo in campos:
    if 'Permite_Stock_Negativo' in campo[0]:
        permite_stock_campo = True
        print(f"✓ Campo encontrado: {campo[0]} | Tipo: {campo[1]} | Null: {campo[2]} | Default: {campo[4]}")
        break

if not permite_stock_campo:
    print("✗ El campo Permite_Stock_Negativo NO existe en la tabla productos")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
