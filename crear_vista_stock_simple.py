import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

# Vista simplificada de stock crítico (sin precios por ahora)
sql = """
CREATE OR REPLACE VIEW v_stock_critico_alertas AS
SELECT 
    p.ID_Producto,
    p.Codigo,
    p.Descripcion,
    p.Stock_Minimo,
    cat.Nombre AS Nombre_Categoria,
    CASE 
        WHEN p.Stock_Minimo = 0 THEN 'SIN STOCK MÍNIMO DEFINIDO'
        ELSE 'REQUIERE ATENCIÓN'
    END AS Nivel_Alerta
FROM productos p
LEFT JOIN categorias cat ON p.ID_Categoria = cat.ID_Categoria
WHERE p.Stock_Minimo > 0
ORDER BY p.Stock_Minimo ASC
"""

try:
    cursor.execute(sql)
    conn.commit()
    print("✓ Vista v_stock_critico_alertas creada exitosamente")
    print("  (Versión simplificada - solo muestra productos con stock mínimo definido)")
except Exception as e:
    print(f"✗ Error: {e}")

conn.close()
