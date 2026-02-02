import MySQLdb
from datetime import datetime

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 80)
print("PRUEBA DE MOVIMIENTOS DE STOCK")
print("=" * 80)

# Obtener un producto de almuerzo y uno normal
cursor.execute("""
    SELECT p.ID_Producto, p.Codigo, p.Descripcion, p.Permite_Stock_Negativo,
           IFNULL(s.Stock_Actual, 0) as Stock_Actual
    FROM productos p
    LEFT JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
    WHERE p.Codigo IN ('ALM001', 'COC500')
    ORDER BY p.Codigo
""")
productos = cursor.fetchall()

print("\n1. PRODUCTOS DE PRUEBA:")
print("-" * 80)
for prod in productos:
    permite = "SÍ" if prod[3] else "NO"
    print(f"{prod[1]} - {prod[2]}")
    print(f"   Stock actual: {prod[4]} | Permite stock negativo: {permite}")

print("\n2. SIMULACIÓN DE MOVIMIENTOS:")
print("-" * 80)

# Test 1: Producto que permite stock negativo (ALM001)
print("\nTest 1: Vender 5 unidades de ALM001 (permite stock negativo)")
print("   Stock actual: 0.000")
print("   Cantidad a vender: 5.000")
print("   ✓ Debería permitir (stock resultante: -5.000)")

# Test 2: Producto que NO permite stock negativo (COC500)
cursor.execute("""
    SELECT IFNULL(Stock_Actual, 0) 
    FROM stock_unico 
    WHERE ID_Producto = (SELECT ID_Producto FROM productos WHERE Codigo = 'COC500')
""")
stock_coc = cursor.fetchone()
if stock_coc:
    stock_actual = float(stock_coc[0])
    print(f"\nTest 2: Vender 200 unidades de COC500 (NO permite stock negativo)")
    print(f"   Stock actual: {stock_actual}")
    print(f"   Cantidad a vender: 200.000")
    if stock_actual >= 200:
        print("   ✓ Debería permitir (hay stock suficiente)")
    else:
        print(f"   ✗ Debería rechazar (stock insuficiente, faltan {200 - stock_actual})")

print("\n3. INSTRUCCIONES PARA PRUEBA MANUAL:")
print("-" * 80)
print("\nVe a: http://127.0.0.1:8000/admin/gestion/movimientosstock/add/")
print("\nPrueba A - Producto con stock negativo permitido:")
print("  - ID Producto: ALM001 - ALMUERZO POR KILO")
print("  - Tipo movimiento: Venta")
print("  - Cantidad: 5.000")
print("  - ✅ Debería guardarse sin error")
print("  - Stock resultante: -5.000")

print("\nPrueba B - Producto SIN stock negativo permitido:")
print("  - ID Producto: COC500 - Coca Cola 500ml")
print("  - Tipo movimiento: Venta")
print(f"  - Cantidad: 999.000 (más del stock disponible)")
print("  - ❌ Debería dar error 'Stock insuficiente'")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ SISTEMA LISTO PARA PRUEBAS")
print("=" * 80)
