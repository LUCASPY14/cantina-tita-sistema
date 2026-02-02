import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("CREANDO VISTAS DE REPORTES AVANZADOS")
print("=" * 70)

vistas = [
    {
        'nombre': 'v_ventas_dia_detallado',
        'sql': """
        CREATE OR REPLACE VIEW v_ventas_dia_detallado AS
        SELECT 
            v.ID_Venta,
            v.Fecha,
            v.Monto_Total,
            c.Nombres,
            c.Apellidos,
            CONCAT(c.Nombres, ' ', c.Apellidos) AS Cliente_Completo,
            e.Nombre AS Empleado,
            dt.Nro_Timbrado,
            dt.Nro_Secuencial,
            COUNT(DISTINCT dv.ID_Detalle) AS Cantidad_Items,
            GROUP_CONCAT(CONCAT(p.Descripcion, ' (', dv.Cantidad, ')') SEPARATOR ', ') AS Productos,
            COALESCE(SUM(pv.Monto_Aplicado), 0) AS Total_Pagado,
            v.Monto_Total - COALESCE(SUM(pv.Monto_Aplicado), 0) AS Saldo_Pendiente
        FROM ventas v
        LEFT JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
        LEFT JOIN empleados e ON v.ID_Empleado_Cajero = e.ID_Empleado
        LEFT JOIN documentos_tributarios dt ON v.ID_Documento = dt.ID_Documento
        LEFT JOIN detalle_venta dv ON v.ID_Venta = dv.ID_Venta
        LEFT JOIN productos p ON dv.ID_Producto = p.ID_Producto
        LEFT JOIN pagos_venta pv ON v.ID_Venta = pv.ID_Venta
        GROUP BY v.ID_Venta
        ORDER BY v.Fecha DESC
        """,
        'descripcion': 'Vista completa de ventas con detalles de productos, clientes y pagos'
    },
    {
        'nombre': 'v_consumos_estudiante',
        'sql': """
        CREATE OR REPLACE VIEW v_consumos_estudiante AS
        SELECT 
            h.ID_Hijo,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            c.Nombres AS Responsable_Nombre,
            c.Apellidos AS Responsable_Apellido,
            t.Nro_Tarjeta,
            t.Saldo_Actual,
            COUNT(ct.ID_Consumo) AS Total_Consumos,
            COALESCE(SUM(ct.Monto_Consumido), 0) AS Total_Consumido,
            MAX(ct.Fecha_Consumo) AS Ultimo_Consumo,
            COUNT(cs.ID_Carga) AS Total_Recargas,
            COALESCE(SUM(cs.Monto_Cargado), 0) AS Total_Recargado
        FROM hijos h
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN tarjetas t ON h.ID_Hijo = t.ID_Hijo
        LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
        LEFT JOIN cargas_saldo cs ON t.Nro_Tarjeta = cs.Nro_Tarjeta
        GROUP BY h.ID_Hijo, t.Nro_Tarjeta
        ORDER BY h.Apellido, h.Nombre
        """,
        'descripcion': 'Resumen de consumos por estudiante con saldos y recargas'
    },
    {
        'nombre': 'v_stock_critico_alertas',
        'sql': """
        CREATE OR REPLACE VIEW v_stock_critico_alertas AS
        SELECT 
            p.ID_Producto,
            p.Codigo,
            p.Descripcion,
            p.Stock_Minimo,
            p.Stock_Resultante,
            p.Stock_Minimo - p.Stock_Resultante AS Unidades_Faltantes,
            ROUND((p.Stock_Resultante / NULLIF(p.Stock_Minimo, 0)) * 100, 2) AS Porcentaje_Stock,
            cat.Nombre AS Nombre_Categoria,
            hp.Precio_Nuevo AS Precio_Venta,
            hp.Precio_Nuevo * (p.Stock_Minimo - p.Stock_Resultante) AS Costo_Reposicion_Estimado,
            CASE 
                WHEN p.Stock_Resultante = 0 THEN 'CRÍTICO - SIN STOCK'
                WHEN p.Stock_Resultante < p.Stock_Minimo * 0.25 THEN 'URGENTE'
                WHEN p.Stock_Resultante < p.Stock_Minimo * 0.5 THEN 'BAJO'
                ELSE 'ATENCIÓN'
            END AS Nivel_Alerta
        FROM productos p
        LEFT JOIN categorias cat ON p.ID_Categoria = cat.ID_Categoria
        LEFT JOIN (SELECT ID_Producto, Precio_Nuevo FROM historico_precios ORDER BY Fecha_Cambio DESC LIMIT 1) hp ON p.ID_Producto = hp.ID_Producto
        WHERE p.Stock_Resultante <= p.Stock_Minimo
        ORDER BY 
            CASE 
                WHEN p.Stock_Resultante = 0 THEN 1
                WHEN p.Stock_Resultante < p.Stock_Minimo * 0.25 THEN 2
                WHEN p.Stock_Resultante < p.Stock_Minimo * 0.5 THEN 3
                ELSE 4
            END,
            p.Stock_Resultante ASC
        """,
        'descripcion': 'Productos con stock crítico ordenados por urgencia'
    },
    {
        'nombre': 'v_recargas_historial',
        'sql': """
        CREATE OR REPLACE VIEW v_recargas_historial AS
        SELECT 
            cs.ID_Carga,
            cs.Fecha_Carga,
            cs.Monto_Cargado,
            cs.Nro_Tarjeta,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            CONCAT(c.Nombres, ' ', c.Apellidos) AS Responsable,
            c.Telefono,
            e.Nombre AS Empleado_Registro,
            t.Saldo_Actual AS Saldo_Actual_Tarjeta
        FROM cargas_saldo cs
        INNER JOIN tarjetas t ON cs.Nro_Tarjeta = t.Nro_Tarjeta
        INNER JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN empleados e ON cs.ID_Cliente_Origen = e.ID_Empleado
        ORDER BY cs.Fecha_Carga DESC
        """,
        'descripcion': 'Historial completo de recargas con datos del estudiante y responsable'
    },
    {
        'nombre': 'v_resumen_caja_diario',
        'sql': """
        CREATE OR REPLACE VIEW v_resumen_caja_diario AS
        SELECT 
            DATE(v.Fecha) AS Fecha,
            COUNT(DISTINCT v.ID_Venta) AS Total_Ventas,
            SUM(v.Monto_Total) AS Monto_Total_Ventas,
            COUNT(DISTINCT cs.ID_Carga) AS Total_Recargas,
            COALESCE(SUM(cs.Monto_Cargado), 0) AS Monto_Total_Recargas,
            SUM(v.Monto_Total) + COALESCE(SUM(cs.Monto_Cargado), 0) AS Total_Ingresos_Dia,
            COUNT(DISTINCT pv.ID_Pago_Venta) AS Total_Transacciones_Pago,
            SUM(CASE WHEN mp.Descripcion = 'Efectivo' THEN pv.Monto_Aplicado ELSE 0 END) AS Total_Efectivo,
            SUM(CASE WHEN mp.Descripcion = 'Tarjeta Débito' THEN pv.Monto_Aplicado ELSE 0 END) AS Total_Tarjeta_Debito,
            SUM(CASE WHEN mp.Descripcion = 'Tarjeta Crédito' THEN pv.Monto_Aplicado ELSE 0 END) AS Total_Tarjeta_Credito,
            SUM(CASE WHEN mp.Descripcion = 'Transferencia' THEN pv.Monto_Aplicado ELSE 0 END) AS Total_Transferencias
        FROM ventas v
        LEFT JOIN pagos_venta pv ON v.ID_Venta = pv.ID_Venta
        LEFT JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
        LEFT JOIN cargas_saldo cs ON DATE(v.Fecha) = DATE(cs.Fecha_Carga)
        GROUP BY DATE(v.Fecha)
        ORDER BY Fecha DESC
        """,
        'descripcion': 'Resumen diario de ventas, recargas e ingresos por método de pago'
    }
]

resultados = []
for vista in vistas:
    try:
        cursor.execute(vista['sql'])
        conn.commit()
        resultados.append({'nombre': vista['nombre'], 'status': '✓', 'descripcion': vista['descripcion']})
        print(f"\n✓ Vista {vista['nombre']} creada exitosamente")
    except Exception as e:
        resultados.append({'nombre': vista['nombre'], 'status': '✗', 'descripcion': str(e)})
        print(f"\n✗ Error en {vista['nombre']}: {e}")

print("\n" + "=" * 70)
print("RESUMEN DE VISTAS CREADAS")
print("=" * 70)

for r in resultados:
    print(f"\n{r['status']} {r['nombre']}")
    print(f"   {r['descripcion']}")

print("\n" + "=" * 70)
print("✅ VISTAS DE REPORTES CONFIGURADAS")
print("=" * 70)

print("\nVistas disponibles para reportes:")
print("1. v_ventas_dia_detallado - Ventas completas con productos y pagos")
print("2. v_consumos_estudiante - Resumen por estudiante")
print("3. v_stock_critico_alertas - Productos a reponer")
print("4. v_recargas_historial - Historial de recargas")
print("5. v_resumen_caja_diario - Resumen financiero diario")

conn.close()
