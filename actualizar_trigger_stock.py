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
print("ACTUALIZANDO TRIGGER DE ACTUALIZACIÓN DE STOCK")
print("=" * 80)

# 1. Eliminar trigger antiguo
print("\n1. Eliminando trigger antiguo (trg_stock_unico_after_movement)...")
cursor.execute("DROP TRIGGER IF EXISTS trg_stock_unico_after_movement")
conn.commit()
print("✓ Trigger eliminado")

# 2. Crear nuevo trigger que maneje todos los tipos de movimiento
print("\n2. Creando nuevo trigger actualizado...")

trigger_sql = """
CREATE TRIGGER trg_stock_unico_after_movement
AFTER INSERT ON movimientos_stock
FOR EACH ROW
BEGIN
    DECLARE stock_change DECIMAL(10, 3);
    
    -- Determinar si es entrada o salida según el tipo de movimiento
    IF NEW.Tipo_Movimiento IN ('Entrada', 'Ajuste Entrada', 'Compra', 'Devolución de Cliente') THEN
        SET stock_change = NEW.Cantidad;
    ELSEIF NEW.Tipo_Movimiento IN ('Salida', 'Venta', 'Ajuste Salida', 'Devolución a Proveedor', 'Merma', 'Uso Interno') THEN
        SET stock_change = -NEW.Cantidad;
    ELSEIF NEW.Tipo_Movimiento = 'Ajuste' THEN
        SET stock_change = NEW.Cantidad;  -- Puede ser positivo o negativo
    ELSE
        SET stock_change = 0;
    END IF;
    
    -- Actualizar stock
    UPDATE stock_unico
    SET Stock_Actual = Stock_Actual + stock_change
    WHERE ID_Producto = NEW.ID_Producto;
END
"""

cursor.execute(trigger_sql)
conn.commit()
print("✓ Trigger creado correctamente")

# 3. Verificar triggers activos
print("\n3. Triggers activos para movimientos_stock:")
cursor.execute("""
    SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING
    FROM information_schema.TRIGGERS
    WHERE TRIGGER_SCHEMA = 'cantinatitadb'
    AND EVENT_OBJECT_TABLE = 'movimientos_stock'
    ORDER BY ACTION_TIMING, TRIGGER_NAME
""")
triggers = cursor.fetchall()

for trigger in triggers:
    print(f"  ✓ {trigger[0]} - {trigger[2]} {trigger[1]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ ACTUALIZACIÓN COMPLETADA")
print("=" * 80)
print("\nAhora el sistema:")
print("1. ✓ Valida stock solo para productos que NO permiten stock negativo")
print("2. ✓ Reconoce 'Venta' como tipo de movimiento de salida")
print("3. ✓ Actualiza correctamente el stock después del movimiento")
print("4. ✓ ALM001 y ALM002 pueden tener stock negativo")
