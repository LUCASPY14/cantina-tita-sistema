import MySQLdb

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("Ejecutando scripts SQL...")
print("-" * 50)

# 1. Actualizar productos de almuerzo
sql_update = """
UPDATE productos 
SET Permite_Stock_Negativo = TRUE 
WHERE Descripcion LIKE '%Almuerzo%' 
   OR Descripcion LIKE '%almuerzo%' 
   OR Codigo LIKE 'ALM%'
"""
cursor.execute(sql_update)
conn.commit()
print(f"✓ {cursor.rowcount} productos configurados para stock negativo")

# 2. Verificar productos configurados
sql_verify = """
SELECT ID_Producto, Codigo, Descripcion, Permite_Stock_Negativo
FROM productos
WHERE Permite_Stock_Negativo = TRUE
"""
cursor.execute(sql_verify)
results = cursor.fetchall()

print("\nProductos con stock negativo permitido:")
print("-" * 50)
for row in results:
    print(f"ID: {row[0]} | Código: {row[1]} | {row[2]}")

# 3. Crear nuevo trigger
print("\nCreando nuevo trigger de validación...")
print("-" * 50)

sql_trigger = """
CREATE TRIGGER trg_validar_stock_movimiento
BEFORE INSERT ON movimientos_stock
FOR EACH ROW
BEGIN
    DECLARE stock_actual_producto DECIMAL(10,3);
    DECLARE permite_negativo BOOLEAN;
    
    -- Obtener stock actual y configuración del producto
    SELECT s.Stock_Actual, COALESCE(p.Permite_Stock_Negativo, FALSE)
    INTO stock_actual_producto, permite_negativo
    FROM stock_unico s
    INNER JOIN productos p ON s.ID_Producto = p.ID_Producto
    WHERE s.ID_Producto = NEW.ID_Producto;
    
    -- Validar solo si NO permite stock negativo
    IF permite_negativo = FALSE THEN
        -- Solo validar en movimientos de salida
        IF NEW.Tipo_Movimiento IN ('Venta', 'Ajuste Salida', 'Devolución a Proveedor', 'Merma', 'Uso Interno') THEN
            IF stock_actual_producto < NEW.Cantidad THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Stock insuficiente para realizar la salida';
            END IF;
        END IF;
    END IF;
END
"""

cursor.execute(sql_trigger)
conn.commit()
print("✓ Trigger creado correctamente")

cursor.close()
conn.close()

print("\n" + "=" * 50)
print("✅ Script ejecutado exitosamente")
print("=" * 50)
print("\nAhora puedes:")
print("1. Reiniciar el servidor Django")
print("2. Intentar crear movimientos de stock para productos de almuerzo")
print("3. El stock puede quedar negativo para productos configurados")
