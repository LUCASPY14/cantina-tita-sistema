"""
Script para reparar vistas rotas en la base de datos
Corrige referencias a columnas renombradas y estructuras actualizadas
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
import django
django.setup()

from django.db import connection

def execute_sql(sql, description):
    """Ejecuta un comando SQL y maneja errores"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            print(f"  ✓ {description}")
            return True
    except Exception as e:
        print(f"  ✗ {description}")
        print(f"    Error: {str(e)[:100]}")
        return False

def repair_views():
    """Repara todas las vistas con errores"""
    
    print("\n" + "="*80)
    print("REPARACIÓN DE VISTAS - PRIORIDAD ALTA".center(80))
    print("="*80 + "\n")
    
    views_fixed = 0
    views_failed = 0
    
    # 1. v_ventas_dia_detallado - Corregir ID_Documento → Nro_Factura_Venta
    print("1. Reparando v_ventas_dia_detallado...")
    sql = """
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
        (v.Monto_Total - COALESCE(SUM(pv.Monto_Aplicado), 0)) AS Saldo_Pendiente
    FROM ventas v
    LEFT JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
    LEFT JOIN empleados e ON v.ID_Empleado_Cajero = e.ID_Empleado
    LEFT JOIN documentos_tributarios dt ON v.Nro_Factura_Venta = dt.ID_Documento
    LEFT JOIN detalle_venta dv ON v.ID_Venta = dv.ID_Venta
    LEFT JOIN productos p ON dv.ID_Producto = p.ID_Producto
    LEFT JOIN pagos_venta pv ON v.ID_Venta = pv.ID_Venta
    GROUP BY v.ID_Venta
    ORDER BY v.Fecha DESC
    """
    if execute_sql(sql, "v_ventas_dia_detallado"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 2. v_ventas_dia - Versión simplificada
    print("\n2. Reparando v_ventas_dia...")
    sql = """
    CREATE OR REPLACE VIEW v_ventas_dia AS
    SELECT 
        v.ID_Venta,
        v.Fecha,
        v.Monto_Total,
        v.Estado_Pago,
        v.Tipo_Venta,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Cliente,
        e.Nombre AS Empleado
    FROM ventas v
    INNER JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
    INNER JOIN empleados e ON v.ID_Empleado_Cajero = e.ID_Empleado
    WHERE DATE(v.Fecha) = CURDATE()
    ORDER BY v.Fecha DESC
    """
    if execute_sql(sql, "v_ventas_dia"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 3. v_saldo_clientes - Corregir lógica de saldo
    print("\n3. Reparando v_saldo_clientes...")
    sql = """
    CREATE OR REPLACE VIEW v_saldo_clientes AS
    SELECT 
        c.ID_Cliente,
        c.Nombres,
        c.Apellidos,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Nombre_Completo,
        c.Ruc_CI,
        tc.Nombre_Tipo AS Tipo_Cliente,
        COALESCE(SUM(CASE WHEN v.Estado_Pago IN ('PENDIENTE', 'PARCIAL') 
                          THEN v.Saldo_Pendiente ELSE 0 END), 0) AS Saldo_Actual,
        COUNT(v.ID_Venta) AS Total_Movimientos,
        MAX(v.Fecha) AS Ultima_Actualizacion
    FROM clientes c
    LEFT JOIN tipos_cliente tc ON c.ID_Tipo_Cliente = tc.ID_Tipo_Cliente
    LEFT JOIN ventas v ON c.ID_Cliente = v.ID_Cliente
    WHERE c.Activo = 1
    GROUP BY c.ID_Cliente
    """
    if execute_sql(sql, "v_saldo_clientes"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 4. v_saldo_proveedores - Similar a clientes
    print("\n4. Reparando v_saldo_proveedores...")
    sql = """
    CREATE OR REPLACE VIEW v_saldo_proveedores AS
    SELECT 
        p.ID_Proveedor,
        p.Razon_Social,
        p.RUC,
        COALESCE(SUM(CASE WHEN c.Estado_Pago IN ('PENDIENTE', 'PARCIAL') 
                          THEN c.Saldo_Pendiente ELSE 0 END), 0) AS Saldo_Actual,
        COUNT(c.ID_Compra) AS Total_Compras,
        MAX(c.Fecha) AS Ultima_Compra
    FROM proveedores p
    LEFT JOIN compras c ON p.ID_Proveedor = c.ID_Proveedor
    WHERE p.Activo = 1
    GROUP BY p.ID_Proveedor
    """
    if execute_sql(sql, "v_saldo_proveedores"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 5. v_stock_alerta - Productos con stock bajo
    print("\n5. Reparando v_stock_alerta...")
    sql = """
    CREATE OR REPLACE VIEW v_stock_alerta AS
    SELECT 
        p.ID_Producto,
        p.Codigo_Barra,
        p.Descripcion,
        c.Nombre AS Categoria,
        s.Stock_Actual,
        p.Stock_Minimo,
        (p.Stock_Minimo - s.Stock_Actual) AS Diferencia,
        CASE 
            WHEN s.Stock_Actual = 0 THEN 'CRÍTICO'
            WHEN s.Stock_Actual <= (p.Stock_Minimo * 0.5) THEN 'URGENTE'
            ELSE 'ALERTA'
        END AS Nivel_Alerta,
        s.Fecha_Ultima_Actualizacion,
        u.Nombre AS Unidad_Medida
    FROM productos p
    INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
    INNER JOIN categorias c ON p.ID_Categoria = c.ID_Categoria
    LEFT JOIN unidades_medida u ON p.ID_Unidad_de_Medida = u.ID_Unidad_de_Medida
    WHERE p.Activo = 1
    AND s.Stock_Actual <= p.Stock_Minimo
    ORDER BY s.Stock_Actual ASC, p.Descripcion
    """
    if execute_sql(sql, "v_stock_alerta"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 6. v_stock_critico_alertas - Solo productos críticos
    print("\n6. Reparando v_stock_critico_alertas...")
    sql = """
    CREATE OR REPLACE VIEW v_stock_critico_alertas AS
    SELECT 
        p.ID_Producto,
        p.Codigo_Barra,
        p.Descripcion,
        c.Nombre AS Categoria,
        s.Stock_Actual,
        p.Stock_Minimo
    FROM productos p
    INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
    INNER JOIN categorias c ON p.ID_Categoria = c.ID_Categoria
    WHERE p.Activo = 1
    AND s.Stock_Actual = 0
    ORDER BY p.Descripcion
    """
    if execute_sql(sql, "v_stock_critico_alertas"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 7. v_productos_mas_vendidos - Top productos
    print("\n7. Reparando v_productos_mas_vendidos...")
    sql = """
    CREATE OR REPLACE VIEW v_productos_mas_vendidos AS
    SELECT 
        p.ID_Producto,
        p.Codigo_Barra,
        p.Descripcion,
        c.Nombre AS Categoria,
        SUM(dv.Cantidad) AS Cantidad_Vendida,
        COUNT(DISTINCT dv.ID_Venta) AS Num_Ventas,
        SUM(dv.Precio_Unitario * dv.Cantidad) AS Total_Vendido
    FROM detalle_venta dv
    INNER JOIN productos p ON dv.ID_Producto = p.ID_Producto
    INNER JOIN categorias c ON p.ID_Categoria = c.ID_Categoria
    INNER JOIN ventas v ON dv.ID_Venta = v.ID_Venta
    WHERE v.Estado = 'COMPLETO'
    GROUP BY p.ID_Producto
    ORDER BY Cantidad_Vendida DESC
    LIMIT 50
    """
    if execute_sql(sql, "v_productos_mas_vendidos"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 8. v_tarjetas_detalle - Información de tarjetas
    print("\n8. Reparando v_tarjetas_detalle...")
    sql = """
    CREATE OR REPLACE VIEW v_tarjetas_detalle AS
    SELECT 
        t.Nro_Tarjeta,
        t.Saldo_Actual,
        t.Estado,
        t.Fecha_Vencimiento,
        h.Nombre AS Nombre_Hijo,
        h.Apellido AS Apellido_Hijo,
        CONCAT(h.Nombre, ' ', h.Apellido) AS Hijo_Completo,
        c.Nombres AS Nombre_Responsable,
        c.Apellidos AS Apellido_Responsable,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Responsable_Completo,
        c.Telefono,
        c.Email
    FROM tarjetas t
    INNER JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
    WHERE c.Activo = 1
    """
    if execute_sql(sql, "v_tarjetas_detalle"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 9. v_control_asistencia - Asistencia de hijos
    print("\n9. Reparando v_control_asistencia...")
    sql = """
    CREATE OR REPLACE VIEW v_control_asistencia AS
    SELECT 
        h.ID_Hijo,
        CONCAT(h.Nombre, ' ', h.Apellido) AS Hijo_Completo,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Responsable,
        COUNT(DISTINCT DATE(ct.Fecha_Consumo)) AS Dias_Asistencia,
        MAX(ct.Fecha_Consumo) AS Ultima_Asistencia,
        YEAR(CURDATE()) AS Anio,
        MONTH(CURDATE()) AS Mes
    FROM hijos h
    INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
    LEFT JOIN tarjetas t ON h.ID_Hijo = t.ID_Hijo
    LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
        AND YEAR(ct.Fecha_Consumo) = YEAR(CURDATE())
        AND MONTH(ct.Fecha_Consumo) = MONTH(CURDATE())
    WHERE h.Activo = 1
    GROUP BY h.ID_Hijo
    """
    if execute_sql(sql, "v_control_asistencia"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 10. v_notas_credito_detallado - Notas de crédito
    print("\n10. Reparando v_notas_credito_detallado...")
    sql = """
    CREATE OR REPLACE VIEW v_notas_credito_detallado AS
    SELECT 
        nc.ID_Nota,
        nc.Fecha,
        nc.Monto_Total,
        nc.Estado,
        nc.Observacion,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Cliente,
        v.ID_Venta AS Venta_Original,
        v.Fecha AS Fecha_Venta_Original,
        v.Monto_Total AS Monto_Venta_Original,
        COUNT(dn.ID_Detalle) AS Cantidad_Items,
        GROUP_CONCAT(CONCAT(p.Descripcion, ' (', dn.Cantidad, ')') SEPARATOR ', ') AS Productos
    FROM notas_credito_cliente nc
    INNER JOIN clientes c ON nc.ID_Cliente = c.ID_Cliente
    LEFT JOIN ventas v ON nc.ID_Venta_Original = v.ID_Venta
    LEFT JOIN detalle_nota dn ON nc.ID_Nota = dn.ID_Nota
    LEFT JOIN productos p ON dn.ID_Producto = p.ID_Producto
    GROUP BY nc.ID_Nota
    ORDER BY nc.Fecha DESC
    """
    if execute_sql(sql, "v_notas_credito_detallado"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 11. v_resumen_silencioso_hijo - Resumen hijo sin consumos
    print("\n11. Reparando v_resumen_silencioso_hijo...")
    sql = """
    CREATE OR REPLACE VIEW v_resumen_silencioso_hijo AS
    SELECT 
        h.ID_Hijo,
        CONCAT(h.Nombre, ' ', h.Apellido) AS Hijo_Completo,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Responsable,
        c.Telefono,
        c.Email,
        t.Nro_Tarjeta,
        t.Saldo_Actual,
        DATEDIFF(CURDATE(), MAX(ct.Fecha_Consumo)) AS Dias_Sin_Consumo,
        MAX(ct.Fecha_Consumo) AS Ultimo_Consumo
    FROM hijos h
    INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
    LEFT JOIN tarjetas t ON h.ID_Hijo = t.ID_Hijo
    LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
    WHERE h.Activo = 1
    GROUP BY h.ID_Hijo
    HAVING Dias_Sin_Consumo > 30 OR Dias_Sin_Consumo IS NULL
    ORDER BY Dias_Sin_Consumo DESC
    """
    if execute_sql(sql, "v_resumen_silencioso_hijo"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 12. v_saldo_tarjetas_compras - Saldo para compras
    print("\n12. Reparando v_saldo_tarjetas_compras...")
    sql = """
    CREATE OR REPLACE VIEW v_saldo_tarjetas_compras AS
    SELECT 
        t.Nro_Tarjeta,
        t.Saldo_Actual,
        CONCAT(h.Nombre, ' ', h.Apellido) AS Hijo,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Responsable,
        SUM(cs.Monto_Cargado) AS Total_Recargas,
        SUM(ct.Monto_Consumido) AS Total_Consumos,
        COUNT(DISTINCT ct.ID_Consumo) AS Num_Consumos
    FROM tarjetas t
    INNER JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
    LEFT JOIN cargas_saldo cs ON t.Nro_Tarjeta = cs.Nro_Tarjeta
    LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
    WHERE t.Estado = 'ACTIVA'
    GROUP BY t.Nro_Tarjeta
    """
    if execute_sql(sql, "v_saldo_tarjetas_compras"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # 13. vista_movimientos_cta_cte_clientes - Movimientos cuenta corriente
    print("\n13. Reparando vista_movimientos_cta_cte_clientes...")
    sql = """
    CREATE OR REPLACE VIEW vista_movimientos_cta_cte_clientes AS
    SELECT 
        v.ID_Venta AS ID_Movimiento,
        'VENTA' AS Tipo_Movimiento,
        v.Fecha AS Fecha_Movimiento,
        v.ID_Cliente,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Cliente,
        v.Monto_Total AS Monto,
        v.Saldo_Pendiente,
        v.Estado_Pago AS Estado
    FROM ventas v
    INNER JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
    WHERE v.Estado_Pago IN ('PENDIENTE', 'PARCIAL')
    ORDER BY v.Fecha DESC
    """
    if execute_sql(sql, "vista_movimientos_cta_cte_clientes"):
        views_fixed += 1
    else:
        views_failed += 1
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE REPARACIÓN".center(80))
    print("="*80)
    print(f"\n✅ Vistas reparadas exitosamente: {views_fixed}")
    print(f"❌ Vistas con errores: {views_failed}")
    print(f"📊 Total procesadas: {views_fixed + views_failed}")
    
    if views_failed == 0:
        print("\n🎉 ¡Todas las vistas fueron reparadas exitosamente!")
    else:
        print("\n⚠️  Algunas vistas requieren revisión manual")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    repair_views()
